#!/usr/bin/python3
# _*_ coding: utf-8
'''Текстовый onik-фильтр

Обрабатывает полученные через pipe текст,
результат выводит в stdout

Опции для титла - on, off, open
'''


import sys
import argparse
sys.path.insert(0, './pythonpath')
from Onik_run import get_string_converted


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--titlo', nargs='?', choices=['on', 'off', 'open'], default='on')

    return parser

# FIXME: some errors in regs
# претерпевшихъ
# ѻ҆мрача́етъ
# ѻ҆сквернѧетъ


parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])
titles_flag = namespace.titlo

for line in sys.stdin:
    converted = get_string_converted(line, titles_flag=titles_flag) + '\n'
    sys.stdout.write(converted)
