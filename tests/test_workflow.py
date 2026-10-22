"""Synthetic end-to-end publication tests; no user data or acquisition."""
import json
from pathlib import Path
from unittest.mock import patch
import test_selected_chat as fixtures
import unittest
import workflow


class WorkflowTests(unittest.TestCase):
    setUp=fixtures.SelectedChatTests.setUp
    module=fixtures.SelectedChatTests.module
    add=fixtures.SelectedChatTests.add
    query=fixtures.SelectedChatTests.query
    def test_preexisting_linked_output_ancestors_refused(self):
        self.add()
        result=self.query()
        for relative in ('nested','nested/.workflow.lock','nested/generations'):
            with self.subTest(path=relative):
                import tempfile
                with tempfile.TemporaryDirectory(dir=self.root.parent) as tmp:
                    base=Path(tmp);outside=base/'outside';outside.mkdir()
                    link=base/relative;link.parent.mkdir(parents=True,exist_ok=True)
                    link.symlink_to(outside,target_is_directory=True)
                    with self.assertRaisesRegex(ValueError,'linked'):
                        workflow.publish(result,base/'nested')
                    self.assertEqual([],list(outside.iterdir()))

    def test_exclusive_writer_rejects_concurrent_publish(self):
        self.add();out=self.root.parent/'published'
        with workflow.exclusive(out):
            with self.assertRaises(self.module().SelectedChatError):
                workflow.publish(self.query(),out)

    def test_status_has_durable_snapshot_reference(self):
        self.add()
        result=self.query()
        result['manifest']['snapshot_path']=str(self.root)
        out=self.root.parent/'published'
        workflow.publish(result,out)
        self.assertEqual(str(self.root),workflow.status(out)['snapshot_path'])

    def test_artifact_corruption_blocks_readers(self):
        self.add();out=self.root.parent/'published'
        workflow.publish(self.query(),out)
        _,path=workflow.current(out)
        (path/'messages.jsonl').write_text('[]\n')
        with self.assertRaises(self.module().SelectedChatError):
            workflow.search(out,'synthetic')

    def test_missing_record_not_shown_or_treated_as_proven_deletion(self):
        self.add();out=self.root.parent/'published'
        workflow.publish(self.query(),out)
        import sqlite3
        with sqlite3.connect(self.db) as con:
            con.execute(f'DELETE FROM [{self.table}]')
        report=workflow.publish(self.query(),out)
        self.assertEqual(1,report['changes']['missing'])
        self.assertEqual([],workflow.search(out))
        self.assertEqual(1,report['archive_total'])
        self.assertIn('not proof',report['missing_interpretation'])

    def test_publish_diff_and_failure_preserves_previous(self):
        self.add()
        out=self.root.parent/'published'
        first=workflow.publish(self.query(),out)
        self.assertEqual({'added':1,'updated':0,'unchanged':0,'missing':0},first['changes'])
        self.assertEqual(1,len(workflow.search(out,'synthetic')))
        self.add(lid=2,sid=102,ts=1727712001,content='new fixture')
        import sqlite3
        with sqlite3.connect(self.db) as con:
            con.execute(f'UPDATE [{self.table}] SET message_content=? WHERE server_id=101',('corrected fixture',))
        second=workflow.publish(self.query(),out)
        self.assertEqual({'added':1,'updated':1,'unchanged':0,'missing':0},second['changes'])
        pointer=(out/'current.json').read_bytes()
        original_replace=workflow.os.replace
        def fail_pointer(src,dest):
            if Path(dest).name=='current.json':
                raise OSError('synthetic disk failure')
            return original_replace(src,dest)
        with patch.object(workflow.os,'replace',side_effect=fail_pointer):
            with self.assertRaises(OSError):
                workflow.publish(self.query(),out)
        self.assertEqual(pointer,(out/'current.json').read_bytes())
        self.assertEqual(2,workflow.status(out)['total'])
        self.assertEqual(1,len(workflow.search(out,'corrected')))
        third=workflow.publish(self.query(),out)
        self.assertEqual({'added':0,'updated':0,'unchanged':2,'missing':0},third['changes'])
        self.assertEqual(3,len(workflow.history(out)))


if __name__=='__main__':
    import unittest
    unittest.main()
