# _*_ coding: utf-8
"""
Модуль содержит функции для обработки текста на церковно-славянском языке.

Интерфейсные функции:
---------------------
onik, onik_titled, onik_titles_open, ucs_convert_from_office, ucs_convert_from_shell, ucs_run_dialog
    привязаны к LO меню/кнопкам, и принимают при запуске
    либо неявно XSCRIPTCONTEXT
    либо для ucs_convert_from_shell явно oDoc
    (при запуске основного оо-макроса из командной строки.)

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
    Принимает неявно XSCRIPTCONTEXT, от него получает доступ к текущему документу.

    Вызывается либо напрямую (menu/button) либо через
    GUI-диалог (фуекцией ucs_run_dialog).

    В нем представлены список всех шрифтов в документе,
    список цся-шрифтов, для которых доступна конвертация,
    кнопки запуска, отмены и опций (пока не реализовно).
    Через "опции" можно задать параметры конвертации, например,
    варианты обработки некоторых символов (вид прописной У),
    удалить надстрочники, раскрыть титла, обработка цифр, чисел и т.д.

ucs_ucs_convert_from_shell(oDoc)
--------------------------
    Основной оо-макрос запускается из командной строки, и, в свою очередь,
    запускает эту функцию, передавая ей в качестве параметра
    oDoc - документ из открытого odt файла, переданного
    в качестве параметра oo-макросу.

    Пока не ясно, как передать аргументы при запуске оо-макросв из командной строки
    python-скрипту из OO-библиотеки напрямую => написана  обертка.
    Как вариант - писать отдельный py/perl скрипт открывающий odt напрямую,
    получающий доступ к XML атрибутам шрифта и конвертирующий текст
    в зависимости от шрифта.

    Сохранение и закрытие обработанного документа совершается средствами OOBasic.


2. Приведение орфографии русского или смешанного рус\цся текста
к ЦСЯ-форме.
    - Заменяются буквы: у я о е, и прочие.
    - Выставялется звательце.
    - В некоторых словах выставляются ударения.
    - В некотрых словах выставляются титла (опционально).
    - Титла (основные) можно раскрыть
    Исходный текст предполагается набран в Ponomar Unicode
    (но проверки на шрифт не осуществляется)
    Обрабатывается только открытый документ (все равно требуется ручная доводка)

    NB: Текст можно набирать в обычной русской раскладке, выставив шрифт Ponomar
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

Структура модулей:
==================
onik.py - главный модуль для запуска из LO,
содержит интерфейсные функции и обработку шрифтов ucs

Letters.py  - определения символов (используется всеми остальными модулями)
Ucs_functions.py - функции для конвертации [USC] шрифтов в Ponomar Unicode
Ft.py       - таблицы (словари) соответствий [USC] шрифтов и Ponomar Unicode
Onik_functions.py - функции приводки к ЦСЯ виду
Regs.py     - наборы регулярных выражений для Onik_run

утилита onik_test.py - текстовый фильтр, принимает на вход unicod-текст,
выводит приведенный к ЦСЯ виду. Опции -t --titlo [on|off|open]

PS: поскольку это первый скрипт на python'е, то ожидается множество нелепостей.
"""


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
from Onik_functions import *
from Ucs_functions import *

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
