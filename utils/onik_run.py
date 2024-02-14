#!/usr/bin/env python3
# _*_ coding: utf-8
'''Текстовый onik-фильтр

Обрабатывает полученный текст,
результат выводит в stdout

Опции для титла - on, off, open
'''

# import re
import sys
import argparse

# sys.path.insert(0, './pythonpath')

# import Onik_functions

from Onik_functions import (
    # debug,
    # RawWord,
    get_string_converted,
    acute_util,
    # acute_cycler,
    convert_string_with_digits,
    convert_string_letters_to_digits,
    # convert_unstripped,
    letters_util,
    convert_pluralis,
    add_oxia_for_unacuted_word_handler,
    csl_to_russian,
    get_text_from_file,
    unicode_to_ucs,
    TitleFlags,
)
# from Ucs_functions import get_font_table
# from numerals import cu_parse_int, cu_format_int

# TODO: обработка файлов.


def create_parser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-t', '--titlo', nargs='?',
                         choices=[TitleFlags.ON, TitleFlags.OFF, TitleFlags.OPEN, TitleFlags.OPEN_ONLY],
                         default=TitleFlags.ON)
    _parser.add_argument('csl', nargs='?')
    _parser.add_argument('-D', '--debug', action='store_true', default=False)
    _parser.add_argument('-l', '--digits_to_letters', action='store_true', default=False)
    _parser.add_argument('-L', '--digits_from_letters', action='store_true', default=False)
    _parser.add_argument('-o', '--new_oxia', action='store_true', default=False)
    _parser.add_argument('-A', '--ch_acute', action='store_true', default=False)
    _parser.add_argument('-F', '--move_acute_forward', action='store_true', default=False)
    _parser.add_argument('-B', '--move_acute_backward', action='store_true', default=False)
    _parser.add_argument('-V', '--move_acute_end', action='store_true', default=False)
    _parser.add_argument('-S', '--chlett_at_start', action='store_true', default=False)
    _parser.add_argument('-E', '--chlett_at_end_e', action='store_true', default=False)
    _parser.add_argument('-O', '--chlett_at_end_o', action='store_true', default=False)
    _parser.add_argument('-e', '--chlett_e', action='store_true', default=False)
    _parser.add_argument('-I', '--chlett_i', action='store_true', default=False)
    _parser.add_argument('-P', '--chlett_i_pluralis', action='store_true', default=False)
    # _parser.add_argument('-f', '--font_table', action='store_true', default=False)
    _parser.add_argument('-r', '--csl_to_russian', action='store_true', default=False)
    _parser.add_argument('-R', '--csl_to_russian_with_acutes', action='store_true', default=False)
    _parser.add_argument(
        '-f', '--file',
        nargs=1, metavar='FILE',
    )
    _parser.add_argument('-u', '--to_ucs', action='store_true', default=False)
    _parser.add_argument('-U', '--to_ucs_splitted', action='store_true', default=False)

    return _parser


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

def _debug():
    from Onik_functions import acute_util, convert_pluralis, convert_unstripped, convert_varia2oxia, get_string_converted
    # _str = 'ꙗ҆́кѡ Ꙗ҆́кѡ Ꙗ҆кѡ Ꙗ́кѡ є҆́же а҆́бїе'
    _str = 'ᲂубѡ ᲂу҆бѡ ᲂу́бѡ ᲂу҆́бѡ Оубѡ Оу҆бѡ Оу́бѡ Оу҆́бѡ'
    # _str = 'ᲂу́бѡ'
    # _str = 'ЄЕ'
    # _str = 'степе́ней а҆по́столомъ'
    _str = 'стопе́ноней стопе́ноненой стопе́нонєй стопе́ноненѡй'
    _str = 'дш҃ѝ же дꙋшѝ же.'
    _str = "1 января"
    cnv = get_string_converted(_str, titles_flag=TitleFlags.ON)
    print(f"{cnv=}")

    # print(_str)
    # print(convert_varia2oxia(_str))
    pass


if __name__ == '__main__':
    w = 'ѻн'
    converted = ''
    if namespace.file:
        # Для вывода в kile (выделенный текст помещается во временный файл).
        namespace.csl = True
        file_url = namespace.file[0]
        string = get_text_from_file(file_url)
    if namespace.debug:
        # Do some debug
        _debug()
    elif namespace.csl:
        # числа в буквы
        if namespace.digits_to_letters:
            converted = convert_string_with_digits(string)
        elif namespace.digits_from_letters:
            converted = convert_string_letters_to_digits(string)
        elif namespace.new_oxia:
            converted = add_oxia_for_unacuted_word_handler(string)
        elif namespace.ch_acute:
            converted = acute_util(string, 'change_type')
        elif namespace.move_acute_forward:
            converted = acute_util(string, 'move_right')
        elif namespace.move_acute_backward:
            converted = acute_util(string, 'move_left')
        elif namespace.move_acute_end:
            converted = acute_util(string, 'move_to_end')
        elif namespace.chlett_at_start:
            converted = letters_util(string, 0)
        elif namespace.chlett_at_end_o:
            converted = letters_util(string, 1)
        elif namespace.chlett_at_end_e:
            converted = letters_util(string, 2)
        elif namespace.chlett_i:
            converted = letters_util(string, 3)
        elif namespace.chlett_i_pluralis:
            converted = convert_pluralis(string)
        elif namespace.chlett_e:
            convert = letters_util(string, 4)
        elif namespace.csl_to_russian:
            converted = csl_to_russian(string)
        elif namespace.csl_to_russian_with_acutes:
            converted = csl_to_russian(string, save_acute=True)
        elif namespace.to_ucs:
            converted = unicode_to_ucs(string)
        elif namespace.to_ucs_splitted:
            converted = unicode_to_ucs(string, split_monograph=True)
        # elif namespace.font_table:
        #     ft = get_font_table(string)
        #     converted = ft

        # остальное
        else:
            converted = get_string_converted(string, titles_flag=titles_flag)

        if converted:
            # Для вывода в kile (выделенный текст помещается во временный файл).
            if namespace.file:
                print(converted, end='')
            else:
                print(converted)

"""
# Пример фильтра python 3
По умолчанию input() читает данные из stdin, print() печатает данные в stdout. Так что можете считать вашу задачу решённой.

В Питоне stdin, stdout представлены sys.stdin, sys.stdout объектами (текстовые потоки, как правило), которые в общем случае могут быть любого типа (если их интерфейс достаточно file-like) и могут быть переопределены кем-угодно (IDLE, bpython, ipython, IDE, win-unicode-console, etc). Иногда достаточно предоставить объект, который поддерживает единственный метод .write(), если нужно только print() функцию поддерживать. В других случаях, даже экземпляр io.TextIOWrapper (тип sys.stdin/sys.stdout по умолчанию) может быть недостаточным, если .fileno() не возвращает настоящий file descriptor (см. детали в Redirect stdout to a file in Python?).

При запуске Питона, sys.stdin/sys.stdout обычно указывают на стандартные потоки ввода/вывода, унаследованные от родительского процесса или полученные от консоли. Интерактивный ввод/вывод как правило связан с терминалом. Из оболочки легко перенаправить ввод/вывод из файла, канала (pipe)

"""
# for line in sys.stdin:
#     print(line.rstrip('\n')[::-1])
# # или
# str = sys.stdin.read()
# print str

"""
# Пример фильтра python 2
import sys
# import stdio
lo = int(sys.argv[1])
hi = int(sys.argv[2])
while not stdio.isEmpty():
    # Обрабо тат ь одно целое числ о .
    value = stdio.readInt()
    if (value >= lo) and (value <= hi):
        stdio.write(str(value) + ' ')
    stdio.writeln()
"""
