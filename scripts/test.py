"""Run bundled synthetic tests from any directory. Never captures real data."""
import argparse
from pathlib import Path
import sys
import unittest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--list',action='store_true')
    args=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'scripts'))
    sys.path.insert(0,str(root/'tests'))
    suite=unittest.defaultTestLoader.discover(str(root/'tests'))
    if args.list:
        def tests(node):
            for item in node:
                if isinstance(item,unittest.TestSuite):yield from tests(item)
                else:yield item.id()
        print('\n'.join(tests(suite)))
        return 0
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
