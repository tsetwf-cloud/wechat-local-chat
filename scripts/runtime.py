"""Private configuration and Windows helper runtime; no network or model calls."""
from __future__ import annotations
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path, PureWindowsPath

PACKAGE = Path(__file__).resolve().parents[1]
CONFIG_SCHEMA = 'wechat-local-chat/config-v1'


def platform_kind():
    if os.name == 'nt':
        return 'windows'
    return 'wsl' if 'microsoft' in platform.release().lower() else 'linux'


def win_to_wsl(value):
    text = str(value)
    if not re.match(r'^[A-Za-z]:[\\/]', text):
        raise RuntimeError('absolute Windows drive path required')
    p = PureWindowsPath(text)
    if '..' in p.parts or any(ord(c) < 32 for c in text):
        raise RuntimeError('unsafe Windows path')
    return Path('/mnt') / p.drive[0].lower() / Path(*p.parts[1:])


def wsl_to_win(value):
    p = Path(value)
    if not p.is_absolute() or '..' in p.parts or len(p.parts) < 3 or p.parts[1] != 'mnt' or not re.fullmatch('[a-zA-Z]', p.parts[2]):
        raise RuntimeError('Windows mounted path required')
    return str(PureWindowsPath(p.parts[2].upper() + ':\\', *p.parts[3:]))


def local_path(value):
    text = str(value)
    if os.name == 'nt' and re.match(r'^/mnt/[A-Za-z](?:/|$)', text):
        parts = text.split('/')
        return Path(str(PureWindowsPath(parts[2].upper() + ':\\', *parts[3:])))
    if re.match(r'^[A-Za-z]:[\\/]', text) and os.name != 'nt':
        return win_to_wsl(value)
    return Path(value)


def windows_path(value):
    return str(Path(value)) if os.name == 'nt' else wsl_to_win(value)


def run_command(args, timeout=120):
    try:
        result = subprocess.run([str(a) for a in args], capture_output=True, text=True,
                                encoding='utf-8', errors='strict', timeout=timeout, shell=False)
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        raise RuntimeError('local command unavailable, timed out, or invalid UTF-8') from None
    if result.returncode:
        raise RuntimeError('local command failed; no private command output is logged')
    return result.stdout.lstrip('\ufeff').strip()


def powershell(script, timeout=30):
    executable = shutil.which('powershell.exe') or shutil.which('powershell')
    if not executable:
        raise RuntimeError('Windows PowerShell must be available on PATH')
    preamble = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false); "
    return run_command([executable, '-NoProfile', '-NonInteractive', '-Command', preamble + script], timeout)


def default_private_root():
    override = os.environ.get('WECHAT_LOCAL_CHAT_ROOT')
    if override:
        return local_path(override).absolute()
    kind = platform_kind()
    if kind == 'windows':
        base = os.environ.get('LOCALAPPDATA')
        if not base:
            raise RuntimeError('LOCALAPPDATA unavailable; provide explicit private root')
        return Path(base) / 'WeChatLocalChat' / 'private'
    if kind == 'wsl':
        base = powershell("[Environment]::GetFolderPath('LocalApplicationData')")
        return win_to_wsl(base) / 'WeChatLocalChat' / 'private'
    raise RuntimeError('Windows/WSL capture only; provide explicit root for offline use')


def reject_links(path):
    path = Path(path).absolute()
    if '..' in path.parts or any(ord(c) < 32 for c in str(path)):
        raise RuntimeError('path traversal/control characters rejected')
    for item in (path, *path.parents):
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise RuntimeError('linked path rejected')
    return path


def validate_locations(root, source_db_storage):
    if not str(source_db_storage) or not Path(source_db_storage).is_absolute():
        raise RuntimeError('explicit absolute source directory required')
    root = reject_links(root)
    source = reject_links(source_db_storage)
    if root.is_relative_to(PACKAGE) or source.is_relative_to(PACKAGE) or root.is_relative_to(source) or source.is_relative_to(root):
        raise RuntimeError('private output must be separate from package and source')
    return root, source


def ps_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def protect_private_root(root, create=False):
    root = reject_links(root)
    if platform_kind() == 'linux':
        if create:
            root.mkdir(mode=0o700)
            os.chmod(root, 0o700)
        elif root.stat().st_mode & 0o077:
            raise RuntimeError('private root permissions must be 0700')
        return
    path = ps_literal(windows_path(root))
    script = "$p=" + path + "; $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User; "
    script += "for($d=New-Object IO.DirectoryInfo($p);$null -ne $d;$d=$d.Parent){if($d.Exists -and ($d.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Linked ancestor rejected'}}; "
    if create:
        script += "if(Test-Path -LiteralPath $p){throw 'Output exists'}; $acl=New-Object Security.AccessControl.DirectorySecurity; $acl.SetOwner($sid); $acl.SetAccessRuleProtection($true,$false); foreach($who in @($sid,(New-Object Security.Principal.SecurityIdentifier('S-1-5-18')))){ $rule=New-Object Security.AccessControl.FileSystemAccessRule($who,'FullControl','ContainerInherit,ObjectInherit','None','Allow'); $acl.AddAccessRule($rule) }; (New-Object IO.DirectoryInfo($p)).Create($acl); "
    script += "$actual=Get-Acl -LiteralPath $p; if(!$actual.AreAccessRulesProtected -or !$actual.GetOwner([Security.Principal.SecurityIdentifier]).Equals($sid)){throw 'ACL owner/protection failed'}; $rules=@($actual.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])); if($rules.Count -ne 2){throw 'ACL count failed'}; foreach($r in $rules){if($r.IdentityReference.Value -notin @($sid.Value,'S-1-5-18') -or $r.AccessControlType -ne 'Allow' -or $r.FileSystemRights -ne 'FullControl' -or $r.InheritanceFlags -ne 'ContainerInherit,ObjectInherit' -or $r.PropagationFlags -ne 'None'){throw 'ACL rule failed'}}; '{\"private_acl\":true}'"
    try:
        result = json.loads(powershell(script))
    except (ValueError, TypeError):
        raise RuntimeError('private ACL verification failed') from None
    if result.get('private_acl') is not True:
        raise RuntimeError('private ACL verification failed')


def initialize(root, account, source_db_storage):
    if not isinstance(account, str) or not account.strip() or any(ord(c) < 32 for c in account):
        raise RuntimeError('explicit owner account required')
    root, source = validate_locations(local_path(root), local_path(source_db_storage))
    if root.exists():
        raise RuntimeError('private root already exists; refusing overwrite')
    root.parent.mkdir(parents=True, exist_ok=True)
    protect_private_root(root, create=True)
    config = {'schema': CONFIG_SCHEMA, 'account': account, 'source_db_storage': str(source)}
    with os.fdopen(os.open(root / 'config.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as stream:
        json.dump(config, stream, ensure_ascii=False)
    return {'initialized': True, 'capture_tested': False}


def load_config(root):
    root = reject_links(local_path(root))
    path = reject_links(root / 'config.json')
    try:
        config = json.loads(path.read_text(encoding='utf-8'))
        if config.get('schema') != CONFIG_SCHEMA or not isinstance(config.get('account'), str) or not config['account'].strip():
            raise ValueError()
        validate_locations(root, local_path(config['source_db_storage']))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        raise RuntimeError('valid private config.json required; run init first') from None
    return config


def native_dependencies():
    if platform_kind() not in ('windows', 'wsl'):
        raise RuntimeError('Windows x64 or WSL Windows interop required')
    script = "$c=Join-Path $env:WINDIR 'Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe'; $s=Join-Path $env:WINDIR 'System32\\winsqlite3.dll'; @{csc=$c;compiler_available=(Test-Path -LiteralPath $c);sqlite_available=(Test-Path -LiteralPath $s);windows_x64=([Environment]::Is64BitOperatingSystem -and $env:PROCESSOR_ARCHITECTURE -ne 'ARM64')} | ConvertTo-Json -Compress"
    try:
        data = json.loads(powershell(script))
        if not isinstance(data, dict):
            raise ValueError()
    except (ValueError, TypeError):
        raise RuntimeError('Windows dependency metadata unavailable') from None
    return data


def doctor(root):
    root = local_path(root).absolute()
    status = {'platform': platform_kind(), 'configured': False, 'private_root_verified': False,
              'compiler_available': False, 'sqlite_available': False, 'windows_x64': False,
              'helper_built': False, 'capture_ready': False, 'capture_tested': False,
              'process_memory_read': False, 'supported_weixin_version': '4.1.15.56',
              'capture_mode': 'main-db-only', 'wal_included': False}
    try:
        load_config(root)
        status['configured'] = True
        protect_private_root(root)
        status['private_root_verified'] = True
        status['helper_built'] = reject_links(root / 'bin' / 'probe_main.exe').is_file()
    except RuntimeError:
        pass
    if status['platform'] in ('windows', 'wsl'):
        try:
            deps = native_dependencies()
            for key in ('compiler_available', 'sqlite_available', 'windows_x64'):
                status[key] = deps.get(key) is True
        except RuntimeError:
            pass
    try:
        status['native_sources_available'] = all(reject_links(PACKAGE / 'scripts/native/src' / name).is_file() for name in ('Main.cs', 'Probe.cs', 'Runtime.cs'))
    except RuntimeError:
        status['native_sources_available'] = False
    status['build_ready'] = all(status[k] for k in ('configured', 'private_root_verified', 'compiler_available', 'sqlite_available', 'windows_x64', 'native_sources_available'))
    status['capture_ready'] = all(status[k] for k in ('configured', 'private_root_verified', 'sqlite_available', 'windows_x64', 'helper_built'))
    status['next_action'] = 'explicit collect request required' if status['capture_ready'] else 'initialize private root and run build on Windows x64/WSL'
    return status


def build(root, test=False):
    """Compile trusted bundled sources, never download or invoke an installer."""
    root = local_path(root).absolute()
    load_config(root)
    protect_private_root(root)
    deps = native_dependencies()
    if not all(deps.get(k) is True for k in ('compiler_available', 'sqlite_available', 'windows_x64')):
        raise RuntimeError('Windows x64 Framework64 csc and winsqlite3.dll required')
    sources = [reject_links(PACKAGE / 'scripts/native/src' / name) for name in ('Main.cs', 'Probe.cs', 'Runtime.cs')]
    fixtures = [reject_links(PACKAGE / 'tests/native' / name) for name in ('MainFixture.cs', 'SecurityFixture.cs')] if test else []
    if not all(p.is_file() for p in sources + fixtures):
        raise RuntimeError('bundled native sources/fixtures missing; reinstall complete skill')
    bin_dir = reject_links(root / 'bin')
    bin_dir.mkdir(mode=0o700, exist_ok=True)
    import uuid
    stage = bin_dir / ('build_' + uuid.uuid4().hex)
    stage.mkdir(mode=0o700)
    try:
        staged_sources = []
        staged_fixtures = []
        for originals, staged in ((sources, staged_sources), (fixtures, staged_fixtures)):
            for original in originals:
                target_source = stage / original.name
                shutil.copyfile(original, target_source)
                staged.append(target_source)
        sources, fixtures = staged_sources, staged_fixtures
        def compile_to(name, entry, extra=()):
            output = stage / name
            command = [str(local_path(deps['csc'])), '/nologo', '/platform:x64', '/target:exe', '/main:' + entry,
                       '/out:' + windows_path(output), *[windows_path(p) for p in [*sources, *extra]]]
            run_command(command, timeout=120)
            if not output.is_file():
                raise RuntimeError('compiler did not produce requested helper')
            return output
        helper = compile_to('probe_main.exe', 'MainCollector')
        for fixture in fixtures:
            executable = compile_to(fixture.stem.lower() + '.exe', fixture.stem, [fixture])
            scratch = stage / (fixture.stem + '_scratch')
            run_command([str(executable), windows_path(scratch)], timeout=180)
        target = reject_links(bin_dir / 'probe_main.exe')
        os.replace(helper, target)
    finally:
        shutil.rmtree(stage)
    return {'helper_built': True, 'fixture_tests_passed': bool(test), 'capture_tested': False}
