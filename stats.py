#!/usr/bin/env python3

import os
import os.path
import argparse
import math

DEFAULT_EXT = [
    'java', 'jsp', 'xml', 'yml', 'yaml', 'properties', 'sql', 'css', 'js', 'cs'
]

exclude_dirs = [
    '.svn', 'exploded', 'node_modules'
]

TRACE = False

argparse = argparse.ArgumentParser(description='Simple source code stats')

argparse.add_argument('-e',
                      type=str,
                      help='list of extensions')

argparse.add_argument('-t',
                      action='store_true',
                      help='trace')

args, unknown = argparse.parse_known_args()

exts = args.e.split(",") if args.e else DEFAULT_EXT
TRACE = bool(args.t)
src_dirs = unknown


def process_dir(_dir):
    if os.path.basename(_dir) in exclude_dirs:
        return
    if TRACE: print('Scanning', _dir)
    for _file in os.listdir(_dir):
        f = _dir + '/' + _file
        if os.path.isdir(f):
            process_dir(f)
        elif os.path.isfile(f) and any([f.endswith('.' + ext) for ext in exts]):
            process_file(f)


def process_file(f_name):
    f = open(f_name, errors='ignore')
    file_content = f.read()
    f.close()
    if TRACE: print('\tFile:', f_name, get_loc(file_content), get_f_size(f_name))
    ext = get_ext(f_name)
    stat[ext]["loc"] += get_loc(file_content)
    stat[ext]["size"] += get_f_size(f_name)
    stat[ext]["count"] += 1


def get_ext(f_name):
    if '.' in f_name:
        return f_name.rsplit('.', 1)[1]
    else:
        return ''


def get_loc(content):
    return len(content.split('\n'))


def get_f_size(f_name):
    return os.path.getsize(f_name)


def init():
    global stat
    stat = {}
    for ext in exts:
        stat[ext] = {"count": 0, "loc": 0, "size": 0}


def report():
    total_loc = 0
    total_size = 0
    total_cnt = 0
    print("Ext | count | loc | size")
    for ext in stat:
        size = stat[ext]["size"]
        print(" | ".join(str(s) for s in [ext, stat[ext]["count"], stat[ext]["loc"], renderFileSize(size)]))
        total_loc += stat[ext]["loc"]
        total_size += size
        total_cnt += stat[ext]["count"]
    print(" | ".join(str(s) for s in ["TOTAL", total_cnt, total_loc, renderFileSize(total_size)]))


# Renders human-readable file size. Ex.: "15 KB". Based on
# http://stackoverflow.com/a/3758880/104522
#
# @param bytes file size in bytes
# @return human-readable file size
def renderFileSize(bytes: int):
    return humanReadableByteCount(bytes, False).replace("i", "")


# Renders human-readable file size. Ex.: "15 KB". Based on
# http://stackoverflow.com/a/3758880/104522
#
# @param bytes file size in bytes
# @param si true to use units of 1000, otherwise 1024
# @return human-readable file size
def humanReadableByteCount(bytes: int, si: bool):
    unit = 1000 if si else 1024
    if bytes < unit:
        return str(bytes) + " B"
    exp = int(math.log(bytes) / math.log(unit))
    pre = ("kMGTPE" if si else "KMGTPE")[exp - 1] + ("" if si else "i")
    return "{:.1f} {}B".format(bytes / math.pow(unit, exp), pre)


if __name__ == '__main__':
    init()
    for d in src_dirs:
        process_dir(d)
    report()
