"""On-demand Windows/WSL main-database adapter. Keys remain native-runtime-only."""
from __future__ import annotations
from pathlib import Path
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
import runtime
from runtime import default_private_root, win_to_wsl, wsl_to_win

# Optional legacy-compatible override; do not resolve Windows metadata at import.
PRIVATE = Path(value) if (value := os.environ.get('WECHAT_LOCAL_CHAT_ROOT')) else None


def refresh(config):
    if runtime.platform_kind() not in ('windows', 'wsl'):
        raise RuntimeError('live acquisition requires Windows x64/WSL; offline snapshots are explicit reuse')
    root = runtime.local_path(config.get('private_root') or PRIVATE or default_private_root()).absolute()
    saved = runtime.load_config(root)
    if any(config.get(k) != saved[k] for k in ('schema', 'account', 'source_db_storage')):
        raise RuntimeError('capture config differs from private initialized configuration')
    root, source = runtime.validate_locations(root, runtime.local_path(saved['source_db_storage']))
    runtime.protect_private_root(root)
    files = [source / 'contact/contact.db', *sorted(p for p in (source / 'message').glob('message_*.db') if re.fullmatch(r'message_\d+\.db', p.name))]
    if len(files) < 2 or not all(runtime.reject_links(p).is_file() for p in files):
        raise RuntimeError('contact database and at least one message shard required')
    helper = runtime.reject_links(root / 'bin/probe_main.exe')
    if not helper.is_file():
        runtime.build(root)
    try:
        info = json.loads(runtime.powershell("Get-CimInstance Win32_Process -Filter \"Name='Weixin.exe'\" | Where-Object {$_.CommandLine -and $_.CommandLine -notmatch '--type='} | Select-Object ProcessId | ConvertTo-Json -Compress"))
    except (ValueError, TypeError):
        raise RuntimeError('exactly one accessible Weixin main process required') from None
    if not isinstance(info, dict) or type(info.get('ProcessId')) is not int or info['ProcessId'] <= 0:
        raise RuntimeError('exactly one accessible Weixin main process required')
    snapshot = root / ('snapshot_' + uuid.uuid4().hex)
    snapshot.mkdir(mode=0o700)
    reports = []
    try:
        for src in files:
            try:
                report = json.loads(runtime.run_command([str(helper), str(info['ProcessId']), runtime.windows_path(src), runtime.windows_path(root)], timeout=300))
                result = report['result']
                if (report.get('wechat_version') != '4.1.15.56' or report.get('capture_mode') != 'main-db-only'
                    or report.get('wal_included') is not False or report.get('source_copy_hash_stable') is not True
                    or report.get('original_modified') is not False or result.get('key_found') is not True
                    or result.get('all_nonzero_pages_hmac_valid') is not True or result.get('sqlite_integrity_ok') is not True):
                    raise ValueError()
                plain = runtime.reject_links(runtime.local_path(report['decrypted_path']))
                if not plain.is_relative_to(root) or plain.is_relative_to(snapshot) or plain.name != 'decrypted.db':
                    raise ValueError()
                with closing(sqlite3.connect(plain.as_uri() + '?mode=ro&immutable=1', uri=True)) as con:
                    if con.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                        raise ValueError()
                relative = src.relative_to(source)
                target = snapshot / relative
                target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                with plain.open('rb') as inp, os.fdopen(os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as out:
                    shutil.copyfileobj(inp, out)
                with target.open('rb') as inp:
                    sha = hashlib.file_digest(inp, 'sha256').hexdigest()
                reports.append({'relative_path': str(relative), 'plaintext_sha256': sha, 'integrity_ok': True,
                                'wechat_version': '4.1.15.56', 'capture_mode': 'main-db-only', 'wal_included': False,
                                'source_copy_hash_stable': True, 'original_modified': False,
                                'result': {k: result[k] for k in ('key_found', 'all_nonzero_pages_hmac_valid', 'sqlite_integrity_ok', 'pages_decrypted', 'zero_pages_preserved')}})
            except (OSError, ValueError, KeyError, TypeError, AttributeError, sqlite3.Error):
                raise RuntimeError('local capture evidence or SQLite validation failed; no private output is logged') from None
        manifest = {'schema': 'wechat-archive-snapshot/v1', 'account': saved['account'],
                    'snapshot_id': snapshot.name, 'created_at': datetime.now(timezone.utc).isoformat(),
                    'provenance': {'collector': 'local-csharp-readonly-main-v1', 'reports': reports,
                                   'capture_mode': 'main-db-only', 'wal_included': False, 'cross_database_atomic': False,
                                   'account_binding': 'explicit owner account/source directory; not independently attested',
                                   'completeness_warning': 'WAL is intentionally excluded; recent committed messages may be absent. Media files are not captured.'}}
        with os.fdopen(os.open(snapshot / 'snapshot-manifest.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as out:
            json.dump(manifest, out, ensure_ascii=False, indent=2)
        return snapshot
    except BaseException:
        shutil.rmtree(snapshot)
        raise
