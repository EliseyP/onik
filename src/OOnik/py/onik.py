# _*_ coding: utf-8
"""
Модуль содержит функции для обработки текста на церковно-славянском языке.

Интерфейсные функции:
---------------------
    onik,
    onik_titled,
    onik_titles_open,
    ucs_convert_from_office,
    ucs_run_dialog,
    change_acute,
    digits_to_letters,
    digits_from_letters,
    change_letter_at_start,
    change_letter_at_end_o,
    change_letter_at_end_e,
    move_acute_right,
    move_acute_left,
    varia2oxia_ending,
    move_acute_end,
    change_letter_i,
    change_letter_e,
    pluralis,
    add_oxia_for_unacuted_word,
    onik_csl2ru,
    onik_csl2ru_with_acutes,
    привязаны к LO меню/кнопкам, и принимают при запуске
    либо неявно XSCRIPTCONTEXT
    либо для ucs_convert_from_shell явно oDoc
    (при запуске основного оо-макроса из командной строки.)

1. Приведение текста со смешанными ЦСЯ-шрифтами к тексту со шрифтом Ponomar Unicode.

    Проблема:
    ---------
    при обработке некоторых шрифтов, при примении "Поиска и Замены"
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
    и при использовании метода Поиск/Замена, сначала была мысль
    сократить таблицы, чтобы не обрабатывать совпадающие символы.
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
    UPD: В выделенном фрагменте текст также обрабатывается посекционно

    // В выделенном фрагменте с помощью текстового курсора совершается обход каждого символа.
    // (функция ucs_convert_in_oo_text_cursor(oCursor) )
    // Таким образом в многошрифтовой среде имеется доступ к шрифту отдельного символа.
    // Полученный символ проверяется также по короткому словарю.


ucs_convert_from_office
------------------------
    Принимает неявно XSCRIPTCONTEXT, от него получает доступ к текущему документу.

    Вызывается либо напрямую (menu/button) либо через
    GUI-диалог (фуекцией ucs_run_dialog).

    В диалоге представлены список всех шрифтов в документе,
    список цся-шрифтов, для которых доступна конвертация,
    кнопки запуска, отмены и опций (пока не реализовно).
    Через "опции" можно задать параметры конвертации, например,
    варианты обработки некоторых символов (вид прописной У),
    удалить надстрочники, раскрыть титла, обработка цифр, чисел и т.д.

ucs_convert_from_shell(oDoc)
--------------------------

    Основной оо-макрос-обертка запускается из командной строки, и, в свою очередь,
    запускает эту функцию, передавая ей в качестве параметра
    oDoc - документ из открытого odt файла, переданного
    в качестве параметра oo-макросу.

    Вариант - отдельный py/perl скрипт, открывающий odt напрямую,
    получающий доступ к XML атрибутам шрифта и конвертирующий текст
    в зависимости от шрифта.

    Сохранение и закрытие обработанного документа совершается средствами OOBasic.


2. Приведение орфографии русского или смешанного рус/цся текста
к ЦСЯ-форме.
    - Заменяются буквы: у я о е, и прочие.
    - Выставляется звательце.
    - В некоторых словах выставляются ударения.
    - В некоторых словах выставляются титла (опционально).
    - Титла (основные) можно раскрыть
    Исходный текст, предполагается, набран в Ponomar Unicode
    (но проверки на шрифт не осуществляется,
    возможно это нужносделать, для предотвращения срабатывания во всем документе,
    когда в нем есть не-ЦСЯ текст)
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
    (в выделенном тексте)

2.4 change_acute
----------------
    Замена ударения в слове под курсором.
    Обрабатывает начало, середину и конец слова, и буквы о|ѡ и е|є

2.5 move_acute_left, move_acute_right
----------------
    Перемещение ударения влево и вправо в слове под курсором.

2.6 digits_to_letters
---------------------
    Преобразует числа в выделенном тексте в буквенную форму с титлами.

2.7 change_letter_at_start, change_letter_at_end_o, change_letter_at_end_e
--------------------------------------------------------------------------
    Замена букв ѻ|ѡ в начале и о|ѡ и е|ѣ|є в конце слова под курсором

Структура модулей:
==================
onik.py - главный модуль для запуска из LO,
содержит интерфейсные функции

Letters.py  - определения символов (используется всеми остальными модулями)
Ucs_functions.py - функции для конвертации [USC] шрифтов в Ponomar Unicode
Ft.py       - таблицы (словари) соответствий [USC] шрифтов и Ponomar Unicode
Onik_functions.py - функции приводки к ЦСЯ виду
RegsLetters.py - наборы регулярных выражений для Onik_functions (буквы)
Regs.py     - наборы регулярных выражений для Onik_functions (ударения и титла)
numerals,py - перевод чисел в буквы (https://github.com/pgmmpk/cslavonic)

Скрипты:
onik_run.py
    принимает текст в качестве аргумента. Опции аналогичные.
    Через опции доступны все возможности onik-модуля, напр.:
    '-t', '--titlo'['on', 'off', 'open'], default='on'
    '-l', '--digits_to_letters'
    '-L', '--digits_from_letters'
    '-A', '--ch_acute'
    '-F', '--move_acute_forward'
    '-B', '--move_acute_backward'
    '-S', '--chlett_at_start'
    '-E', '--chlett_at_end_e'
    '-O', '--chlett_at_end_o'
    '-I', '--chlett_i'
    '-r', '--csl_to_russian'
    '-R', '--csl_to_russian_with_acutes'
onik_test.py
    текстовый фильтр, принимает на вход unicod-текст,
    выводит приведенный к ЦСЯ виду.
    Опции
        -t --titlo [on|off|open]
        -d --debug
        -l --digits_to_letters
        -r --csl_to_russian
        -R --csl_to_russian_with_acutes

   TODO: объединить два скрипта в один

PS: поскольку это первый скрипт на python'е, то ожидается множество нелепостей.
"""

import re
# import copy
import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
from com.sun.star.awt.MessageBoxResults import OK, YES, NO, CANCEL

# import unohelper

# from com.sun.star.script import CannotConvertException
# from com.sun.star.uno import Exception

from Letters import *
from Ft import *
from Onik_functions import *
from Ucs_functions import *


# from numerals import cu_parse_int, cu_format_int

# попытки сохрянять атрибуты символов.
# from com.sun.star.awt.FontWeight import BOLD, NORMAL
# from com.sun.star.awt.FontSlant import ITALIC
# BOLD = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
# NORMAL = uno.getConstantByName("com.sun.star.awt.FontWeight.NORMAL")
# ITALIC = uno.getConstantByName("com.sun.star.awt.FontSlant.ITALIC")
# ITALIC = uno.Enum("com.sun.star.awt.FontSlant", "ITALIC")
# ----------------------------------------------------------

def MsgBox(message, title=''):
    '''MsgBox'''
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()
    parent_window = doc.CurrentController.Frame.ContainerWindow
    box = parent_window.getToolkit().createMessageBox(parent_window, MESSAGEBOX, BUTTONS_OK, title, message)
    box.execute()
    return None


def get_all_fonts_in_doc(v_doc):
    """get all fonts in current document"""
    allfonts_set = set()
    paragrph_enumeration = v_doc.Text.createEnumeration()
    while paragrph_enumeration.hasMoreElements():
        paragraph = paragrph_enumeration.nextElement()
        if paragraph.supportsService("com.sun.star.text.Paragraph"):
            section_enumeration = paragraph.createEnumeration()
            while section_enumeration.hasMoreElements():
                section = section_enumeration.nextElement()
                section_font = section.CharFontName
                if section_font != "":
                    allfonts_set.add(section_font)
    return allfonts_set


def onik_prepare(v_doc, titles_flag='off'):
    """takes oDoc (CurrentComponent. Convert whole text or selected text)"""

    # для get_string_converted()
    # для запуска onik_titled и onik_titles_open
    def save_new_line(string):
        # TODO: вывод None если не было новой строки
        if re.search(r'\u000A', string):
            return re.sub(r'\u000A', r'<LE> ', string)
        else:
            return string

    def restore_new_line(string):
        # TODO: вывод None если не было новой строки
        # Восстановление перевода строки
        if re.search(r'<LE> ', string):
            return re.sub(r'<LE> ', '\u000A', string)
        else:
            return string

    def convert(string, titles_flags):
        # TODO: проверка на string Null
        #  и в дальнейшем заменять только измененные фрагменты.
        #  Придется поменять все места (5 раз), где встречается convert
        # Сохранение перевода строки
        string = save_new_line(string)

        # Конвертированный текст абзаца
        new_string = get_string_converted(string, titles_flag=titles_flags)

        # Восстановление перевода строки
        new_string = restore_new_line(new_string)
        # TODO: вывод None если не было новой строки
        if new_string:
            return new_string
        else:
            return string

    all_selections = v_doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()
    text = v_doc.Text

    # TODO: Нижеследующий код обработки с учетом выделения
    #  выделить в отдельную функцию. Он повторяется в нескольких местах.
    # Если нет выделенных фрагментов:
    if count == 1 and first_selection_string == '':

        if titles_flag == 'open':
            # msg('Ничего не выделено!')
            MsgBox('Ничего не выделено!')
            return None

        o_par_enum = text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()  # текущий абзац
            o_par_string = o_par.getString()  # текст всего абзаца
            # replace with converted
            # TODO: заменять только если было изменение (если уже есть верный цся текст )
            # придется поменять все места где встречается convert
            o_par.setString(convert(o_par_string, titles_flag))

    # Если есть выделенный текст
    else:

        # код частично из OOO capitalisePython()
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            # selected_string = selection.getString()  # текст выделенной области

            o_par_enum = selection.createEnumeration()

            i = 0
            # обработка поабзацно
            while o_par_enum.hasMoreElements():
                i += 1  # счетчик абзацев (1-based)
                o_par = o_par_enum.nextElement()  # текущий абзац

                # Получение строки для конвертации.
                # Получить выделенный текст [или его часть при мультиабз. выделении] в текущем абзаце
                # Если далее нет абзаца с выделенным текстом
                if not o_par_enum.hasMoreElements():
                    if i == 1:
                        # для 1-го абзаца
                        o_par_string = selection.getString()
                        # replace with converted
                        selection.setString(convert(o_par_string, titles_flag))
                    else:
                        # для остальных
                        t_cursor = text.createTextCursorByRange(o_par.getStart())
                        t_cursor.gotoRange(selection.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string, titles_flag))
                # если далее есть абзац с выделенным текстом
                else:
                    if i == 1:
                        # для 1-го абзаца
                        t_cursor = text.createTextCursorByRange(selection.getStart())
                        t_cursor.gotoRange(o_par.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string, titles_flag))
                    else:
                        # для остальных
                        o_par_string = o_par.getString()
                        o_par.setString(convert(o_par_string, titles_flag))

            j += 1

    return None


def varia2oxia_ending(*args):
    """Меняет варию на оксию перед частицами или местоимениями (ли же бо ся тя etc.)"""

    # desktop = XSCRIPTCONTEXT.getDesktop()
    # v_doc = desktop.getCurrentComponent()
    v_doc = get_current_component()

    all_selections = v_doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()
    text = v_doc.Text

    # если нет выделенных фрагментов:
    if count == 1 and first_selection_string == '':

        o_par_enum = text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()  # текущий абзац
            o_par_string = o_par.getString()  # текст всего абзаца
            # replace with converted
            new_ = convert_varia2oxia(o_par_string)
            if new_:
                o_par.setString(convert_varia2oxia(o_par_string))

    # Если есть выделенный текст
    else:

        # код частично из OOO capitalisePython()
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            # selected_string = selection.getString()  # текст выделенной области

            o_par_enum = selection.createEnumeration()

            i = 0
            # обработка поабзацно
            while o_par_enum.hasMoreElements():
                i += 1  # счетчик абзацев (1-based)
                o_par = o_par_enum.nextElement()  # текущий абзац

                # Получение строки для конвертации.
                # Получить выделенный текст [или его часть при мультиабз. выделении] в текущем абзаце
                # Если далее нет абзаца с выделенным текстом
                if not o_par_enum.hasMoreElements():
                    if i == 1:
                        # для 1-го абзаца
                        o_par_string = selection.getString()
                        # replace with converted
                        new_ = convert_varia2oxia(o_par_string)
                        if new_:
                            selection.setString(convert_varia2oxia(o_par_string))
                    else:
                        # для остальных
                        t_cursor = text.createTextCursorByRange(o_par.getStart())
                        t_cursor.gotoRange(selection.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        new_ = convert_varia2oxia(o_par_string)
                        if new_:
                            t_cursor.setString(convert_varia2oxia(o_par_string))
                # если далее есть абзац с выделенным текстом
                else:
                    if i == 1:
                        # для 1-го абзаца
                        t_cursor = text.createTextCursorByRange(selection.getStart())
                        t_cursor.gotoRange(o_par.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        new_ = convert_varia2oxia(o_par_string)
                        if new_:
                            t_cursor.setString(convert_varia2oxia(o_par_string))
                    else:
                        # для остальных
                        o_par_string = o_par.getString()
                        new_ = convert_varia2oxia(o_par_string)
                        if new_:
                            o_par.setString(convert_varia2oxia(o_par_string))

            j += 1

    return None


# устарела, но возможно пригодится код с локалью
def word_walker(selected_string, titles_flag):
    '''
    Обрабатывает пословно с учетом ЦСЯ-локали некоторой onik-функцией
    :param selected_string: текст абзаца
    :param titles_flag: тип onik-операции с титлом
    :return: обработанный onik-текст
    '''
    # import uno
    from com.sun.star.i18n.WordType import WORD_COUNT
    ctx = uno.getComponentContext()

    def create(name):
        return ctx.getServiceManager().createInstanceWithContext(name, ctx)

    nextwd_bound = uno.createUnoStruct("com.sun.star.i18n.Boundary")
    firstwd_bound = uno.createUnoStruct("com.sun.star.i18n.Boundary")
    a_locale = uno.createUnoStruct("com.sun.star.lang.Locale")
    a_locale.Language = "cu"
    a_locale.Country = "RU"
    mystartpos = 0  # начальная позиция
    brk = create("com.sun.star.i18n.BreakIterator")
    converted_string = selected_string
    # Границы второго слова
    nextwd_bound = brk.nextWord(converted_string, mystartpos, a_locale, WORD_COUNT)

    # границы первого слова (на основе границ второго)
    firstwd_bound = \
        brk.previousWord(converted_string, nextwd_bound.startPos, a_locale, WORD_COUNT)
    if firstwd_bound.startPos >= 0 or firstwd_bound.endPos >= 0:
        # первое слово (текст)
        first_word = \
            converted_string[firstwd_bound.startPos:firstwd_bound.endPos - firstwd_bound.startPos]
        # получить обработанное первое слово
        new_first_word = \
            get_string_converted(first_word, titles_flag=titles_flag)
        # замена первого слова на обработанное
        # (первая граница = 0 ) - уточнить
        _string = \
            new_first_word + converted_string[firstwd_bound.endPos:]
        # замена во всей строке
        converted_string = _string

    # обновление с учетом внесенных изменений первого слова в общую строку
    nextwd_bound = brk.nextWord(converted_string, mystartpos, a_locale, WORD_COUNT)

    #  проход по всем словам со второго
    while nextwd_bound.startPos != nextwd_bound.endPos:
        if nextwd_bound.endPos != 0:
            # текст следующ. слова
            next_word = converted_string[nextwd_bound.startPos:nextwd_bound.endPos]
            # обработанное следующ. слово
            new_next_word = get_string_converted(next_word, titles_flag=titles_flag)
            # замена следующ. слова на обработанное
            _string = \
                converted_string[:nextwd_bound.startPos] + new_next_word + converted_string[nextwd_bound.endPos:]
            # замена во всей строке
            converted_string = _string

        # следующая итерация
        nextwd_bound = brk.nextWord(converted_string, nextwd_bound.startPos, a_locale, WORD_COUNT)

    return converted_string


def onik_titled(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient and set some titles."""
    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    onik_prepare(doc, titles_flag='on')
    return None


def onik_titles_open(*args):
    """In words with titlo - "opens" titlo."""
    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    onik_prepare(doc, titles_flag='open')
    return None


def onik(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient.

    Без титлов (напр. для песнопений)
    """
    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # smgr = ctx.getServiceManager()
    # desktop = smgr.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    onik_prepare(doc, titles_flag='off')

    return None


def onik_csl2ru_prepare(v_doc, save_acutes=False):
    def save_new_line(string):
        # TODO: вывод None если не было новой строки
        if re.search(r'\u000A', string):
            return re.sub(r'\u000A', r'<LE> ', string)
        else:
            return string

    def restore_new_line(string):
        # TODO: вывод None если не было новой строки
        # Восстановление перевода строки
        if re.search(r'<LE> ', string):
            return re.sub(r'<LE> ', '\u000A', string)
        else:
            return string

    def convert(string):
        # Сохранение перевода строки
        string = save_new_line(string)

        # Конвертированный текст абзаца
        new_string = csl_to_russian(string, save_acute=save_acutes)

        # Восстановление перевода строки
        new_string = restore_new_line(new_string)
        if new_string:
            return new_string
        else:
            return string

    all_selections = v_doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()
    text = v_doc.Text

    # если нет выделенных фрагментов:
    if count == 1 and first_selection_string == '':

        o_par_enum = text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()  # текущий абзац
            o_par_string = o_par.getString()  # текст всего абзаца
            # replace with converted
            o_par.setString(convert(o_par_string))

    # Если есть выделенный текст
    else:

        # код частично из OOO capitalisePython()
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            # selected_string = selection.getString()  # текст выделенной области

            o_par_enum = selection.createEnumeration()

            i = 0
            # обработка поабзацно
            while o_par_enum.hasMoreElements():
                i += 1  # счетчик абзацев (1-based)
                o_par = o_par_enum.nextElement()  # текущий абзац

                # Получение строки для конвертации.
                # Получить выделенный текст [или его часть при мультиабз. выделении] в текущем абзаце
                # Если далее нет абзаца с выделенным текстом
                if not o_par_enum.hasMoreElements():
                    if i == 1:
                        # для 1-го абзаца
                        o_par_string = selection.getString()
                        # replace with converted
                        selection.setString(convert(o_par_string))
                    else:
                        # для остальных
                        t_cursor = text.createTextCursorByRange(o_par.getStart())
                        t_cursor.gotoRange(selection.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string))
                # если далее есть абзац с выделенным текстом
                else:
                    if i == 1:
                        # для 1-го абзаца
                        t_cursor = text.createTextCursorByRange(selection.getStart())
                        t_cursor.gotoRange(o_par.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string))
                    else:
                        # для остальных
                        o_par_string = o_par.getString()
                        o_par.setString(convert(o_par_string))

            j += 1

    return None


def onik_csl2ru(*args):
    doc = get_current_component()
    onik_csl2ru_prepare(doc, save_acutes=False)
    return None


def onik_csl2ru_with_acutes(*args):
    doc = get_current_component()
    onik_csl2ru_prepare(doc, save_acutes=True)
    return None


def ucs_convert_from_shell(*args):
    """Convert text with various Orthodox fonts to Ponomar Unicode.

    For runnig from shell from oo-macro run_ucs_convert_py (library OOnik).
    To pass oDoc (ThisComponent) to py-script as first argument
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
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    all_selections = doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()

    if count == 1 and first_selection_string == '':
        # обработка всего документа посекционно
        ucs_convert_by_sections(doc)

    else:  # selected text
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            ucs_convert_by_sections(doc, selection)
            j += 1

    # MsgBox("Done!")
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
    all_fonts_set = get_all_fonts_in_doc(doc)
    all_fonts = list(all_fonts_set)
    # TODO: переписать с учетом check_orthodox_fonts
    orth_fonts = []
    for font_name in all_fonts:
        if check_orthodox_fonts(font_name):
            orth_fonts.append(font_name)
    # orth_fonts = list(all_fonts_set.intersection(aKnownOrthodoxFonts))

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


def change_acute(*args):
    """Меняет ударение в слове под курсором

    Варианты ударений:
    по позиции в слове:
    1. в середине слова
        циклическая замена [оксия|камора]
        Если буква е то замена на е-широкое.
        Если о, то на омегу
    2. начало слова
        циклическая замена [Исо|Апостроф]
    3. Конец слова
        циклическая замена [Вария|оксия|камора]
        также учитываются буквы е и о
    """

    # get the doc from the scripting context which is made available to all scripts
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # TODO: посмотреть locale-код в word_walker
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    new_word = convert_unstripped(cursored_word, acute_util, 'change_type')

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def move_acute_end(*args):
    """
    Перемещает или устанавливает ударение в конец слова под курсором

    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    try:
        new_word = convert_unstripped(cursored_word, acute_util, 'move_to_end')
    except TypeError:
        new_word = ''  # cursored_word

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def move_acute_right(*args):
    """
    Перемещает ударение вправо в слове под курсором
    Циклически.
    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    new_word = convert_unstripped(cursored_word, acute_util, 'move_right')

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def move_acute_left(*args):
    """
    Перемещает ударение влево в слове под курсором
    Циклически.
    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()

    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    new_word = convert_unstripped(cursored_word, acute_util, 'move_left')

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def change_letter_at_start(*args):
    """Меняет буквы в слове под курсором

    начало слова
        циклическая замена [ѻ|ѡ]
    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    change_letter_prepare(doc, 0)
    return None


def change_letter_at_end_o(*args):
    """Меняет буквы в слове под курсором

    Конец слова
        циклическая замена [о|ѡ]
    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    change_letter_prepare(doc, 1)

    return None


def change_letter_at_end_e(*args):
    """Меняет буквы в слове под курсором

    Конец слова
        циклическая замена [е|ѣ|є]
    """

    # get the doc from the scripting context which is made available to all scripts
    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    change_letter_prepare(doc, 2)

    return None


def change_letter_i(*args):
    """Меняет буквы в слове под курсором

    Ударная буква циклическая замена [и|і|ѵ]
    """
    doc = get_current_component()
    change_letter_prepare(doc, 3)
    return None


def change_letter_e(*args):
    """Меняет буквы в слове под курсором

    Ударная буква циклическая замена [е|ѣ|є]
    """
    doc = get_current_component()
    change_letter_prepare(doc, 4)
    return None


def change_letter_prepare(v_doc, change_type):
    # принцип аналогичен change_acute

    view_cursor = v_doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    new_word = convert_unstripped(cursored_word, letters_util, change_type)

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def digits_to_letters(*args):
    '''Преобразует числа в буквы
    в выделенном фрагменте или во всем документе

    Совершает замену текста если в нем были числа,
    и их получилось преобразовать

    :param args: XSCRIPTCONTEXT (неявно)
    :return: None
    '''

    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    all_selections = doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()

    if count == 1 and first_selection_string == '':
        # by paragraph
        o_par_enum = doc.Text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()
            o_par_string = o_par.getString()  # текст абзаца

            # конвертированный текст абзаца
            new_string = \
                convert_string_with_digits(o_par_string)
            if new_string:
                # replace with converted
                o_par.setString(new_string)
        return None

    # если текст выделен
    else:
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            selected_string = selection.getString()
            # пробуем преобразовать числа
            letters = convert_string_with_digits(selected_string)
            if letters:
                # замена выделенного текста если в нем были числа
                selection.setString(letters)

            j += 1

        return None


def digits_from_letters(*args):
    '''Преобразует буквы в числа
    в выделенном фрагменте или во всем документе

    Совершает замену текста если в нем были числа,
    и их получилось преобразовать

    :param args: XSCRIPTCONTEXT (неявно)
    :return: None
    '''

    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    all_selections = doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()

    if count == 1 and first_selection_string == '':
        # msg('Ничего не выделено!')
        MsgBox('Ничего не выделено!')
        '''
        # Пока не имеет смысла
        # by paragraph
        o_par_enum = doc.Text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()
            o_par_string = o_par.getString()  # текст абзаца

            # конвертированный текст абзаца
            new_string = \
                convert_string_letters_to_digits(o_par_string)
            if new_string:
                # replace with converted
                o_par.setString(new_string)
        '''
        return None

    # если текст выделен
    else:
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            selected_string = selection.getString()
            # пробуем преобразовать числа
            letters = convert_string_letters_to_digits(selected_string)
            if letters:
                # замена выделенного текста если в нем были числа
                selection.setString(letters)

            j += 1

        return None


def pluralis(*args):
    '''Заменяет 'и' на 'ы' в окончаниях для мн.ч.: '-[шщ][ы](ѧ|мъ?)(сѧ)?'

    :param args: XSCRIPTCONTEXT (неявно)
    :return: None
    '''

    # ctx = uno.getComponentContext()
    # desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = desktop.getCurrentComponent()
    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с измененным ударением
    new_word = convert_pluralis(cursored_word)

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def add_oxia_for_unacuted_word(*args):
    """Выставляет ударение (оксию) для слова без ударения

    Ударение ставится для первой гласной.
    :param args:
    :return: None
    """
    doc = get_current_component()

    view_cursor = doc.CurrentController.getViewCursor()
    tc = view_cursor.Text.createTextCursorByRange(view_cursor)

    # если выделено, перейти в начало выделения
    tc.collapseToStart()

    tc.gotoStartOfWord(True)

    # длина от курсора до начала
    to_start = len(tc.String)

    tc.goRight(0, False)
    tc.gotoNextWord(True)

    # от начала слова до след-го слова
    gen_len = len(tc.String)

    # LO не может перейти в конец слова
    # в которам ударная буква последняя
    # tc.gotoEndOfWord(True) # not always work

    # слово под курсором
    cursored_word = tc.String

    # слово с ударением
    new_word = add_oxia_for_unacuted_word_handler(cursored_word)

    if new_word:
        tc.String = new_word
        # вернуться в исходное положение
        view_cursor.goLeft(gen_len - to_start, False)

    return None


def get_current_component():
    _ctx = uno.getComponentContext()
    _smgr = _ctx.getServiceManager()
    _desktop = _smgr.createInstanceWithContext('com.sun.star.frame.Desktop', _ctx)
    _doc = _desktop.getCurrentComponent()
    if _doc:
        return _doc


def onik_unicode_to_ucs_prepare(v_doc, split_monograph=False):
    def save_new_line(string):
        # TODO: вывод None если не было новой строки
        if re.search(r'\u000A', string):
            return re.sub(r'\u000A', r'<LE> ', string)
        else:
            return string

    def restore_new_line(string):
        # TODO: вывод None если не было новой строки
        # Восстановление перевода строки
        if re.search(r'<LE> ', string):
            return re.sub(r'<LE> ', '\u000A', string)
        else:
            return string

    def convert(string):
        # Сохранение перевода строки
        string = save_new_line(string)

        # Конвертированный текст абзаца
        new_string = unicode_to_ucs(
            string,
            split_monograph=split_monograph
        )

        # Восстановление перевода строки
        new_string = restore_new_line(new_string)
        if new_string:
            return new_string
        else:
            return string

    all_selections = v_doc.getCurrentController().getSelection()
    first_selection = all_selections.getByIndex(0)
    first_selection_string = first_selection.getString()
    count = all_selections.getCount()
    text = v_doc.Text

    # если нет выделенных фрагментов:
    if count == 1 and first_selection_string == '':

        o_par_enum = text.createEnumeration()
        while o_par_enum.hasMoreElements():
            o_par = o_par_enum.nextElement()  # текущий абзац
            o_par_string = o_par.getString()  # текст всего абзаца
            # replace with converted
            o_par.setString(convert(o_par_string))

    # Если есть выделенный текст
    else:

        # код частично из OOO capitalisePython()
        if count >= 1:  # ie we have a selection
            j = 0
        while j < count:
            selection = all_selections.getByIndex(j)
            # selected_string = selection.getString()  # текст выделенной области

            o_par_enum = selection.createEnumeration()

            i = 0
            # обработка поабзацно
            while o_par_enum.hasMoreElements():
                i += 1  # счетчик абзацев (1-based)
                o_par = o_par_enum.nextElement()  # текущий абзац

                # Получение строки для конвертации.
                # Получить выделенный текст [или его часть при мультиабз. выделении] в текущем абзаце
                # Если далее нет абзаца с выделенным текстом
                if not o_par_enum.hasMoreElements():
                    if i == 1:
                        # для 1-го абзаца
                        o_par_string = selection.getString()
                        # replace with converted
                        selection.setString(convert(o_par_string))
                    else:
                        # для остальных
                        t_cursor = text.createTextCursorByRange(o_par.getStart())
                        t_cursor.gotoRange(selection.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string))
                # если далее есть абзац с выделенным текстом
                else:
                    if i == 1:
                        # для 1-го абзаца
                        t_cursor = text.createTextCursorByRange(selection.getStart())
                        t_cursor.gotoRange(o_par.getEnd(), True)
                        o_par_string = t_cursor.getString()
                        t_cursor.setString(convert(o_par_string))
                    else:
                        # для остальных
                        o_par_string = o_par.getString()
                        o_par.setString(convert(o_par_string))

            j += 1

    return None


def onik_unicode_to_ucs(*args):
    doc = get_current_component()
    onik_unicode_to_ucs_prepare(doc, split_monograph=False)
    return None


def onik_unicode_to_ucs_splitted(*args):
    doc = get_current_component()
    onik_unicode_to_ucs_prepare(doc, split_monograph=True)
    return None


# lists the scripts, that shall be visible inside OOo. Can be omitted, if
# all functions shall be visible.
g_exportedScripts = (
    onik,
    onik_titled,
    onik_titles_open,
    ucs_convert_from_office,
    ucs_run_dialog,
    change_acute,
    digits_to_letters,
    digits_from_letters,
    change_letter_at_start,
    change_letter_at_end_o,
    change_letter_at_end_e,
    move_acute_right,
    move_acute_left,
    varia2oxia_ending,
    move_acute_end,
    change_letter_i,
    change_letter_e,
    pluralis,
    add_oxia_for_unacuted_word,
    onik_csl2ru,
    onik_csl2ru_with_acutes,
    onik_unicode_to_ucs,
)
