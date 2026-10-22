"""Request-driven business workflow: synthetic data only."""
import importlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_selected_chat as fixtures
import workflow


class BusinessTests(unittest.TestCase):
    setUp=fixtures.SelectedChatTests.setUp
    add=fixtures.SelectedChatTests.add

    def module(self):
        try:
            return importlib.import_module('business')
        except ModuleNotFoundError:
            self.fail('request-driven business workflow is not implemented')

    def prepare(self):
        self.add()
        self.add(lid=2,sid=102,ts=1727715600,content='later fixture')
        self.private=self.root.parent/'private'
        self.private.mkdir(mode=0o700)
        (self.private/'config.json').write_text(json.dumps({
            'account':'fixture_self','source_db_storage':'synthetic-only'}))
        manifest=json.loads((self.root/'snapshot-manifest.json').read_text())
        manifest['created_at']='2024-10-02T00:00:00+08:00'
        manifest['provenance']={'capture_mode':'main-db-only','wal_included':False,'reports':[
            {'relative_path':str(p.relative_to(self.root)), 'plaintext_sha256':workflow.sha(p),'integrity_ok':True}
            for p in [self.db,self.root/'contact/contact.db']]}
        (self.root/'snapshot-manifest.json').write_text(json.dumps(manifest))

    def test_linked_business_directory_refuses_all_output(self):
        self.prepare();m=self.module()
        outside=self.root.parent/'outside';outside.mkdir()
        (self.private/'business').symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'linked'):
            m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        self.assertEqual([],list(outside.iterdir()))

    def test_saved_snapshot_refuses_nonprivate_output_root(self):
        self.prepare();m=self.module()
        self.private.chmod(0o755)
        with self.assertRaisesRegex(RuntimeError,'permissions'):
            m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        self.assertFalse((self.private/'business').exists())
        self.assertEqual(0o755,self.private.stat().st_mode & 0o777)

    def test_request_collects_exact_name_time_and_creates_evidence(self):
        self.prepare()
        m=self.module()
        result=m.collect(self.private,name='Fixture Nick',start='2024-10-01T00:00',
                         end='2024-10-01T00:30',question='What happened?',snapshot=self.root)
        self.assertEqual(1,result['total'])
        self.assertEqual('saved-snapshot',result['source_mode'])
        self.assertFalse(result['wal_included'])
        request=m.inspect_request(self.private,result['request_id'])
        self.assertEqual('Fixture Nick',request['name'])
        self.assertEqual(1,request['total'])
        chunks=m.context(self.private,result['request_id'])
        self.assertEqual(1,chunks['total_messages'])
        data=json.loads(Path(chunks['paths'][0]).read_text())
        self.assertEqual('synthetic body',data['messages'][0]['text'])
        self.assertEqual('What happened?',data['analysis_question'])
        self.assertEqual(64,len(data['messages'][0]['id']))
        self.assertIn('untrusted',data['kind'])
        repeated=m.collect(self.private,name='Fixture Nick',start='2024-10-01T00:00',
                         end='2024-10-01T00:30',snapshot=self.root)
        self.assertNotEqual(result['request_id'],repeated['request_id'])
        self.assertEqual(0,repeated['changes']['added'])
        self.assertEqual(1,m.inspect_request(self.private,result['request_id'])['total'])

    def test_ambiguous_names_and_unmatched_identity_do_not_publish(self):
        self.prepare();m=self.module()
        with sqlite3.connect(self.root/'contact/contact.db') as c:
            c.execute('INSERT INTO contact VALUES (?,?,?)',('other_peer','Fixture Nick','other'))
        manifest=json.loads((self.root/'snapshot-manifest.json').read_text())
        manifest['provenance']['reports'][1]['plaintext_sha256']=workflow.sha(self.root/'contact/contact.db')
        (self.root/'snapshot-manifest.json').write_text(json.dumps(manifest))
        for options in ({},{'talker':'not_a_match'}):
            with self.assertRaisesRegex(ValueError,'ambiguous'):
                m.collect(self.private,name='Fixture Nick',start='2024-10-01',end='2024-10-01',snapshot=self.root,**options)
        self.assertFalse((self.private/'business/requests').exists())
        r=m.collect(self.private,name='Fixture Nick',talker=self.talker,start='2024-10-01',end='2024-10-01',snapshot=self.root)
        self.assertEqual(2,r['total'])

    def test_tampered_snapshot_and_publication_refused(self):
        self.prepare();m=self.module()
        with patch('run_selected.refresh') as refresh:
            with self.assertRaises(ValueError):
                m.collect(self.private,name='Fixture Nick',start='2024-10-02',end='2024-10-01')
            refresh.assert_not_called()
        r=m.collect(self.private,name='Fixture Nick',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        request,_,path=m.load(self.private,r['request_id'])
        (path/'messages.jsonl').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'integrity'):
            m.context(self.private,r['request_id'])
        with self.db.open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'hash'):
            m.collect(self.private,name='Fixture Nick',start='2024-10-01',end='2024-10-01',snapshot=self.root)

    def test_reused_source_rowid_never_revives_historic_evidence(self):
        self.prepare();m=self.module()
        first=m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        _,original,_=m.load(self.private,first['request_id'])
        old_id=next(r['archive_id'] for r in original if r['server_id']==101)
        with sqlite3.connect(self.db) as con:
            con.execute(f'DELETE FROM [{self.table}] WHERE rowid=1')
            con.execute(f'INSERT INTO [{self.table}] (rowid,local_id,server_id,local_type,create_time,real_sender_id,message_content,WCDB_CT_message_content) VALUES (1,1,202,1,1727712000,2,?,0)',('replacement fixture',))
        manifest=json.loads((self.root/'snapshot-manifest.json').read_text())
        manifest['provenance']['reports'][0]['plaintext_sha256']=workflow.sha(self.db)
        (self.root/'snapshot-manifest.json').write_text(json.dumps(manifest))
        second=m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        request,rows,path=m.load(self.private,second['request_id'])
        self.assertEqual([102,202],sorted(r['server_id'] for r in rows))
        self.assertEqual(2,request['total'])
        self.assertEqual({'added':1,'updated':0,'unchanged':1,'missing':1},second['changes'])
        context=m.context(self.private,second['request_id'])
        ids={x['id'] for p in context['paths'] for x in json.loads(Path(p).read_text())['messages']}
        self.assertNotIn(old_id,ids)
        self.assertEqual(2,len(ids))
        with sqlite3.connect(path/'archive.sqlite') as con:
            self.assertEqual(3,con.execute('SELECT COUNT(*) FROM messages').fetchone()[0])
        self.assertEqual(2,len(m.load(self.private,first['request_id'])[1]))

    def test_report_discloses_snapshot_clipped_coverage(self):
        self.prepare();m=self.module()
        result=m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-05',snapshot=self.root)
        request,rows,_=m.load(self.private,result['request_id'])
        draft=self.root.parent/'coverage.md'
        draft.write_text('Observation [消息:'+rows[0]['archive_id']+']',encoding='utf-8')
        saved=Path(m.save_analysis(self.private,result['request_id'],draft)['path'])
        report=saved.read_text(encoding='utf-8')
        self.assertIn('请求范围：2024-10-01 至 2024-10-05',report)
        self.assertIn('证据时间窗：[2024-10-01T00:00:00+08:00, 2024-10-02T00:00:00+08:00)',report)
        self.assertIn('saved-snapshot',report)
        self.assertIn('快照采集时间：2024-10-02T00:00:00+08:00',report)
        self.assertIn('已截短',report)
        meta=json.loads(saved.with_suffix('.json').read_text(encoding='utf-8'))
        for key in ('begin_inclusive','requested_end_exclusive','effective_end_exclusive','source_mode','source_captured_at'):
            self.assertEqual(request[key],meta[key])
        self.assertIs(meta['coverage_clipped'],True)

    def test_citation_save_and_empty_result(self):
        self.prepare();m=self.module()
        r=m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        rows=m.search(self.private,r['request_id'],'synthetic')['messages']
        draft=self.root.parent/'draft.md';draft.write_text('unsupported analysis')
        with self.assertRaises(ValueError):m.save_analysis(self.private,r['request_id'],draft)
        draft.write_text('Fixture observation [消息:'+rows[0]['id']+']')
        saved=m.save_analysis(self.private,r['request_id'],draft)
        self.assertEqual(1,saved['cited_messages'])
        self.assertIn('主库模式',Path(saved['path']).read_text())
        r=m.collect(self.private,name='Fixture Peer',start='2024-10-01T02:00',end='2024-10-01T03:00',snapshot=self.root)
        self.assertEqual(0,r['total'])
        self.assertEqual(0,m.context(self.private,r['request_id'])['total_messages'])

    def test_over_500_messages_paginated_without_loss(self):
        self.prepare();m=self.module()
        with sqlite3.connect(self.db) as c:
            c.executemany(f'INSERT INTO [{self.table}] VALUES (?,?,?,?,?,?,?)',
                          [(i,1000+i,1,1727712000,2,'bulk '+str(i),0) for i in range(3,606)])
        manifest=json.loads((self.root/'snapshot-manifest.json').read_text())
        manifest['provenance']['reports'][0]['plaintext_sha256']=workflow.sha(self.db)
        (self.root/'snapshot-manifest.json').write_text(json.dumps(manifest))
        r=m.collect(self.private,name='Fixture Peer',start='2024-10-01',end='2024-10-01',snapshot=self.root)
        ctx=m.context(self.private,r['request_id'],100)
        self.assertEqual(605,ctx['total_messages']);self.assertEqual(7,ctx['chunks'])
        ids=[x['id'] for p in ctx['paths'] for x in json.loads(Path(p).read_text())['messages']]
        self.assertEqual(605,len(set(ids)))

    def test_cli_saved_request_can_be_found_and_queried(self):
        self.prepare()
        def call(*args):
            cli=Path(__file__).resolve().parents[1]/'scripts'/'chat.py'
            r=subprocess.run([sys.executable,str(cli),'--root',str(self.private),*args],capture_output=True,text=True,encoding='utf-8',timeout=20)
            self.assertEqual(0,r.returncode,r.stderr)
            return json.loads(r.stdout)
        r=call('collect','--name','Fixture Peer','--start','2024-10-01','--end','2024-10-01','--snapshot',str(self.root))
        history=call('history')
        self.assertEqual(r['request_id'],history['requests'][0]['request_id'])
        found=call('search','--request',r['request_id'],'--keyword','later')
        self.assertEqual(1,found['count'])
        self.assertEqual(2,call('context','--request',r['request_id'],'--chunk-size','1')['chunks'])


if __name__=='__main__':unittest.main()
