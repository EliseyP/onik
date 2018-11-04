# _*_ coding: utf-8

from Letters import *
from Ft import *


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
    font_of_section = section.CharFontName
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


def ucs_convert_by_sections(v_doc):
    """convert for every sections"""

    # в поисках способа замены:
    method = 1  # 1 - char-by-char; other - string.replace
    paragraph_enumeration = v_doc.Text.createEnumeration()

    # for every Paragraph
    while paragraph_enumeration.hasMoreElements():
        paragraph = paragraph_enumeration.nextElement()
        if paragraph.supportsService("com.sun.star.text.Paragraph"):
            section_enumeration = paragraph.createEnumeration()
            # for every Section
            while section_enumeration.hasMoreElements():
                section = section_enumeration.nextElement()
                # convert it
                ucs_process_one_section(section, method)
    # TODO: post-process: repair repeating diacritics
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
        font_table = get_font_table(font_of_selected_symbol)  # get font dictionary

        # В шрифте "Ustav" есть ударения, которые ставятся ПЕРЕД гласной
        # меняем их местами перед конвертацией
        if font_of_selected_symbol == "Ustav" \
                and selected_symbol in {"m", "M", "x"}:
            selected_symbol = \
                ucs_ustav_acute_repair_by_oo_text_cursor(text_cursor, selected_symbol)

        # get value from font dictionary for char
        if font_table.items() and font_table.get(selected_symbol):
            new_selected_symbol = font_table.get(selected_symbol)
            text_cursor.setString(new_selected_symbol)  # replace char with converted

        char.restore_attrib(text_cursor)  # restore attributes of selected char
        text_cursor.collapseToEnd()

    # set font to all symbols into Text-cursor
    text_cursor.goLeft(length_string + 1, True)
    text_cursor.CharFontName = UnicodeFont
    # TODO: post-process: repair repeating diacritics
    return None

