"""Synthetic-only tests. No user databases or metadata are accessed."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

SCRATCH = Path(tempfile.gettempdir())


class SelectedChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='selected-chat-fixture-', dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'snapshot'
        (self.root / 'message').mkdir(parents=True)
        self.manifest = {'schema': 'wechat-archive-snapshot/v1', 'account': 'fixture_self',
                         'snapshot_id': 'synthetic-snapshot-1', 'provenance': {'kind': 'synthetic'}}
        (self.root / 'snapshot-manifest.json').write_text(json.dumps(self.manifest))
        self.talker = 'fixture_peer'
        self.table = 'Msg_' + hashlib.md5(self.talker.encode()).hexdigest()
        self.db = self.root / 'message/message_0.db'
        with sqlite3.connect(self.db) as con:
            con.execute(f'''CREATE TABLE [{self.table}] (
                local_id INTEGER, server_id, local_type INTEGER, create_time INTEGER,
                real_sender_id INTEGER, message_content, WCDB_CT_message_content INTEGER)''')
            con.execute('CREATE TABLE Name2Id (user_name TEXT)')
            con.executemany('INSERT INTO Name2Id(rowid,user_name) VALUES (?,?)',
                            [(1, 'fixture_self'), (2, self.talker)])
        (self.root / 'contact').mkdir()
        with sqlite3.connect(self.root / 'contact/contact.db') as con:
            con.execute('CREATE TABLE contact (username TEXT, nick_name TEXT, remark TEXT)')
            con.executemany('INSERT INTO contact VALUES (?,?,?)',
                            [(self.talker, 'Fixture Nick', 'Fixture Peer'),
                             ('fixture_self', 'Fixture Self', '')])

    def module(self):
        try:
            return importlib.import_module('selected_chat')
        except ModuleNotFoundError:
            self.fail('selected_chat module is not implemented')

    def add(self, lid=1, sid=101, ts=1727712000, content='synthetic body', ct=0, sender=2):
        # 2024-10-01 00:00:00 UTC+8
        with sqlite3.connect(self.db) as con:
            con.execute(f'INSERT INTO [{self.table}] VALUES (?,?,?,?,?,?,?)',
                        (lid, sid, 1, ts, sender, content, ct))

    def query(self, **kwargs):
        options = dict(snapshot=self.root, account='fixture_self', talker=self.talker,
                       start='2024-10-01', end='2024-10-01')
        options.update(kwargs)
        return self.module().query_selected(**options)

    def test_single_selected_chat_date_window_and_sender(self):
        self.add()
        self.add(lid=2, sid=102, ts=1727711999)
        self.add(lid=3, sid=103, ts=1727798399, sender=1)
        self.add(lid=4, sid=104, ts=1727798400)
        result = self.query()
        self.assertEqual([1, 3], [r['local_id'] for r in result['records']])
        self.assertEqual(['incoming', 'outgoing'], [r['direction'] for r in result['records']])
        self.assertEqual(['fixture_peer', 'fixture_self'], [r['sender_username'] for r in result['records']])
        self.assertEqual('2024-10-01T00:00:00+08:00', result['records'][0]['time'])
        self.assertEqual(2, result['manifest']['record_count'])
        self.assertEqual(self.manifest, result['manifest']['source_manifest'])
        self.assertTrue(result['manifest']['all_selected_rows_traversed'])

    def test_required_scope_exact_dates_and_no_cross_talker(self):
        m = self.module()
        for options in ({'account': ''}, {'account': 'wrong'}, {'talker': ''},
                        {'start': None}, {'end': None}, {'start': '2024-1-01'},
                        {'start': '2024-10-02'}, {'start': '2024-02-30'},
                        {'talker': self.talker, 'display_name': 'Fixture Peer'}):
            with self.subTest(options=options), self.assertRaises(m.SelectedChatError):
                self.query(**options)
        self.add()
        result = self.query(talker="x']; DROP TABLE contact;--")
        self.assertEqual([], result['records'])
        self.assertEqual(1, len(self.query()['records']))

    def test_exact_display_resolution_rejects_ambiguity_and_substrings(self):
        m = self.module()
        self.add()
        self.assertEqual(self.talker, self.query(talker=None, display_name='Fixture Peer')['manifest']['talker'])
        for name in ('Fixture', 'fixture peer', ''):
            with self.assertRaises(m.SelectedChatError):
                self.query(talker=None, display_name=name)
        with sqlite3.connect(self.root / 'contact/contact.db') as con:
            con.execute('INSERT INTO contact VALUES (?,?,?)', ('another_fixture', 'x', 'Fixture Peer'))
        with self.assertRaises(m.SelectedChatError):
            self.query(talker=None, display_name='Fixture Peer')
        self.assertEqual(1, len(self.query()['records']))

    def test_cutoff_and_archive_repeat(self):
        self.add()
        self.add(lid=2, sid=0, ts=1727712001)
        self.assertEqual(1, len(self.query(cutoff=1727712001)['records']))
        m = self.module()
        out = self.root.parent / 'archive'
        first = m.persist_selected(self.query(), out)
        second = m.persist_selected(self.query(), out)
        self.assertEqual(2, first['inserted'])
        self.assertEqual(0, second['inserted'])
        self.assertEqual(2, second['total'])
        self.assertTrue((out / 'messages.jsonl').exists())
        self.assertIn('synthetic body', (out / 'messages.md').read_text())
        self.assertEqual(2, len(m.search_selected(out, 'synthetic')))
        self.assertEqual([], m.search_selected(out, 'not present'))
        self.assertEqual('[文件] fixture.pdf', m.readable_content({'local_type': 25769803825, 'content':'<msg><appmsg><title>fixture.pdf</title><type>6</type></appmsg></msg>'}))
        # Narrowing the authorized view must not re-expose earlier archived rows.
        narrow = self.query(cutoff=1727712001)
        m.persist_selected(narrow, out)
        self.assertEqual(1, len(m.search_selected(out, 'synthetic')))

    def test_more_than_500_and_zero_ids_no_loss(self):
        with sqlite3.connect(self.db) as con:
            con.executemany(f'INSERT INTO [{self.table}] VALUES (?,?,?,?,?,?,?)',
                            [(i,0,1,1727712000,2,'fixture '+str(i),0) for i in range(1,604)])
        m=self.module()
        result=self.query()
        self.assertEqual(603,len(result['records']))
        out=self.root.parent/'many'
        self.assertEqual(603,m.persist_selected(result,out)['inserted'])
        self.assertEqual(0,m.persist_selected(result,out)['inserted'])
        self.assertEqual(603,len(m.search_selected(out,'fixture')))

    def test_zstd_strict_bounded_utf8_and_marker_validation(self):
        import zstandard as z
        m = self.module()
        encoded = z.ZstdCompressor().compress('fixture 中文'.encode())
        self.add(content=encoded, ct=4)
        result = self.query()
        self.assertEqual('fixture 中文', result['records'][0]['content'])
        self.assertEqual('zstd', result['records'][0]['content_encoding'])
        self.assertEqual('fixture 中文', m.decode_content(encoded, 4)[0])
        self.assertEqual('fixture 中文', m.decode_content(encoded, 0)[0])
        self.assertEqual('x'*20, m.decode_content(z.ZstdCompressor(write_content_size=False).compress(b'x'*20), 4, max_bytes=64)[0])
        invalid = [(encoded[:-1], 4), (encoded+b'junk', 4), (encoded+encoded, 4),
                   (b'not a frame', 4), ('plain but flagged', 4), (b'\xff', 0),
                   (None, 4), ('ok', 5), (b'ok', '4'), (123, 0),
                   (z.ZstdCompressor().compress(b'\xff'), 4)]
        for value, marker in invalid:
            with self.subTest(marker=marker, kind=type(value).__name__), self.assertRaises(m.SelectedChatError):
                m.decode_content(value, marker)
        for value, marker in [('界'*30, 0), (b'x'*65, 0),
                               (z.ZstdCompressor().compress(b'x'*200), 4),
                               (z.ZstdCompressor(write_content_size=False).compress(b'x'*200), 4)]:
            with self.assertRaises(m.SelectedChatError):
                m.decode_content(value, marker, max_bytes=64)
        from unittest.mock import patch
        with patch.object(m, 'zstandard', None), self.assertRaises(m.SelectedChatError):
            m.decode_content(encoded, 4)


if __name__ == '__main__':
    unittest.main()
