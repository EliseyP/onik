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
from Onik_functions import get_string_converted, acute_util
# from onik import chahge_acute


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--titlo', nargs='?', choices=['on', 'off', 'open'], default='on')
    parser.add_argument('-d', '--debug', action='store_true', default=False)

    return parser

# FIXME: some errors in regs
# претерпевшихъ
# ѻ҆мрача́етъ
# ѻ҆сквернѧетъ


parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])
titles_flag = namespace.titlo
# w = 'а҆́'
w = 'ю҆̀'
ww = 'ю҆́'
w_f = 'ᲂу҆́мъ'
w_m = 'ᲂу҆спе́нїе'
w_l = 'дꙋшѐ'
w_e = 'о҆тє́цъ'
w_ee = 'деє̀'
w_a = 'дары̀'
w_aa = 'дары̑'
w_aaa = 'дары́'
w_i = 'да́ръ'
w_ii = 'да̑ръ'
w_o = 'домо́въ'
w_oo = 'домѡ́въ'
# acute_util(w_f)
# acute_util(w_m)
# acute_util(w_l)
print(w_e, acute_util(w_e))
# acute_util(w_ee)
print(w, acute_util(w))
print(ww, acute_util(ww))
print(w_a, acute_util(w_a))
print(w_aa, acute_util(w_aa))
print(w_aaa, acute_util(w_aaa))
print(w_i, acute_util(w_i))
print(w_ii, acute_util(w_ii))
print(w_o, acute_util(w_o))
print(w_oo, acute_util(w_oo))

'''
if namespace.debug:
    #
    acute_util(w)
else:
    for line in sys.stdin:
        converted = get_string_converted(line, titles_flag=titles_flag) + '\n'
        sys.stdout.write(converted)
'''