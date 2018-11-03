# _*_ coding: utf-8
"""
Модуль содержит функции для обработки текста на церковно-славянском языке.

Интерфейсные функции:
---------------------
onik, onik_titled, onik_titles_open, ucs_convert_from_office, ucs_convert_from_shell
запускаются из OOBasic макроса, и принимают либо неявно XSCRIPTCONTEXT
либо явно oDoc (при запуске основного оо-макроса из командной строки.)

1. Приведение текста со смешанными ЦСЯ-шрифтами к тексту со шрифтом Ponomar Unicode.

    Проблема:
    ---------
    при обработке некоторых шрифтов, при примении Поиска и Замены
    по всей строке, используя словарь (perl-хэш, массивы в OOBasic)
    возникают повторные срабатывания - коды символов замены оказываются в словаре.
    Вариант решения: обрабатывать текст посимвольно, также со словарем.
    Средствами OOBasic такое решение всесьма медленно, поэтому основная обработка была перенесена в данный python-модуль.

Общий подход для ucs конвертеров:
=================================

Для целого документа:
---------------------
    совершается обход в каждом абзаце каждой "секции" TextPortion.
    (Секция - набор символов с одинаковыми атрибутами.
    Таким образом в смешанной шрифтовой среде можно выделить относительно протяженные моношрифтовые фрагменты.)
    Текст из таких фрагментов конвертируется посимвольно средствами python'а
    (функция ucs_convert_string_with_font_bforce(string, font_table))
    Конвертация совершается по "короткому словарю", в котором находятся только несовпадающие символы.

    -------------------------------------------------------
    Исторически, при обработке только средствами OOBasic,
    и при использовании метода Поиск\Замена, сначала была мысль сократить таблицы, чтобы не обрабатывать совпадающие символы.
    Затем, при использовании посимвольной обработки были использованы
    уже полные таблицы, но с учетом статистики, чтобы также сократить
    время обхода словаря, но уже с другой стороны, -
    наиболее частые символы были помещены в начало таблицы.

    При использовании python-словарей вероятно нет большой разницы -
    выбирать совпадающий символ из полного словаря,
    либо, проверив короткий словарь на отсутствие ключа,
    оставить символ без изменений.
    Пока используются короткие словари.
    -------------------------------------------------------

Для выделенного текста
----------------------
    В выделенном фрагменте с помощью текстового курсора совершается обход каждого символа.
    (функция ucs_convert_in_oo_text_cursor(oCursor) )
    Таким образом в многошрифтовой среде имеется доступ к шрифту отдельного символа.
    Полученный символ проверяется также по короткому словарю.


ucs_convert_from_office
------------------------
    для запуска из среды Libre Office
    Принимает неявно XSCRIPTCONTEXT, от него получает доступ к текущему документу.

    Эту функцию использует GUI-диалог.
    В нем представлены список всех шрифтов в документе,
    список цся-шрифтов, для которых доступна конвертация,
    кнопки запуска, отмены и опций (пока не реализовно).
    Через "опции" можно задать параметры конвертации, например,
    варианты обработки некоторых символов (вид прописной У),
    удалить надстрочники, раскрыть титла, обработка цифр, чисел и т.д.

ucs_ucs_convert_from_shell(oDoc)
--------------------------
    Основной оо-макрос запускается из командной строки, и, в свою очередь, запускает эту функцию,
    передавая ей в качестве параметра oDoc - документ из открытого odt файла, переданного
    в качестве параметра oo-макросу.
    Пока не ясно, как передать аргументы при запуске оо-макросв из командной строки
    python-скрипту из OO-библиотеки напрямую => написана  обертка.
    Сохранение и закрытие обработанного документа совершается средствами OOBasic.


2. Приведение орфографии русского или смешанного рус\цся текста
к ЦСЯ-форме.
    - Заменяются буквы: у я о е, и прочие.
    - Выставялется звательце.
    - В некоторых словах выставляются ударения.
    - В некотрых словах выставляются титла (опционально).
    - Титла (основные) можно раскрыть
    Исходный текст - в Ponomar Unicode
    Обрабатывается только открытый документ (все равно требуется ручная доводка)

    NB: Текст можно набирать в обычной русской раскладке,
    потом обрабатывать этим скриптом. Далее конечно руками :-)

2.1 onik
--------
    Текст обрабатывается поабзацно для всего документа,
    и через текстовый курсор для выделенного фрагмента.

2.2 onik_titled
--------------------
    То же, что и onik, только выставляются некотрые титла.

2.3 onik_titles_open
--------------------
    Раскрываются титла в соответствующих словах и пробуется выставить ударение.

PS: поскольку это первый скрипт на python'е, то ожидается множество нелепостей.
"""

# TODO: разделить на модули чтобы можно было тестировать отдельно, вне LibreOffice

import re
# import copy
# import uno
# import unohelper

#  для msg() - для отладки.
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, \
    BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
from com.sun.star.awt.MessageBoxResults import OK, YES, NO, CANCEL

from Letters import *
from Ft import *
from Onik_run import *
# from regs

# попытки сохрянять атрибуты символов.
# from com.sun.star.awt.FontWeight import BOLD, NORMAL
# from com.sun.star.awt.FontSlant import ITALIC
# BOLD = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
# NORMAL = uno.getConstantByName("com.sun.star.awt.FontWeight.NORMAL")
# ITALIC = uno.getConstantByName("com.sun.star.awt.FontSlant.ITALIC")
# ITALIC = uno.Enum("com.sun.star.awt.FontSlant", "ITALIC")
# ----------------------------------------------------------

aKnownOrthodoxFonts = {
    "Hirmos Ponomar TT",
    "Hirmos Ponomar TT1",
    "Hirmos Ucs",
    "Hirmos Ucs1",
    "Irmologion",
    "Irmologion Ucs",
    "Irmologion Ucs1",
    "Irmologion Ucs2",
    "Orthodox",
    "OrthodoxDigits",
    "OrthodoxDigits1",
    "OrthodoxDigitsLoose",
    "OrthodoxLoose",
    "Orthodoxtt eRoos",
    "Orthodox.tt eRoos",
    "Orthodox.tt eRoos1",
    "Orthodox.tt ieERoos",
    "Orthodox.tt ieERoos1",
    "Orthodox.tt ieUcs8",
    "Orthodox.tt ieUcs81",
    "Orthodox.tt ieUcs8 Caps",
    "Orthodox.tt Ucs8",
    "Orthodox.tt Ucs81",
    "Orthodox.tt Ucs8 Caps",
    "Orthodox.tt Ucs8 Caps tight",
    "Orthodox.tt Ucs8 tight",
    "Orthodox.tt Ucs8 tight1",
    "Triodion ieUcs",
    "Triodion Ucs",
    "Triodion Ucs1",
    "Ustav",
    "Ustav1",
    "Valaam",
    "Valaam1"
}

# -------------------------------------
# only for debug (now)


def msg(message, title=''):
    v_doc = XSCRIPTCONTEXT.getDesktop().getCurrentComponent()
    parent_window = v_doc.CurrentController.Frame.ContainerWindow
    box = parent_window.getToolkit().createMessageBox(parent_window, MESSAGEBOX, BUTTONS_OK, title, message)
    box.execute()
    return None


def get_all_fonts_in_doc(vDoc):
    """get all fonts in current document"""
    myset = set()
    oParEnum = vDoc.Text.createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.Paragraph"):
            oSecEnum = oPar.createEnumeration()
            while oSecEnum.hasMoreElements():
                oParSection = oSecEnum.nextElement()
                sSecFnt = oParSection.CharFontName
                if sSecFnt != "":
                    myset.add(sSecFnt)
    return myset


def get_font_table(font_name):
    """return fonttable-set"""
    if font_name in {
        "Triodion Ucs",
        "Triodion ieUcs",
        "Triodion Ucs1",
        "Hirmos Ucs",
        "Hirmos Ucs1",
    }:
        return font_table_triodion
    elif font_name in {
        "Orthodox.tt Ucs8",
        "Orthodox.tt Ucs81",
        "Orthodox.tt Ucs8 tight",
        "Orthodox.tt Ucs8 tight1",
        "Orthodox.tt ieUcs8",
        "Orthodox.tt ieUcs81",
        "Irmologion Ucs",
        "Irmologion Ucs1",
        "Irmologion Ucs2",
    }:
        return font_table_orthodox_tt
    elif font_name in {
        "Orthodox.tt Ucs8 Caps",
        "Orthodox.tt Ucs8 Caps tight",
        "Orthodox.tt ieUcs8 Caps",
    }:
        return font_table_orthodox_tt_caps
    elif font_name in {
        "Orthodox.tt eRoos",
        "Orthodox_tt eRoos",
        "Orthodox.tt eRoos1",
        "Orthodox.tt ieERoos",
        "Orthodox.tt ieERoos1",
    }:
        return font_table_orthodox_e_roos
    elif font_name in {
        "OrthodoxDigitsLoose",
        "OrthodoxDigits",
        "OrthodoxDigits1",
    }:
        return font_table_orthodox_digits_loose
    elif font_name in {
        "OrthodoxLoose",
        "Orthodox",
    }:
        return font_table_orthodox_loose
    elif font_name in {
        "Ustav",
        "Ustav1",
    }:
        return font_table_ustav
    elif font_name in {
        "Valaam",
        "Valaam1",
    }:
        return font_table_valaam
    elif font_name in {
        "Hirmos Ponomar TT",
        "Hirmos Ponomar TT1",
    }:
        return font_table_hirmos_ponomar
    elif font_name in {
        "Irmologion",
    }:
        return font_table_irmologion
    else:
        return {}


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


def onik_prepare(v_doc, titles_flag='off'):
    """takes oDoc (CurrentComponent. Convert whole text or selected text)"""
    # для get_string_converted()
    # для запуска onik_titled и onik_titles_open

    # видимый курсор для обработки выделенного текста
    o_view_cursor = \
        v_doc.CurrentController.getViewCursor()
    selected_string = o_view_cursor.getString()  # текст выделенной области
    is_titled_flag = titles_flag

    if selected_string == '':  # whole document
        # by paragraph, for preserv it
        o_par_enum = v_doc.Text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()
            if o_par.supportsService("com.sun.star.text.Paragraph"):
                o_par_string = o_par.getString()  # текст абзаца
                # конвертированный текст абзаца

                new_string = \
                    get_string_converted(o_par_string, titles_flag=titles_flag)

                # replace with converted
                o_par.setString(new_string)

    else:  # selected text
        # TODO: multi-selection (see Capitalise.py)
        # конвертированный текст выделенной области

        new_selected_string = get_string_converted(selected_string, titles_flag=titles_flag)

        # replace with converted (for selected area)
        o_view_cursor.setString(new_selected_string)
    return None


def onik_titled(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient and set some titles."""
    # get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    doc = desktop.getCurrentComponent()

    onik_prepare(doc, titles_flag='on')
    return None


def onik_titles_open(*args):
    """In words with titlo - "opens" titlo."""
    # get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    doc = desktop.getCurrentComponent()

    onik_prepare(doc, titles_flag='open')
    return None


def onik(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient.

    Без титлов (напр. для песнопений)
    """
    # get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    doc = desktop.getCurrentComponent()

    onik_prepare(doc, titles_flag='off')

    return None


def ucs_convert_from_shell(*args):
    """Convert text with various Orthodox fonts to Ponomar Unicode.

    For runnig from oo-macro from shell
    to pass oDoc (ThisComponent) to py-script as first argument
    $ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"
    """
    o_doc = args[0]
    # обработка всего документа посекционно
    ucs_convert_by_sections(o_doc)

    return None


def ucs_convert_from_office(*args):
    """Convert text with various Orthodox fonts to Ponomar Unicode.
    for running from Libre/Open Office - Menu, toolbar or gui-dialog.
    """
    desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = XSCRIPTCONTEXT.getDocument()
    doc = desktop.getCurrentComponent()
    # msg('test')
    # видимый курсор для обработки выделенного текста
    view_cursor = doc.CurrentController.getViewCursor()
    selected_string = view_cursor.getString()  # текст выделенной области

    if selected_string == '':  # whole document
        # обработка всего документа посекционно
        ucs_convert_by_sections(doc)

    else:  # selected text
        # TODO: multi-selection (see Capitalise.py)
        text_cursor = view_cursor.Text.createTextCursorByRange(view_cursor)
        # обработка выделенного фрагмента через текстовый курсор
        ucs_convert_in_oo_text_cursor(text_cursor)
        view_cursor.collapseToEnd()
    # msg("Done!")
    return None


def ucs_dialog(x=None, y=None):
    """ Shows dialog with two list boxes.
        @param x dialog positio in twips, pass y also
        @param y dialog position in twips, pass y also
        @return 1 if OK button pushed, otherwise 0
    """
    title = 'Orthodox шрифты -> в Ponomar Unicode'
    WIDTH = 600
    HORI_MARGIN = VERT_MARGIN = 8
    LBOX_WIDTH = 200
    LBOX_HEIGHT = 160
    BUTTON_WIDTH = 165
    BUTTON_HEIGHT = 26
    HORI_SEP = VERT_SEP = 8
    label_width = LBOX_WIDTH  # WIDTH - BUTTON_WIDTH - HORI_SEP - HORI_MARGIN * 2
    LABEL_HEIGHT = BUTTON_HEIGHT  # * 2 + 5
    EDIT_HEIGHT = 24
    HEIGHT = VERT_MARGIN * 2 + LABEL_HEIGHT + VERT_SEP + EDIT_HEIGHT + 150
    import uno
    from com.sun.star.awt.PosSize import POS, SIZE, POSSIZE
    from com.sun.star.awt.PushButtonType import OK, CANCEL
    from com.sun.star.util.MeasureUnit import TWIP
    ctx = uno.getComponentContext()

    def create(name):
        return ctx.getServiceManager().createInstanceWithContext(name, ctx)

    dialog = create("com.sun.star.awt.UnoControlDialog")
    dialog_model = create("com.sun.star.awt.UnoControlDialogModel")
    dialog.setModel(dialog_model)
    dialog.setVisible(False)
    dialog.setTitle(title)
    dialog.setPosSize(0, 0, WIDTH, HEIGHT, SIZE)

    def add(name, type, x_, y_, width_, height_, props):
        model = dialog_model.createInstance("com.sun.star.awt.UnoControl" + type + "Model")
        dialog_model.insertByName(name, model)
        control = dialog.getControl(name)
        control.setPosSize(x_, y_, width_, height_, POSSIZE)
        for key, value in props.items():
            setattr(model, key, value)

    add(
        "label", "FixedText",
        HORI_MARGIN,
        VERT_MARGIN,
        label_width,
        LABEL_HEIGHT,
        {"Label": 'Шрифты в документе', "NoLabel": True}
    )
    add(
        "label1", "FixedText",
        HORI_MARGIN + LBOX_WIDTH,
        VERT_MARGIN,
        label_width,
        LABEL_HEIGHT,
        {"Label": 'Orthodox шрифты', "NoLabel": True}
    )

    add(
        "btn_ok", "Button",
        HORI_MARGIN + LBOX_WIDTH * 2 + HORI_SEP,
        VERT_MARGIN,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        {"PushButtonType": OK, "DefaultButton": True, 'Label': 'Конвертировать'}
    )
    add(
        "btn_cancel", "Button",
        HORI_MARGIN + LBOX_WIDTH * 2 + HORI_SEP,
        VERT_MARGIN + BUTTON_HEIGHT + 5,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        {"PushButtonType": CANCEL, 'Label': 'Отмена'}
    )

    add(
        "lbox1", "ListBox",
        HORI_MARGIN, LABEL_HEIGHT + VERT_MARGIN + VERT_SEP,
                     WIDTH / 3 - HORI_MARGIN,
        LBOX_HEIGHT,
        {}
    )
    add(
        "lbox2", "ListBox",
        HORI_MARGIN + LBOX_WIDTH,
        LABEL_HEIGHT + VERT_MARGIN + VERT_SEP,
        WIDTH / 3 - HORI_MARGIN,
        LBOX_HEIGHT,
        {}
    )

    desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = XSCRIPTCONTEXT.getDocument()
    doc = desktop.getCurrentComponent()

    # получить список всех шрифтов
    # и инициализировать списки
    all_fonts_ = get_all_fonts_in_doc(doc)
    all_fonts = list(all_fonts_)
    orth_fonts = list(all_fonts_.intersection(aKnownOrthodoxFonts))

    lb1 = dialog.getControl('lbox1')
    lb2 = dialog.getControl('lbox2')
    lb1.addItems(all_fonts, 0)
    lb2.addItems(orth_fonts, 0)
    lb1.selectItemPos(0, True)  # not work

    frame = create("com.sun.star.frame.Desktop").getCurrentFrame()
    window = frame.getContainerWindow() if frame else None
    dialog.createPeer(create("com.sun.star.awt.Toolkit"), window)
    if not x is None and not y is None:
        ps = dialog.convertSizeToPixel(uno.createUnoStruct("com.sun.star.awt.Size", x, y), TWIP)
        _x, _y = ps.Width, ps.Height
    elif window:
        ps = window.getPosSize()
        _x = ps.Width / 2 - WIDTH / 2
        _y = ps.Height / 2 - HEIGHT / 2
    dialog.setPosSize(_x, _y, 0, 0, POS)
    n = dialog.execute()
    dialog.dispose()
    return n


def ucs_run_dialog(*args):
    n = ucs_dialog()
    if n == 1:
        ucs_convert_from_office()


# button url
# vnd.sun.star.script:onik.py$onik?language=Python&location=user

# lists the scripts, that shall be visible inside OOo. Can be omitted, if
# all functions shall be visible, however here getNewString shall be suppressed
g_exportedScripts = onik, onik_titled, onik_titles_open,  ucs_convert_from_office, ucs_run_dialog # UCSconvert_from_shell,
