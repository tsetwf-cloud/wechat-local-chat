"""Create an isolated local Python environment. Never opens WeChat data.

Only dependency installation may access the configured package index. It is not
run implicitly during collection; inspect --check before opting into installation.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import venv


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,help='private state root outside the installed skill')
    p.add_argument('--check',action='store_true',help='report paths without installing or writing')
    a=p.parse_args(argv)
    if sys.version_info<(3,11):raise RuntimeError('Python 3.11+ required')
    if a.root is None:
        import runtime
        root=runtime.default_private_root()
    else:root=a.root.absolute()
    package=Path(__file__).resolve().parents[1]
    if root.resolve().is_relative_to(package):raise ValueError('private environment must be outside the skill')
    if any(x.is_symlink() for x in [root,*root.parents]):raise ValueError('linked private root rejected')
    # Setup must not pre-create the data root: init owns its ACL creation.
    env=root.parent/(root.name+'-python-env')
    if any(x.is_symlink() for x in [env,*env.parents]):raise ValueError('linked environment rejected')
    executable=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if a.check:
        ready=False
        if executable.is_file():
            ready=subprocess.run([str(executable),'-c','import zstandard'],capture_output=True,timeout=20).returncode==0
        print(json.dumps({'ready':ready,'python':str(executable),'chat':str(package/'scripts/chat.py')}))
        return 0
    os.umask(0o077)
    root.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not executable.exists():venv.EnvBuilder(with_pip=True).create(env)
    subprocess.run([str(executable),'-m','pip','install','--disable-pip-version-check','-r',str(package/'requirements.txt')],check=True,timeout=180)
    print(json.dumps({'ready':True,'python':str(executable),'chat':str(package/'scripts/chat.py'),'data_opened':False}))
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:
        print(json.dumps({'error':type(e).__name__,'detail':str(e)}),file=sys.stderr)
        raise SystemExit(1)
