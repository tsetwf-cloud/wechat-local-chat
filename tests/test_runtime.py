"""Offline-only adapter tests. No live process, chat or key acquisition."""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        if importlib.util.find_spec('runtime'):
            runtime = importlib.import_module('runtime')
            if hasattr(runtime, 'platform_kind'):
                patcher = patch.object(runtime, 'platform_kind', return_value='linux')
                patcher.start()
                self.addCleanup(patcher.stop)

    def test_initialize_creates_private_explicit_config_and_refuses_overwrite(self):
        self.assertIsNotNone(importlib.util.find_spec('runtime'), 'runtime adapter must exist')
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'source'
            source.mkdir()
            root = base / 'private'
            old = os.umask(0)
            try:
                result = runtime.initialize(root, 'fixture_owner', source)
            finally:
                os.umask(old)
            config = json.loads((root / 'config.json').read_text(encoding='utf-8'))
            self.assertEqual(config, {'schema': 'wechat-local-chat/config-v1',
                                     'account': 'fixture_owner', 'source_db_storage': str(source)})
            self.assertFalse(result['capture_tested'])
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            self.assertEqual((root / 'config.json').stat().st_mode & 0o777, 0o600)
            before = (root / 'config.json').read_bytes()
            with self.assertRaises(RuntimeError):
                runtime.initialize(root, 'another_owner', source)
            self.assertEqual(before, (root / 'config.json').read_bytes())


    def test_initialize_rejects_unsafe_locations_and_missing_owner_without_writes(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'source'
            source.mkdir()
            cases = [(source / 'out', 'owner', source),
                     (base, 'owner', source),
                     (SCRIPTS / 'private_test', 'owner', source),
                     (base / 'private', '', source),
                     (base / 'private', 'owner', ''),
                     (base / 'private', 'owner', Path('relative'))]
            for root, account, src in cases:
                with self.subTest(root=root, account=account, source=src):
                    with self.assertRaises(RuntimeError):
                        runtime.initialize(root, account, src)
            link = base / 'linked'
            link.symlink_to(source, target_is_directory=True)
            with self.assertRaises(RuntimeError):
                runtime.initialize(link / 'out', 'owner', base / 'other')
            self.assertFalse((base / 'private').exists())
            self.assertFalse((source / 'out').exists())


    def test_portable_paths_and_private_default_use_windows_metadata_only(self):
        runtime = importlib.import_module('runtime')
        self.assertTrue(hasattr(runtime, 'default_private_root'), 'portable root API missing')
        self.assertEqual(str(runtime.win_to_wsl(r'E:\数据\db_storage')), '/mnt/e/数据/db_storage')
        self.assertEqual(runtime.wsl_to_win('/mnt/e/数据/db_storage'), 'E:\\数据\\db_storage')
        for path in ['relative', r'\\server\share\x', 'C:relative']:
            with self.assertRaises(RuntimeError):
                runtime.win_to_wsl(path)
        with self.assertRaises(RuntimeError):
            runtime.wsl_to_win('/home/test')
        with patch.object(runtime, 'platform_kind', return_value='wsl'), \
             patch.object(runtime, 'powershell', return_value=r'C:\Users\fixture\AppData\Local') as ps, \
             patch.object(runtime, 'os', SimpleNamespace(environ={})):
            root = runtime.default_private_root()
            self.assertEqual(str(root), '/mnt/c/Users/fixture/AppData/Local/WeChatLocalChat/private')
            self.assertEqual(ps.call_count, 1)
        with patch.object(runtime, 'platform_kind', return_value='linux'), patch.object(runtime, 'os', SimpleNamespace(environ={})):
            with self.assertRaises(RuntimeError):
                runtime.default_private_root()


    def test_windows_initialize_verifies_acl_before_config_creation(self):
        runtime = importlib.import_module('runtime')
        self.assertTrue(hasattr(runtime, 'protect_private_root'), 'ACL protection missing')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            source = base / 'source'
            with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                 patch.object(runtime, 'windows_path', side_effect=lambda x: str(x)), \
                 patch.object(runtime, 'powershell', side_effect=RuntimeError('ACL unavailable')):
                with self.assertRaises(RuntimeError):
                    runtime.initialize(root, 'owner', source)
                self.assertFalse((root / 'config.json').exists())
            def fake_acl(script):
                root.mkdir()
                return '{"private_acl":true}'
            with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                 patch.object(runtime, 'windows_path', side_effect=lambda x: str(x)), \
                 patch.object(runtime, 'powershell', side_effect=fake_acl) as ps:
                runtime.initialize(root, 'owner', source)
                script = ps.call_args.args[0]
                self.assertIn('SetAccessRuleProtection', script)
                self.assertIn('S-1-5-18', script)
                self.assertIn('GetAccessRules', script)
                self.assertNotIn('ExecutionPolicy', script)
                self.assertTrue((root / 'config.json').exists())


    def test_doctor_offline_reports_no_live_validation_without_process_scan(self):
        runtime = importlib.import_module('runtime')
        self.assertTrue(hasattr(runtime, 'doctor'), 'doctor missing')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'secret_owner', base / 'source')
            with patch.object(runtime, 'powershell', side_effect=AssertionError('offline must not invoke Windows')):
                status = runtime.doctor(root)
            self.assertTrue(status['configured'])
            self.assertFalse(status['capture_ready'])
            self.assertFalse(status['capture_tested'])
            self.assertFalse(status['helper_built'])
            self.assertEqual(status['supported_weixin_version'], '4.1.15.56')
            self.assertNotIn('secret_owner', json.dumps(status))
            self.assertNotIn(str(root), json.dumps(status))
            self.assertFalse(status['process_memory_read'])


    def test_build_stages_only_package_sources_and_deploys_after_fixture_success(self):
        runtime = importlib.import_module('runtime')
        self.assertTrue(hasattr(runtime, 'build'), 'build missing')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'owner', base / 'source')
            with self.assertRaises(RuntimeError):
                runtime.build(root)
            package = base / 'package'
            for directory, names in [('scripts/native/src', ['Main.cs', 'Probe.cs', 'Runtime.cs']),
                                     ('tests/native', ['MainFixture.cs', 'SecurityFixture.cs'])]:
                (package / directory).mkdir(parents=True)
                for name in names:
                    (package / directory / name).write_text('// synthetic source only')
            calls = []
            def compiler(args, timeout=120):
                calls.append(args)
                for arg in args:
                    if str(arg).startswith('/out:'):
                        Path(str(arg)[5:]).write_bytes(b'fixture executable stub, never executed')
                return '{"fixture_checks":6,"passed":true,"real_data_used":false}'
            with patch.object(runtime, 'PACKAGE', package), \
                 patch.object(runtime, 'native_dependencies', return_value={'csc': 'csc.exe', 'compiler_available': True, 'sqlite_available': True, 'windows_x64': True}), \
                 patch.object(runtime, 'protect_private_root'), \
                 patch.object(runtime, 'windows_path', side_effect=str), \
                 patch.object(runtime, 'run_command', side_effect=compiler):
                result = runtime.build(root, test=True)
            self.assertTrue(result['helper_built'])
            self.assertTrue(result['fixture_tests_passed'])
            self.assertFalse(result['capture_tested'])
            self.assertTrue((root / 'bin/probe_main.exe').exists())
            self.assertEqual(len(calls), 5)
            self.assertIn('/platform:x64', calls[0])
            self.assertIn('/main:MainCollector', calls[0])
            self.assertFalse(any('ExecutionPolicy' in str(arg) for args in calls for arg in args))
            self.assertFalse((package / 'bin').exists())


    def test_refresh_offline_rejects_without_process_access(self):
        self.assertIsNotNone(importlib.util.find_spec('run_selected'), 'capture adapter missing')
        adapter = importlib.import_module('run_selected')
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'owner', base / 'source')
            config = runtime.load_config(root)
            config['private_root'] = str(root)
            with patch.object(runtime, 'powershell', side_effect=AssertionError('no process access offline')):
                with self.assertRaises(RuntimeError):
                    adapter.refresh(config)
            self.assertFalse(any(root.glob('snapshot_*')))


    def test_refresh_publishes_only_verified_synthetic_main_databases(self):
        runtime = importlib.import_module('runtime')
        adapter = importlib.import_module('run_selected')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'source'
            for rel in ('contact/contact.db', 'message/message_0.db', 'message/message_2.db'):
                path = source / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                import sqlite3
                with sqlite3.connect(path) as con:
                    con.execute('CREATE TABLE synthetic(value INTEGER)')
            (source / 'message/not_a_shard.db').write_bytes(b'ignored')
            (source / 'message/message_0.db-wal').write_bytes(b'WAL intentionally excluded')
            root = base / 'private'
            runtime.initialize(root, 'fixture_owner', source)
            config = dict(runtime.load_config(root), private_root=str(root))
            captured = []
            def helper(args, timeout=120):
                import shutil
                src = Path(args[2])
                output = root / ('helper_' + str(len(captured))) / 'decrypted.db'
                output.parent.mkdir()
                shutil.copyfile(src, output)
                captured.append(src)
                return json.dumps({'wechat_version': '4.1.15.56', 'pid': 123,
                    'source_name': src.name, 'decrypted_path': str(output),
                    'source_copy_hash_stable': True, 'capture_mode': 'main-db-only',
                    'wal_included': False, 'original_modified': False,
                    'result': {'key_found': True, 'all_nonzero_pages_hmac_valid': True,
                               'pages_decrypted': 2, 'zero_pages_preserved': 0,
                               'sqlite_integrity_ok': True}, 'unexpected_secret': 'must_not_persist'})
            def fake_build(root_arg):
                (root / 'bin').mkdir()
                (root / 'bin/probe_main.exe').write_bytes(b'not executed')
            with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                 patch.object(runtime, 'protect_private_root'), \
                 patch.object(runtime, 'windows_path', side_effect=str), \
                 patch.object(runtime, 'powershell', return_value='{"ProcessId":123}') as process, \
                 patch.object(runtime, 'run_command', side_effect=helper), \
                 patch.object(runtime, 'build', side_effect=fake_build) as build:
                snapshot = adapter.refresh(config)
            self.assertEqual(build.call_count, 1)
            self.assertEqual(len(captured), 3)
            self.assertIn('Win32_Process', process.call_args.args[0])
            manifest = json.loads((snapshot / 'snapshot-manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['schema'], 'wechat-archive-snapshot/v1')
            self.assertEqual(manifest['account'], 'fixture_owner')
            self.assertFalse(manifest['provenance']['wal_included'])
            self.assertFalse(manifest['provenance']['cross_database_atomic'])
            self.assertEqual(len(manifest['provenance']['reports']), 3)
            self.assertNotIn('must_not_persist', json.dumps(manifest))
            self.assertFalse(any(snapshot.rglob('*-wal')))
            import hashlib
            for report in manifest['provenance']['reports']:
                self.assertTrue(report['integrity_ok'])
                self.assertEqual(report['plaintext_sha256'], hashlib.sha256((snapshot / report['relative_path']).read_bytes()).hexdigest())


    def test_initialize_rejects_traversal_alias_before_writing(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'source'
            source.mkdir()
            wrapper = base / 'wrapper'
            wrapper.mkdir()
            with self.assertRaises(RuntimeError):
                runtime.initialize(wrapper / '..' / 'source' / 'output', 'owner', source)
            self.assertFalse((source / 'output').exists())


    def test_subprocess_transport_is_utf8_bounded_and_never_leaks_failure_output(self):
        runtime = importlib.import_module('runtime')
        with patch.object(runtime.subprocess, 'run') as run:
            run.return_value = runtime.subprocess.CompletedProcess(['safe'], 0, '\ufeff中文\n', '')
            self.assertEqual(runtime.run_command(['safe', 'space and quote\"'], timeout=7), '中文')
            self.assertFalse(run.call_args.kwargs['shell'])
            self.assertEqual(run.call_args.kwargs['timeout'], 7)
            self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
            run.return_value = runtime.subprocess.CompletedProcess(['safe'], 1, 'private_key_or_text', 'private_path')
            with self.assertRaises(RuntimeError) as caught:
                runtime.run_command(['safe'])
            self.assertNotIn('private_key_or_text', str(caught.exception))
            self.assertNotIn('private_path', str(caught.exception))
        self.assertEqual(runtime.ps_literal("C:\\目录\\a'b"), "'C:\\目录\\a''b'")

    def test_refresh_rejects_ambiguous_process_and_bad_capture_flags_without_manifest(self):
        runtime = importlib.import_module('runtime')
        adapter = importlib.import_module('run_selected')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            source = base / 'source'
            for rel in ('contact/contact.db', 'message/message_0.db'):
                p = source / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'synthetic-invalid-sqlite')
            runtime.initialize(root, 'owner', source)
            (root / 'bin').mkdir()
            (root / 'bin/probe_main.exe').write_bytes(b'never executed')
            config = dict(runtime.load_config(root), private_root=str(root))
            for process in ('null', '[]', '[{"ProcessId":1},{"ProcessId":2}]', '{"ProcessId":true}'):
                with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                     patch.object(runtime, 'protect_private_root'), \
                     patch.object(runtime, 'powershell', return_value=process), \
                     patch.object(runtime, 'run_command', side_effect=AssertionError('must reject before helper')):
                    with self.assertRaises(RuntimeError):
                        adapter.refresh(config)
            with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                 patch.object(runtime, 'protect_private_root'), \
                 patch.object(runtime, 'powershell', return_value='{"ProcessId":123}'), \
                 patch.object(runtime, 'windows_path', side_effect=str), \
                 patch.object(runtime, 'run_command', return_value='{"result":{"key_found":true},"wal_included":true}'):
                with self.assertRaises(RuntimeError):
                    adapter.refresh(config)
            self.assertFalse(any(root.glob('snapshot_*')))
            bad_config = dict(config, account='another_owner')
            with patch.object(runtime, 'platform_kind', return_value='wsl'), \
                 patch.object(runtime, 'powershell', side_effect=AssertionError('must reject config before process')):
                with self.assertRaises(RuntimeError):
                    adapter.refresh(bad_config)

    def test_local_path_accepts_mounted_paths_for_native_windows(self):
        runtime = importlib.import_module('runtime')
        with patch.object(runtime.os, 'name', 'nt'), patch.object(runtime, 'Path', side_effect=lambda s: s):
            self.assertEqual(str(runtime.local_path('/mnt/e/目录/db_storage')), 'E:\\目录\\db_storage')


    def test_initialize_windows_form_source_is_portably_stored_without_opening_it(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'private'
            runtime.initialize(root, 'owner', r'E:\synthetic_account\db_storage')
            config = runtime.load_config(root)
            self.assertEqual(str(runtime.local_path(config['source_db_storage'])), '/mnt/e/synthetic_account/db_storage')

    def test_doctor_never_marks_missing_native_sources_build_ready(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'owner', base / 'source')
            with patch.object(runtime, 'PACKAGE', base / 'missing_package'):
                status = runtime.doctor(root)
            self.assertIn('native_sources_available', status)
            self.assertFalse(status['native_sources_available'])
            self.assertFalse(status['build_ready'])


    def test_failed_fixture_build_preserves_previous_helper(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'owner', base / 'source')
            (root / 'bin').mkdir()
            target = root / 'bin/probe_main.exe'
            target.write_bytes(b'previous-good-helper')
            call_count = 0
            def fail_fixture(args, timeout=120):
                nonlocal call_count
                call_count += 1
                for arg in args:
                    if str(arg).startswith('/out:'):
                        Path(str(arg)[5:]).write_bytes(b'synthetic-staged-helper')
                if call_count == 3:
                    raise RuntimeError('synthetic fixture failure')
                return ''
            with patch.object(runtime, 'native_dependencies', return_value={'csc': 'csc.exe', 'compiler_available': True, 'sqlite_available': True, 'windows_x64': True}), \
                 patch.object(runtime, 'windows_path', side_effect=str), \
                 patch.object(runtime, 'run_command', side_effect=fail_fixture):
                with self.assertRaises(RuntimeError):
                    runtime.build(root, test=True)
            self.assertEqual(target.read_bytes(), b'previous-good-helper')
            self.assertFalse(any((root / 'bin').glob('build_*')))

    def test_doctor_missing_private_root_is_sanitized(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            status = runtime.doctor(Path(tmp) / 'missing')
            self.assertFalse(status['configured'])
            self.assertFalse(status['private_root_verified'])
            self.assertFalse(status['capture_ready'])

    def test_initialize_rejects_source_inside_package(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'private'
            with self.assertRaises(RuntimeError):
                runtime.initialize(root, 'owner', SCRIPTS / 'native/src')
            self.assertFalse(root.exists())


    def test_build_stages_sources_for_wsl_package_on_linux_filesystem(self):
        runtime = importlib.import_module('runtime')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'private'
            runtime.initialize(root, 'owner', base / 'source')
            converted = []
            def only_private_paths(path):
                path = Path(path)
                self.assertTrue(path.is_relative_to(root), 'Windows compiler cannot directly read WSL-only package paths')
                converted.append(path)
                return str(path)
            def compiler(args, timeout=120):
                for arg in args:
                    if str(arg).startswith('/out:'):
                        Path(str(arg)[5:]).write_bytes(b'never executed')
                return ''
            with patch.object(runtime, 'native_dependencies', return_value={'csc': 'csc.exe', 'compiler_available': True, 'sqlite_available': True, 'windows_x64': True}), \
                 patch.object(runtime, 'windows_path', side_effect=only_private_paths), \
                 patch.object(runtime, 'run_command', side_effect=compiler):
                runtime.build(root)
            self.assertTrue((root / 'bin/probe_main.exe').is_file())
            self.assertEqual(sum(p.suffix == '.cs' for p in converted), 3)


if __name__ == '__main__':
    unittest.main()
