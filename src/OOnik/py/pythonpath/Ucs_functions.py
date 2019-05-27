# _*_ coding: utf-8

import re
from Letters import *
from Ft import *


class Char:
    """for chars from Cursor, save and restore it attributes"""

    def __init__(self, o_cursor):
        self.char = o_cursor.getString()
        self.fontname = o_cursor.CharFontName
        self.color = o_cursor.CharColor
        self.bold = o_cursor.CharWeight
        self.italic = o_cursor.CharPosture
        # self.uline = uline

    def restore_attrib(self, o_cursor):
        # TODO: сделать проверку, поддерживает ли o_cursor типы
        #  CharColor CharWeight CharPosture
        #  т.к. иногда возникает ошибка 'TYPE is not supported'
        #  когда в мультиабзацном выделении новый абзац
        #  начинается с символа с форматированием цвет, жирность
        #  при этом если нет форматирования, или нет нового абзаца
        #  то ошибки нет.
        #  Ошибка точно возникает, когда в выделении есть символ нового абзаца (даже только он),
        #  за которым следует символ с форматированием.
        o_cursor.CharColor = self.color
        o_cursor.CharWeight = self.bold
        o_cursor.CharPosture = self.italic


def check_orthodox_fonts(font_name):
    '''
    Определяет для шрифта принадлежность к orthodox-группе
    UCS-шрифты, и некоторые другие.
    :type font_name: str
    :param font_name: название шрифта
    :return: Bool
    '''
    if re.search(r"^.*(Ucs|Orthodox|Ustav|Valaam|Hirmos|Irmologion).*$", font_name):
        return True
    else:
        return False


def get_font_table(font_name):
    _ft = {}
    # UCS-шрифты
    if re.search(r"^.*Ucs.*$", font_name):
        # шрифты, у кот-х u406 - I без точек (Orthodox.tt, Irmologion)
        if not re.search(r"^.*Caps*$", font_name):
            _ft = font_table_ucs
        else:
            _ft = font_table_usc_caps

        # шрифты, у кот-х u406 - I с точками (triodion)
        if not re.search(r'^.*(Orthodox\.tt|Irmologion|Ostrog).*$', font_name):
            # добавляем значение в словарь для Ї with dots
            _ft['І'] = unicCapitalYi

    elif re.search(r"^.*[Ee]Roos.*$", font_name):
        _ft = font_table_orthodox_e_roos
    elif re.search(r"OrthodoxDigits.*$", font_name):
        _ft = font_table_orthodox_digits
    elif re.search(r"Orthodox(Loose)?\d*$", font_name):
        _ft = font_table_orthodox_loose
    elif re.search(r"Ustav\d*$", font_name):
        _ft = font_table_ustav
    elif re.search(r"Valaam\d*$", font_name):
        _ft = font_table_valaam
    elif re.search(r"Hirmos\ Ponomar\ TT\d*$", font_name):
        _ft = font_table_hirmos_ponomar
    elif re.search(r"Irmologion\d*$", font_name):
        _ft = font_table_irmologion
    return _ft


def ucs_convert_string_by_search_and_replace(section_string, font_table):
    """get string and fonttable and convert"""
    for ucs_str, unic_str in font_table.items():
        section_string = section_string.replace(ucs_str, unic_str)
    return section_string


def ucs_convert_string_with_font_bforce(section_string, font_table):
    """get string and font dict and return converted char-by-char string"""
    out = ""
    for ucs in section_string:
        out += font_table.get(ucs, ucs)

    return out


def ucs_process_one_section(section, method):
    # font_of_section = section.CharFontName
    font_of_section = section.CharFontName
    if font_of_section.find(';') != -1:
        # TODO: загрузить весь список и найти первый подходящий для конвертации
        #  (не обязательно первый)
        font_of_section = font_of_section.split(';')[0]

    if font_of_section != "":
        section_string = section.getString()
        font_table = get_font_table(font_of_section)

        # если шрифт доступен для конвертации
        if font_table.items():

            # В шрифте "Ustav" есть ударения, которые ставятся ПЕРЕД гласной
            # меняем их местами перед конвертацией
            if font_of_section == "Ustav":
                repaired_string = ucs_ustav_acute_repair_by_regex_sub(section_string)
                section.setString(repaired_string)
                section_string = section.getString()

            if method == 1:
                # process string char-by-char
                new_section_string = \
                    ucs_convert_string_with_font_bforce(section_string, font_table)
            else:
                # возможно этот метод еще пригодится
                new_section_string = \
                    ucs_convert_string_by_search_and_replace(section_string, font_table)
            # replace  string with converted
            section.setString(new_section_string)

        # set Unicode font for all symbols, replaced and not-replaced
        section.CharFontName = UnicodeFont

    return None


def ucs_convert_by_sections(v_doc, selection=''):
    """convert for every sections"""

    # в поисках способа замены:
    method = 1  # 1 - char-by-char; other - string.replace
    if not selection:
        # для всего текста
        paragraph_enumeration = v_doc.Text.createEnumeration()
    else:
        # для выделения
        paragraph_enumeration = selection.createEnumeration()
    # for every Paragraph
    while paragraph_enumeration.hasMoreElements():
        paragraph = paragraph_enumeration.nextElement()
        if paragraph.supportsService("com.sun.star.text.Paragraph"):
            section_enumeration = paragraph.createEnumeration()
            # for every Section
            while section_enumeration.hasMoreElements():
                section = section_enumeration.nextElement()
                # сохранить некоторое форматирование
                color_of_section = section.CharColor
                underlined_section = section.CharUnderline
                char_weight_section = section.CharWeight
                font_size = section.CharHeight

                # convert it
                ucs_process_one_section(section, method)

                # восстановить некоторое форматирование
                section.CharColor = color_of_section
                section.CharUnderline = underlined_section
                section.CharWeight = char_weight_section
                section.CharHeight = font_size
    # TODO: post-process: repair repeating diacritics
    # (пока реализовано в onik-функциях)
    return None


def convert_one_symbol(symbol, font_table):
    symbol = font_table.get(symbol, '')
    return symbol


def ucs_ustav_acute_repair_by_oo_text_cursor(text_cursor, symbol):
    acutes = {
        "m": "'",
        "M": '"',
        "x": "`",
    }
    ustav_acute = acutes.get(symbol, symbol)

    # look on next char
    text_cursor.goRight(1, True)
    next_char = text_cursor.String[1:2]

    # reverse two chars with replace acute
    text_cursor.String = next_char + ustav_acute
    symbol = next_char
    text_cursor.collapseToStart()
    text_cursor.goRight(1, True)

    return symbol


def ucs_ustav_acute_repair_by_regex_sub(string):
    """Via regex search & replace reverse acute from before to after letter"""
    acutes = {
        "m": "'",
        "M": '"',
        "x": "`"
    }
    for uc, acute in acutes.items():
        pat = uc + r'(.)'
        replace = r'\1' + acute
        re_obj = re.compile(pat, re.U)
        match = re_obj.search(string)
        if match:
            string = re_obj.sub(replace, string)
    return string


def ucs_convert_in_oo_text_cursor(text_cursor):
    """process char-by-char text in TextCursor"""
    length_string = len(text_cursor.getString())

    text_cursor.collapseToStart()

    # for every symbol in string
    for i in range(length_string):
        text_cursor.goRight(1, True)  # select next char to cursor
        char = Char(text_cursor)  # save attributes of selected char
        selected_symbol = text_cursor.getString()  # get one char from cursor
        font_of_selected_symbol = text_cursor.CharFontName  # get font of char
        font_table = {}
        # TODO: проблема с символом нового абзаца, - CharFontName - void
        # пока обходим так: (м.б. делать проверку на такие символы и сразу их пропускать?)
        if font_of_selected_symbol:
            font_table = get_font_table(font_of_selected_symbol)  # get font dictionary

        # В шрифте "Ustav" есть ударения, которые ставятся ПЕРЕД гласной
        # меняем их местами перед конвертацией
        if font_of_selected_symbol == "Ustav" \
                and selected_symbol in {"m", "M", "x"}:
            selected_symbol = \
                ucs_ustav_acute_repair_by_oo_text_cursor(text_cursor, selected_symbol)

        # get value from font dictionary for char
        if font_table and font_table.items():
            new_selected_symbol = font_table.get(selected_symbol, selected_symbol)
            text_cursor.setString(new_selected_symbol)  # replace char with converted
            text_cursor.CharFontName = UnicodeFont

            # только если было изменение
            char.restore_attrib(text_cursor)  # restore attributes of selected char

        text_cursor.collapseToEnd()

    # TODO: post-process: repair repeating diacritics
    return None

