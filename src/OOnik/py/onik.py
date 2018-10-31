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

# попытки сохрянять атрибуты символов.
# from com.sun.star.awt.FontWeight import BOLD, NORMAL
# from com.sun.star.awt.FontSlant import ITALIC
# BOLD = uno.getConstantByName("com.sun.star.awt.FontWeight.BOLD")
# NORMAL = uno.getConstantByName("com.sun.star.awt.FontWeight.NORMAL")
# ITALIC = uno.getConstantByName("com.sun.star.awt.FontSlant.ITALIC")
# ITALIC = uno.Enum("com.sun.star.awt.FontSlant", "ITALIC")
# ----------------------------------------------------------



# Init letters-variables
NoSymbols = ''  #
# ---------------------------------------
Oxia = '\u0301'  #
Varia = '\u0300'  #
Zvatelce = '\u0486'  #
Kamora = '\u0311'  #
Titlo = '\u0483'  #
Pokrytie = '\u0487'  #
Kendema = '\u0308'  # two dots
# ---------------------------------------
ZvatelceUp = '\uE000'  #
Iso = Zvatelce + Oxia  # '\uE001'  #
IsoUp = '\uE002'  #
Apostrof = Zvatelce + Varia  # '\uE003'  #
ApostrofUp = '\uE004'  #
ApostrofGreat = '\uE005'  #
# ---------------------------------------
CrossOrthodox = '\u2626'  # ☦
# Dagger = '\u2020'  # †

NotationSlash = "/"
NotationDoubleSlash = "//"
# ---------------------------------------
DigitZero = "0"
DigitOne = "1"
DigitTwo = "2"
DigitThree = "3"
DigitFour = "4"
DigitFive = "5"
DigitSix = "6"
DigitSeven = "7"
DigitEight = "8"
DigitNine = "9"
# bold, "in-style" shape
unicDigitZero = '\uF430'  #
unicDigitOne = '\uF431'  #
unicDigitTwo = '\uF432'  #
unicDigitThree = '\uF433'  #
unicDigitFour = '\uF434'  #
unicDigitFive = '\uF435'  #
unicDigitSix = '\uF436'  #
unicDigitSeven = '\uF437'  #
unicDigitEight = '\uF438'  #
unicDigitNine = '\uF439'  #
# ---------------------------------------
unicNarrowD = '\u1C81'  # ᲁ
unicCapitalIe = '\u0415'  # Е
unicSmallIe = '\u0435'  # е
unicCapitalUkrIe = '\u0404'  # Є
unicSmallUkrIe = '\u0454'  # є
unicCapitalYat = '\u0462'  # Ѣ
unicSmallYat = '\u0463'  # ѣ
# ---------------------------------------
unicCapitalI = '\u0418'  # И
unicSmallI = '\u0438'  # и
unicCapitalUkrI = '\u0406'  # I
unicSmallUkrI = '\u0456'  # i without dot (decimal), as base
# unicSmallUkrIWithDot = '\uE926'  # i with dot
unicCapitalYi = '\u0407'  # Ї with dots
unicSmallYi = '\u0457'  # ї with dots

unicCapitalIzhitsa = '\u0474'  # Ѵ
unicSmallIzhitsa = '\u0475'  # ѵ
unicCapitalIzhitsaDblGrave = '\u0476'  # Ѷ
unicSmallIzhitsaDblGrave = '\u0477'  # ѷ
# ---------------------------------------
unicCapitalO = '\u041E'  # О
unicSmallO = '\u043E'  # о
unicNarrowO = '\u1C82'  # ᲂ
unicCapitalRoundOmega = '\u047A'  # Ѻ
unicSmallRoundOmega = '\u047B'  # ѻ
unicCapitalOmega = '\u0460'  # Ѡ
unicSmallOmega = '\u0461'  # ѡ
unicCapitalBroadOmega = '\uA64C'  # Ꙍ
unicSmallBroadOmega = '\uA64D'  # ꙍ
unicCapitalOmegaTitled = '\u047C'  # Ѽ
unicSmallOmegaTitled = '\u047D'  # ѽ
# ---------------------------------------
unicCapitalOt = '\u047E'  # Ѿ
unicSmallOt = '\u047F'  # ѿ
# ---------------------------------------
unicCapitalU = '\u0423'  # У
unicSmallU = '\u0443'  # у
unicCapitalUk = unicCapitalO + unicSmallU  # Oy '\u0478'
unicSmallUk = unicNarrowO + unicSmallU  # ᲂy
unicCapitalMonogrUk = '\uA64A'  # ' Ꙋ
unicSmallMonogrUk = '\uA64B'  # ' ꙋ
# ---------------------------------------
unicCapitalEf = '\u0424'  # Ф
unicSmallEf = '\u0444'  # ф
unicCapitalFita = '\u0472'  # Ѳ
unicSmallFita = '\u0473'  # ѳ
# ---------------------------------------
unicCapitalIotifA = '\u0656'  # Ꙗ
unicSmallIotifA = '\u0657'  # ꙗ
unicCapitalLittleYus = '\u0466'  # Ѧ
unicSmallLittleYus = '\u0467'  # ѧ
unicCapitalIotifLittleYus = '\u0468'  # Ѩ
unicSmallIotifLittleYus = '\u0469'  # ѩ
unicCapitalYa = '\u042F'  # Я
unicSmallYA = '\u044F'  # я
# ---------------------------------------
# unicSmallMonogrUkAndZvatelce = '\uE8E5'  # 
# unicSmallYatAndOxia = '\uE901'  # 
# unicSmallYatAndVaria = '\uE903'  # 
# unicSmallYatAndZvatelce = '\uE904'  # 
unicSmallYeru = '\u044B'  # ы
# unicSmallYeruAndZvatelce = '\uE928'  # 

# Some variants while converting

# Orthodox.tt eRoos	: chr(&H0456) і ->  chr(&HE926)
# Valaam			: chr(&H0152) Œ	->  chr(&HE926)
unicSmallUkrIWithDot = unicSmallYi  # i -> ї

Dagger = CrossOrthodox  # † -> ☦

unicSmallMonogrUkAndZvatelce = unicSmallMonogrUk + Zvatelce  # 
unicSmallYatAndOxia = unicSmallYat + Oxia  # 
unicSmallYatAndVaria = unicSmallYat + Varia  # 
unicSmallYatAndZvatelce = unicSmallYat + Zvatelce  # 
unicSmallYeruAndZvatelce = unicSmallYeru + Zvatelce  # 

UnicodeFont = "Ponomar Unicode"

# -------------------------------------
# set of dictionaries for Orthodox fonts
# this is short form - symbols are not matching with Ponomar Unicode
# (matching symbols not replaced).

font_table_triodion = {
    '#': Zvatelce,
    '$': Zvatelce + Oxia,
    '%': Zvatelce + Varia,
    '&': Titlo,
    '+': '\u2DE1' + Pokrytie,
    '0': unicSmallO + Oxia,
    '1': Oxia,
    '2': Varia,
    '3': Zvatelce,
    '4': Zvatelce + Oxia,
    '5': Zvatelce + Varia,
    '6': Kamora,
    '7': Titlo,
    '8': '\u033E',
    '9': '\u0436' + Titlo,
    '<': '\u2DEF',
    '=': '\u2DE9' + Pokrytie,
    '>': '\u2DEC' + Pokrytie,
    '?': '\u2DF1' + Pokrytie,
    '@': Varia,
    'A': '\u0430' + Varia,
    'B': unicSmallYat + Kamora,
    'C': '\u2DED' + Pokrytie,
    'D': '\u0434' + '\u2DED' + Pokrytie,
    'E': unicSmallIe + Varia,
    'F': unicCapitalFita,
    'G': '\u0433' + Titlo,
    'H': unicSmallOmega + Oxia,
    'I': unicCapitalUkrI,
    'J': unicSmallUkrI + Varia,
    'K': '\uA656' + Zvatelce,
    'L': '\u043B' + '\u2DE3',
    'M': unicCapitalIzhitsaDblGrave,
    'N': unicCapitalRoundOmega + Zvatelce,
    'O': unicCapitalRoundOmega,
    'P': '\u0470',
    'Q': unicCapitalOmegaTitled,
    'R': '\u0440' + Titlo,
    'S': unicSmallLittleYus + Varia,
    'T': '\u047E',
    'U': unicCapitalUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': '\u046E',
    'Y': unicSmallMonogrUk + Varia,
    'Z': unicCapitalLittleYus,
    '\\': Titlo,
    '^': Kamora,
    '_': '\u033E',
    'a': '\u0430' + Oxia,
    'b': '\u2DEA' + Pokrytie,
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicSmallIe + Oxia,
    'f': unicSmallFita,
    'g': '\u2DE2' + Pokrytie,
    'h': '\u044B' + Oxia,
    'i': unicSmallUkrI,
    'j': unicSmallUkrI + Oxia,
    'k': '\uA657' + Zvatelce,
    'l': '\u043B' + Titlo,
    'm': unicSmallIzhitsaDblGrave,
    'n': unicSmallRoundOmega + Zvatelce,
    'o': unicSmallRoundOmega,
    'p': '\u0471',
    'q': unicSmallOmegaTitled,
    'r': '\u0440' + '\u2DED' + Pokrytie,
    's': unicSmallLittleYus + Oxia,
    't': '\u047F',
    'u': unicSmallUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'x': '\u046F',
    'y': unicSmallMonogrUk + Oxia,
    'z': unicSmallLittleYus,
    '{': unicSmallMonogrUk + Kamora,
    '|': unicSmallLittleYus + Zvatelce + Varia,
    '}': unicSmallI + Titlo,
    '~': Oxia,
    '¤': '\u0482',
    '¦': '\u0445' + Titlo,
    '§': '\u0447' + Titlo,
    '©': '\u0441' + Titlo,
    '®': '\u0440' + '\u2DE3',
    '°': '\uA67E',
    '±': '\uA657' + Zvatelce + Varia,
    'µ': unicSmallU,
    'Ё': unicSmallYat + Varia,
    'Ђ': unicSmallIzhitsa + Oxia,
    'Ѓ': '\u0410' + Zvatelce + Oxia,
    'І': unicCapitalYi,
    'Ї': unicCapitalUkrI + Zvatelce,
    'Ј': unicCapitalUkrI + Zvatelce + Oxia,
    'Љ': unicCapitalLittleYus + Zvatelce,
    'Њ': unicCapitalOmega + Zvatelce,
    'Ћ': '\uA656' + Zvatelce + Oxia,
    'Ќ': unicCapitalUk + Zvatelce + Oxia,
    'Ў': unicCapitalUk + Zvatelce,
    'Џ': unicCapitalRoundOmega + Zvatelce + Oxia,
    'Э': unicCapitalYat,
    'Я': '\uA656',
    'э': unicSmallYat,
    'я': '\uA657',
    'ё': unicSmallYat + Oxia,
    'ђ': unicSmallIzhitsa + '\u2DE2' + Pokrytie,
    'ѓ': '\u0430' + Zvatelce + Oxia,
    'і': unicSmallUkrI + Kendema,
    'ї': unicSmallUkrI + Zvatelce,
    'ј': unicSmallUkrI + Zvatelce + Oxia,
    'љ': unicSmallLittleYus + Zvatelce,
    'њ': unicSmallOmega + Zvatelce,
    'ћ': '\uA657' + Zvatelce + Oxia,
    'ќ': unicSmallUk + Zvatelce + Oxia,
    'ў': unicSmallUk + Zvatelce,
    'џ': unicSmallRoundOmega + Zvatelce + Oxia,
    'Ґ': '\u0410' + Zvatelce,
    'ґ': '\u0430' + Zvatelce,
    '†': '\u0430' + Kamora,
    '‡': unicSmallUkrI + Kamora,
    '•': '\u2DE4',
    '…': '\u046F' + Titlo,
    '‰': unicSmallLittleYus + Kamora,
    '‹': unicSmallUkrI + Titlo,
    '›': unicSmallIzhitsa + Kamora,
    '€': '\u2DE5',
    '№': '\u0430' + Titlo,
    '™': '\u0442' + Titlo,
    'У': unicCapitalMonogrUk,
    'у': unicSmallMonogrUk,
}

font_table_orthodox_tt = {
    '#': Zvatelce,
    '$': Zvatelce + Oxia,
    '%': Zvatelce + Varia,
    '&': Titlo,
    '+': '\u2DE1' + Pokrytie,
    '0': unicSmallO + Oxia,
    '1': Oxia,
    '2': Varia,
    '3': Zvatelce,
    '4': Zvatelce + Oxia,
    '5': Zvatelce + Varia,
    '6': Kamora,
    '7': Titlo,
    '8': '\u033E',
    '9': '\u0436' + Titlo,
    '<': '\u2DEF',
    '=': '\u2DE9' + Pokrytie,
    '>': '\u2DEC' + Pokrytie,
    '?': '\u2DF1' + Pokrytie,
    '@': Varia,
    'A': '\u0430' + Varia,
    'B': unicSmallYat + Kamora,
    'C': '\u2DED' + Pokrytie,
    'D': '\u0434' + '\u2DED' + Pokrytie,
    'E': unicSmallIe + Varia,
    'F': unicCapitalFita,
    'G': '\u0433' + Titlo,
    'H': unicSmallOmega + Oxia,
    'I': unicCapitalUkrI,
    'J': unicSmallUkrI + Varia,
    'K': '\uA656' + Zvatelce,
    'L': '\u043B' + '\u2DE3',
    'M': unicCapitalIzhitsaDblGrave,
    'N': unicCapitalRoundOmega + Zvatelce,
    'O': unicCapitalRoundOmega,
    'P': '\u0470',
    'Q': unicCapitalOmegaTitled,
    'R': '\u0440' + Titlo,
    'S': unicSmallLittleYus + Varia,
    'T': '\u047E',
    'U': unicCapitalUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': '\u046E',
    'Y': unicSmallMonogrUk + Varia,
    'Z': unicCapitalLittleYus,
    '\\': Titlo,
    '^': Kamora,
    '_': '\u033E',
    'a': '\u0430' + Oxia,
    'b': '\u2DEA' + Pokrytie,
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicSmallIe + Oxia,
    'f': unicSmallFita,
    'g': '\u2DE2' + Pokrytie,
    'h': '\u044B' + Oxia,
    'i': unicSmallUkrI,
    'j': unicSmallUkrI + Oxia,
    'k': '\uA657' + Zvatelce,
    'l': '\u043B' + Titlo,
    'm': unicSmallIzhitsaDblGrave,
    'n': unicSmallRoundOmega + Zvatelce,
    'o': unicSmallRoundOmega,
    'p': '\u0471',
    'q': unicSmallOmegaTitled,
    'r': '\u0440' + '\u2DED' + Pokrytie,
    's': unicSmallLittleYus + Oxia,
    't': '\u047F',
    'u': unicSmallUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'x': '\u046F',
    'y': unicSmallMonogrUk + Oxia,
    'z': unicSmallLittleYus,
    '{': unicSmallMonogrUk + Kamora,
    '|': unicSmallLittleYus + Zvatelce + Varia,
    '}': unicSmallI + Titlo,
    '~': Oxia,
    '¤': '\u0482',
    '¦': '\u0445' + Titlo,
    '§': '\u0447' + Titlo,
    '©': '\u0441' + Titlo,
    '®': '\u0440' + '\u2DE3',
    '°': '\uA67E',
    '±': '\uA657' + Zvatelce + Varia,
    'µ': unicSmallU,
    'Ё': unicSmallYat + Varia,
    'Ђ': unicSmallIzhitsa + Oxia,
    'Ѓ': '\u0410' + Zvatelce + Oxia,
    'І': unicCapitalUkrI,
    'Ї': unicCapitalUkrI + Zvatelce,
    'Ј': unicCapitalUkrI + Zvatelce + Oxia,
    'Љ': unicCapitalLittleYus + Zvatelce,
    'Њ': unicCapitalOmega + Zvatelce,
    'Ћ': '\uA656' + Zvatelce + Oxia,
    'Ќ': unicCapitalUk + Zvatelce + Oxia,
    'Ў': unicCapitalUk + Zvatelce,
    'Џ': unicCapitalRoundOmega + Zvatelce + Oxia,
    'Э': unicCapitalYat,
    'Я': '\uA656',
    'э': unicSmallYat,
    'я': '\uA657',
    'ё': unicSmallYat + Oxia,
    'ђ': unicSmallIzhitsa + '\u2DE2' + Pokrytie,
    'ѓ': '\u0430' + Zvatelce + Oxia,
    'і': unicSmallUkrI + Kendema,
    'ї': unicSmallUkrI + Zvatelce,
    'ј': unicSmallUkrI + Zvatelce + Oxia,
    'љ': unicSmallLittleYus + Zvatelce,
    'њ': unicSmallOmega + Zvatelce,
    'ћ': '\uA657' + Zvatelce + Oxia,
    'ќ': unicSmallUk + Zvatelce + Oxia,
    'ў': unicSmallUk + Zvatelce,
    'џ': unicSmallRoundOmega + Zvatelce + Oxia,
    'Ґ': '\u0410' + Zvatelce,
    'ґ': '\u0430' + Zvatelce,
    '†': '\u0430' + Kamora,
    '‡': unicSmallUkrI + Kamora,
    '•': '\u2DE4',
    '…': '\u046F' + Titlo,
    '‰': unicSmallLittleYus + Kamora,
    '‹': unicSmallUkrI + Titlo,
    '›': unicSmallIzhitsa + Kamora,
    '€': '\u2DE5',
    '№': '\u0430' + Titlo,
    '™': '\u0442' + Titlo,
    'У': unicCapitalMonogrUk,
    'у': unicSmallMonogrUk,
}

font_table_orthodox_tt_caps = {
    '#': Zvatelce,
    '$': Zvatelce + Oxia,
    '%': Zvatelce + Varia,
    '&': Titlo,
    '+': '\u2DE1' + Pokrytie,
    '0': unicCapitalO + Oxia,
    '1': Oxia,
    '2': Varia,
    '3': Zvatelce,
    '4': Zvatelce + Oxia,
    '5': Zvatelce + Varia,
    '6': Kamora,
    '7': Titlo,
    '8': '\u033E',
    '9': '\u0416' + Titlo,
    '<': '\u2DEF',
    '=': '\u2DE9' + Pokrytie,
    '>': '\u2DEC' + Pokrytie,
    '?': '\u2DF1' + Pokrytie,
    '@': Varia,
    'A': '\u0410' + Varia,
    'B': unicCapitalYat + Kamora,
    'C': '\u2DED' + Pokrytie,
    'D': '\u0414' + '\u2DED' + Pokrytie,
    'E': unicCapitalIe + Varia,
    'F': unicCapitalFita,
    'G': '\u0413' + Titlo,
    'H': unicCapitalOmega + Oxia,
    'I': unicCapitalUkrI,
    'J': unicCapitalUkrI + Varia,
    'K': '\uA656' + Zvatelce,
    'L': '\u041B' + '\u2DE3',
    'M': unicCapitalIzhitsaDblGrave,
    'N': unicCapitalRoundOmega + Zvatelce,
    'O': unicCapitalRoundOmega,
    'P': '\u0470',
    'Q': unicCapitalOmegaTitled,
    'R': '\u0420' + Titlo,
    'S': unicCapitalLittleYus + Varia,
    'T': '\u047E',
    'U': unicCapitalO + unicCapitalMonogrUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': '\u046E',
    'Y': unicCapitalMonogrUk + Varia,
    'Z': unicCapitalLittleYus,
    '\\': Titlo,
    '^': Kamora,
    '_': '\u033E',
    'a': '\u0410' + Oxia,
    'b': '\u2DEA' + Pokrytie,
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicCapitalIe + Oxia,
    'f': unicCapitalFita,
    'g': '\u2DE2' + Pokrytie,
    'h': '\u042B' + Oxia,
    'i': unicCapitalUkrI,
    'j': unicCapitalUkrI + Oxia,
    'k': '\uA656' + Zvatelce,
    'l': '\u041B' + Titlo,
    'm': unicCapitalIzhitsaDblGrave,
    'n': unicCapitalRoundOmega + Zvatelce,
    'o': unicCapitalRoundOmega,
    'p': '\u0470',
    'q': unicCapitalOmegaTitled,
    'r': '\u0420' + '\u2DED' + Pokrytie,
    's': unicCapitalLittleYus + Oxia,
    't': '\u047E',
    'u': unicCapitalO + unicCapitalMonogrUk,
    'v': unicCapitalIzhitsa,
    'w': unicCapitalOmega,
    'x': '\u046E',
    'y': unicCapitalMonogrUk + Oxia,
    'z': unicCapitalLittleYus,
    '{': unicCapitalMonogrUk + Kamora,
    '|': unicCapitalLittleYus + Zvatelce + Varia,
    '}': unicCapitalI + Titlo,
    '~': Oxia,
    '¤': '\u0482',
    '¦': '\u0425' + Titlo,
    '§': '\u0427' + Titlo,
    '©': '\u0421' + Titlo,
    '®': '\u0420' + '\u2DE3',
    '°': '\uA67E',
    '±': '\uA656' + Zvatelce + Varia,
    'µ': unicCapitalMonogrUk,
    '¶': '\u00B6',
    '·': '\u00B7',
    '»': '\u00BB',
    'Ё': unicCapitalYat + Varia,
    'Ђ': unicCapitalIzhitsa + Oxia,
    'Ѓ': '\u0410' + Zvatelce + Oxia,
    'Є': unicCapitalUkrIe,
    'Ї': unicCapitalUkrI + Zvatelce,
    'Ј': unicCapitalUkrI + Zvatelce + Oxia,
    'Љ': unicCapitalLittleYus + Zvatelce,
    'Њ': unicCapitalOmega + Zvatelce,
    'Ћ': '\uA656' + Zvatelce + Oxia,
    'Ќ': unicCapitalO + unicCapitalMonogrUk + Zvatelce + Oxia,
    'Ў': unicCapitalO + unicCapitalMonogrUk + Zvatelce,
    'Џ': unicCapitalRoundOmega + Zvatelce + Oxia,
    'У': unicCapitalMonogrUk,
    'Я': '\uA656',
    'а': '\u0410',
    'б': '\u0411',
    'в': '\u0412',
    'г': '\u0413',
    'д': '\u0414',
    'е': unicCapitalIe,
    'ж': '\u0416',
    'з': '\u0417',
    'и': unicCapitalI,
    'й': '\u0419',
    'к': '\u041A',
    'л': '\u041B',
    'м': '\u041C',
    'н': '\u041D',
    'о': unicCapitalO,
    'п': '\u041F',
    'р': '\u0420',
    'с': '\u0421',
    'т': '\u0422',
    'у': unicCapitalMonogrUk,
    'ф': unicCapitalEf,
    'х': '\u0425',
    'ц': '\u0426',
    'ч': '\u0427',
    'ш': '\u0428',
    'щ': '\u0429',
    'ъ': '\u042A',
    'ы': '\u042B',
    'ь': '\u042C',
    'э': unicCapitalYat,
    'ю': '\u042E',
    'я': '\uA656',
    'ё': unicCapitalYat + Oxia,
    'ђ': unicCapitalIzhitsa + '\u2DE2' + Pokrytie,
    'ѓ': '\u0410' + Zvatelce + Oxia,
    'є': unicCapitalUkrIe,
    'ѕ': '\u0405',
    'і': unicCapitalUkrI,
    'ї': unicCapitalUkrI + Zvatelce,
    'ј': unicCapitalUkrI + Zvatelce + Oxia,
    'љ': unicCapitalLittleYus + Zvatelce,
    'њ': unicCapitalOmega + Zvatelce,
    'ћ': '\uA656' + Zvatelce + Oxia,
    'ќ': unicCapitalO + unicCapitalMonogrUk + Zvatelce + Oxia,
    'ў': unicCapitalO + unicCapitalMonogrUk + Zvatelce,
    'џ': unicCapitalRoundOmega + Zvatelce + Oxia,
    'Ґ': '\u0410' + Zvatelce,
    'ґ': '\u0410' + Zvatelce,
    '†': '\u0410' + Kamora,
    '‡': unicCapitalUkrI + Kamora,
    '•': '\u2DE4',
    '…': '\u046E' + Titlo,
    '‰': unicCapitalLittleYus + Kamora,
    '‹': unicCapitalUkrI + Titlo,
    '›': unicCapitalIzhitsa + Kamora,
    '€': '\u2DE5',
    '№': '\u0410' + Titlo,
    "™": '\u0422' + Titlo,
}

font_table_orthodox_e_roos = {
    '#': '\uD83D' + '\uDD44',
    '$': '\uD83D' + '\uDD42',
    '%': '\uD83D' + '\uDD41',
    '0': unicDigitZero,
    '1': unicDigitOne,
    '2': unicDigitTwo,
    '3': unicDigitThree,
    '4': unicDigitFour,
    '5': unicDigitFive,
    '6': unicDigitSix,
    '7': unicDigitSeven,
    '8': unicDigitEight,
    '9': unicDigitNine,
    '@': '\uD83D' + '\uDD43',
    'A': '\u0410' + Oxia,
    'E': unicCapitalIe + Oxia,
    'I': unicCapitalUkrI,
    'M': '\uD83D' + '\uDD45',
    'O': unicCapitalRoundOmega,
    'U': unicCapitalMonogrUk + Oxia,
    'V': unicCapitalIzhitsa + Oxia,
    'W': unicCapitalO + Oxia,
    'Y': '\u042B' + Oxia,
    '^': '\uD83D' + '\uDD40',
    'a': '\u0430' + Oxia,
    'e': unicSmallIe + Oxia,
    'i': unicSmallUkrI,
    'o': unicSmallRoundOmega,
    'u': unicSmallU + Oxia,
    'v': unicSmallIzhitsa + Oxia,
    'w': unicSmallO + Oxia,
    'y': '\u044B' + Oxia,
    'Ђ': unicCapitalYat + Oxia,
    'Є': '\uE1A5',
    'Ј': unicCapitalUkrI + Oxia,
    'Њ': Oxia,
    'Ћ': unicCapitalYat,
    'Ќ': unicCapitalFita,
    'Џ': unicCapitalIzhitsa,
    'ђ': unicSmallYat + Oxia,
    'і': unicSmallUkrIWithDot,
    'ј': unicSmallUkrI + Oxia,
    'њ': Oxia,
    'ћ': unicSmallYat,
    'ќ': unicSmallFita,
    'џ': unicSmallIzhitsa,
    '†': CrossOrthodox,
    '‡': Dagger,
    'У': unicCapitalMonogrUk,
    "Ў": unicCapitalMonogrUk + '\u0306',
}

font_table_orthodox_digits_loose = {
    '!': '\uD83D' + '\uDD43',
    '#': '\uD83D' + '\uDD42',
    '$': '\uD83D' + '\uDD41',
    '%': '\uD83D' + '\uDD40',
    '+': Dagger,
    ',': '\u002C',
    '.': '\u002E',
    '0': '\u0482',
    '1': '\u0430' + '\u20DD',
    '2': '\u0430' + '\u0488',
    '3': '\u0430' + '\u0489',
    '4': '\u0430' + '\uA670',
    '5': '\u0430' + '\uA671',
    '6': '\u044B' + '\uA672',
    ';': '\u002E',
    '=': CrossOrthodox,
    '?': '\u003B',
    '@': '\uD83D' + '\uDD43',
    'E': unicSmallUkrIe + Titlo,
    'F': unicSmallFita + Titlo,
    'J': unicSmallUkrI + Titlo,
    'K': '\u046F' + Titlo,
    'M': '\uD83D' + '\uDD45',
    'O': unicSmallRoundOmega + Titlo,
    'P': '\u0471' + Titlo,
    'S': '\u0455' + Titlo,
    'T': '\u047F',
    'W': unicSmallOmega + Titlo,
    'e': unicSmallUkrIe,
    'f': unicSmallFita,
    'j': unicSmallUkrI,
    'k': '\u046F',
    'o': unicSmallRoundOmega,
    'p': '\u0471',
    's': '\u0455',
    't': '\u047F',
    'w': unicSmallOmega,
    ';': '\u002E',
    'А': '\u0430' + Titlo,
    'Б': '\u0431' + Titlo,
    'В': '\u0432' + Titlo,
    'Г': '\u0433' + Titlo,
    'Д': '\u0434' + Titlo,
    'Е': unicSmallIe + Titlo,
    'Ж': '\u0436' + Titlo,
    'З': '\u0437' + Titlo,
    'И': unicSmallI + Titlo,
    'К': '\u043A' + Titlo,
    'Л': '\u043B' + Titlo,
    'М': '\u043C' + Titlo,
    'Н': '\u043D' + Titlo,
    'О': unicSmallO + Titlo,
    'П': '\u043F' + Titlo,
    'Р': '\u0440' + Titlo,
    'С': '\u0441' + Titlo,
    'Т': '\u0442' + Titlo,
    'У': unicSmallU + Titlo,
    'Ф': unicSmallEf + Titlo,
    'Х': '\u0445' + Titlo,
    'Ц': '\u0446' + Titlo,
    'Ч': '\u0447' + Titlo,
    'Ш': '\u0448' + Titlo,
    'Щ': '\u0449' + Titlo,
    'ё': unicSmallYat,
    '∙': '\u00B7',
}

font_table_orthodox_loose = {
    '!': Oxia,
    '"': Varia,
    '#': Zvatelce,
    '$': Zvatelce + Oxia,
    '%': Zvatelce + Oxia,
    '&': Kamora,
    "'": '\uA67E',
    '*': unicSmallUkrI + Zvatelce,
    '+': Titlo,
    '-': '\u005F',
    '0': '\u030F',
    '1': Oxia,
    '2': Varia,
    '3': Zvatelce,
    '4': Zvatelce + Oxia,
    '5': Zvatelce + Varia,
    '6': Kamora,
    '8': unicSmallMonogrUk + Oxia,
    '9': unicSmallMonogrUk + Varia,
    '<': unicCapitalYa,
    '=': Titlo,
    '>': unicSmallYA,
    '?': '\u0021',
    '@': Varia,
    'F': unicCapitalFita,
    'G': '\u2DE4',
    'H': '\u2DEF',
    'I': unicCapitalUkrI,
    'J': unicSmallUkrI + Kamora,
    'K': '\u046E',
    'L': unicSmallYat + Varia,
    'O': unicSmallOmegaTitled,
    'P': '\u0470',
    'Q': unicCapitalO,
    'R': '\u2DEC' + Pokrytie,
    'S': '\u0405',
    'T': '\u047E',
    'U': '\uE3BE',
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'Y': unicSmallU,
    'Z': '\u0302',
    '\\': unicSmallUkrI + Zvatelce + Oxia,
    '^': Zvatelce + Varia,
    '`': '\u2E2F',
    'b': '\u0304',
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicSmallUkrIe,
    'f': unicSmallFita,
    'g': '\u2DE2' + Pokrytie,
    'h': '\u2DF1' + Pokrytie,
    'i': '\u0457',
    'j': unicSmallUkrI,
    'k': '\u046F',
    'l': unicSmallYat + Kamora,
    'o': unicCapitalRoundOmega,
    'p': '\u0471',
    'q': '\u2DEA' + Pokrytie,
    'r': '\u0440' + Titlo,
    's': '\u0455',
    't': '\u047F',
    'u': unicCapitalUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'y': unicSmallMonogrUk + Kamora,
    '{': '\u2DE1' + Pokrytie,
    '|': unicCapitalUkrI + Zvatelce + Oxia,
    '}': '\u2DE5',
    '~': '\u2E2F',
    '«': unicSmallUkrI + Oxia,
    'Ё': unicCapitalYat,
    'Ђ': '\u0433' + Titlo,
    'Ѓ': '\u043B' + Titlo,
    'Љ': unicCapitalUk + Zvatelce + Oxia,
    'Њ': unicCapitalUk + Zvatelce + Varia,
    'Ћ': unicSmallRoundOmega + Zvatelce,
    'Ќ': unicSmallUk + Zvatelce + Varia,
    'Џ': unicSmallRoundOmega + Zvatelce + Oxia,
    'О': unicCapitalRoundOmega,
    'У': unicSmallUk,
    'Э': '\uA656',
    'Я': unicCapitalYa,  # unicCapitalLittleYus,
    'у': unicSmallMonogrUk,
    'э': '\uA657',
    'я': unicSmallLittleYus,
    'ё': unicSmallYat,
    'ђ': '\u0430' + Zvatelce + Oxia,
    'ѓ': '\u0445' + Titlo,
    'љ': '\u0436' + Titlo,
    'њ': unicSmallI + Titlo,
    '‘': unicCapitalRoundOmega + Zvatelce,
    '’': unicCapitalRoundOmega + Zvatelce + Oxia,
    '‚': '\u0442' + Titlo,
    '„': '\u0447' + Titlo,
    '†': unicSmallIzhitsa + Zvatelce,
    '‡': unicSmallIzhitsa + Zvatelce + Oxia,
    '…': unicSmallIzhitsa + Oxia,
    '‰': unicSmallUk + Zvatelce,
    '‹': unicSmallUk + Zvatelce + Oxia,
    '€': unicCapitalUk + Zvatelce,
    '№': Zvatelce,
    '™': unicSmallUkrI + Oxia,
}

font_table_ustav = {
    '"': Oxia,
    '#': Zvatelce + Oxia,
    '$': '\u003B',
    '%': Zvatelce,
    '&': Zvatelce + Varia,
    "'": Oxia,
    '*': Zvatelce + Varia,
    '+': '\u033E',
    '/': Titlo,
    '0': unicDigitZero,
    '1': unicDigitOne,
    '2': unicDigitTwo,
    '3': unicDigitThree,
    '4': unicDigitFour,
    '5': unicDigitFive,
    '6': unicDigitSix,
    '7': unicDigitSeven,
    '8': unicDigitEight,
    '9': unicDigitNine,
    ':': '\u003A',
    ';': '\u003B',
    '<': '\u00AB',
    '=': '\u033E',
    '>': '\u00BB',
    '@': Zvatelce + Oxia,
    'A': '\uA656',
    'B': unicCapitalUkrI,
    'C': '\u2DED' + Pokrytie,
    'D': '\u2DE3',
    'E': unicCapitalYat,
    'F': unicCapitalFita,
    'G': '\u2DE2' + Pokrytie,
    'H': unicCapitalIzhitsaDblGrave,
    'I': unicCapitalYi,
    'J': unicCapitalRoundOmega,
    'K': '\u046E',
    'L': '\uA67E',
    'M': Oxia,
    'N': '\u047E',
    'O': '\u2DEA' + Pokrytie,
    'P': '\u0470',
    'Q': unicCapitalOmegaTitled,
    'R': Pokrytie,
    'S': '\u0405',
    'T': '\u0465',
    'U': unicSmallMonogrUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': '\u2DF1' + Pokrytie,
    'Y': unicCapitalUk,
    'Z': unicCapitalYa,
    '\\': Titlo,
    '^': Zvatelce,
    '`': Varia,
    'a': '\uA657',
    'b': unicSmallUkrI,
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicSmallYat,
    'f': unicSmallFita,
    'g': '\u2DE2' + Pokrytie,
    'h': unicSmallIzhitsaDblGrave,
    'i': unicSmallUkrI + Kendema,
    'j': unicSmallRoundOmega,
    'k': '\u046F',
    'l': '\u1C82',
    'm': Oxia,
    'n': '\u047F',
    'o': '\u2DEA' + Pokrytie,
    'p': '\u0471',
    'q': unicSmallOmegaTitled,
    'r': Pokrytie,
    's': '\u0455',
    't': unicSmallUkrIe,
    'u': unicSmallMonogrUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'x': Varia,
    'y': unicSmallUk,
    'z': unicSmallYA,
    '{': Kamora,
    '|': Titlo,
    '}': Kamora,
    '~': Varia,
    '': unicCapitalIotifLittleYus,
    '': unicCapitalYa,
    '': '\u046B',
    '': '\u2DF1' + Pokrytie,
    '': unicCapitalFita,
    '': unicSmallIotifLittleYus,
    '': '\u040B',
    '': '\u1C82',
    '¡': unicCapitalUk,
    '¢': unicSmallUk,
    '£': unicCapitalIzhitsaDblGrave,
    '¥': '\u047E',
    '¨': Varia,
    'ª': '\uA67E',
    '¯': unicCapitalYi,
    '²': unicCapitalUkrI,
    '³': unicSmallUkrI,
    '´': '\u047F',
    'µ': unicSmallMonogrUk + Varia,
    '¸': '\uA657',
    '¹': '\u0482',
    'º': unicSmallUkrIe,
    '¼': unicSmallIzhitsaDblGrave,
    '½': '\u0405',
    '¾': '\u0455',
    '¿': '\u0457',
    'À': '\u0410',
    'Á': '\u0411',
    'Â': '\u0412',
    'Ã': '\u0413',
    'Ä': '\u0414',
    'Å': unicCapitalIe,
    'Æ': '\u0416',
    'Ç': '\u0417',
    'È': unicCapitalI,
    'É': '\u0419',
    'Ê': '\u041A',
    'Ë': '\u041B',
    'Ì': '\u041C',
    'Í': '\u041D',
    'Î': unicCapitalO,
    'Ï': '\u041F',
    'Ð': '\u0420',
    'Ñ': '\u0421',
    'Ò': '\u0422',
    'Ó': unicCapitalMonogrUk,
    'Ô': unicCapitalEf,
    'Õ': '\u0425',
    'Ö': '\u0426',
    '×': '\u0427',
    'Ø': '\u0428',
    'Ù': '\u0429',
    'Ú': '\u042A',
    'Û': '\u042B',
    'Ü': '\u042C',
    'Ý': '\u042D',
    'Þ': '\u042E',
    'ß': unicCapitalLittleYus,
    'à': '\u0430',
    'á': '\u0431',
    'â': '\u0432',
    'ã': '\u0433',
    'ä': '\u0434',
    'å': unicSmallIe,
    'æ': '\u0436',
    'ç': '\u0437',
    'è': unicSmallI,
    'é': '\u0439',
    'ê': '\u043A',
    'ë': '\u043B',
    'ì': '\u043C',
    'í': '\u043D',
    'î': unicSmallO,
    'ï': '\u043F',
    'ð': '\u0440',
    'ñ': '\u0441',
    'ò': '\u0442',
    'ó': unicSmallU,
    'ô': unicSmallEf,
    'õ': '\u0445',
    'ö': '\u0446',
    '÷': '\u0447',
    'ø': '\u0448',
    'ù': '\u0449',
    'ú': '\u044A',
    'û': '\u044B',
    'ü': '\u044C',
    'ý': '\u044D',
    'þ': '\u044E',
    'ÿ': unicSmallLittleYus,
    'Œ': unicSmallU,
    'œ': '\u045B',
    'Š': '\u0470',
    'š': '\u046D',
    'Ÿ': unicCapitalUkrI,
    'ƒ': unicCapitalYa,
    '˜': '\u2053',
    'Ё': Varia,
    'Ђ': unicCapitalIotifLittleYus,
    'Ѓ': unicCapitalYa,
    'Є': '\uA67E',
    'Ѕ': '\u0405',
    'Ј': unicCapitalIzhitsaDblGrave,
    'Ћ': '\u2DF1' + Pokrytie,
    'Ќ': '\u046B',
    'Ў': unicCapitalUk,
    'Џ': unicCapitalFita,
    'Я': unicCapitalLittleYus,
    'я': unicSmallLittleYus,
    'ё': '\uA657',
    'ђ': unicSmallIotifLittleYus,
    'ј': unicSmallIzhitsaDblGrave,
    'ћ': '\u1C82',
    'ќ': '\u040B',
    'ў': unicSmallUk,
    'Ґ': '\u047E',
    'ґ': '\u047F',
    '‘': Oxia,
    '’': Oxia,
    '‚': '\u002C',
    '“': Oxia,
    '”': Oxia,
    '‡': CrossOrthodox,
    '№': '\u0482',
    '™': '\u002A',
    'У': unicCapitalMonogrUk,
}

font_table_valaam = {
    '"': '\u030F',
    '#': '\u0482',
    '$': '\u003B',
    '%': Zvatelce,
    '&': Zvatelce,
    "'": Oxia,
    '*': '\u002A',
    '+': '\u033E',
    '/': Oxia,
    '0': unicDigitZero,
    '1': unicDigitOne,
    '2': unicDigitTwo,
    '3': unicDigitThree,
    '4': unicDigitFour,
    '5': unicDigitFive,
    '6': unicDigitSix,
    '7': unicDigitSeven,
    '8': unicDigitEight,
    '9': unicDigitNine,
    '<': '\u00AB',
    '=': '\uA67E',
    '>': '\u00BB',
    '@': Zvatelce + Oxia,
    'A': unicCapitalIotifLittleYus,
    'B': unicCapitalUkrI,
    'C': '\u2DED' + Pokrytie,
    'D': '\u2DE3',
    'E': unicCapitalYat,
    'F': unicCapitalFita,
    'G': '\u2DE2' + Pokrytie,
    'H': '\u040B',
    'I': unicCapitalUkrI,
    'J': unicCapitalRoundOmega + Zvatelce,
    'K': '\u046E',
    'L': Zvatelce + Varia,
    'M': Zvatelce + Varia,
    'N': '\u2DEA' + Pokrytie,
    'O': '\u047E',
    'P': '\u0470',
    'Q': unicCapitalBroadOmega,
    'R': Pokrytie,
    'S': '\u0405',
    'T': '\u0465',
    'U': unicSmallMonogrUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': Zvatelce + Oxia,
    'Y': unicCapitalUk,
    'Z': '\uA656',
    '\\': Varia,
    '^': Pokrytie,
    '_': '\u2014',
    '`': Varia,
    'a': unicSmallIotifLittleYus,
    'b': '\u046D',
    'c': '\u2DED' + Pokrytie,
    'd': '\u2DE3',
    'e': unicSmallYat,
    'f': unicSmallFita,
    'g': '\u2DE2' + Pokrytie,
    'h': '\u045B',
    'i': '\u0457',
    'j': unicSmallRoundOmega + Zvatelce,
    'k': '\u046F',
    'l': Zvatelce + Varia,
    'm': Zvatelce + Varia,
    'n': '\u2DEA' + Pokrytie,
    'o': '\u047F',
    'p': '\u0471',
    'q': unicSmallUkrI,
    'r': '\u046B',
    's': '\u0455',
    't': unicSmallIe,
    'u': unicSmallMonogrUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'x': Zvatelce + Oxia,
    'y': unicSmallUk,
    'z': '\uA657',
    '|': Kamora,
    '~': Titlo,
    '': '\u2DF1' + Pokrytie,
    '¨': Titlo,
    '´': unicCapitalMonogrUk,
    'µ': '\u2DE8',
    '¸': '\u033E',
    '¹': '\u2116',
    'À': '\u0410',
    'Á': '\u0411',
    'Â': '\u0412',
    'Ã': '\u0413',
    'Ä': '\u0414',
    'Å': unicCapitalIe,
    'Æ': '\u0416',
    'Ç': '\u0417',
    'È': unicCapitalI,
    'É': '\u0419',
    'Ê': '\u041A',
    'Ë': '\u041B',
    'Ì': '\u041C',
    'Í': '\u041D',
    'Î': unicCapitalO,
    'Ï': '\u041F',
    'Ð': '\u0420',
    'Ñ': '\u0421',
    'Ò': '\u0422',
    'Ó': unicCapitalMonogrUk,
    'Ô': unicCapitalEf,
    'Õ': '\u0425',
    'Ö': '\u0426',
    '×': '\u0427',
    'Ø': '\u0428',
    'Ù': '\u0429',
    'Ú': '\u042A',
    'Û': '\u042B',
    'Ü': '\u042C',
    'Ý': '\u042D',
    'Þ': '\u042E',
    'ß': unicCapitalLittleYus,
    'à': '\u0430',
    'á': '\u0431',
    'â': '\u0432',
    'ã': '\u0433',
    'ä': '\u0434',
    'å': unicSmallIe,
    'æ': '\u0436',
    'ç': '\u0437',
    'è': unicSmallI,
    'é': '\u0439',
    'ê': '\u043A',
    'ë': '\u043B',
    'ì': '\u043C',
    'í': '\u043D',
    'î': unicSmallO,
    'ï': '\u043F',
    'ð': '\u0440',
    'ñ': '\u0441',
    'ò': '\u0442',
    'ó': unicSmallU,
    'ô': unicSmallEf,
    'õ': '\u0445',
    'ö': '\u0446',
    '÷': '\u0447',
    'ø': '\u0448',
    'ù': '\u0449',
    'ú': '\u044A',
    'û': '\u044B',
    'ü': '\u044C',
    'ý': '\u044D',
    'þ': '\u044E',
    'ÿ': unicSmallLittleYus,
    'Œ': unicSmallUkrIWithDot,
    'Š': '\u2DE9' + Pokrytie,
    'ƒ': '\u0027',
    'ˆ': '\u0485',
    'μ': '\u2DE8',
    'Ё': Titlo,
    'Ѓ': '\u2DF0' + Pokrytie,
    'Ќ': '\u2DED' + Pokrytie,
    'У': unicCapitalMonogrUk,
    'Я': unicCapitalLittleYus,
    'я': unicSmallLittleYus,
    'ё': '\u033E',
    '‐': '\u002D',
    '–': '\u0027',
    '‘': Oxia,
    '’': Oxia,
    '“': '\u030F',
    '”': '\u030F',
    '„': '\u2DE6' + Pokrytie,
    '†': CrossOrthodox,
    '‡': CrossOrthodox,
    '…': '\u2DE7' + Pokrytie,
    '‰': Kendema,
    '‹': '\u2DE4',
    '™': '\u2DEF',
}

font_table_hirmos_ponomar = {
    '0': unicDigitZero,
    '1': unicDigitOne,
    '2': unicDigitTwo,
    '3': unicDigitThree,
    '4': unicDigitFour,
    '5': unicDigitFive,
    '6': unicDigitSix,
    '7': unicDigitSeven,
    '8': unicDigitEight,
    '9': unicDigitNine,
    'Ў': '\uE3BF',
    'У': unicCapitalMonogrUk,
    '': '\uEF00',
    '': '\uEF01',
    '': '\uEF02',
    '': '\uEF03',
    '': '\uEF04',
    '': '\uEF05',
    '': '\uEF06',
    '': '\uEF07',
    '': '\uEF08',
    '': '\uEF09',
    '': '\uEF0A',
    '': '\uEF0B',
    '': '\uEF10',
    '': '\uEF11',
    '': '\uEF12',
    '': '\uEF13',
    '': '\uEF14',
    '': '\uEF15',
    '': '\uEF16',
    '': '\uEF17',
    '': '\uE5D0',
    '': '\uE5D1',
    '': '\uE5D2',
    '': '\uE5D3',
    '': ZvatelceUp,
    '': Iso,
    '': IsoUp,
    '': Apostrof,
    '': ApostrofUp,
    '': ApostrofGreat,
    '': '\uE016',
    '': '\uDB80' + '\uDC23',
    '': '\uDB80' + '\uDC30',
    '': '\uE0E2',
    '': '\uE0E4',
    '': '\uE0EC',
    '': '\uE0ED',
    '': '\uE612',
    '': '\uE714',
    '': '\uE800',
    '': '\uE92D',
    '': '\uE92E',
    '': '\uE8E5',
    '': '\uE901',
    '': '\uE903',
    '': '\uE904',
    '': '\uE928',
    '': unicSmallUkrIWithDot,
}

font_table_irmologion = {
    '#': '\u0482',
    '$': '\uD83D' + '\uDD40',
    '%': NotationDoubleSlash,
    '&': '\uD83D' + '\uDD41',
    "'": Oxia,
    '0': unicDigitZero,
    '1': unicDigitOne,
    '2': unicDigitTwo,
    '3': unicDigitThree,
    '4': unicDigitFour,
    '5': unicDigitFive,
    '6': unicDigitSix,
    '7': unicDigitSeven,
    '8': unicDigitEight,
    '9': unicDigitNine,
    '<': '\uD83D' + '\uDD43',
    '>': '\uD83D' + '\uDD44',
    '@': '\uA67E',
    'E': '\uE0E4',
    'F': unicCapitalFita,
    'I': unicCapitalUkrI,
    'J': '\u046A',
    'K': unicCapitalIotifLittleYus,
    'L': '\u046C',
    'O': unicCapitalRoundOmega,
    'P': '\u0470',
    'Q': unicCapitalOmegaTitled,
    'S': '\u0405',
    'T': unicCapitalOt,
    'U': unicCapitalUk,
    'V': unicCapitalIzhitsa,
    'W': unicCapitalOmega,
    'X': '\u046E',
    'Y': unicCapitalIzhitsaDblGrave,
    'Z': unicCapitalIotifA,
    'c': '\u1C83',
    'e': unicSmallUkrIe,
    'f': unicSmallFita,
    'g': unicSmallU,
    'i': unicSmallYi,
    'j': '\u046B',
    'k': unicSmallIotifLittleYus,
    'l': '\u046D',
    'm': '\uA641',
    'n': '\u0465',
    'o': unicSmallRoundOmega,
    'p': '\u0471',
    'q': unicSmallOmegaTitled,
    'r': unicSmallUkrI,
    's': '\u0455',
    't': unicSmallOt,
    'u': unicSmallUk,
    'v': unicSmallIzhitsa,
    'w': unicSmallOmega,
    'x': '\u046F',
    'y': unicSmallIzhitsaDblGrave,
    'z': unicSmallIotifA,
    '~': '\u0027',
    '°': '\u00AB',
    '±': '\u00AC',
    'Ē': '\u00B7',
    'У': unicCapitalMonogrUk,
    'Э': unicCapitalYat,
    'Я': unicCapitalLittleYus,
    'у': unicSmallMonogrUk,
    'э': unicSmallYat,
    'я': unicSmallLittleYus,
    '‡': Dagger,
}
# ========================================

dbl_grave = '\u030F'  # in ѷ
# TODO: уточнить как обрабатывать dbl_grave
acutes = Oxia + Varia + Kamora + dbl_grave
erok_comb = '\u033E'  # д̾
erok = '\u2E2F'  # дⸯ
titlo = '\u0483'  # а҃
pokrytie = '\u0487'
titlo_v = '\u2DE1' + pokrytie
titlo_g = '\u2DE2' + pokrytie
titlo_d = '\u2DE3'
titlo_o = '\u2DEA' + pokrytie
titlo_r = '\u2DEC' + pokrytie
titlo_s = '\u2DED' + pokrytie
titles = titlo + titlo_v + titlo_g + \
         titlo_d + titlo_o + titlo_r + titlo_s
overlines_for_consonants = \
    titles + erok_comb  # + erok
overlines_for_vowels = acutes + Zvatelce + Kendema

cu_before_er = "[БВГДЖЗКЛМНПРСТФѲХЦЧШЩбвгджзклмнпрстфѳхцчшщ]"
cu_cap_letters = \
    "АБВГДЕЄѢЖЗЅꙀИІЇѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦЧШЩЪЫЬЮѦꙖЯѮѰ"
cu_small_letters = \
    "абвгдеєѣжзѕꙁиіїѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ" + unicNarrowO + unicNarrowD + erok
cu_cap_letters_text = \
    "АБВГДЕЄѢЖЗЅꙀИІѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦЧШЩЪЫЬЮѦꙖЯѮѰ"
cu_small_letters_text = \
    "абвгдеєѣжзѕꙁиіѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ" + unicNarrowO + unicNarrowD + erok
cu_letters = cu_cap_letters + cu_small_letters
cu_letters_text = cu_cap_letters_text + cu_small_letters_text
cu_superscripts = overlines_for_vowels + overlines_for_consonants
cu_letters_with_superscripts = cu_letters + cu_superscripts
cu_non_letters = '[^' + cu_letters + ']'


# Наборы регулярных выражений вида:
# [find, replace [, flags] ]
# компилируются перед запуском основной функции

# Буквы в словах: ѿ, ѡ, ѵ, ѣ, etc
regs_letters_in_word = (
    [  # ѿ
        r'''
        \bот
        (?!
            е?[цч]|
            да[нт]|
            враща|
            врещи|
            в[еѣ][тщ]|
            жен|
            зд[еѣ]|
            иш|
            крове|
            расль|
            реб|
            ро[кч]
        )
        ''',
        r'ѿ'
    ],  # или наоборот, перечислить ѿ ?

    [  # Ѿ
        r'''
        \bОт
        (?!
            е?[цч]|
            да[нт]|
            враща|
            врещи|
            в[еѣ][тщ]|
            жен|
            зд[еѣ]|
            иш|
            крове|
            расль|
            реб|
            ро[кч]
        )
        ''',
        r'Ѿ'
    ],  # или наоборот, перечислить ѿ ?

    [r'\bОу(?=[' + cu_cap_letters + r']+)', r'ОꙊ'],  # УМ -> ОꙊ҆МЪ
    [r'\bО\b', r'Ѽ'],  # как правило - обращение
    [r'\bо\b', r'ѡ'],
    [r'\bо', r'ѻ'],
    [r'\bО(?!у)', r'Ѻ'],

    [  # ᲂꙋ -> ᲂу (для исправления ошибок набора)
        # проблема: узкое о
        # на границе слова '\bᲂ' не работает
        # условно \b = не буквы (ноль или больше)
        # все не-буквы попадают в pref и post
        # и вырезаются (с сохранением) в начале,
        # поэтому можно (конкретно для этого случая) использовать
        # ^ - начало строки
        # Вариант:  cu_non_letter + '*' + unicNarrowO + '?ꙋ'
        r'^' + unicNarrowO + 'ꙋ',
        'ᲂу'
    ],
    [  # -ии- -> -їи-
        # TODO: -їѧ & -їа
        r'и(?=[аеєийоѡꙋюѧ])', r'ї'
    ],

    [r'И(?=[АЕЄИЙОѠꙊЮѦаеєийоѡꙋюѧ])', r'І'],
    [r'ᲂ+', r'ᲂ'],

    # Zvatelce for first letter of word
    [r'^([АЄИІѴѺѠЮꙖаєиіѻѡюѧ])', r'\1' + Zvatelce],


    # =========================
    [r'([Аа])кафист', r'\1каѳїст'],
    #
    [r'\bбед(?=[аеносꙋъы])', r'бѣд'],

    # -бѣг- -бѣж-
    [r'''  
        (
            \b(?:
                из|при|ѿ|на
            )?
            |^ᲂу
        )
        бе
        (?=[гж][аеилноꙋъ])
        ''',
     r'\1бѣ'
     ],
    [r'(\b|^ᲂу)бел', r'\1бѣл'],
    [r'\bбес(?=[аиноѡꙋы])', r'бѣс'],
    [r'\bбе\b', r'бѣ'],
    [r'\bбесте\b', r'бѣсте'],
    [r'\bбех(?=(ом)?ъ\b)', r'бѣх'],
    [r'\bбеша\b', r'бѣша'],
    [r'\bбде(?=[нт])', r'бдѣ'],
    [r'([Бб])лагоговейн', r'\1лагоговѣ́йн'],
    [r'([Бб])оговеден', r'\1оговѣдѣн'],
    [r'\b([Бб])озе\b', r'\1озѣ'],
    [r'болезн', r'болѣзн'],

    # ========================
    #   вѣд вѣж вѣм вѣт вѣс вѣщ
    #   -вѣд-
    [r'''
        \b(не|из|([Зз]а|ис)?по)?
        вед
        (?=[аеоꙋиь])
        ''',
     r'\1вѣд'
     ],
    #   -вѣж-
    [r'\b(не)?веж', r'\1вѣж'],

    #   -вѣм-
    [r'''
        \b((ис)?по)?
        вем
        (?=[ыъ])
        ''',
     r'\1вѣм'
     ],

    #   -вѣс-
    [r'\b([Нн]е|со)?вес(?=и\b|т)', r'\1вѣс'],

    #   -вѣт-
    [r''' 
        \b([Зз]а|из|ѻт|ꙋ|на|со)
        вет
        (?=[ълнаеиоѡꙋы])
        ''',
     r'\1вѣт'
     ],
    [r'веті(?=[иѧ])', r'вѣті'],

    #   -вѣщ-
    [r'''
        вещ
        (?!
            # ! вещи, вещество
            (и|ей|ами|еств)\b
        )
        ''',
     r'вѣщ'
     ],
    # ---- вѣд вѣж вѣм вѣт вѣс вѣщ ----

    # ========================
    # вѣк- вѣц- вѣч-
    [r'\bвек(?=[аеиꙋъ](ми)?\b)', r'вѣк'],
    [r'\bвековъ', r'вѣкѡвъ'],
    [r'веце(хъ)?', r'вѣцѣ\1'],
    [r'веч(?=е?н)', r'вѣч'],
    # ------------------------

    [r'вен(?=е?[чц])', r'вѣн'],
    [r'вер(?=[аеиноꙋѧ])', r'вѣр'],
    [r'ветв', r'вѣтв'],
    [r'вет(е?р)', r'вѣт\1'],

    [r'\b(нена)?видені', r'\1видѣнї'],
    [r'\bвин(?=[аеоу]\b|оград)', r'вїн'],
    [r'вменѧ', r'вмѣнѧ'],
    [r'возде(?=(ва)?ти|еши|ющ)', r'воздѣ'],
    [r'восп[еѣ]ва', r'воспѣва'],
    [r'врач[ьъ]', r'врачь'],
    [r'\bвсе(?=м[иъ]|хъ)', r'всѣ'],
    [r'втайне', r'втайнѣ'],

    [r'([Гг])ефсиман', r'\1еѳсїман'],
    [r'(([Гг])еѳсімані)ѧ', r'\g<1>а'],
    [r'(([Гг])еѳсіманійст)ей', r'\g<1>ѣй'],

    [r'гнев', r'гнѣв'],
    [r'горет', r'горѣт'],

    [r'([Гг])ресех', r'\1рѣсѣх'],
    [r'([Гг])ре(?=[схш])', r'\1рѣ'],

    [r'''
        \b
        ([Пп]рисно)?
        ([Дд])ев
        (?=[аеоꙋы]|ств|ическ)
        ''',
     r'\1\2ѣв'
     ],
    [r'\bдет(?!=инец)', r'дѣт'],
    [r'издетска', r'издѣтска'],
    [r'дел(?=[оаꙋ])', r'дѣл'],
    [r'деѧти', r'дѣѧти'],
    [r'\bдне\b', r'днѣ'],
    [r'добродетел', r'добродѣтел'],
    [r'([Дд])околе', r'\1околѣ'],
    [r'\b([Дд])ꙋсе\b', r'\1ꙋсѣ'],

    [r'([Єє])в(?=ангел)', r'\1ѵ'],
    [r'([Єє])в(?=фрафовъ)', r'\1ѵ'],
    [r'([Єє])го\b', r'\1гѡ'],  # Род: єгѡ Вин.: єго
    [r'([Єє])лисе(?=\w)', r'\1лиссе'],  # var: єлїссей

    [r'желез', r'желѣз'],

    [r'([Зз])авес', r'\1авѣс'],
    [r'Звезд', r'Ѕвѣзд'],
    [r'звезд', r'ѕвѣзд'],
    [r'звер', r'ѕвѣр'],
    [r'\bзд(?=е(сь)?\b)', r'зд'],
    [r'зело', r'ѕѣлѡ'],

    [r'зельне', r'ѕѣльнѣ'],
    [r'зельн', r'ѕѣльн'],

    [r'зениц', r'зѣниц'],
    [r'\bзл(?=[аеѣіоꙋы])', r'ѕл'],
    [r'зме(?=[йюѧ]\b|[еи]\w+)', r'ѕмѣ'],
    [r'(при)?зре(?=ти|ні|\b)', r'\1зрѣ'],

    [r'идеже', r'идѣже'],
    [r'И(?=зраил)', r'І'],
    [r'и(?=зраил)', r'і'],
    [r'изрѧдно', r'изрѧднѡ'],
    [r'икосъ', r'ікосъ'],
    [r'Икосъ', r'Ікосъ', 'i'],
    [r'([Іі])о(?=ан|аким|в|на|сиф|ил|ота)', r'\1ѡ'],
    [r'([Іі])ордан', r'\1ѻрдан'],
    [r'Ирмос', r'Ірмос'],
    [r'ирмос', r'ірмос'],
    [r'иссоп', r'ѵссѡп'],
    [r'исцелен', r'исцѣлен'],

    [r'\bкако\b', r'какѡ'],
    [r'колен', r'колѣн'],
    [r'крепк', r'крѣпк'],
    [r'крѣпко', r'крѣпкѡ'],
    [r'крепост', r'крѣпост'],
    [r'кꙋпел', r'кꙋпѣл'],

    [r'\bлес(?=[аъ])', r'лѣс'],
    [r'\bлестви(?=[чц])', r'лѣстви'],
    [r'\bлето', r'лѣто'],
    [r'\b(не|ѻб|раз)?лен(?=ь|ив|ост|ѧщ|ен)', r'\1лѣн'],

    [r'\b(из|от)?мер(?=[аеыу]\b|ил)', r'\1мѣр'],
    [r'мест(?=[аеѣоꙋ]\b)', r'мѣст'],
    [r'\b([Мм])е(?=сѧц)', r'\1ѣ'],
    [r'\b([Мм])не\b', r'\1нѣ'],
    [r'мнети\b', r'мнѣти'],

    [r'надеѧ(?=ніе|тисѧ)', r'надѣѧ'],
    [r'надею(?=щі|с)', r'надѣю'],
    [r'намерен', r'намѣрен'],
    [r'([Нн])евест', r'\1евѣст'],
    [r'([Нн])егоже\b', r'\1егѡже'],
    [r'([Нн])едел', r'\1едѣл'],
    [r'недр', r'нѣдр'],
    [r'\bнежн', r'нѣжн'],
    [r'\bнем(?=[аіоꙋы]\w|ы\b)', r'нѣм'],
    [r'\bнеси\b', r'нѣси'],
    [r'\bнесм(?=[ыь]\b)', r'нѣсм'],
    [r'\bнест(?=[еь]\b)', r'нѣст'],
    [r'([Нн])икол', r'\1їкол'],
    [r'([Нн])ыне', r'\1ынѣ'],

    [r'Ѻбаче', r'Ѡбаче'],
    [r'ѻбаче', r'ѡбаче'],
    [r'ѻбесити', r'ѡбѣсити'],
    [r'ѻбет', r'ѻбѣт'],
    [r'ѻбеща', r'ѻбѣща'],
    [r'ѻблец', r'ѡблец'],
    [r'Ѻбнов', r'Ѡбнов'],
    [r'ѻбнов', r'ѡбнов'],
    [r'Ѻбраз', r'Ѡбраз'],
    [r'([ѻо])браз', r'ѡбраз'],
    [r'ѻблекоша', r'ѡблекоша'],
    [r'ѻбре(?=[лст])', r'ѡбрѣ'],
    [r'ѻбрѧщ', r'ѡбрѧщ'],
    [r'ѻде(?=ва[еюѧ]|ющ|ѧ)', r'ѡдѣ'],
    [r'Ѻзар(?=[еєиѧ])', r'Ѡзар'],
    [r'ѻзар(?=[еєиѧ])', r'ѡзар'],
    [r'ѻкропи', r'ѡкропи'],
    [r'Ѻмы(?=\w)', r'Ѡмы'],  # ѡ҆мы́й
    [r'ѻмы(?=\w)', r'ѡмы'],
    [r'ѻправд', r'ѡправд'],
    [r'Ѻсен', r'Ѡсѣн'],
    [r'ѻсен', r'ѡсѣн'],
    [r'Ѻчи(?=сти|щ)', r'Ѡчи'],
    [r'ѻчи(?=сти|щ)', r'ѡчи'],

    [r'([Пп])е(ні|сн|ти|л)', r'\1ѣ\2'],

    [r'''  
        (
            [зн]а       # напѣвъ
            |ѿ          # ѿпѣванїе
            |пр[ио]     # припѣвъ
            |[Пп]салмо  
            |р[ао]с     # распѣвъ
            |с          # спѣлъ
        )
        пе([влт])       # пѣти
    ''', r'\1пѣв'],

    [r'([Пп])лач[ьъ]\b', r'\1лачь'],
    [r'плен', r'плѣн'],
    [r'побе(?=ж?д)', r'побѣ'],
    [r'([Пп])онедельник', r'\1онедѣльник'],
    [r'([Пп])осе(?=[тщ])', r'\1осѣ'],
    [r'([Пп])осле', r'\1ослѣ'],
    [r'пререкан', r'прерѣкан'],
    [r'прилеж(?=а|н)', r'прилѣж'],
    [r'присещ', r'присѣщ'],
    [r'([Пп])рисно\b', r'\1риснѡ'],
    [r'Псал(?=о?м|т)', r'Ѱал'],
    [r'псал(?=о?м|т)', r'ѱал'],

    # рѣчь
    [r'\bреч(?=[иь]|ам[иъ]\b)', r'рѣч'],
    # рѣка
    [r'\bрек(?=[аеѣиоꙋ])', r'рѣк'],
    [r'([Рр])осс', r'\1ѡсс'],

    [r'([Сс])ветле(?=[ей])', r'\1вѣтлѣ'],
    [r'([Сс])ве(?=[тщ])', r'\1вѣ'],
    [r'([Сс])вѧтемъ', r'\1вѧтѣмъ'],
    [r'семо', r'сѣмо'],
    [r'\bсен(?=[иіь])', r'сѣн'],
    [r'\bсено', r'сѣно'],
    [r'''
        \b
        сет
        (?=([иь]|ію)\b|ѧм)
    ''', r'сѣт'],

    [r'''
        стен #
        (?!  # ! стенать
            а([нт][иь]|ющ)
        )
    ''', r'стѣн'],

    [r'сиречь', r'сирѣчь'],
    [r'сне(?=[гж])', r'снѣ'],
    [r'совест', r'совѣст'],
    [r'([Сс])овет', r'\1овѣт'],
    [r'([Сс])офрон', r'\1офрѡн'],

    [r'([Тт])ако\b', r'\1акѡ'],
    [r'тайнемъ', r'тайнѣмъ'],
    # [r'([Тт])ебе\b', r'\1ебѣ'],  # ? в Дат. Предложн
    [r'\bтел(?=[аоꙋ]|е(с[аеин]|х)?)', r'тѣл'],
    [r'([Тт])емже', r'\1ѣмже'],
    [r'([Тт])епле', r'\1еплѣ'],
    [r'([Тт])ле(?=н[інъ]|т[иь])', r'\1лѣ'],
    [r'\bтьме\b', r'тьмѣ'],
    [r'\bтокмо\b', r'токмѡ'],

    # граница слова для ᲂу :
    # (\b - для `ᲂ' не работает)
    # (?<=\W)ᲂу
    # или (?<=(\W))?ᲂу - И для начала строки
    # или ^ᲂу - только для начала строки
    # (в *этом* модуле ᲂу всегда должен оказаться
    # в начале строки, т.к.
    # - обрабатывается отдельное слово
    # без предшествующих буквам символов)
    [r'^([Оᲂ]у)б[оѡ]\b', r'\1бѡ'],
    [r'^([Оᲂ]у)теш', r'\1тѣш'],

    [r'фарисе', r'фарїсе'],

    [r'([Хх])леб', r'\1лѣб'],
    [r'([Хх])рист', r'\1рїст'],

    [r'царск[ао]го', r'царскагѡ'],
    [r'([Цц])ве(?=[лст])', r'\1вѣ'],
    [r'цел(?=[еєиюѧ]|ьб|омꙋ)', r'цѣл'],

    [r'([Чч])елове(?=[кч])', r'\1еловѣ'],
    [r'([Чч])естнейш', r'\1естнѣйш'],

    [r'([Ꙗꙗ])ко\b', r'\1кѡ'],

    [r'', r'0'],
    [r'', r'1'],
    [r'', r'2'],
    [r'', r'3'],
    [r'', r'4'],
    [r'', r'5'],
    [r'', r'6'],
    [r'', r'7'],
    [r'', r'8'],
    [r'', r'9'],

    # months
    [r'ентѧбрѧ', r'ептемврїа'],
    [r'ктѧбрѧ', r'ктѡврїа'],
    [r'оѧбрѧ', r'оемврїа'],
    [r'екабрѧ', r'екемврїа'],
    [r'ꙗнварѧ', r'іаннꙋарїа'],
    [r'Ꙗнварѧ', r'Іаннꙋарїа'],
    [r'евралѧ', r'еврꙋарїа'],
    [r'([Мм])арта\b', r'\1арта'],
    [r'прелѧ', r'прілїа'],
    [r'([Мм])аѧ\b', r'\1аїа'],
    [r'([Іі])ю([лн])ѧ\b', r'\1ꙋ\2їа'],
    [r'([Аа])вгꙋста', r'\1ѵгꙋста'],
)

# Ударения
regs_acutes = (
    [r'([Аа])(?=зъ)', r'\1' + Iso],
    [r'([Аа])ка(?=ѳіст)', r'\1ка' + Oxia],
    [r'([Аа])ллилꙋ(?=іѧ)', r'\1ллилꙋ' + Oxia],
    [r'([Аа])ми(?=нь)', r'\1ми' + Oxia],
    [r'([Аа])(?=нгел)', r'\1' + Iso],
    [r'([Аа])по(?=стол)', r'\1по' + Oxia],
    [r'([Аа])рха(?=нгел)', r'\1рха' + Oxia],
    [r'([Аа])(?=ще)', r'\1' + Iso],

    # =========================
    # -бед-
    [r'\bбѣ(?=д[енс]\w|ъ\b)', r'бѣ' + Oxia],
    [r'\bбѣд([аеꙋ]\b|о(?=\w))', r'бѣд\1' + Oxia],
    [r'\bбѣд([аꙋ]\b)', r'бѣд\1' + Varia],

    # =========================
    # -бег-, -беж-
    [r''' # отбеже 
        (
            ^ᲂу
            |\b(?:
                из|при|ѿ
            )?
        )
        бѣ([гж])
        ([аеиꙋ]\b)
        ''',
     r'\1бѣ\2\3' + Varia
     ],
    [r''' # избѣглъ избѣгнꙋти
        (
            ^ᲂу
            |\b(?:
                из|при|ѿ|на
                )?
        )
        бѣ
        (?=г(л?ъ|н))
        ''',
     r'\1бѣ' + Oxia
     ],

    [r'\bбѣ(?=гати\b)', r'бѣ' + Oxia],
    [r'(^ᲂу|\b(?:из|при|ѿ)?)бѣжа(?=ти\b)', r'\1бѣжа' + Oxia],

    [r''' # избѣга́ти избѣго́х
        (   ^ᲂу
            |\b(?:
                из|при|ѿ
                )
        )
        бѣг
        ([оа])
        (?=\w+)
        ''',
     r'\1бѣг\2' + Oxia
     ],
    # ---- -бег-, -беж- ---------------

    [r''' # бѣлый
        \bбѣл 
        (?=[аоꙋы]\w)
        ''',
     r'бѣ' + Oxia + r'л'
     ],

    [r'''  # убеленный 
        (\b|^ᲂу)
        бѣл
        (?![аоꙋы]\w) # ! бѣлый
        ([еиоѧ])''',
     r'\1бѣл\2' + Oxia
     ],
    # ---- -бел- -----------------

    [r'\bбѣс(?=[аиꙋыъ]\b)', r'бѣ' + Oxia + r'с'],
    [r'\bбѣ\b', r'бѣ' + Varia],

    [r''' # бесте беша бехом
        \b
        бѣ
        (?=
            сте
            |х(?=(ом)?ъ)
            |ша
        )   
        ''',
     r'бѣ' + Oxia
     ],

    [r'\bбде\b', r'бдѣ' + Varia],
    [r'\bбде(?=[нт])', r'бдѣ' + Oxia],

    # =========================
    # -благ- -блаж -
    [r'\b([Бб])ла(?=го\b)', r'\1ла' + Oxia],
    [r'([Бб])лагі(?=[йеѧ])', r'\1лагі' + Oxia],
    [r'([Бб])лагоговѣ(?=йн)', r'\1лагоговѣ' + Oxia],
    [r'([Бб])лагодар([ѧю])\b', r'\1лагодар\2' + Varia],
    # благодарим
    [r'([Бб])лагодар([иеѧ])(?=\w+)', r'\1лагодар\2' + Oxia],
    # благодарно, благодать
    [r'([Бб])лагода(?=[рт](?![иеѧ]\w+|ѧ\b))', r'\1лагода' + Oxia],
    # благослове́нїе
    [r'([Бб])лагослове(?=н)', r'\1лагослове' + Oxia],
    # благослови
    [r'([Бб])лагослови\b', r'\1лагослови' + Varia],

    # -блаж-
    [r'\b([Бб])ла(?=же\b)', r'\1ла' + Oxia],
    [r''' # ᲂу҆блажа́емъ блаже́нный
        ([Бб])лаж
        (?!е\b) # ! блаже
        ([аеи])
        ''',
     r'\1лаж\2' + Oxia
     ],
    # --------------------------

    # =========================
    # -бог- -бож- -боз-
    [r''' # бо́гъ бо́гꙋ бо́гомъ  
        (^ᲂу|\b) # ᲂу҆бо́гїй вынести отдельно
        ([Бб])ог
        (?=
            (
                [аеиꙋъ]
                |ій  # вынести отдельно
                |о(мъ|ви)
            )\b
        )
        ''',
     r'\1\2о' + Oxia + r'г'
     ],
    [r'''  # бога́тый бога́тно
        богат
        (?=
            ъ
            |[аіоꙋы]\w\b # бога́тый
            |[оы]м\w?   # бога́томꙋ бога́тымъ 
            |н([аеоѡꙋы]) # бога́тно
            |ств
        )
        ''', r'бога' + Oxia + r'т'],
    [r''' # бо́же бо́жїй
        \b
        ([Бб])ож
        (?=
            (е|і[аеийюѧ])\b
        )
        ''',
     r'\1о' + Oxia + r'ж'
     ],

    [r'([Бб])оже(?=ственн)', r'\1оже' + Oxia],
    [r'\b([Бб])ожество\b', r'\1ожество' + Varia],

    [r''' # бо́зе бо́зи
        \b
        ([Бб])оз
        (?=[еѣи]\b)
        ''',
     r'\1о' + Oxia + r'з'
     ],
    # ---- -бог- -бож- -боз- -------

    [r'([Бб])оговѣ(?=дѣн)', r'\1оговѣ' + Oxia],
    [r'([Бб])огодꙋхнове(?=нн)', r'\1огодꙋхнове' + Oxia],
    [r'([Бб])огоро(?=ди[чц])', r'\1огоро' + Oxia],
    [r'([Бб])огороди(?=тельниц)', r'\1огороди' + Oxia],
    [r'болѣ(?=зн)', r'болѣ' + Oxia],

    [r'бꙋ(?=д(етъ|и))', r'бꙋ' + Oxia],
    [r'([Бб])ы(?=(ли|ти|сть|ша)\b)', r'\1ы' + Oxia],

    # ========================
    #   вѣд вѣж вѣм вѣт вѣс вѣщ
    #   -вѣд-
    [r'''
        \b
        (
            (не)?(из)?
            |(ис)?по
        )?
        вѣд
        (?=
             а [елнтхюѧ]?
            |е [нтхш]
            |и [хш]
            |о [м]
            |ꙋ [еюѧ]
            |ѧ т 
        )
        ''',
     r'\1вѣ' + Oxia + r'д'
     ],

    #   -вѣж-
    [r'\b(не)?вѣ(?=ж)', r'\1вѣ' + Oxia],

    #   -вѣм-
    [r'''    
        \b
        ((ис)?по)?
        вѣм
        (?=[ыъ])
        ''',
     r'вѣ' + Oxia + r'м'
     ],

    #   -вѣс-
    [r'\b([Нн]е)?вѣ(?=с(и\b|т))', r'\1вѣ' + Oxia],
    # со́вѣсть
    [r'\bсо(?=вѣст)', r'со' + Oxia],

    #   -вѣт- (! цвѣ́тъ свѣт вѣтіи, вѣтвѧми)
    [r'(?<![сц])вѣт(?!(і[иѧ]|вѧм))', r'вѣ' + Oxia + r'т'],
    # вѣтіи
    [r'\bвѣті(?=[иѧ])', r'вѣті' + Oxia],

    #   -вѣщ-
    [r'вѣ(?=щій\b)', r'вѣ' + Oxia],
    [r'вѣщ([ае])', r'вѣщ\1' + Oxia],
    [r'вѣщꙋ\b', r'вѣщꙋ' + Varia],

    # ---- вѣд вѣж вѣм вѣт вѣс вѣщ ----

    # ========================
    # век- вец- веч-
    [r'\bвѣк(?![оѡ]в|ам)', r'вѣ' + Oxia + r'к'],
    [r'''
        \b
        вѣк
        ([аоѡ])(?=[мвх][иъ])
        ''',
     r'вѣк\1' + Oxia
     ],

    [r'вѣ(?=цѣ(хъ)?)', r'вѣ' + Oxia],
    [r'вѣ(?=че?н)', r'вѣ' + Oxia],
    # ---- век- вец- веч- ----------

    # ========================
    #   венц- венч-
    [r'\bвѣне(?=цъ\b)', r'вѣне' + Oxia],
    [r'\bвѣнц([аеѣꙋы])\b', r'вѣнц\1' + Varia],
    # вѣнца́ми
    [r''' 
        \b
        вѣнц
        (?!
            [аеѣꙋы]\b   # ! вѣнцꙋ̀
            |ецъ\b      # ! вѣне́цъ   
        )
        (?P<acut>[аеєоѡ])
        (?=\w+)
        ''',
     r'вѣнц\g<acut>' + Oxia
     ],

    # вѣнча̀
    [r'(^ᲂу|\b(?:[ѻѡ]б)?)вѣнча\b', r'\1вѣнча' + Varia],

    # вѣ́нче вѣ́нчанъ
    [r'''    
        (
            ^ᲂу
            |\b(?:
                раз 
                |[ѻѡ]б
            )?
        )
        вѣнч
        (?=(е|анъ)\b)
        ''',
     r'\1вѣ' + Oxia + r'нч'
     ],
    # вѣнча́еши
    [r'''
        (
            ^ᲂу
            |\b(?:[ѻѡ]б)?
        )
        вѣнч
        (?! 
            # ! вѣнча̀ вѣ́нче вѣ́нчанъ 
            ([ае]|анъ)\b
        )
        а   # ударн.
        ''',
     r'\1вѣнча' + Oxia
     ],
    # ----  венц- венч- --------------

    [r'вѣ(?=р[аеиноꙋѧ])', r'вѣ' + Oxia],
    [r'вѣтвѧ(?=м)', r'вѣтвѧ' + Oxia],
    [r'взыва', r'взыва' + Oxia],
    [r'він([аеоу])\b', r'вїн\1' + Varia],
    [r'\b(нена)?видѣ(?=ні)', r'\1видѣ' + Oxia],
    [r'віногра', r'вїногра' + Oxia],
    [r'([Вв])лады(?=[кчц])', r'\1лады' + Oxia],

    [r'\bвмѣнѧ', r'вмѣнѧ' + Oxia],
    [r'\bвмѣни\B', r'вмѣни' + Oxia],
    [r'\bвмѣни\b', r'вмѣни' + Varia],

    [r'воздѣва', r'воздѣва' + Oxia],
    [r'воздѣ(?=ти|еши|ющ)', r'воздѣ' + Oxia],

    # возсїѧ̀
    [r'([Вв])озсіѧ\b', r'\1озсїѧ' + Varia],
    # возсїѧ́й
    [r'([Вв])озсіѧ(?!\b|ва)', r'\1озсїѧ' + Oxia],
    [r'([Вв])озсїѧва', r'\1озсїѧва' + Oxia],

    [r'воспѣва', r'воспѣва' + Oxia],
    [r'воспою', r'воспою' + Varia],

    # вра́гъ вра́жїй вражд-
    [r'''
        \b
        вра
        (?=
            гъ
            |ж(?!д) # ! вражда
        )
        ''',
     r'вра' + Oxia
     ],
    [r'\bвра([гз])([аеиꙋ])\b', r'вра\1\2' + Varia],
    [r'\bвражд([аеꙋы])\b', r'вражд\1' + Varia],
    [r'\bвражд([еоꙋ])\B', r'вражд\1' + Oxia],

    [r'([Вв])ра(?=чь)', r'\1ра' + Oxia],
    [r'([Вв])рачꙋ', r'\1рачꙋ' + Varia],
    [r'всегда', r'всегда' + Varia],
    [r'всѣ(?=м[иъ]|хъ)', r'всѣ' + Oxia],
    [r'всемꙋ', r'всемꙋ' + Varia],
    [r'всеѧ', r'всеѧ' + Varia],
    [r'\bвс([ию])\b', r'вс\1' + Varia],
    [r'\bвсѧ\b', r'всѧ' + Kamora],
    [r'\bвсѧ(?=[кцч])', r'всѧ' + Oxia],
    [r'вта(?=йне)', r'вта' + Oxia],

    # геѳсїма́нїа
    [r'([Гг])еѳсіма(?!нійс)', r'\1еѳсїма' + Oxia],
    # геѳсїмані́йстѣй
    [r'([Гг])еѳсімані(?=йс)', r'\1еѳсїмані' + Oxia],

    # Глаго́лъ
    [r'\b([Гг])лаго(?=л)', r'\1лаго' + Oxia],
    # гла́съ
    [r'\b([Гг])ла(?=с[аноеꙋыъ])', r'\1ла' + Oxia],
    # глаша́ти ѻ҆глаше́нный
    [r'([Гг])лаш([ае])', r'\1лаш\2' + Oxia],
    # ѻ҆гласѝ
    [r'(воз|[ѻѡ])гласи\b', r'\1гласи' + Varia],

    [r'гнѣ(?=в)', r'гнѣ' + Oxia],
    # годи́на
    [r'\bгоди(?=н[аеѣоꙋы])', r'годи' + Oxia],
    [r'горѣ(?=т)', r'горѣ' + Oxia],
    [r'\bгорѣ\b', r'горѣ' + Varia],
    # го́ре
    [r'\bго(?=ре\b)', r'го' + Oxia],

    # Го́споди
    [r'([Гг])о(?=спод([аеиꙋ]|омъ)\b)', r'\1о' + Oxia],
    # Госпо́дне
    [r'([Гг])оспо(?=д([нь]|ств))', r'\1оспо' + Oxia],
    # Госпожа̀
    [r'([Гг])оспож([аеиѣꙋ])\b', r'\1оспож\2' + Varia],

    # ==============================
    # грѣ́хъ грѣ́шникъ грѣ́шенъ грѣшны̀ согрѣшѝ прегрѣше́нїѧ грѣсѝ грѣсѣ́хъ

    # грѣх (ѣ - ударн.)
    [r'''
        \b
        ([Гг])рѣ
        (?=
            хъ
            |шенъ
            |шн(?!\w\b)) # ! гръшны
        ''',
     r'\1рѣ' + Oxia
     ],

    [r'(со)?грѣш([иꙋ]|н[аоѡы])\b', r'\1грѣш\2' + Varia],
    [r'грѣси\b', r'грѣси' + Varia],
    [r'грѣсѣ(?=хъ\b)', r'грѣсѣ' + Oxia],
    # прегрѣше́нїѧ
    [r'''
        грѣш
        (?P<acut>
            [аи]
            |е(?!нъ) # ! грѣ́шенъ
        )\B
        ''',
     r'грѣш\g<acut>' + Oxia
     ],
    # -------------------------------

    [r'грѧд([иꙋ])\b', r'грѧд\1' + Varia],

    [r'да(?=бы|же)', r'да' + Oxia],

    [r'\bда(?=р([аеѣꙋъ]\b|ꙋ\B))', r'да' + Oxia],
    [r'\bдары\b', r'дары' + Varia],
    [r'\bдарова\B', r'дарова' + Oxia],
    [r'\bдарова\b', r'дарова' + Varia],

    # дѣ́ва
    [r'''
        \b
        ([Пп]рисно)?
        ([Дд])ѣ(?=в(?!омати))
        ''',
     r'\1\2ѣ' + Oxia
     ],

    [r'\bде(?=нь)', r'де' + Oxia],
    [r'\bднѣ\b', r'днѣ' + Varia],
    [r'дне(?=сь)', r'дне' + Oxia],

    [r'\bдѣ(?=т)(?!то[вр]од)', r'дѣ' + Oxia],
    [r'\bдѣто([вр]од)([иѧ])', r'дѣто\1\2' + Oxia],
    [r'издѣ(?=тска)', r'издѣ' + Oxia],

    # дѣ́ло
    [r'\bдѣ(?=л[оаꙋ]\b)', r'дѣ' + Oxia],
    [r'дѣ(?=ѧти)', r'дѣ' + Oxia],
    [r'\bдлѧ\b', r'bдлѧ' + Varia],
    [r'добродѣ(?=тел)', r'добродѣ' + Oxia],
    [r'([Дд])око(?=лѣ)', r'\1око' + Oxia],

    # дꙋша̀
    [r'([Дд])ꙋш([аеѣ])\b', r'\1ꙋш\2' + Varia],
    # дꙋше́внꙋю
    [r'([Дд])ꙋше(?=вн|ю)', r'\1ꙋше' + Oxia],
    # дꙋ́шꙋ
    [r'([Дд])ꙋ(?=ш[ꙋъ]\b)', r'\1ꙋ' + Oxia],
    # дꙋ́сѣ
    [r'\b([Дд])ꙋ(?=сѣ\b)', r'\1ꙋ' + Oxia],

    # є҆̀ ю҆̀ ꙗ҆̀
    [r'\b([ЄєЮюꙖꙗ])\b', r'\1' + Apostrof],

    [r'([Єє])ѵа(?=нгел)', r'\1ѵа' + Oxia],

    [r'([Єє])вфра(?=фовъ)', r'\1вфра' + Oxia],
    # є҆гда̀ є҆да̀
    [r'([Єє]г?)да\b', r'\1да' + Varia],
    # є҆гѡ̀ є҆го̀
    [r'([Єє])г([оѡ])\b', r'\1г\2' + Varia],
    # є҆го́же
    [r'([Єє])го(?=же\b)', r'\1го' + Oxia],
    # є҆́же є҆́й є҆́сть є҆́юже
    [r'([Єє])(?=же|й|сть|юже\b)', r'\1' + Iso],
    # є҆ли́ко є҆ли́цы є҆ли́жды
    [r'єли(?=жды|ко|цы)', r'єли' + Oxia],
    # є҆мꙋ̀ є҆сѝ є҆щѐ є҆стѐ
    [r'\b([Єє])(мꙋ|си|сте|ще)\b', r'\1\2' + Varia],

    [r'желѣ(?=з)', r'желѣ' + Oxia],
    # же́но
    [r'\b([Жж])е(?=но\b)', r'\1е' + Oxia],
    # жена̀ женѐ
    [r'\b([Жж])ен([аеѣꙋы])\b', r'\1ен\2' + Varia],
    # живꙋ́щїй
    [r'живꙋ(?=щ\w+)', r'живꙋ' + Oxia],
    # жива̀
    [r'жив([аꙋ])\b', r'жив\1' + Varia],
    # жи́знь жи́зненный
    [r'([Жж])и(?=зн([иь]|енн))', r'\1и' + Oxia],

    # завѣ́са
    [r'\b([Зз])авѣ(?=с)', r'\1авѣ' + Oxia],

    # за́повѣдь
    [r'([Зз])а(?=повѣд[иь])', r'\1а' + Oxia],
    # заповѣ́далъ (! за́повѣдь)
    [r'([Зз])аповѣ(?=д)(?!д[иь])', r'\1аповѣ' + Oxia],

    # зва́ти
    [r'\b(при|воз|на)?зва(?=[лнтхш])', r'\1зва' + Oxia],
    # воззва̀
    [r'\b(при|воз|на)?зва\b', r'\1зва' + Varia],

    # ѕвѣ́зды ѕвѣ́здный
    [r'([Ѕѕ])вѣ(?=зд(ы\b|н))', r'\1вѣ' + Oxia],
    # ѕвѣзда̀
    [r'([Ѕѕ])вѣзд([аеѣоꙋ])\b', r'\1вѣзд\2' + Varia],
    # ѕвѣздо́ю
    [r'([Ѕѕ])вѣзд([ао])\B', r'\1вѣзд\2' + Oxia],

    [r'ѕвѣ(?=р[иеѣ]|рь(?!ми))', r'ѕвѣ' + Oxia],
    [r'ѕвѣ(?=р[иеѧѣ]\b|ь(?!ми))', r'ѕвѣ' + Oxia],
    [r'ѕвѣрѧ(?=ми)', r'ѕвѣрѧ' + Oxia],
    [r'ѕвѣрьми\b', r'ѕвѣрьми' + Varia],
    # [r'ѕдѣрьми\b', r'ѕвѣрьми' + Varia],
    [r'\bздѣ\b', r'здѣ' + Varia],
    [r'\bздѣ(?=сь\b)', r'здѣ' + Oxia],
    [r'ѕѣлѡ\b', r'ѕѣлѡ' + Varia],
    [r'ѕѣ(?=льн)', r'ѕѣ' + Oxia],

    [r'([Зз])емл(?=[иѧ]\b)', r'\1емл' + Varia],
    [r'([Зз])е(?=млю\b)', r'\1е' + Oxia],

    [r'зѣ(?=ниц)', r'зѣ' + Oxia],

    [r'ѕл([аеіѣоꙋы])\b', r'ѕл\1' + Varia],
    [r'ѕл([аеѣіоы])\B', r'ѕл\1' + Oxia],

    [r'\bѕмі(?=й)\b', r'bѕмі' + Oxia],
    [r'\bзра(?=к|ц)', r'зра' + Oxia],

    # зрѣ́ти ᲂу҆зрѣ́ти
    [r'(^ᲂу|\b(?:при)?)зрѣ(?=[лнтхш])', r'\1зрѣ' + Oxia],
    # зрю̀  призрѣ̀
    [r'\b(при)?зр([еѣиюѧ])\b', r'\1зр\2' + Varia],

    [r'([Іі])а(?=ков)', r'\1а' + Oxia],
    [r'([Іі])езекі(?=ил)', r'\1езекі' + Oxia],
    # іерей
    [r'([Іі])ере(?!м)', r'\1ере' + Oxia],
    [r'([Іі])еремі', r'\1еремі' + Oxia],
    [r'([Іі])ерꙋсали(?=м)', r'\1ерꙋсали' + Oxia],
    [r'([Іі])зра(?=ил)', r'\1зра' + Oxia],
    [r'([Іі])исꙋ(?=с)', r'\1исꙋ' + Oxia],
    [r'([Ии])(?=мѧрекъ)', r'\1' + Iso],
    [r'([Іі])ѻрда(?=н)', r'\1ѻрда' + Oxia],
    [r'([Іі])ꙋ(?=д(\w\b|о))', r'\1ꙋ' + Oxia],
    [r'([Іі])ꙋде(?=\w)', r'\1ꙋде' + Oxia],
    # і҆ѡа́ннъ
    [r'([Іі])ѡа(?=нн(?![іи]к))', r'\1ѡа' + Oxia],
    # і҆ѡанни́кїй
    [r'([Іі])ѡа(нн?[іи])(?=к)', r'\1ѡа\2' + Oxia],
    # і҆́ѡвъ
    [r'([Іі])(?=ѡв)', r'\1' + Iso],
    [r'([Іі])ѡ(?=сиф)', r'\1ѡ' + Oxia],

    [r'\bидѣ(?=же\b)', r'идѣ' + Oxia],
    [r'изба(?=ви)', r'изба' + Oxia],
    [r'изрѧ(?=дн)', r'изрѧ' + Oxia],
    # і҆́косъ
    [r'([Іі])(?=кос)', r'\1' + Iso],
    [r'([Іі])рм(?=ос)', r'\1' + Oxia],
    [r'([Ии])(?=мже)', r'\1' + Iso],
    [r'([Ии])(?=мѧ)', r'\1' + Iso],
    [r'испещре(?=н)', r'испещре' + Oxia],
    [r'([Ии])(?=сповѣд(ь|и\b))', r'\1' + Iso],
    [r'ѵссѡ(?=п)', r'ѵссѡ' + Oxia],

    [r'исцѣле(?=н)', r'исцѣле' + Oxia],
    [r'неисцѣ(?=льн)', r'неисцѣ' + Oxia],
    [r'исцѣле\b', r'исцѣле' + Varia],

    [r'\bи(?=хъ\b)', r'и' + Iso],

    [r'\b([Кк])а(?=ѧ)', r'\1а' + Oxia],
    [r'([Кк])а(?=кѡ)', r'\1а' + Oxia],
    [r'([Нн])ика(?=коже)', r'\1а' + Oxia],
    [r'\b(([Нн]е)?[Кк])і(?=ими|й)', r'\1і' + Oxia],
    [r'\b([Кк])о(?=е)', r'\1о' + Oxia],
    [r'([Кк])оли(?=ко)', r'\1оли' + Oxia],

    [r'([Кк])онда(?=къ)', r'\1онда' + Oxia],
    [r'колѣ(?=н[ао](?!прекл))', r'колѣ' + Oxia],

    # прекра́снаѧ
    [r'прекра(?=с)', r'прекра' + Oxia],
    # кра́снаѧ
    [r'\bкра(?=сн[аоіꙋы]\B)', r'кра' + Oxia],
    # красны̀ красна̀
    [r'\bкрасн([аы])\b', r'красн\1' + Varia],
    # красе́нъ
    [r'\bкрасе(?=нъ\b)', r'красе' + Oxia],

    [r'красот([аеѣоꙋы])\b', r'красот\1' + Varia],
    [r'красото(?=ю)', r'красото' + Oxia],
    [r'красото\b', r'красото' + Varia],
    [r'крѣ(?=пк)', r'крѣ' + Oxia],
    [r'([Кк])ре(?=стн)', r'\1ре' + Oxia],
    [r'кро(?=т[коц])', r'кро' + Oxia],
    [r'кꙋпѣ(?=л)', r'кꙋпѣ' + Oxia],
    [r'([Кк])ꙋпин([аеоꙋы])\b', r'\1ꙋпин\2' + Varia],
    [r'([Кк])ꙋпино\B', r'\1ꙋпино' + Oxia],
    [r'([Кк])ꙋ(?=ю)', r'\1ꙋ' + Oxia],

    [r'([Лл])ѣ(?=стви)', r'\1ѣ' + Oxia],
    [r'лѣ(?=то)', r'лѣ' + Oxia],
    # ли́къ
    [r'\b([Лл])и(?=к\w\b)', r'\1и' + Oxia],

    # любвѐ любы̀
    [r'([Лл])юб(в[ие]|ы)\b', r'\g<0>' + Varia],
    # любо̀вь
    [r'([Лл])юбо(?=в([їь]ю?))', r'\1юбо' + Oxia],

    [r'\b([Мм])арі(?=[еиѧю])', r'\1арі' + Oxia],
    [r'\b([Мм])аріа(?=м)', r'\1аріа' + Oxia],

    [r'''
        ([Бб]ого)?
        ([Мм])а
        (?=
            т
            (
                и         # ма́ти
                |ер[нісь] # богома́терїю
            )
        )
        ''',
     r'\1\2а' + Oxia
     ],

    # бг҃омт҃ери́нскїй
    [r'''
        (
            ([Бб]ого)?
            [Мм]
        )
        атери(?=нск)
        ''', r'\1атери' + Oxia
     ],

    # мѣ́сто
    [r'мѣ(?=ст)', r'мѣ' + Oxia],
    [r'([Мм])ѣ(?=сѧц)', r'\1ѣ' + Oxia],
    [r'([Мм])илосе(?=рд)', r'\1илосе' + Oxia],
    [r'([Мм])и(?=лост(?!ивлен))', r'\1и' + Oxia],
    [r'([Мм])ладе(?=не?[цч])', r'\1ладе' + Oxia],
    [r'\b([Мм])ѵ(?=р\w\b)', r'\1ѵ' + Oxia],
    [r'\b([Мм])ѵ(?=роно)', r'\1ѵ' + dbl_grave],
    [r'мнѣ(?=ти)', r'мнѣ' + Oxia],
    [r'\b([Мм])нѣ\b', r'\1нѣ' + Varia],
    # моѐ мою̀ моѧ̀
    [r'\b([Мм])о([еюѧ])\b', r'b\1о\2' + Varia],
    [r'\b([Мм])о(?=й\b)', r'\1о' + Oxia],
    [r'моли\b', r'моли' + Varia],
    [r'моли(?=тв(?!ослов))', r'моли' + Oxia],
    # -мꙋ́др-
    [r'''
        ([Мм])ꙋ
        (?!
            др(
                ец
                |и(вш|[лcш])
                |[оѡ]([влт]|с(тьми|ост))
                |ѧ
                |ѣйш
            )
        )
        (?=др)
        ''', r'\1ꙋ' + Oxia],
    # мученик (! мученіе - ???)
    [r'([Мм])ꙋдрова(?=н)', r'\1ꙋдрова' + Oxia],
    [r'([Мм])ꙋ(?=чен(?!і))', r'\1ꙋ' + Oxia],
    [r'([Мм])ꙋче(?=ні)', r'\1ꙋче' + Oxia],

    [r'надѣ(?=[жѧю])', r'надѣ' + Oxia],
    [r'намѣ(?=рен)', r'намѣ' + Oxia],

    # на́мъ на́шꙋ на́шего на́съ
    [r'''
        \b
        на
        (?=
            (
                [мс]
                [иъ]
                |
                ш
                (
                    [аꙋыъѧ]
                    |е([йюѧ]|го|м[уъ])?
                    |и([мх]ъ)?
                )
            )
            \b
        )
        ''',
     r'на' + Oxia
     ],

    # небеса̀
    [r'\b([Нн])ебес([аеѣи])\b', r'\g<0>' + Varia],
    # не́бо не́бꙋ
    [r'\b([Нн])е(?=б\w\b)', r'\1е' + Oxia],
    # небе́сный небе́съ
    [r'\b([Нн])ебе(?=с(н\w|ъ))', r'\1ебе' + Oxia],
    [r'([Нн])евѣ(?=ст|щ)', r'\1евѣ' + Oxia],

    [r'([Нн])егѡ(?=же\b)', r'\1егѡ' + Oxia],
    [r'([Нн])едѣ(?=л)', r'\1едѣ' + Oxia],
    [r'нѣ(?=др)', r'нѣ' + Oxia],
    [r'\bнѣ(?=жн)', r'нѣ' + Oxia],

    [r'неизрече(?=нн)', r'неизрече' + Oxia],
    [r'([Нн])е(?=йже)', r'\1е' + Oxia],

    # нѣмы̑ѧ
    [r'\bнѣмы(?=ѧ)', r'нѣмы' + Kamora],
    # нѣмо́й
    [r'\bнѣм(?!ыѧ?\b|от\w)([аіоꙋы])', r'нѣм\1' + Oxia],
    # нѣмота̀
    [r'\bнѣмот[аꙋы]\b', r'\g<0>' + Varia],
    # нѣ́мы
    [r'\bнѣ(?=мы\b)', r'нѣ' + Oxia],

    [r'непоро(?=че?н)', r'непоро' + Oxia],

    # нѣ́си нѣ́смь нѣ́смы нѣ́сть
    [r'\bнѣ(?=с([мт][ыь]|и)\b)', r'нѣ' + Oxia],

    # нїко́лае
    [r'([Нн])іко(?=лае\b)', r'\1їко' + Oxia],
    # нїкола́й
    [r'([Нн])ікола(?!е\b)', r'\1їкола' + Oxia],

    # но́ваго но́вый но́вомꙋ но́выхъ
    [r'''
        \b
        ([Нн])о
        (?=
            в
            (
                а(г[оѡ]|ѧ)
                |ꙋю
                |о(г[оѡ]|[ейю]|м[ъꙋ])
                |ы([ейѧ]|[мх][аиъ])
            )
        )
        ''',
     r'\1о' + Oxia
     ],

    # но́чь но́щїю но́чи
    [r'\bно(?=[чщ](ь|ію|(?<=ч)и))', r'но' + Oxia],
    # нощѝ
    [r'\bнощи\b', r'нощи' + Varia],

    # ны́нѣ
    [r'([Нн])ы(?=нѣ)', r'\1ы' + Oxia],

    [r'([Ѡѡ])ба(?=че)', r'\1ба' + Oxia],
    [r'ѡбѣ(?=сити)', r'ѡбѣ' + Oxia],

    [r'ѻбѣ(?=тъ)', r'ѻбѣ' + Oxia],
    [r'ѻбѣща\b', r'ѻбѣща' + Varia],
    # ѻ҆бѣ́тъ ѻ҆бѣща́нїе ѻ҆бѣща́хомъ ѻ҆бѣща́въ
    [r'ѻбѣща(?=[влхшеюѧ]|ні|ти)', r'ѻбѣща' + Oxia],

    [r'([Ѻѻ])би(?=тел)', r'\1би' + Oxia],

    [r'ѡблек([аіо])', r'ѡблек\1' + Oxia],
    [r'ѡбле(?=кл)', r'ѡбле' + Oxia],
    [r'ѡбле(?=кл)', r'ѡбле' + Oxia],
    [r'ѡблече\b', r'ѡблече' + Varia],
    [r'ѡблече\B', r'ѡблече' + Oxia],
    [r'ѡблецы\b', r'ѡблецы' + Varia],
    [r'ѡблецы\B', r'ѡблецы' + Oxia],
    [r'ѡблеце\B', r'ѡблеце' + Oxia],

    [r'([Ѡѡ])бнови\b', r'\1бнови' + Varia],
    [r'([Ѡѡ])бнови\B', r'\1бнови' + Oxia],
    [r'([Ѡѡ])(?=браз)', r'\1' + Iso],

    [r'ѡбрѣ(?=[лт]ъ\b|тені)', r'ѡбрѣ' + Oxia],
    [r'ѡбрѧ(?=щ)', r'ѡбрѧ' + Oxia],
    [r'ѡбрѣт([ао])', r'ѡбрѣт\1' + Oxia],
    [r'ѡбрѣсти\b', r'ѡбрѣсти' + Varia],
    [r'ѡбрѣл([аи])\b', r'ѡбрѣл\1' + Varia],

    # ѡ҆дѣ́ющагосѧ
    [r'ѡдѣ(?=ющ)', r'ѡдѣ' + Oxia],
    [r'ѡдѣѧ\B', r'ѡдѣѧ' + Oxia],
    [r'ѡдѣва(?=[еюѧ])', r'ѡдѣва' + Oxia],

    [r'([Ѡѡ])зари\b', r'\1зари' + Varia],
    [r'([Ѡѡ])зар([еєиѧ])\B', r'\1зар\2' + Oxia],

    [r'([Ѡѡ])кропи\b', r'\1кропи' + Varia],
    [r'([Ѡѡ])кропи\B', r'\1кропи' + Oxia],

    # ѡ҆мы́й ѡ҆мы́ю
    [r'([Ѡѡ])мы(?!ва)', r'\1мы' + Oxia],
    # ѡ҆мыва́ти
    [r'([Ѡѡ])мыва\B', r'\1мыва' + Oxia],

    [r'ѡправд(?P<a>[аи])', r'ѡправд\g<a>' + Oxia],

    [r'([Ѡѡ])сѣни\b', r'\1сѣни' + Varia],
    [r'([Ѡѡ])сѣн([еиѧ]\B)', r'\1сѣн\2' + Oxia],

    [r'([Ѿѿ]|([Ѻѻ]т))крове(?=ні)', r'\1крове' + Oxia],

    # ѻ҆тцы̀ ѻ҆те́цъ ѻ҆те́чь ѻ҆те́ческїй ѻ҆́тча ѻ҆́тчїй ѻ҆те́ческїй ѻ҆те́чество
    [r'([Ѻѻ])т([еєѣ])(?=цъ)', r'\1т\2' + Oxia],
    [r'([Ѻѻ])тц([аеѣꙋы])\b', r'\1тц\2' + Varia],
    [r'([Ѻѻ])тц([аеєѣо])\B', r'\1тц\2' + Oxia],
    [r'([Ѻѻ])(?=тч([аеєѣіꙋ]|и(?!зн)))', r'\1' + Iso],
    [r'([Ѻѻ])те(?=ч(ь\b|ес[кт]))', r'\1те' + Oxia],

    [r'([Ѡѡ])чи(?=с(?!титель)|щꙋ)', r'\1чи' + Oxia],
    [r'([Ѡѡ])чища', r'\1чища' + Oxia],

    [r'([Ѻѻ])чи(?=ма)', r'\1чи' + Oxia],
    [r'([Ѻѻ])(?=чи\b)', r'\1' + Iso],

    [r'([Пп])а(?=ки|че)', r'\1а' + Oxia],

    # пѣ́ти напѣ́въ
    [r'([Пп])ѣ(?!вані)(?=[влнт])', r'\1ѣ' + Oxia],
    # ѿпѣва́нїе
    [r'([Пп])ѣва(?=ні)', r'\1ѣва' + Oxia],

    [r'печа(?=л)', r'печа' + Oxia],

    # пла́чь пла́чꙋщаѧ
    [r'([Пп])ла(?!чевн)(?=[чк])', r'\1ла' + Oxia],
    # плаче́вный
    [r'([Пп])лаче(?=вн)', r'\1лаче' + Oxia],

    [r'побѣжда', r'побѣжда' + Oxia],
    [r'побѣди', r'побѣди' + Oxia],
    [r'побѣ(?!донос)(?=д[аиноꙋы]\b)', r'побѣ' + Oxia],
    [r'побѣдоно(?=сн)', r'побѣдоно' + Oxia],

    # покаѧ́нїе
    [r'([Пп])окаѧ(?=н)', r'\1окаѧ' + Oxia],
    # пока́ѧтисѧ
    [r'([Пп])ока(?=ѧ[стхш])', r'\1ока' + Oxia],

    [r'([Пп])окро(?!венн)(?=в)', r'\1окро' + Oxia],
    [r'([Пп])окрове(?=нн)', r'\1окрове' + Oxia],

    [r'([Пп])окры\b', r'\1окры' + Varia],
    [r'([Пп])окры(?=[ей])', r'\1окры' + Oxia],
    [r'([Пп])окрыва\B', r'\1окрыва' + Oxia],

    [r'([Пп])оми(?=л)', r'\1оми' + Oxia],

    # посѣтѝ
    [r'([Пп])осѣти\b', r'\g<0>' + Varia],
    # посѣти́ша
    [r'([Пп])осѣти\B', r'\g<0>' + Oxia],
    # посѣщꙋ̀
    [r'([Пп])осѣщ([аꙋ])\b', r'\1осѣщ\2' + Varia],
    # посѣща́еши
    [r'([Пп])осѣщ([ае])\B', r'\1осѣщ\2' + Oxia],

    # по́слѣ
    [r'([Пп])о(?=слѣ\b)', r'\1о' + Oxia],
    # послѣ́днїй
    [r'([Пп])ослѣ(?=д)', r'\1ослѣ' + Oxia],

    [r'\bпре(?=дъ)\b', r'пре' + Oxia],
    [r'([Пп])ра(?=вед)', r'\1ра' + Oxia],
    [r'([Пп])редте(?=ч)', r'\1редте' + Oxia],
    [r'([Пп])реподо(?=б)', r'\1реподо' + Oxia],
    [r'([Пп])речи(?=ст)', r'\1речи' + Oxia],

    # прїидѝ
    [r'([Пп])ріид([иꙋ])\b', r'\1рїид\2' + Varia],
    # прїиди́те
    [r'([Пп])ріид([ио])\B', r'\1рїид\2' + Oxia],
    # прїи́демъ
    [r'([Пп])ріи(?=дем)', r'\1рїи' + Oxia],

    [r'прилѣ(?=ж)', r'прилѣ' + Oxia],
    [r'присѣща', r'присѣща' + Oxia],
    [r'([Пп])ри(?=снѡ\b)', r'\1ри' + Oxia],
    [r'простира', r'простира' + Oxia],
    [r'\b([Пп])роро', r'\1роро' + Oxia],

    # ѱало́мъ
    [r'([Ѱѱ])ало(?=м)', r'\1ало' + Oxia],
    # ѱалти́рь
    [r'([Ѱѱ])алт([иы])', r'\1алт\2' + Oxia],
    # ѱалмы̀
    [r'([Ѱѱ])алм([аеѣы])\b', r'\1алм\2' + Varia],
    [r'([Ѱѱ])алмопѣ(?=в)', r'\1алмопѣ' + Oxia],

    [r'пꙋт([еѧ])(?=м[иъ])', r'пꙋт\1' + Oxia],
    [r'пꙋ(?=т(ь|ник))', r'пꙋ' + Oxia],

    # ра́ди
    [r'\b([Рр])а(?=ди\b)', r'\1а' + Oxia],
    # ра́дость ра́дꙋйсѧ ра́дꙋйтесь
    [r'([Рр])а(?=д(ост[ень]|ꙋй(сѧ|тесь)))', r'\1а' + Oxia],

    [r'пререка', r'пререка' + Oxia],
    # рѣ́чь
    [r'\bрѣ(?=ч[иь]|ам[иъ]\b)', r'рѣ' + Oxia],
    # речѐ
    [r'рече\b', r'рече' + Varia],
    # ре́клъ
    [r'(?<!мѧ)ре(?=кл?ъ)', r'ре' + Oxia],
    # рцы̀
    [r'рцы\b', r'рцы' + Varia],
    # рцы́те
    [r'рцы\B', r'рцы' + Oxia],

    # ро́дъ ро́дꙋ
    [r'ро(?=д[аеѣиꙋъ]\b)', r'ро' + Oxia],

    [r'\bри(?=з([аеоꙋы]))', r'ри' + Oxia],

    # рꙋ́сскїй
    [r'([Рр])ꙋ(?=сск)', r'\1ꙋ' + Oxia],
    # рѡссі́ѧ
    [r'([Рр])ѡссі(?!ѧн)', r'\1ѡссі' + Oxia],

    # [r'([Сс])вѣ(?=т)', r'\1вѣ' + Oxia],
    # [r'([Сс])вѣт([ъаꙋеѣ]|омъ|л(аѧ|о([еѣй]|мꙋ)|ꙋю|ый))\b', r''],

    # свѣ́тъ свѣ́тлый свѣ́та свѣ́телъ
    [r'''
        # ! (свѣтисѧ свѣтлейш. 
        # свѣтозарн. свѣтоподат.
        # свѣтоносн. свѣтѧщійсѧ)
        ([Сс])вѣ
        (?!
            т
            (
                и 
                |л
                    (
                        а\b
                        |[еѣ][ей]
                        #|о\B
                    ) 
                |о[дзлнп]
                |ѧ\B
            )

        )
        (?=т)
        ''',
     r'\1вѣ' + Oxia
     ],
    # свѣти́сѧ свѣти́льникъ свѣти́ло
    [r'([Сс])вѣти(?=л[оь]|сѧ)', r'\1вѣти' + Oxia],
    [r'([Сс])вѣтода(?=в)', r'\1вѣтода' + Oxia],
    [r'([Сс])вѣтоза(?=рн)', r'\1вѣтоза' + Oxia],
    [r'([Сс])вѣтоли(?=т)', r'\1вѣтоли' + Oxia],
    [r'([Сс])вѣтоно(?=с)', r'\1вѣтоно' + Oxia],
    [r'([Сс])вѣтопода(?=т)', r'\1вѣтопода' + Oxia],
    # свѣтлѣ́е свѣтлѣ́йшꙋю
    [r'([Сс])вѣтлѣ(?=[ей])', r'\1вѣтлѣ' + Oxia],

    # свѧ́тъ свѧ́те
    [r'([Сс])вѧ(?=т[аеѣиоѡꙋъы]\b)',
     r'\1вѧ' + Oxia],
    # свѧта́ѧ свѧте́й свѧтꙋ́ю свѧты́ѧ свѧти́тель
    [r'([Сс])вѧт(?P<ac>[аеѣиꙋы]\B)',
     r'\1вѧт\g<ac>' + Oxia],
    # свѧто́е
    [r'([Сс])вѧт(?P<ac>о)(?=[ейм])',
     r'\1вѧт\g<ac>' + Oxia],

    # свѧще́нникъ свѧще́нїе ѻ҆свѧще́нный
    [r'''
        ([Сс])вѧще
        (?=
            нн?
            (
                [аиіеѣꙋы]\B
                # ! свѧщеннолѣп- свѧщеннотайн-
                |о(?![дилт]|мон)
            )
        )
        ''',
     r'\1вѧще' + Oxia],
    # посвѧща̀ти
    [r'свѧща\B', r'свѧща' + Varia],
    [r'([Сс])вѧщꙋ\b', r'\1вѧщꙋ' + Varia],

    # сего̀
    [r'\b([Сс])его\b', r'\1его' + Varia],
    # се́й
    [r'\b([Сс])е(?=й\b)', r'\1е' + Oxia],
    # сеѧ̀ сїѐ
    [r'\b([Сс])(еѧ|іе)\b', r'\g<0>' + Varia],
    # сі́и
    [r'\b([Сс])і(?=и\b)', r'\1і' + Oxia],

    [r'селе(?=ні)', r'селе' + Oxia],

    [r'\bсе(?=мъ\b)', r'се' + Oxia],

    # сѣ́мо
    [r'\bсѣ(?=мо\b)', r'сѣ' + Oxia],
    # сѣ́нь
    [r'сѣ(?=н)', r'сѣ' + Oxia],

    [r'([Сс])е(?=рдц([ꙋы]|[ѣе](мъ)?))',
     r'\1е' + Oxia],
    # [r'([Сс])ердца\b', r'\1ердца' + Varia],  # от числа.
    [r'([Сс])ердца(?=м)', r'\1ердца' + Kamora],

    # сѣ́ть
    [r'\bсѣ(?=т)', r'сѣ' + Oxia],

    [r'([Сс])илꙋа(?=н)', r'\1илꙋа' + Oxia],
    # си́це
    [r'([Сс])и(?=це\b)', r'\1и' + Oxia],

    [r'си(?=рѣчь)', r'си' + Oxia],

    # скорбѧ́щемъ
    [r'\bскорбѧ(?=[мщ])', r'скорбѧ' + Oxia],
    # ско́рби (! скорбѧ́щ- )
    [r'\bско(?=рб(?!ѧ[мщ]))', r'ско' + Oxia],

    # славле́нїе
    [r'([Сс])лавл([ея])', r'\1лавл\2' + Oxia],
    # славосло́вїе
    [r'([Сс])лавосло(?=в)', r'\1лавосло' + Oxia],
    # сла́ва сла́внаѧ (! славле́н- славосло́в-)
    [r'([Сс])ла(?=в(?!ослов|л[ея]))',
     r'\1ла' + Oxia],

    # сле́зъ слеза̀ слеза́ми слезѧ́щи прослези́шасѧ
    [r'слез([аꙋ])\b', r'слез\1' + Varia],
    [r'сле(?=з(([ыъ])|н([аоꙋы])))', r'сле' + Oxia],
    [r'слеза(?=[мх])', r'слеза' + Oxia],
    [r'слезо(?=[йю])', r'слезо' + Oxia],
    [r'слезѧ(?=щ)', r'слезѧ' + Oxia],
    [r'слези(?=[хш])', r'слези' + Oxia],

    # смире́нїе смире́нно
    [r'смире(?=н(і|н(?!омꙋд)))', r'смире' + Oxia],
    # смиренномꙋ́дрый
    [r'смиренномꙋ(?=д)', r'смиренномꙋ' + Oxia],

    # снѣ́гъ снѣ́жный
    [r'снѣ(?!гам|жат)(?=[гж])', r'снѣ' + Oxia],
    [r'([Сс])офрѡ(?=н)', r'\1офрѡ' + Oxia],

    # стѣна̀
    [r'стѣн([аеѣоꙋы])\b', r'стѣн\1' + Varia],
    # стѣно́ю
    [r'стѣно(?=ю)', r'стѣно' + Oxia],
    # стра́ждꙋщїй стра́ждетъ
    [r'стра(?=жд(ꙋщ|е))', r'стра' + Oxia],

    [r'страда(?=[влнстхш])', r'страда' + Oxia],
    # стра́хъ стра́шный стра́се
    [r'стра(?=(х(?!ован)|ше?н|с[еѣ]))',
     r'стра' + Oxia],

    # стра́сть стра́сти
    [r'([Сс])тра(?=ст([иь]|но))', r'стра' + Oxia],
    # страсте́мъ страстѧ́хъ
    [r'([Сс])траст(?P<ac>[еѧ])(?=[ймх])',
     r'страст\g<ac>' + Oxia],
    # страстна́ѧ
    [r'([Сс])трастн(?P<ac>[аоꙋы])(?=[ейюѧ])',
     r'страстн\g<ac>' + Oxia],
    # страстоте́рпецъ
    [r'([Сс])трастоте(?=рп)', r'страстоте' + Oxia],

    # спа́съ спа́слъ спа́совъ спа́се спасе́нїе спасѝ спаси́тель спасо́шасѧ спаса́ти спасе́нъ спаса́ющїй
    [r'([Сс])пас[иꙋ]\b', r'\g<0>' + Varia],
    [r'([Сс])па(?=с([аеѣ]|л?ъ|овъ)\b)', r'\1па' + Oxia],
    [r'([Сс])пас([аеи])\B', r'\1пас\2' + Oxia],
    [r'([Сс])пасо(?!въ)\B', r'\1пасо' + Oxia],

    [r'([Сс])подо(?=би)', r'\1подо' + Oxia],

    # сы́нъ сыны̀ сы́номъ сы́не сыно́внїй сыново́мъ сыно́въ
    [r'\b([Сс])ыны\b', r'\1ыны' + Varia],
    [r'\b([Сс])ы(?=н([аеѣꙋъ]|омъ))', r'\1ы' + Oxia],
    [r'\b([Сс])ыно(?=в[нъ])', r'\1ыно' + Oxia],
    [r'\b([Сс])ыново(?=м)', r'\1ыново' + Oxia],
    [r'\b([Сс])ына(?=ми)', r'\1ына' + Oxia],

    # та́къ та́коже та́кѡ та́кожде
    [r'\b([Тт])а(?=к[ѡоъ](жд?е)?\b)', r'\1а' + Oxia],

    [r'\b([Тт])а(?=же\b)', r'\1а' + Oxia],
    [r'\b([Тт])а(?=ѧ(же)?)', r'\1а' + Oxia],
    [r'\b([Тт])ꙋ(?=ю(же)?)', r'\1ꙋ' + Oxia],
    [r'\b([Тт])ы(?=ѧ)', r'\1ы' + Oxia],

    # та́йна та́йнѣмъ та́йнымъ та́йномꙋ
    [r'та(?=йн([аеѣꙋы]|ом[ꙋъ]))', r'та' + Oxia],
    [r'та(?=ин(ъ|ство))', r'та' + Oxia],
    [r'таи(?=нни)', r'таи' + Oxia],

    [r'тва(?=рь)', r'тва' + Oxia],

    [r'\b([Тт])вое\b', r'\1вое' + Varia],
    [r'\b([Тт])во(е?ѧ)', r'\g<0>' + Varia],
    [r'\b([Тт])вою', r'\1вою' + Varia],
    [r'\b([Тт])вое(мꙋ|г[оѡ])', r'\g<0>' + Varia],
    [r'\b([Тт])вое(?=[йю])', r'\1вое' + Oxia],
    [r'\b([Тт])во(?=и([мх])ъ)', r'\1во' + Oxia],
    [r'\b([Тт])во(?=й)', r'\1во' + Oxia],
    [r'\b([Тт])еб([еѣ])', r'\1еб\2' + Varia],
    [r'\b([Тт])ѣ(?=мже)', r'\1ѣ' + Oxia],

    # тѣ́ло тѣ́лꙋ
    [r'\b([Тт])ѣ(?=л\w\b)', r'\1ѣ' + Oxia],
    # тѣле́сн-
    [r'\b([Тт])ѣле(?=сн)', r'\1ѣле' + Oxia],
    # тѣлесѝ
    [r'\b([Тт])ѣлеси\b', r'\1ѣлеси' + Varia],

    # тепло̀
    [r'\bтепло\b', r'тепло' + Varia],
    # те́плый те́плой
    [r'\bте(?=пл([аеѣыꙋ]|о(?!хл|т|\b)))', r'те' + Oxia],
    # теплота̀
    [r'\bтеплот[аеѣоꙋы]\b', r'\g<0>' + Varia],
    # теплото́ю
    [r'\bтеплото\B', r'теплото' + Oxia],
    # теплохла́дный
    [r'\bтеплохла(?=дн)', r'теплохла' + Oxia],

    # тлѣ́нъ тлѣ́нїе нетлѣ́нный тлѣ́ть
    [r'тлѣ(?=н[інъ]|т[иь])', r'тлѣ' + Oxia],
    # тобо́ю
    [r'\b([Тт])обо(?=ю)', r'\1обо' + Oxia],
    # то́кмѡ
    [r'то(?=кмѡ)', r'то' + Oxia],
    # Тро́ица
    [r'\b([Тт])ро(?=[ий][цч])', r'\1ро' + Oxia],
    # тьма̀ тьмѣ̀
    [r'\bтьм([аѣꙋы]\b)', r'тьм\1' + Varia],

    # ᲂу҆́бѡ
    [r'^([Оᲂ]у)(?=бѡ\b)', r'\1' + Iso],
    # ᲂу҆вы̀
    [r'^([Оᲂ]у)вы\b', r'\1вы' + Varia],
    # ᲂу҆́дъ ᲂу҆́ды
    [r'^([Оᲂ]у)(?=д[ыъ]\b)', r'\1' + Iso],
    # ᲂу҆миле́нїе ᲂу҆миле́ннный
    [r'^([Оᲂ]у)миле(?=н)', r'\1миле' + Oxia],
    # ᲂу҆́мъ ᲂу҆́мный ᲂу҆́мно ᲂу҆́ме
    [r'''
        ^
        ([Оᲂ]у)
        (?=
            м
            (
                [ъеѣ]\b # ᲂу҆́м ᲂу҆́ме
                |н
                (?!
                    [еѣ] # ! ᲂумнѣй-
                    |о\B # ! ᲂумножая
                )
            )
        )
        ''',
     r'\1' + Iso
     ],
    # ᲂу҆мы̀ ᲂу҆мꙋ̀
    [r'^([Оᲂ]у)м([аꙋы])\b', r'\1м\2' + Varia],

    # ᲂу҆мно́жить ᲂу҆мно́жꙋ
    [r'^([Оᲂ]у)мно(?=ж[иꙋ])', r'\1мно' + Oxia],
    # ᲂу҆множа́ти
    [r'^([Оᲂ]у)множа(?=\w)', r'\1множа' + Oxia],
    # ᲂу҆твердѝ
    [r'^([Оᲂ]у)тверди\b', r'\1тверди' + Varia],
    # ᲂу҆тверди́ша
    [r'^([Оᲂ]у)тверди\B', r'\1тверди' + Oxia],

    # ᲂу҆твержде́нный
    [r'^([Оᲂ]у)твержде(?=н)', r'\1твержде' + Oxia],
    # ᲂу҆твержда́еши
    [r'^([Оᲂ]у)твержда(?=\w)', r'\1твержда' + Oxia],

    # ᲂу҆тѣше́нїе
    [r'^([Оᲂ]у)тѣше(?=ні)', r'\1тѣше' + Oxia],
    # ᲂу҆тѣ́ши ᲂу҆тѣ́шꙋ ᲂу҆тѣ́шитель ᲂу҆тѣ́шивъ
    [r'''
        ^([Оᲂ]у)тѣ
        (?=
            ш
            (
                ([иꙋ]|енъ)\b
                |и
                (
                    тел
                    # ! ᲂу҆тѣши́тельный
                    (?!ьн) # ???  
                    |в
                ) 
            )
        )
        ''',
     r'\1тѣ' + Oxia
     ],

    # ᲂу҆тѣша́ти
    [r'^([Оᲂ]у)тѣша\B', r'\1тѣша' + Oxia],
    # ᲂу҆тѣши́тельный ???
    [r'^([Оᲂ]у)тѣши(?=тельн)', r'\1тѣши' + Oxia],

    [r'фарісе', r'фарїсе' + Oxia],

    [r'ходи(?=ша)', r'ходи' + Oxia],
    [r'([Хх])лѣ(?=б)', r'\1лѣ' + Oxia],

    # хрїсто́съ
    [r'([Хх])рісто(?=[вмс])', r'\1рїсто' + Oxia],
    # хрїста̀
    [r'([Хх])ріст([аеѣꙋ])\b', r'\1рїст\2' + Varia],

    # ца́рь ца́рскїй
    [r'([Цц])а(?=р([сь]))', r'\1а' + Oxia],
    # царю̀
    [r'([Цц])ар([иеѣюѧ])\b', r'\1ар\2' + Varia],
    # царе́ви
    [r'([Цц])ар([еє])\B', r'\1ар\2' + Oxia],
    # цари́ца
    [r'([Цц])ари(?=ц)', r'\1ари' + Oxia],

    # цвѣ́тъ цвѣ́те цвѣ́лъ цвѣ́томъ
    [r'''
        ([Цц])вѣ
        (?=
            (
                т
                (
                    [еѣꙋиъ]
                    |омъ
                )
            )\b
            |лъ
        )''',
     r'\1вѣ' + Oxia
     ],

    # це́рковь це́ркви
    [r'([Цц])е(?=рк(в(?!([аѧ]м|ей))|овь))', r'\1е' + Oxia],
    # церква́ми церквѧ́ми
    [r'([Цц])еркв([аѧ])(?=м)', r'\1еркв\2' + Oxia],
    # церкве́й
    [r'([Цц])еркве(?=й)', r'\1еркве' + Oxia],
    # церко́вный
    [r'([Цц])ерко(?=вн)', r'\1ерко' + Oxia],

    # человѣ́къ
    [r'([Чч])еловѣ(?=ч|к(?!олюб))', r'\1еловѣ' + Oxia],
    # человѣколю́бный
    [r'([Чч])еловѣколю(?=б)', r'\1еловѣколю' + Oxia],

    [r'([Чч])естнѣ(?=йш)', r'\1естнѣ' + Oxia],

    # чи́стый чи́стꙋю чи́стей чи́стилъ
    [r'([Чч])и(?=ст(?!от|ейш|илищ|итель))', r'\1и' + Oxia],
    # чистота̀
    [r'([Чч])истот([аеѣꙋы])\b', r'\1истот\2' + Varia],
    # чистото́ю
    [r'([Чч])истото(?=ю)', r'\1истото' + Oxia],
    # чисте́йшаѧ
    [r'([Чч])ист([еѣ])(?=йш)', r'\1ист\2' + Oxia],
    # ѡ҆чисти́тельный
    [r'([Чч])исти(?=тель)', r'\1исти' + Oxia],

    [r'\b([Юю])(?=же\b)', r'\1' + Iso],

    [r'\b([Ꙗꙗ])ви\b', r'\1ви' + Varia],
    [r'\b([Ꙗꙗ])ви\B', r'\1ви' + Oxia],
    [r'', r''],
    [r'', r''],
    [r'\b([Ꙗꙗ])(?=(ко)?же\b)', r'\1' + Iso],
    [r'\b([Ꙗꙗ])(?=кѡ\b)', r'\1' + Iso],

    # months
    [r'епте(?=мвріа)', r'епте' + Oxia],
    [r'ктѡ(?=вріа)', r'ктѡ' + Oxia],
    [r'ое(?=мвріа)', r'ое' + Oxia],
    [r'еке(?=мвріа)', r'еке' + Oxia],
    [r'([Іі])аннꙋа(?=ріа)', r'\1аннꙋа' + Oxia],
    [r'еврꙋа(?=ріа)', r'еврꙋа' + Oxia],
    [r'([Мм])а(?=рта)', r'\1а' + Oxia],
    [r'прі(?=ліа)', r'прі' + Oxia],
    [r'([Мм])а(?=іа)', r'\1а' + Oxia],
    [r'([Іі])ꙋ(?=[лн]іа)', r'\1ꙋ' + Oxia],
    [r'([Аа])(?=ѵгꙋста)', r'\1' + Iso],
)

# Выставить титла
regs_titles_set = (
    [r'(?<!ѵ)([Аа])нге(?=л)', r'\1гг' + titlo],
    [r'([Аа])посто(?=л)', r'\1п' + titlo_s],
    [r'([Бб])лагода(?=т)', r'\1лг' + titlo_d],
    [r'([Бб])лагосло(?=в)', r'\1лг' + titlo_s],
    [r'([Бб])ла(?=[гж])', r'\1л' + titlo],
    [r'''
        \b
        ([Бб])ог
        (?=
            [еꙋъ]
            |а\B(?![тщ])
            |о(?!родиц|хꙋл|мерз) # ???
        )
        ''',
     r'\1г' + titlo
     ],
    [r'([Бб])огородиц', r'\1ц' + titlo_d],
    [r'''
        \b
        ([Бб])ож
        (?=і|е(ств|\b))
        ''',
     r'\1ж' + titlo
     ],
    [r'\b([Бб])оз(?=ѣ)', r'\1з' + titlo],
    [r'([Вв])лады(?=[кчц])', r'\1л' + titlo_d],
    [r'\b([Гг])лагол', r'\1л' + titlo],
    [r'\b([Гг])ласъ', r'\1ла' + titlo_s],
    [r'\b([Гг])оспод', r'\1д' + titlo_s],
    [r'\b([Гг])оспо(?=ж)', r'\1п' + titlo_s],

    [r'\b([Дд])ави(?=д)', r'\1в' + titlo],

    # дѣва
    [r'''
        \b
        ([Пп]рисно)?
        ( 
            [Дд] 
        )
        (?P<remove> # <- указание удалить ударение
            ѣ
        )
        в
        (?=[аеѣиоꙋы])
        ''',
     r'\1\2в' + titlo
     ],

    [r'([Дд])ѣвс(?=тв)', r'\1в' + titlo_s],
    [r'\b([Дд])ен(?=ь)', r'\1н' + titlo],
    [r'\b([Дд])не(?=сь)', r'\1н' + titlo],
    [r'\b([Дд])ꙋх', r'\1х' + titlo],

    # !!! два титла
    [r'''
        \b
        ([Бб])о?г
        о?дꙋх''',
     r'\1г' + titlo + r'одх' + titlo
    ],

    [r'\b([Дд])ꙋш', r'\1ш' + titlo],
    [r'\b([Дд])ꙋс(?=[еѣ]\b)', r'\1с' + titlo],
    [r'\b([Єє])ѵанге(?=л)', r'\1ѵ' + titlo_g],
    [r'([Іі])ерꙋса(?=л)', r'\1ер' + titlo_s],
    [r'([Іі])зраи(?=л)', r'\1и' + titlo],
    [r'([Іі])исꙋ(?=с)', r'\1и' + titlo],
    [r'([Ии])мѧ(?=рек)', r'\1м' + titlo],
    [r'\b([Кк])рес(?=т)', r'\1р' + titlo_s],
    [r'\b([Мм])ар(?=(і[аеѣиюѧ]))',
     r'\1р' + titlo],

    # ма́терь ма́ти
    [r'''
        (?P<prefix>
            \b
            |
            (?:
                [Бб](?:г҃|ог)о
                |[Дд](?:ѣв|в҃)о
            )?
        )   
        (?P<m>[Мм])ат
        (?=
            и
            |ер
        )
        ''', r'\g<prefix>\g<m>т' + titlo
    ],
    [r'([Мм])ѣсѧц(?=ъ)', r'\1ц' + titlo_s],
    [r'([Мм])илосе(?=рд)', r'\1л' + titlo_s],
    [r'([Мм])илос(?=т)', r'\1л' + titlo_s],
    [r'([Мм])оли(?=тв)', r'\1л' + titlo],
    [r'мꙋд(?=р)', r'м' + titlo_d],
    [r'([Мм])ꙋче(?=ни[кчц])', r'\1ч' + titlo],
    [r'([Мм])ладе(?=не?[чц])', r'\1л' + titlo_d],
    [r'\b([Нн])еб(?=\w\b)', r'\1б' + titlo],
    [r'\b([Нн])ебес(?=н)', r'\1б' + titlo_s],
    [r'\b([Нн])едѣл', r'\1л' + titlo_d],
    [r'([Нн])ын(?=ѣ)', r'\1н' + titlo],
    [r'([Ѻѻ])те?ц', r'\1ц' + titlo],  # @@@ вариат.
    [r'([Ѻѻ])те?ч(?!ест)', r'\1ч' + titlo],  # @@@ вариат.
    [r'([Пп])равед(?=е?н)', r'\1рв' + titlo_d],
    [r'([Пп])реподо(?=б(е?н))', r'\1рп' + titlo_d],
    [r'([Пп])ред(?=теч)', r'\1р' + titlo_d],
    [r'([Пп])рис(?=нѡ\b)', r'\1р' + titlo_s],
    [r'([Пп])ро(?=ро[кч])', r'\1р' + titlo_o],
    [r'([Рр])ождес(?=тв)', r'\1ж' + titlo_s],
    [r'([Сс])вѧ([тщ])', r'\1\2' + titlo],
    [r'([Сс])ерде?(?=[цч])', r'\1р' + titlo_d],
    # FIXME: смр҃ть (??? вариант см҃рть)
    [r'([Сс])мер(?=т)', r'\1мр' + titlo],
    [r'([Сс])па(?=с)', r'\1п' + titlo],

    # страсть
    [r'''
        ([Сс])тр
        (?P<remove>
            а
        )
        с(?=т)
        ''', r'\1тр' + titlo_s
    ],
    [r'([Сс])ын(?=[аеєѣоꙋъ])', r'\1н' + titlo],  # @@@ вариат.
    [r'([Тт])рои(?=[цч])', r'\1р' + titlo_o],
    [r'([Хх])ріс(?=т)', r'\1р' + titlo_s],
    [r'([Чч])ело(?=вѣ[кч])', r'\1л' + titlo],
    [r'([Чч])ес(?=тн)', r'\1' + titlo_s],
    [r'([Чч])ис(?=т)', r'\1' + titlo_s],
    [r'([Цц])арс', r'\1р' + titlo_s],
    [r'([Цц])ар(?=\w)', r'\1р' + titlo],
    [r'([Цц])ер(?=к)', r'\1р' + titlo],
)

# Раскрыть титла
regs_titles_open = (
    [r'([Аа])гг' + titlo, r'\1нге'],
    [r'([Аа])п' + titlo_s, r'\1посто'],
    [r'([Бб])л' + titlo + r'([гж])', r'\1ла\2'],
    [r'([Бб])лг' + titlo_d, r'\1лагода'],
    [r'([Бб])лг' + titlo_s, r'\1лагосло'],
    [r'([Бб])([гжз])' + titlo, r'\1о\2'],
    [r'([Бб])ц' + titlo_d, r'\1огородиц'],
    [r'([Вв])л' + titlo_d, r'\1лады'],
    [r'\b([Гг])л' + titlo, r'\1лагол'],
    [r'\b([Гг])ла' + titlo_s, r'\1ласъ'],
    [r'\b([Гг])д' + titlo_s, r'\1оспод'],
    [r'\b([Гг])п' + titlo_s + r'ж', r'\1оспож'],
    [r'\b([Дд])в' + titlo + r'д', r'\1авид'],
    [r'\b([Дд])в' + titlo + r'(?=[аеѣиоꙋы])', r'\1ѣв'],
    [r'([Дд])в' + titlo_s + r'(?=тв)', r'\1ѣвс'],
    [r'\b([Дд])н' + titlo + r'(?=ь)', r'\1ен'],
    [r'\b([Дд])н' + titlo + r'(?=сь)', r'\1не'],
    [r'([Дд])х' + titlo, r'\1ꙋх'],
    [r'\b([Дд])ш' + titlo, r'\1ꙋш'],
    [r'\b([Дд])с' + titlo + r'(?=[еѣ]\b)', r'\1ꙋс'],
    [r'\b([Єє])ѵ' + titlo_g + r'(?=л)', r'\1ѵанге'],
    [r'([Іі])ер' + titlo_s + r'(?=л)', r'\1ерꙋса'],
    [r'([Іі])и' + titlo + r'(?=л)', r'\1зраи'],
    [r'([Іі])и' + titlo + r'(?=с)', r'\1исꙋ'],
    [r'([Ии])м' + titlo + r'(?=рек)', r'\1мѧ'],
    [r'\b([Кк])р' + titlo_s + r'(?=т)', r'\1рес'],
    [r'\b([Мм])р' + titlo + r'(?=(і[аеѣиюѧ]))', r'\1ар'],
    [r'([Мм])т' + titlo + r'(?=и|ер)', r'\1ат'],
    [r'([Мм])ц' + titlo_s + r'(?=ъ)', r'\1ѣсѧц'],
    [r'([Мм])л' + titlo_d + r'(?=не?[чц])', r'\1ладе'],
    [r'([Мм])л' + titlo_s + r'(?=рд)', r'\1илосе'],
    [r'([Мм])л' + titlo_s + r'(?=т)', r'\1илос'],
    [r'([Мм])л' + titlo + r'(?=тв)', r'\1оли'],
    [r'м' + titlo_d + r'(?=р)', r'мꙋд'],
    [r'([Мм])ч' + titlo + r'(?=н)', r'\1ꙋче'],
    [r'\b([Нн])б' + titlo + r'(?=\w\b)', r'\1еб'],
    [r'\b([Нн])б' + titlo_s + r'(?=н)', r'\1ебес'],
    [r'\b([Нн])л' + titlo_d, r'\1едѣл'],
    [r'([Нн])н' + titlo + r'(?=ѣ)', r'\1ын'],
    [r'([Ѻѻ])ц' + titlo + r'(?=ъ)', r'\1тец'],
    [r'([Ѻѻ])ц' + titlo + r'(?=[аеєѣоꙋы])', r'\1тц'],
    [r'([Ѻѻ])ч' + titlo + r'(?=ес|н)', r'\1теч'],  #
    [r'([Ѻѻ])ч' + titlo, r'\1тч'],  #
    [r'([Пп])рв' + titlo_d + r'(?=е?н)', r'\1равед'],
    [r'([Пп])рп' + titlo_d + r'(?=б(е?н))', r'\1реподо'],
    [r'([Пп])р' + titlo_d + r'(?=теч)', r'\1ред'],
    [r'([Пп])р' + titlo_s + r'(?=нѡ\b)', r'\1рис'],
    [r'([Пп])р' + titlo_o + r'(?=ро[кч])', r'\1ро'],
    [r'([Рр])ж' + titlo_s + r'(?=тв)', r'\1ождес'],
    [r'([Сс])([тщ])' + titlo, r'\1вѧ\2'],
    [r'([Сс])р' + titlo_d + r'(?=цъ\b|чн)', r'\1ерде'],
    [r'([Сс])р' + titlo_d + r'(?=ц)', r'\1ерд'],
    [r'([Сс])мр' + titlo + r'(?=т)', r'\1мер'],
    [r'([Сс])п' + titlo + r'(?=с)', r'\1па'],
    [r'([Сс])тр' + titlo_s + r'(?=т)', r'\1трас'],
    [r'([Сс])н' + titlo + r'(?=[аеєѣоꙋъ])', r'\1ын'],  # @@@ вариат.
    [r'([Тт])р' + titlo_o + r'(?=[цч])', r'\1рои'],
    [r'([Хх])р' + titlo_s + r'(?=т)', r'\1ріс'],
    [r'([Чч])л' + titlo + r'(?=вѣ[кч])', r'\1ело'],
    [r'([Чч])' + titlo_s + r'(?=тн)', r'\1ес'],
    [r'([Чч])' + titlo_s + r'(?=т)', r'\1ис'],
    [r'([Цц])р' + titlo_s, r'\1арс'],
    [r'([Цц])р' + titlo + r'(?=\w\b)', r'\1ар'],
    [r'([Цц])р' + titlo + r'(?=иц)', r'\1ар'],
    [r'([Цц])р' + titlo + r'(?=к)', r'\1ер'],
)

# TODO: стат. анализ словаря
regs_acutes_morph = (
    # при анализе словаря
    # https://www.ponomar.net/files/wordlist.tsv
    # можно выбрать буквосочетания
    # с ударениями а также определить исключения, если их немного
    # например для -лѧю[щт]- одно исключение
    # 5     1     лѧ̑ющ     лѧющ (и҆спра́влѧюще )
    # 130   0     лѧ́ют     лѧют
    # 593   1     лѧ́ющ     лѧющ (и҆спра́влѧюще )
    #
    # 1 ст. - кол-во совпадений в словаре
    # выбранного фрагмента (3-й ст.)
    # 2 ст. - кол-во совпадений в словаре
    # для выбранного фрагмента, но без ударения (4-й ст.)
    # в скобках - полное слово для совпадения
    # (одно, в данном случае общее для -лѧ̑ющ- и -лѧ́ющ-)
)

# compiled regexes sets
regs_letters_in_word_compiled = []
regs_acutes_compiled = []
regs_titles_set_compiled = []
regs_titles_open_compiled = []


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
        o_cursor.CharColor = self.color
        o_cursor.CharWeight = self.bold
        o_cursor.CharPosture = self.italic


class Letter:
    # одна буква с надстрочниками и др. атрибутами
    def __init__(self, char, superscript=''):
        # TODO: разобраться с ООП-подходом
        # уточнить что и как передается и меняется
        self.char = char
        self.superscript = superscript  # надстрочник
        # вид ударения ['varia', 'oxia', 'kamora']
        self.acute = self.get_acute()
        self.is_acuted = self.get_acute_flag()  # есть ли знак ударения
        # TODO: ??? м.б. разделить оксию варию и камору?
        self.have_zvatelce = self.get_zvatelce_flag()
        self.have_erok = False  # COMBINED !!!
        self.is_first = False
        self.is_last = False
        self.is_consonate = False  # согласная
        self.is_vowel = False  # гласная
        # ук, от?, ї с кендемой, ижица с дв. ударением
        self.is_combined = False
        self.titlo = ''  # титло
        self.is_titled = False  # имеет титло
        self.have_superscript = self.get_superscript_flag()

        # TODO: проверка порядка следования для исо и апострофа

    def get_full_list(self):
        letter_with_superscripts = [self.char]
        if self.have_superscript:
            letter_with_superscripts.append(self.superscript)
        return letter_with_superscripts

    def get_full_letter(self):
        letter_with_superscripts = self.char
        if self.have_superscript:
            letter_with_superscripts += self.superscript
        return letter_with_superscripts

    def get_acute_flag(self):
        for _acute in Oxia, Varia, Kamora:
            if self.superscript.find(_acute) >= 0:
                return True
        return False

    def get_acute(self):
        acute = ''
        for _acute in Oxia, Varia, Kamora:
            if self.superscript and self.superscript.find(_acute) >= 0:
                acute = _acute
        return acute

    def get_zvatelce_flag(self):
        if self.superscript.find(Zvatelce) >= 0:
            return True
        return False

    def get_titlo_flag(self):
        for _titlo in titles:
            if self.superscript.find(_titlo) >= 0:
                return True
        return False

    def get_superscript_flag(self):
        if self.get_acute_flag() \
                or self.is_combined \
                or self.get_zvatelce_flag() \
                or self.is_titled \
                or self.superscript:
            return True
        return False


class LettersPacked(list):
    def __init__(self, letters):
        super().__init__(letters)
        # self.unpacked = self.unpack()

    def unpack(self):
        # из списка letters  получает строку
        # с ударениями
        # print(self)
        string = ''
        for l in self:  # .packed:
            string += l.char
            # if l.have_superscript:
            if l.get_superscript_flag():
                string += l.superscript

        return string

    def get_text_layer(self):
        text_layer = []
        for l in self:  # .packed:
            text_layer.append(l.char)
        return text_layer

    def get_superscripts_layer(self):
        superscripts_layer = []
        for l in self:  # .packed:
            if l.get_superscript_flag():
                superscripts_layer.append(l.superscript)
            else:
                superscripts_layer.append('')
        return superscripts_layer

    def get_text_layer_string(self):
        return ''.join(self.get_text_layer())

    def get_text_anacuted(self):
        # текст без ударений и звательца
        anacuted = ''
        for l in self:
            anacuted += l.char
            if not (l.is_acuted or l.have_zvatelce):
                anacuted += l.superscript
        return anacuted

    def imposing(self, packet_converted):
        # совершает послойное наложение двух packet :
        # исходного и измененного (converted).
        # Возвращает измененный packet.
        # дете́й + дѣт => дѣте́й
        # свѧты́й + ст҃ый => ст҃ы́й

        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()
        # print(_string, _string_converted)
        packed_imposed = self
        for i in range(len(packet_converted)):
            # изменяем текст

            l = packet_converted[i]
            char_conv = l.char
            super_conv = l.superscript
            super = packed_imposed[i].superscript
            if char_conv != '':
                packed_imposed[i].char = char_conv
            # изменяем надстрочники
            if super_conv != '':
                # условия наложения надстрочников (кендема, исо, апостроф)
                # при накладывании кендемы на ударение - ударение не меняется

                # TODO: если у источника звательце у replaced - оксия|вария
                # вариант 1: сразу заменить на Исо|Апостроф

                if not (
                        super in acutes
                        and super != ''
                        and super_conv == Kendema
                ):
                    packed_imposed[i].superscript = super_conv

        return packed_imposed

    def imposing_nonequal(self, packet_converted, match, replace_expanded):
        # для случая когда replace != find [и есть ударение]
        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()
        packed_source = self
        replaced_expanded_text = \
            Word(replace_expanded).pack().get_text_layer_string()

        # если find > replace (от -> ѿ)
        if len(match.group(0)) > len(replaced_expanded_text):
            # print("=== F>R")
            # print("=== " + match.group(0), replaced_expanded_text)
            # print('===', match.span(0), match.start(), match.end(), '(span)')

            # определить кол-во удаляемых символов
            to_remove_amount = len(match.group(0)) - len(replaced_expanded_text)
            # print('=== ', to_remove_amount, 'to_remove_amount')
            # определить позицию удаляемых символов
            # TODO: попробовать оставить фрагмент, в котором есть ударение
            # можно определить метод для поиска и замены с указанием
            # дополнительно - имя группы и позицию в ней символа с ударением
            # fr(find, rerplace, (group_name, pos))
            # fr(r'(?<acute>у)мъ', r'ᲂу҆́мъ', (acute,0))
            # удаляются n символов после первого
            # первый и остальные заменяются обычным наложением
            # print('!!! ', to_remove, '<= to_remove')
            to_remove_start = match.start()

            # Возможен случай, когда ударение исходного фрагмента
            # наложится на новый, когда усечение
            # не затронет саму ударную гласную.
            # (Возможно и для других надстрочников?)
            # Вариант решения - отметить в regex букву
            # именованным сохранением <remove>
            # При обработке удалить перед наложением
            # у этого символа надстрочник.

            # если в regex указана группа 'remove'
            if match.groupdict():
                if 'remove' in match.groupdict().keys():
                    to_remove_pos = match.start('remove')
                    packed_source[to_remove_pos].superscript = ''

            # получить список удаляемых эл-в
            to_remove_list = []
            for i in range(to_remove_amount):
                # print("--- ", i, to_remove_start+1+i, _string[to_remove_start+1+i], ' удалится')
                to_remove_list.append(to_remove_start + 1 + i)
            # обратить список
            to_remove_list.reverse()
            # удалить элементы, начиная с конца
            # (иначе удаление элементов сдвинет последующие индексы)
            for i in to_remove_list:
                packed_source.pop(i)
            # print("--- ", packed_source.unpack(), '(после удаления)')
            # print("--- ", packet_converted.unpack(), '(новая)')

            if len(packed_source) == len(packet_converted):
                # применить обычное наложение
                packed_source.imposing(packet_converted)

        # если find < replace (умъ -> ᲂумъ)
        # цель 1: вставить нужное кол-во букв
        # цель 2: сохранить ударение (если оно было в исх. слове)
        # Определить позицию и кол-во вставленных букв.
        # через match.group(0) match.start(0), match.end(0) и replace_expanded
        # если match.group(0) имел ударение
        #   попробовать найти позицию для ударной буквы в новом фрвгменте
        #   попробовать определить автоматически,
        #   по букве, если есть совпадение в процессе сравнивания F & R
        #   попробовать найти совпадение F и R с начала и с конца.
        #   ум -> оум - совпадение с конца.
        #   ум -> оум : накладываем с конца. 'ум' => 'муо'
        #
        if len(match.group(0)) < len(replaced_expanded_text):
            # print("=== F<R")
            # print("=== " + match.group(0), replaced_expanded_text)
            # print('===', match.span(0), match.start(), match.end())
            # определить кол-во добавляемых символов
            to_add_amount = len(replaced_expanded_text) - len(match.group(0))
            # print('===', to_add_amount)
            # определить позицию добавляемых символов
            # можно попробовать определить фрагмент с ударением
            to_add_start = match.start()
            to_add_list = []
            for i in range(to_add_amount):
                to_add_list.append((to_add_start + 1 + i, _string_converted[to_add_start + 1 + i]))

            # обратить список
            to_add_list.reverse()
            # print(to_add_list)
            # вставить элементы, начиная с конца
            # (иначе вставка элементов сдвинет последующие индексы)
            for i, l in to_add_list:
                packed_source.insert_char(i, l)

            if len(packed_source) == len(packet_converted):
                # применить обычное наложение
                packed_source.imposing(packet_converted)

        return packed_source

    def regex_sub(self, regex_tuple):
        _string = self.get_text_layer_string()

        converted_packet = self

        r, replace = regex_tuple

        _string_replaced, match, replace_expanded = \
            get_search_and_replaced(_string, r, replace)
        if match:
            # result of S&R -> to packet
            replaced_packet = \
                Word(_string_replaced).pack()
            replaced_expanded_text = \
                Word(replace_expanded).pack().get_text_layer_string()

            # impose s&r and source
            if len(replaced_expanded_text) == \
                    len(match.group(0)):
                converted_packet = \
                    self.imposing(replaced_packet)
            else:
                converted_packet = \
                    self.imposing_nonequal(replaced_packet, match, replace_expanded)

        return converted_packet

    def replace_char(self, find, replace):
        packet = self
        for l in packet:
            if l.char == find:
                l.char = replace
        return packet

    def insert_char(self, pos=0, char='', superscript=''):
        # вставляет в позицию pos букву [с надстрочником]
        _letter_inserted = Word(char).pack()[0]
        _letter_inserted.superscript = superscript
        new_packet = self
        new_packet.insert(pos, _letter_inserted)

        return new_packet

    def append_char(self, char='', superscript=''):
        # вставляет в конец букву [с надстрочником]
        _letter_inserted = Word(char).pack()[0]
        _letter_inserted.superscript = superscript
        new_packet = self
        new_packet.append(_letter_inserted)

        return new_packet


class Word:
    # слово с предшеств. и послед. символами

    def __init__(self, string):
        self.string = str(string)
        self.stripped = self.get_text_stripped()
        self.packet = self.pack()  # LettersPacked

    def get_pref_symbols(self):
        # проверка на символы перед буквами - кавычки, кавыки и т.д.
        # TODO: обработка знака "тысяча"
        pat = r'^(?P<pref_symbols>[^' + cu_letters_with_superscripts + r']+)(?=[' + cu_letters_with_superscripts + r'])'
        re_obj = re.compile(pat, re.U | re.X)
        match = re_obj.search(self.string)
        if match:
            return match.group('pref_symbols')

    def get_post_symbols(self):
        # проверка на символы после букв - пунктуация, кавычки, кавыки и т.д.
        pat = r'(?<=[' + cu_letters_with_superscripts + r'])(?P<post_symbols>[^' + cu_letters_with_superscripts + r']+)$'
        re_obj = re.compile(pat, re.U | re.X)
        match = re_obj.search(self.string)
        if match:
            return match.group('post_symbols')

    def get_text_stripped(self):
        # получить текст без пре- и -пост символов
        stripped = self.string
        stripped = stripped.strip(self.get_pref_symbols())
        stripped = stripped.strip(self.get_post_symbols())
        return stripped

    def get_text_unstripped(self, string):
        unstripped = string
        _pre = self.get_pref_symbols() if self.get_pref_symbols() else ''
        _post = self.get_post_symbols() if self.get_post_symbols() else ''
        return _pre + unstripped + _post

    def pack(self):
        # разбивает слово string на объекты класса Letters
        # вместе с самой буквой - флаги и значения надстрочников и т.д.
        packed = LettersPacked([])
        string = self.get_text_stripped()

        string_length = len(string)
        for i in range(string_length):
            _letter = Letter(string[i])
            _char = _letter.char
            if i == 0:
                _letter.is_first = True

            if _char in cu_letters_text:  #
                # если текущий символ - буква, поместить в packed
                packed.append(_letter)

            elif _char in cu_superscripts:
                # если текущий символ - надстрочник
                # выставить флаг и занести символ

                # предыдущая буква, к которой принадежит надстрочник,
                # (уже занесенная в packed)
                prev_letter = packed[-1]  # last

                prev_letter.have_superscript = True
                prev_letter.superscript += _char  # если двойной то добавить к уже имеющемуся
                # TODO: обработка ошибки когда надстр-к после звательца не оксия или вария
                # то есть добавлять после звательца только оксию или варию
                # также ошибка если оксия после кендимы у i - она должна заменять ее

                if _char == Zvatelce:
                    # если звательце,
                    # выставить у предыдущей буквы флаг
                    prev_letter.have_zvatelce = True
                elif _char in acutes:
                    # если ударение,
                    # выставить у предыдущей буквы флаг и символ ударения
                    prev_letter.is_acuted = True  # флаг и
                    prev_letter.acute = _char  # тип ударения
                    # TODO: ??? м.б. разделить оксию варию и камору
                    # TODO: обработка ошибки когда вместе два разных ударения
                elif _char in titles:
                    # если титло, выставить у предыдущей буквы флаг и титло
                    prev_letter.is_titled = True
                    prev_letter.titlo = _char
                elif _char == erok_comb:
                    # если ерок combined, выставить флаг.
                    prev_letter.have_erok = True
                elif _char == Kendema:
                    prev_letter.superscript = Kendema
            else:
                # TODO: другие символы: тире, подчеркивание etc
                # TODO: обработка знака "тысяча" (должен быть в self.pref_symbols)
                packed.append(_letter)

        return packed

    def get_converted(self, titles_flag='off'):
        '''Возвращает преобразованное набором конвертеров слово (как unpack-текст с надстрочниками)

         общий подход
         За исключением замен некотрых отдельных букв (ъ, от, у, я)
         1. Получить текст без надстрочников (текстовый слой).
         2. Обработать его поиском и заменой (regex, (str.replace?)).
         TODO: м.б. выражение find в regex также запаковать
         и взять только текстовый слой, чтобы можно
         указать в find слова ка кесть с надстрочниками
         напр. с ї
         3. Полученный измененный результат необходимо
         "запаковать" в LettersPacked (в нем могут быть надстрочники).
         4. Полученный временный (replaced) пакет
         накладывается отдельно по слоям на исходный пакет
         через imposing(packet_converted)
         результатом будет новый packet (imposed)
         5. получить его "распакованную" строку
         с помощью .unpack
        '''

        # отдельные буквы ꙋ ᲂу ѡ ѿ ꙗ ѧ є ъ ѽ
        converted_packet = \
            self.convert_separate_letters()

        # Преобразование через imposing

        # Буквы в слове,
        converted_packet = \
            self.perlacer_by_regex_set(regs_letters_in_word_compiled)
        # Ударения
        converted_packet = \
            self.perlacer_by_regex_set(regs_acutes_compiled)

        # Титла
        if titles_flag == 'on':
            # Выставить титла
            converted_packet = \
                self.perlacer_by_regex_set(regs_titles_set_compiled)

        converted_text = \
            self.get_text_unstripped(converted_packet.unpack())

        return converted_text

    def convert_separate_letters(self):
        """В исходном packet конвертирует отдельные буквы"""

        packet = self.packet
        c = packet.unpack()

        last_symbol = c[-1]

        # ъ в конце
        if last_symbol in cu_before_er:
            _er = 'ъ' if last_symbol.islower() else 'Ъ'
            packet.append(Letter(_er))

        # е в начале слова
        if packet[0].char == 'е':
            packet[0].char = 'є'
        if packet[0].char == 'Е':
            packet[0].char = 'Є'

        # все у -> ꙋ
        packet = packet.replace_char('у', 'ꙋ')
        packet = packet.replace_char('У', 'Ꙋ')
        # ꙋ -> ᲂу
        if packet[0].char == 'ꙋ':
            packet.pop(0)
            packet.insert(0, Letter('у'))
            packet.insert(0, Letter(unicNarrowO))
            packet[1].superscript = Zvatelce
        if packet[0].char == 'Ꙋ':
            packet.pop(0)
            packet.insert(0, Letter('у'))
            packet.insert(0, Letter('О'))
            packet[1].superscript = Zvatelce

        # все я -> ѧ
        packet = packet.replace_char('я', 'ѧ')
        packet = packet.replace_char('Я', 'Ѧ')
        # е в начале слова
        if packet[0].char == 'ѧ':
            packet[0].char = 'ꙗ'
        if packet[0].char == 'Ѧ':
            packet[0].char = 'Ꙗ'

        return packet

    def perlacer_by_regex_set(self, regex_tuples_set):
        '''Заменяет текст по всем regexes из принятого набора

        '''

        packet = self.packet
        for regex_tuple in regex_tuples_set:
            packet = packet.regex_sub(regex_tuple)
        return packet


def get_search_and_replaced(s, r, replace):
    # вместе с измененной строкой new_string возвращает
    # match и replace expanded
    new_string = s  # действует как фильтр
    replace_expanded = ''
    re_obj = r

    match = re_obj.search(s)
    if match:
        new_string = re_obj.sub(replace, s)
        replace_expanded = match.expand(replace)
    return new_string, match, replace_expanded


def make_compiled_regs(list_regs):
    list_compiled = []
    for reg_tuple in list_regs:
        flags = reg_tuple[2] if len(reg_tuple) > 2 else ''
        if flags and flags.count('i') > 0:
            re_compile = re.compile(reg_tuple[0], re.U | re.X | re.I)
        else:
            re_compile = re.compile(reg_tuple[0], re.U | re.X)
        list_compiled.append((re_compile, reg_tuple[1]))
    return list_compiled


def get_string_converted(string, titles_flag='off'):
    '''Конвертирует переданную строку

    :param string: строка (параграфа)
    :param titles_flag: титла - [on|off*|open].
        on - ставить титла.
        off - не ставить (по умолч.)
        open - раскрыть титла.
    :return: прреобразованная строка
    '''

    strings_converted = []

    # разбить строку по пробельным символам
    # TODO: отследить неразрывный пробел.
    # Возможно разбивать на слова в LOffice
    # здесь обрабатывать только слова

    # init compiled regexes sets

    global regs_letters_in_word_compiled
    global regs_acutes_compiled
    global regs_titles_set_compiled
    global regs_titles_open_compiled

    regs_letters_in_word_compiled = make_compiled_regs(regs_letters_in_word)
    regs_acutes_compiled = make_compiled_regs(regs_acutes)
    regs_titles_set_compiled = make_compiled_regs(regs_titles_set)
    regs_titles_open_compiled = make_compiled_regs(regs_titles_open)

    pat_titles = r'[' + titles + ']'
    re_titled = re.compile(pat_titles, re.U | re.X)
    pat_superscripts = r'[' + Zvatelce + acutes + ']'
    re_superscript = re.compile(pat_superscripts, re.U | re.X)

    for w in string.split():
        # конвертация отдельного слова
        converted_string = w
        word_is_titled = False

        # Предварительная оработка для раскрытия титла
        if titles_flag == 'open':
            # удалить другие надстрочники
            # (чтобы соответсвовать строкам в regex_set)
            if re_superscript.search(w):
                w = re_superscript.sub('', w)
            # Если в слове есть титло
            if re_titled.search(w):
                word_is_titled = True
                for r, replace in regs_titles_open_compiled:
                    if r.search(w):
                        w = r.sub(replace, w)

        # Основная конвертация
        # при опции 'раскрытие титла' обработка только слов с титлами
        if titles_flag != 'open' or word_is_titled:
            word = Word(w)
            converted_string = word.get_converted(titles_flag=titles_flag)

        # слова - в массив
        strings_converted.append(converted_string)

    # массив в строку
    return ' '.join(strings_converted)


# ============================================

# -------------------------------------
# only for debug (now)
def msg(message, title=''):
    v_doc = XSCRIPTCONTEXT.getDesktop().getCurrentComponent()
    parent_window = v_doc.CurrentController.Frame.ContainerWindow
    box = parent_window.getToolkit().createMessageBox(parent_window, MESSAGEBOX, BUTTONS_OK, title, message)
    box.execute()
    return None


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


# button url
# vnd.sun.star.script:onik.py$onik?language=Python&location=user

# lists the scripts, that shall be visible inside OOo. Can be omitted, if
# all functions shall be visible, however here getNewString shall be suppressed
g_exportedScripts = onik, onik_titled, onik_titles_open,  ucs_convert_from_office,  # UCSconvert_from_shell,
