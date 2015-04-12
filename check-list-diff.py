#!/usr/bin/python
# -*- encoding:utf-8 -*-
r"""
check list diff
============================

### git:

git diff -U0 > diff.txt
pylint --msg-template='{path}:{line}:{column}: {msg}' \
        check-list-diff.py > errorlist.txt

### svn:

svn diff --diff-cmd=diff -x-U0 > diff.txt
pylint --msg-template='{path}:{line}:{column}: {msg}' \
        check-list-diff.py > errorlist.txt

### check-list-diff

check-list-diff.py -p1 \
        --format='^{filename}:{lineno}:' \
        --diff=diff.txt \
        --listfile=errorlist.txt

"""

import argparse
import difflib
import re
import string
import subprocess
import StringIO
import sys
import os


def check_list_filter(diff_filename, \
        list_filename,strip_prefix_num, \
        list_format):
    # Extract changed lines for each file.
    filename = None
    lines_by_file = {}
    for line in diff_filename:
        match = re.search('^\+\+\+\ (.*?/){%s}(\S*)' % strip_prefix_num, line)
        if match:
            filename = match.group(2)
        if filename == None:
            continue

        match = re.search('^@@.*\+(\d+)(,(\d+))?', line)
        if match:
            start_line = int(match.group(1))
            line_count = 1
            if match.group(3):
                line_count = int(match.group(3))
            if line_count == 0:
                continue
            end_line = start_line + line_count - 1;
            lines_by_file.setdefault(filename, []).extend(
                    [(start_line, end_line)])


    for line in list_filename:
        match = re.search(list_format.format(
            filename='(?P<filename>[A-Za-z0-9_/.-]+?)',
            lineno='(?P<lineno>\d+?)'), line)
        if match:
            fname=match.group('filename')
            lno=int(match.group('lineno'))
            if lno == 0:
                sys.stdout.write(line)
                continue
            lines=lines_by_file.get(fname)
            if lines:
                if filter(lambda x: x[0] <= lno and x[1] >= lno, lines):
                    sys.stdout.write(line)

def main():
    parser = argparse.ArgumentParser(
            description='输入检查列表和diff,　输出满足diff的检查列表.')
    parser.add_argument('-d', '--diff',
            metavar='DIFF_FILE_PATH',
            required=True,
            default=None,
            help="diff文件")
    parser.add_argument('-f', '--listfile',
            metavar='ERROR_LIST_FILE_PATH',
            required=True,
            default=None,
            help="error list文件.")
    parser.add_argument('--format',
            metavar='PATTERN',
            default='^{filename}:{lineno}:.*',
            help='checklist格式.默认:"{filename}:{lineno}:"')
    parser.add_argument('-p',
            metavar='NUM',
            default=0,
            help='strip the smallest prefix containing P slashes, default=0')
    args = parser.parse_args()

    if args.diff == '-':
        diff_filename=sys.stdin
    elif args.diff is not None and \
            os.path.exists(args.diff) and \
            os.access(args.diff, os.R_OK):
        diff_filename=open(args.diff)
    else:
        sys.stderr.write('文件不存在或者不可读: %s\n' % args.diff)
        sys.exit(1);

    if args.listfile == '-':
        list_filename=sys.stdin
    elif args.listfile is not None \
            and os.path.exists(args.listfile) and \
            os.access(args.listfile, os.R_OK):
        list_filename=open(args.listfile)
    else:
        sys.stderr.write('文件不存在或者不可读: %s\n' % args.listfile)
        sys.exit(1);
    check_list_filter(diff_filename,list_filename, args.p, args.format)

if __name__ == '__main__':
  main()

