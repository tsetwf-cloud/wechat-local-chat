"""Single entry point. Local tools never invoke a model or upload chats."""
import argparse
import json
import os
from pathlib import Path
import sys


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, help='private state directory outside this package')
    s = p.add_subparsers(dest='command', required=True)
    q = s.add_parser('init', help='confirm one owned account and local database path')
    q.add_argument('--account', required=True)
    q.add_argument('--source', required=True)
    s.add_parser('doctor', help='check environment without reading chat data')
    q = s.add_parser('build', help='compile the bundled Windows helper locally')
    q.add_argument('--test', action='store_true')
    q = s.add_parser('collect', help='capture main databases and select one explicit scope')
    q.add_argument('--name', required=True)
    q.add_argument('--start', required=True)
    q.add_argument('--end', required=True)
    q.add_argument('--question', default='')
    q.add_argument('--talker')
    q.add_argument('--snapshot', type=Path, help='explicit offline snapshot reuse, never fresh capture')
    for command in ['inspect', 'search', 'context', 'save-analysis']:
        q = s.add_parser(command)
        q.add_argument('--request', required=True)
        if command == 'search':
            q.add_argument('--keyword', required=True)
        if command == 'context':
            q.add_argument('--chunk-size', type=int, default=100)
        if command == 'save-analysis':
            q.add_argument('--file', type=Path, required=True)
    s.add_parser('history')
    return p


def main(argv=None):
    os.umask(0o077)
    a = parser().parse_args(argv)
    import runtime
    root = a.root if a.root is not None else runtime.default_private_root()
    if a.command == 'init':
        out = runtime.initialize(root, a.account, a.source)
    elif a.command == 'doctor':
        out = runtime.doctor(root)
    elif a.command == 'build':
        out = runtime.build(root, test=a.test)
    else:
        import business
        if a.command == 'collect':
            out = business.collect(root, name=a.name, start=a.start, end=a.end,
                                   question=a.question, talker=a.talker, snapshot=a.snapshot)
        elif a.command == 'inspect':
            out = business.inspect_request(root, a.request)
        elif a.command == 'history':
            out = business.history(root)
        elif a.command == 'search':
            out = business.search(root, a.request, a.keyword)
        elif a.command == 'context':
            out = business.context(root, a.request, a.chunk_size)
        else:
            out = business.save_analysis(root, a.request, a.file)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError, KeyError, ImportError) as error:
        print(json.dumps({'error': type(error).__name__, 'detail': str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
