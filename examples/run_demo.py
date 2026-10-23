"""Offline synthetic example through the real chat.py CLI; Linux/WSL only.

Never opens WeChat, reads real configuration, installs packages, or calls models.
The report body is prewritten test content, not an AI-generated analysis.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parents[1]
CLI = PACKAGE / 'scripts' / 'chat.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(root, *args):
    run = subprocess.run([sys.executable, str(CLI), '--root', str(root), *args],
                         capture_output=True, text=True, encoding='utf-8', timeout=20)
    if run.returncode:
        raise RuntimeError(run.stderr.strip())
    return json.loads(run.stdout)


def run_demo(output):
    if os.name == 'nt':
        raise ValueError('This example is tested on Linux/WSL; native Windows is not supported here')
    sys.path.insert(0, str(PACKAGE / 'scripts'))
    import workflow
    output = workflow.safe_path(output)
    if output.is_relative_to(PACKAGE):
        raise ValueError('Choose an output directory outside the installed package')
    if output.exists():
        raise ValueError('Output already exists; choose a new directory, never overwrite')
    output.mkdir(mode=0o700)  # Parent must exist; leave failed runs for inspection.
    snapshot = output / 'snapshot'
    (snapshot / 'contact').mkdir(parents=True, mode=0o700)
    (snapshot / 'message').mkdir(mode=0o700)
    account, peer, other = 'demo_self', 'demo_peer', 'demo_other'
    contact = snapshot / 'contact' / 'contact.db'
    message = snapshot / 'message' / 'message_0.db'
    with sqlite3.connect(contact) as con:
        con.execute('CREATE TABLE contact (username TEXT, nick_name TEXT, remark TEXT)')
        con.executemany('INSERT INTO contact VALUES (?,?,?)', [
            (account, 'Demo Self', ''), (peer, 'Demo Peer', 'Demo Peer'),
            (other, 'Other Peer', 'Other Peer')])
    def timestamp(value):
        return int(datetime.fromisoformat(value + '+08:00').timestamp())
    inputs = [
        (peer, '2024-10-01T09:00:00', 2, 'I will send the proposal by Friday.'),
        (peer, '2024-10-01T09:05:00', 1, 'I will review it after delivery.'),
        (peer, '2024-10-01T09:10:00', 2, 'Room booking is still unconfirmed.'),
        (peer, '2024-10-02T09:00:00', 2, 'OUTSIDE_SELECTED_SCOPE: next day'),
        (other, '2024-10-01T09:15:00', 3, 'OUTSIDE_SELECTED_SCOPE: other peer'),
    ]
    with sqlite3.connect(message) as con:
        con.execute('CREATE TABLE Name2Id (user_name TEXT)')
        con.executemany('INSERT INTO Name2Id(rowid,user_name) VALUES (?,?)',
                        [(1, account), (2, peer), (3, other)])
        for talker in (peer, other):
            table = 'Msg_' + hashlib.md5(talker.encode()).hexdigest()
            con.execute(f'CREATE TABLE [{table}] (local_id INTEGER, server_id INTEGER, local_type INTEGER, '
                        'create_time INTEGER, real_sender_id INTEGER, message_content TEXT, WCDB_CT_message_content INTEGER)')
            con.executemany(f'INSERT INTO [{table}] VALUES (?,?,?,?,?,?,?)',
                            [(i, 1000+i, 1, timestamp(time), sender, text, 0)
                             for i, (who, time, sender, text) in enumerate(inputs, 1) if who == talker])
    for path in (contact, message):
        with sqlite3.connect(path) as con:
            if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Synthetic SQLite integrity check failed')
    manifest = {'schema': 'wechat-archive-snapshot/v1', 'account': account,
                'snapshot_id': 'reader-demo-synthetic-v1', 'created_at': '2024-10-02T00:00:00+08:00',
                'provenance': {'kind': 'synthetic', 'capture_mode': 'main-db-only', 'wal_included': False,
                               'reports': [{'relative_path': str(p.relative_to(snapshot)),
                                            'plaintext_sha256': sha(p), 'integrity_ok': True}
                                           for p in (contact, message)]}}
    (snapshot / 'snapshot-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    private = output / 'private'
    private.mkdir(mode=0o700)
    # A demo-only config for saved snapshots; no default root or real account is read.
    (private / 'config.json').write_text(json.dumps({'schema': 'wechat-local-chat/config-v1',
                                                   'account': account, 'source_db_storage': str(snapshot)}), encoding='utf-8')
    selected = call(private, 'collect', '--name', 'Demo Peer', '--start', '2024-10-01', '--end', '2024-10-01',
                    '--question', 'Separate agreed actions from open questions.', '--snapshot', str(snapshot))
    request = selected['request_id']
    context = call(private, 'context', '--request', request, '--chunk-size', '2')
    chunks = [json.loads(Path(p).read_text(encoding='utf-8')) for p in context['paths']]
    rows = [m for chunk in chunks for m in chunk['messages']]
    if len(rows) != context['total_messages'] or len({m['id'] for m in rows}) != 3:
        raise RuntimeError('Demo context count/identity mismatch')
    if any('OUTSIDE_SELECTED_SCOPE' in m['text'] for m in rows):
        raise RuntimeError('Demo exclusion control failed')
    search = call(private, 'search', '--request', request, '--keyword', 'booking')
    draft = output / 'draft.md'
    text = ('# Prewritten synthetic demonstration / 预写合成演示\n\n'
            'No model was called. This body is a fixture, not AI analysis.\n'
            '未调用模型，以下正文是预写样本，不是 AI 分析。\n\n')
    text += '\n\n'.join('- ' + row['text'] + ' [消息:' + row['id'] + ']' for row in rows)
    draft.write_text(text + '\n', encoding='utf-8')
    saved = call(private, 'save-analysis', '--request', request, '--file', str(draft))
    report = Path(saved['path'])
    sidecar = report.with_suffix('.json')
    meta = json.loads(sidecar.read_text(encoding='utf-8'))
    meta['generated_by'] = 'prewritten synthetic fixture; no model called'
    sidecar.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if meta['report_sha256'] != sha(report) or set(meta['cited_message_ids']) != {row['id'] for row in rows}:
        raise RuntimeError('Demo report hash/citation mismatch')
    result = {'kind': 'synthetic-cli-example', 'selected_messages': selected['total'],
              'keyword_matches': search['count'], 'cited_messages': saved['cited_messages'],
              'excluded_controls': len(inputs)-len(rows), 'source_mode': selected['source_mode'],
              'wal_included': selected['wal_included'], 'model_called': False,
              'request_id': request, 'report_path': str(report), 'report_sha256': sha(report)}
    (output / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new directory outside the package; existing parent required')
    args = parser.parse_args()
    try:
        print(json.dumps(run_demo(args.output), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
