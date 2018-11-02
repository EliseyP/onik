#!/usr/bin/python3
# _*_ coding: utf-8

import sys
import argparse
sys.path.insert(0, './pythonpath')
from onik_run import get_string_converted

# def create_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-t', '--titlo', choices=['on', 'off', 'open'], default='on')
#
#     return parser

# FIXME: some errors in regs
# застѣнкахъ претерпевшихъ
# ѻ҆мрача́етъ
# ѻ҆сквернѧетъ

for line in sys.stdin:
    # print("== ", line)
    converted = get_string_converted(line, titles_flag='on') + '\n'
    sys.stdout.write(converted)
