#!/usr/bin/python3
# _*_ coding: utf-8


import argparse
from ConvertOdtByXML import (
    Odt,
    convert_ucs_to_unicode_by_font,
    convert_unicode_to_ucs
)

_description = """Скрипт позволяет конвертировать текст odt-файла,
напрямую, с учетом форматирования (шрифты и пр.).
После конвертации текста можно установить новый шрифт для стилей.
К примеру, после конвертации UCS->Unicode
выставить шрифт 'Ponomar Unicode' для всех стилей.
Результат сохранятся в новом файле.
Расширение для нового файла можно задать через опцию (-e).

Скрипт использует ConvertOdtByXML.py:
класс Otd(), и конвертеры для текстовых отрывков:
convert_ucs_to_unicode_by_font,
convert_unicode_to_ucs.

Конвертерами могут быть любые ф-ции, возвращающие измененный текст.

Пример:
$ python convert_xml.py -s -e 'new.odt' -p 'D:/Temp/xml-test.odt'
Конвертация UCS->Unicode с сохранением форматирования,
Рез-т в новый файл: 'D:/Temp/xml-test.new,odt'
"""


def create_parser():
    _parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=_description,
    )
    _parser.add_argument(
        'odt',
        nargs=1,
        metavar="ODT",
        help='ODT url',
    )
    _parser.add_argument(
        '-s', '--save_format',
        action='store_true',
        default=False,
        help='Сохранять форматирование',
    )
    _parser.add_argument(
        '-f', '--style_font',
        nargs=1,
        action="store",
        metavar="FONT",
        help='Шрифт для замены в стилях.',
    )
    _parser.add_argument(
        '-e', '--extension',
        nargs=1,
        action="store",
        metavar="EXENSION",
        help='Расширение для нового файла.',
    )
    group_url_parser_db = _parser.add_argument_group('convert', 'Конвертация')
    gr = group_url_parser_db.add_mutually_exclusive_group()
    gr.add_argument(
        '-p', '--to_unicode',
        action='store_true',
        default=False,
        help='Конвертация в Unicode (Ponomar)',
    )
    gr.add_argument(
        '-u', '--to_ucs',
        action='store_true',
        default=False,
        help='Конвертация в UCS',
    )
    return _parser


def args_hanlder():
    parser = create_parser()
    args = parser.parse_args()
    _odt = None
    odt_obj = None
    _save_format = False
    if args.odt:
        _odt = args.odt[0]
        odt_obj = Odt(_odt)
    if args.save_format:
        _save_format = True
    if args.to_unicode or args.to_ucs:
        _converter = None
        _font = None

        if args.to_unicode:
            _converter = convert_ucs_to_unicode_by_font
            _font = 'Ponomar Unicode'  # default
        elif args.to_ucs:
            _converter = convert_unicode_to_ucs
            _font = 'Triodion Ucs'  # default

        if args.style_font:
            _font = args.style_font[0]
        odt_obj.set_style_font(_font)

        if args.extension:
            odt_obj.set_extension(args.extension[0])

        if _converter:
            odt_obj.set_converter(_converter)

        if _save_format:
            odt_obj.convert_with_saving_format()
        else:
            odt_obj.convert_text_only()
    else:
        print('[!] Or -p or -u option expected!')


def main():
    args_hanlder()


if __name__ == '__main__':
    main()
