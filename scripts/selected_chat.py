"""Offline single-talker query for detached plaintext WeChat 4.x snapshots.

No acquisition, networking, cloud, keys, or process access. Account binding is a
caller assertion checked against snapshot-manifest.json, not independently proven.
Reviewed vocabulary: wx-cli-again src/daemon/query.rs and Yichen scripts/wechat_schema.py.
Only fixture-tested; actual WeChat version/schema compatibility requires validation.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import io
try:
    import zstandard
except ImportError:
    zstandard = None


def decode_content(value, marker, max_bytes=8 * 1024 * 1024):
    if type(marker) is not int or marker not in (0, 4):
        raise SelectedChatError('unknown content compression marker')
    if value is None and marker == 0:
        return '', 'empty'
    if isinstance(value, str):
        if marker != 0 or len(value.encode('utf-8')) > max_bytes:
            raise SelectedChatError('invalid plain content')
        return value, 'text'
    if not isinstance(value, bytes) or len(value) > max_bytes:
        raise SelectedChatError('invalid content bytes')
    compressed = marker == 4 or value.startswith(b'\x28\xb5\x2f\xfd')
    if compressed:
        if zstandard is None:
            raise SelectedChatError('zstandard dependency required')
        try:
            with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(value), read_across_frames=False) as reader:
                decoded = reader.read(max_bytes + 1)
            if len(decoded) > max_bytes:
                raise SelectedChatError('decompressed content exceeds limit')
            obj = zstandard.ZstdDecompressor().decompressobj()
            complete = obj.decompress(value)
            if not obj.eof or obj.unused_data or complete != decoded:
                raise SelectedChatError('truncated or trailing compressed data')
            return decoded.decode('utf-8', errors='strict'), 'zstd'
        except (zstandard.ZstdError, UnicodeDecodeError) as exc:
            raise SelectedChatError('invalid compressed UTF-8 content') from exc
    try:
        return value.decode('utf-8', errors='strict'), 'utf8-bytes'
    except UnicodeDecodeError as exc:
        raise SelectedChatError('invalid UTF-8 content') from exc

TZ = timezone(timedelta(hours=8))


class SelectedChatError(ValueError):
    """Fail-closed schema, scope, content or snapshot validation error."""


def date_window(start, end):
    """Inclusive calendar dates in fixed UTC+8, SQL half-open seconds."""
    try:
        if any(not isinstance(v, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', v) for v in (start, end)):
            raise ValueError
        first = datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=TZ)
        last = datetime.strptime(end, '%Y-%m-%d').replace(tzinfo=TZ)
        if first > last:
            raise ValueError
        return int(first.timestamp()), int((last + timedelta(days=1)).timestamp())
    except (ValueError, OverflowError) as exc:
        raise SelectedChatError('explicit valid YYYY-MM-DD date range required') from exc


def resolve_contact(root, talker, display_name):
    if (talker is None) == (display_name is None):
        raise SelectedChatError('choose exactly one talker or display name')
    chosen = talker if talker is not None else display_name
    if not isinstance(chosen, str) or not chosen or '\x00' in chosen:
        raise SelectedChatError('nonempty exact selector required')
    if talker is not None:
        return talker
    with closing(sqlite3.connect((root / 'contact/contact.db').as_uri() + '?mode=ro&immutable=1', uri=True)) as con:
        matches = con.execute("""SELECT DISTINCT username FROM contact WHERE
            CASE WHEN remark IS NOT NULL AND remark != '' THEN remark
                 WHEN nick_name IS NOT NULL AND nick_name != '' THEN nick_name
                 ELSE username END = ? COLLATE BINARY""", (display_name,)).fetchall()
    if len(matches) != 1:
        raise SelectedChatError('display name missing or ambiguous; use exact talker')
    return matches[0][0]


def query_selected(snapshot, account, start, end, talker=None, display_name=None, cutoff=None):
    begin, finish = date_window(start, end)
    if cutoff is not None:
        if type(cutoff) is not int or cutoff <= begin:
            raise SelectedChatError('invalid frozen cutoff')
        finish = min(finish, cutoff)
    if not isinstance(account, str) or not account or '\x00' in account:
        raise SelectedChatError('exact nonempty account required')
    root = Path(snapshot).absolute()
    source_manifest = json.loads((root / 'snapshot-manifest.json').read_text(encoding='utf-8'))
    if source_manifest.get('schema') != 'wechat-archive-snapshot/v1' or source_manifest.get('account') != account:
        raise SelectedChatError('snapshot account or schema mismatch')
    talker = resolve_contact(root, talker, display_name)
    table = 'Msg_' + hashlib.md5(talker.encode('utf-8')).hexdigest()
    records = []
    for path in sorted(p for p in (root / 'message').glob('message_*.db') if re.fullmatch(r'message_\d+\.db', p.name)):
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True)) as con:
            con.row_factory = sqlite3.Row
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
                continue
            names = dict(con.execute('SELECT rowid,user_name FROM Name2Id'))
            for raw in con.execute(f'SELECT rowid AS source_rowid,* FROM [{table}] WHERE create_time >= ? AND create_time < ? ORDER BY create_time,rowid', (begin, finish)):
                row = dict(raw)
                sender = names.get(row['real_sender_id'])
                content, encoding = decode_content(row['message_content'], row['WCDB_CT_message_content'])
                records.append({**row, 'account': account, 'talker': talker,
                                'shard': path.name, 'source_table': table,
                                'sender_username': sender,
                                'direction': 'unknown' if sender is None else ('outgoing' if sender == account else 'incoming'),
                                'content': content, 'content_encoding': encoding,
                                'time': datetime.fromtimestamp(row['create_time'], TZ).isoformat()})
    records.sort(key=lambda r: (r['create_time'], r['shard'], r['source_rowid']))
    return {'records': records, 'manifest': {'source_manifest': source_manifest,
            'talker': talker, 'record_count': len(records), 'start': start, 'end': end,
            'cutoff_exclusive': finish, 'all_selected_rows_traversed': True}}

def readable_content(record):
    import xml.etree.ElementTree as ET
    if record['local_type'] == 1:
        return record['content']
    if record['local_type'] & 0xffffffff == 49:
        try:
            app = ET.fromstring(record['content']).find('appmsg')
            if app is not None:
                kind = '[文件]' if app.findtext('type') == '6' else '[分享]'
                return kind + ' ' + (app.findtext('title') or '(无标题)')
        except ET.ParseError:
            return '[未解析的应用消息，原文保留]'
    return '[消息类型 '+str(record['local_type'])+'，原文保留]'


def search_selected(output, text):
    if not isinstance(text, str) or not text:
        raise SelectedChatError('nonempty literal search required')
    return [r for line in (Path(output)/'messages.jsonl').read_text(encoding='utf-8').splitlines()
            if text in readable_content(r := json.loads(line))]


def archive_identity(record, account, talker):
    """Canonical archive key, shared by retention and current-capture selection."""
    sid = record.get('server_id')
    identity = ['server', str(sid)] if sid not in (None, 0, '0', '') else ['local', record['shard'], record['source_table'], record['local_id'], record['create_time']]
    return hashlib.sha256(json.dumps([account, talker, *identity], ensure_ascii=False).encode()).hexdigest()


def persist_selected(result, output):
    import base64
    import os
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    def raw_json(value):
        if isinstance(value, bytes):
            return {'base64': base64.b64encode(value).decode('ascii')}
        raise TypeError(type(value).__name__)
    store = root / 'archive.sqlite'
    fd = os.open(store, os.O_CREAT | os.O_RDWR, 0o600)
    os.close(fd)
    with closing(sqlite3.connect(store)) as con:
        con.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        con.execute('CREATE TABLE IF NOT EXISTS scope (singleton INTEGER PRIMARY KEY CHECK(singleton=1), account TEXT,talker TEXT)')
        records = result['records']
        scope = (result['manifest']['source_manifest']['account'], result['manifest']['talker'])
        saved = con.execute('SELECT account,talker FROM scope').fetchone()
        if saved is not None and saved != scope:
            raise SelectedChatError('archive scope mismatch')
        con.execute('INSERT OR IGNORE INTO scope VALUES (1,?,?)', scope)
        inserted = 0
        for record in records:
            key = archive_identity(record, *scope)
            payload = json.dumps({**record, 'archive_id': key}, ensure_ascii=False, default=raw_json)
            prior = con.execute('SELECT 1 FROM messages WHERE id=?', (key,)).fetchone()
            inserted += prior is None
            con.execute('INSERT INTO messages VALUES (?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', (key,payload))
        con.commit()
        all_records = [json.loads(row[0]) for row in con.execute('SELECT payload FROM messages')]
    all_records.sort(key=lambda r:(r['create_time'],r['shard'],r['source_rowid']))
    begin, finish = date_window(result['manifest']['start'], result['manifest']['end'])
    finish = min(finish, result['manifest']['cutoff_exclusive'])
    selected_records = [r for r in all_records if begin <= r['create_time'] < finish]
    exports = {'messages.jsonl': ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in selected_records),
               'messages.md': '# 指定会话归档\n\n' + '\n\n'.join('## '+r['time']+' · '+r['direction']+' · '+r['archive_id'][:12]+'\n\n'+readable_content(r) for r in selected_records),
               'manifest.json': json.dumps(result['manifest'],ensure_ascii=False,indent=2)}
    for name,text in exports.items():
        tmp = root / (name+'.tmp')
        fd = os.open(tmp, os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,root/name)
    return {'inserted': inserted, 'total': len(all_records)}
