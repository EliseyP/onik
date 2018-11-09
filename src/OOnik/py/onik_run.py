#!/usr/bin/python3
# _*_ coding: utf-8
'''Текстовый onik-фильтр

Обрабатывает полученный текст,
результат выводит в stdout

Опции для титла - on, off, open
'''

import re
import sys
import argparse
sys.path.insert(0, '/home/user/opt/scripts/py/OOnik')
from Onik_functions import get_string_converted, acute_util, acute_cycler, convert_string_with_digits
from numerals import cu_parse_int, cu_format_int


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--titlo', nargs='?', choices=['on', 'off', 'open'], default='on')
    parser.add_argument('csl', nargs='?')
    parser.add_argument('-D', '--debug', action='store_true', default=False)
    parser.add_argument('-l', '--digits_to_letters', action='store_true', default=False)
    parser.add_argument('-L', '--digits-from-letters', action='store_true', default=False)

    return parser


parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])
string = namespace.csl
titles_flag = namespace.titlo
# w = 'а҆́'
'''
w = 'ю҆̀'
ww = 'ю҆́'
w_f = 'ᲂу҆́мъ'
w_m = 'ᲂу҆спе́нїе'
w_l = 'дꙋшѐ'
w_e = 'о҆тє́цъ'
w_ee = 'о҆те́цъ'

w_eee = 'деє̀'
w_a = 'дары̀'
w_aa = 'дары̑'
w_aaa = 'дары́'
w_i = 'да́ръ'
w_ii = 'да̑ръ'
w_o = 'домо́въ'
w_oo = 'домѡ́въ'
w_O = 'его̀'
w_OO = 'его́'
w_OOO = 'егѡ́'
w_OOOO = 'егѡ̀'
# acute_util(w_f)
# acute_util(w_m)
# acute_util(w_l)

# print(acute_cycler('oxia', 'varia', 'kamora', acute='oxia'))
# acute_cycler('oxia', 'varia', 'kamora', acute='varia')
# acute_cycler('oxia', 'varia', 'kamora', acute='kamora')
# acute_cycler('oxia', 'varia', acute='oxia', letter='о')
# acute_cycler('oxia', 'varia', acute='varia', letter='о')
# acute_cycler('oxia', 'varia', acute='varia', letter='ѡ')
# print(acute_cycler('́', '̀', acute='́', letter='ѡ'))


# exit(0)

print(w_e, acute_util(w_e))
print(w_ee, acute_util(w_ee))
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
print(w_O, acute_util(w_O))
print(w_OOOO, acute_util(w_OOOO))
print(w_OOO, acute_util(w_OOO))
print(w_OO, acute_util(w_OO))

exit(0)
'''
# print('+++ ', string)
# string = 'аз'
if namespace.debug:
    pass
    # Do some debug
    # acute_util(w)
elif namespace.csl:
     # числа в буквы
    if namespace.digits_to_letters:
        converted = convert_string_with_digits(string)
        if converted:
            print(converted)
    # остальное
    else:
        converted = get_string_converted(string, titles_flag=titles_flag)
        if converted:
            print(converted) 

