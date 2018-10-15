# _*_ coding: utf-8
"""
Модуль содержит функции для обработки текста на церковно-славянском языке.

Интерфейсные функции:
---------------------
onik, onik_titled, ucs_convert_from_office, ucs_convert_from_shell
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
    python-скрипту из OO-библиотеки напрямую. Поэтому такая вложенность.
    Сохранение и закрытие обработанного документа совершается средствами OOBasic.


2. Приведение орфографии русского или смешанного рус\цся текста
к ЦСЯ-форме.
    - Заменяются буквы: у я о е, и прочие.
    - Выставялется звательце.
    - В некоторых словах выставляются ударения.
    - В некотрых словах выставляются титла (опционально).
    Исходный текст - в Ponomar Unicode
    Обрабатывается только открытый документ (все равно требуется ручная доводка)

    NB: Оказалось, что срочно нужно набрать много новых (и обработать старых) цся-текстов,
    и на то, чтобы освоить CU ChSlav-раскладку для относительно скоростного набора, нужно время.
    Поэтому были написаны подобные функции. Текст набирается в обычной русской раскладке,
    потом обрабатывается этим скриптом :-) Далее конечно руками.

2.1 onik
--------
    Текст обрабатывается поабзацно для всего документа,
    и через текстовый курсор для выделенного фрагмента.
    Основная функция обработки onik_search_and_replace(string, istitled)
    перенесена из perl-скрипта, который обрабатывал TXT файл
    обычным для себя способом - серией s/find/replace/g


2.2 onik_titled
--------------------
    То же, что и onik, только выставляются некотрые титла.

2.3 (TODO) onik_untitled
    То же, что и onik, только раскрываются некотрые титла.
"""

import re
import uno
# import unohelper

#  для Msg() - для отладки.
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
#----------------------------------------------------------


""" part of OO code. No need (yet)
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
"""

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


ftUcsTriodionToUnicode = {
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

ftUcsOrthodoxTTToUnicode = {
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

ftUcsOrthodoxTTCapsToUnicode = {
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

ftUcsOrthodoxeRoosToUnicode = {
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

ftUcsOrthodoxDigitsLooseToUnicode = {
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

ftUcsOrthodoxLooseToUnicode = {
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

ftUstavToUnicode = {
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

ftValaamToUnicode = {
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

ftHirmosPonomarToPonomarUnicode = {
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

ftIrmologionToUnicode = {
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


# -------------------------------------
# only for debug (now)
def Msg(message, title=''):
    vDoc = XSCRIPTCONTEXT.getDesktop().getCurrentComponent()
    parentwin = vDoc.CurrentController.Frame.ContainerWindow
    box = parentwin.getToolkit().createMessageBox(parentwin, MESSAGEBOX, BUTTONS_OK, title, message)
    box.execute()
    return None


def get_font_table(f):
    """return fonttable-set"""
    if f in {"Triodion Ucs", "Triodion ieUcs", "Triodion Ucs1", "Hirmos Ucs", "Hirmos Ucs1"}:
        return ftUcsTriodionToUnicode
    elif f in {"Orthodox.tt Ucs8", "Orthodox.tt Ucs81",
               "Orthodox.tt Ucs8 tight", "Orthodox.tt Ucs8 tight1",
               "Orthodox.tt ieUcs8", "Orthodox.tt ieUcs81",
               "Irmologion Ucs", "Irmologion Ucs1",
               "Irmologion Ucs2"}:
        return ftUcsOrthodoxTTToUnicode
    elif f in {"Orthodox.tt Ucs8 Caps", "Orthodox.tt Ucs8 Caps tight", "Orthodox.tt ieUcs8 Caps"}:
        return fnUcsOrthodoxTTCapsToUnicode
    elif f in {"Orthodox.tt eRoos", "Orthodox_tt eRoos", "Orthodox.tt eRoos1", "Orthodox.tt ieERoos",
               "Orthodox.tt ieERoos1"}:
        return ftUcsOrthodoxeRoosToUnicode
    elif f in {"OrthodoxDigitsLoose", "OrthodoxDigits", "OrthodoxDigits1"}:
        return ftUcsOrthodoxDigitsLooseToUnicode
    elif f in {"OrthodoxLoose", "Orthodox"}:
        return ftUcsOrthodoxLooseToUnicode
    elif f in {"Ustav", "Ustav1"}:
        return ftUstavToUnicode
    elif f in {"Valaam", "Valaam1"}:
        return ftValaamToUnicode
    elif f in {"Hirmos Ponomar TT", "Hirmos Ponomar TT1"}:
        return ftHirmosPonomarToPonomarUnicode
    elif f in {"Irmologion"}:
        return ftIrmologionToUnicode
    else:
        return {}


def ucs_convert_string_by_search_and_replace(sSecString, vFontTable):
    """get string and fonttable and convert"""
    for ucs_str, unic_str in vFontTable.items():
        sSecString = sSecString.replace(ucs_str, unic_str)
    return sSecString


def ucs_convert_string_with_font_bforce(sSecString, vFontTable):
    """get string and font dict and return converted char-by-char string"""
    out = ""
    for ucs in sSecString:
        out += vFontTable.get(ucs, ucs)

    return out


def ucs_process_one_section(oParSection, method):
    sSecFnt = oParSection.CharFontName
    if sSecFnt != "":
        sSecString = oParSection.getString()
        vFontTable = get_font_table(sSecFnt)

        # если шрифт доступен для конвертации
        if vFontTable.items():

            # В шрифте "Ustav" есть ударения, которые ставятся ПЕРЕД гласной
            # меняем их местами перед конвертацией
            if sSecFnt == "Ustav":
                repaired = ucs_ustav_acute_repair_by_regex_sub(sSecString)
                oParSection.setString(repaired)
                sSecString = oParSection.getString()

            if method == 1:
                # process string char-by-char
                new_sSecString = \
                    ucs_convert_string_with_font_bforce(sSecString, vFontTable)
            else:
                # возможно этот метод еще пригодится
                new_sSecString = \
                    ucs_convert_string_by_search_and_replace(sSecString, vFontTable)
            # replace  string with converted
            oParSection.setString(new_sSecString)

        # set Unicode font for all symbols, replaced and not-replaced
        oParSection.CharFontName = UnicodeFont

    return None


def ucs_convert_by_sections(vDoc):
    """convert for every sections"""

    # в поисках способа замены:
    method = 1  # 1 - char-by-char; other - string.replace
    oParEnum = vDoc.Text.createEnumeration()

    # for every Paragraph
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.Paragraph"):
            oSecEnum = oPar.createEnumeration()
            # for every Section
            while oSecEnum.hasMoreElements():
                oParSection = oSecEnum.nextElement()
                # convert it
                ucs_process_one_section(oParSection, method)
    # TODO: post-process: repair repeating diacritics
    return None


def convert_one_symbol(sSymb, vFontTable):
    sSymb = vFontTable.get(sSymb, '')
    return sSymb


class Char:
    """for chars from Cursor, save and restore it attributes"""

    def __init__(self, oCursor):
        self.char = oCursor.getString()
        self.fontname = oCursor.CharFontName
        self.color = oCursor.CharColor
        self.bold = oCursor.CharWeight
        self.italic = oCursor.CharPosture
        # self.uline = uline

    def restore_attrib(self, oCursor):
        oCursor.CharColor = self.color
        oCursor.CharWeight = self.bold
        oCursor.CharPosture = self.italic


def ucs_ustav_acute_repair_by_oo_text_cursor(oCursor, sSymb):
    sUstavAcute = ''
    if sSymb == "m":
        sUstavAcute = "'"
    elif sSymb == "M":
        sUstavAcute = '"'
    elif sSymb == "x":
        sUstavAcute = "`"

    # look on next char
    oCursor.goRight(1, True)
    sNextChar = oCursor.String[1:2]
    # reverse two chars with replace acute
    oCursor.String = sNextChar + sUstavAcute
    sSymb = sNextChar
    oCursor.collapseToStart()
    oCursor.goRight(1, True)

    return sSymb


def ucs_ustav_acute_repair_by_regex_sub(sSecString):
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
        match = re_obj.search(sSecString)
        if match:
            sSecString = re_obj.sub(replace, sSecString)
    return sSecString


def ucs_convert_in_oo_text_cursor(oCursor):
    """process char-by-char text in TextCursor"""
    lenth_string = len(oCursor.getString())

    oCursor.collapseToStart()

    # for every symbol in string
    for i in range(lenth_string):
        oCursor.goRight(1, True)  # select next char to cursor
        char = Char(oCursor)  # save attributes of selected char
        sSymb = oCursor.getString()  # get one char from cursor
        font_of_symbol = oCursor.CharFontName  # get font of char
        vFontTable = get_font_table(font_of_symbol)  # get font dictionary

        # В шрифте "Ustav" есть ударения, которые ставятся ПЕРЕД гласной
        # меняем их местами перед конвертацией
        if font_of_symbol == "Ustav" and sSymb in {"m", "M", "x"}:
            sSymb = ucs_ustav_acute_repair_by_oo_text_cursor(oCursor, sSymb)

        # get value from font dictionary for char
        if vFontTable.items() and vFontTable.get(sSymb):
            new_sSymb = vFontTable.get(sSymb)
            oCursor.setString(new_sSymb)  # replace char with converted

        char.restore_attrib(oCursor)  # restore attributes of selected char
        oCursor.collapseToEnd()

    # set font to all symbols into Text-cursor
    oCursor.goLeft(lenth_string + 1, True)
    oCursor.CharFontName = UnicodeFont
    # TODO: post-process: repair repeating diacritics
    return None


def onik_search_and_replace(theString, istitled=False):
    """
    Regex search and replace in pseudo Perl|sed way.
    Nonlocal `newString' variable playing role $_ from Perl.
    Defined:
    `sed' function - change newString.
        sed(r'find', r'replace' [, 'flags'])
    `sr` function - using `sed' and use short form for regexes
        sr(r'find/replace')
        for simple regexes without "/" inside

    in body we run several sr|sed with one regex
        sr('regex1')
        ...
        sr('regexN')
    and after all
    return changed string
    """
    if not theString or len(theString) == 0:
        return ""

    # [:lower:] & [:upper:] classes
    # last two: ᲂ and ᲁ
    pL = "[абвгдеєѣжзѕꙁиіїѵйклмноѻѡѿꙍѽпрстꙋуфѳхцшщъыьюѧꙗяѯѱ\u1C82\u1C81]"
    pU = "[АБВГДЕЄѢЖЗЅꙀИІЇѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦШЩЪЫЬЮѦꙖЯѮѰ]"
    acutes = Oxia + Varia + Kamora
    dbl_grave = '\u030F'  # in ѷ
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
        titles + erok_comb + erok
    newString = theString  #

    def sr(s):
        if s == '': return 0
        c = s.partition('/')
        if not c[1]: return 0
        find = c[0]
        replace = c[2]
        sed(find, replace)

    def sed(find, replace, flags=''):
        nonlocal newString

        pat = find
        re_obj = re.compile(pat, re.U)
        if flags != '' and flags.count('i') > 0:
            re_obj = re.compile(pat, re.U | re.I)

        match = re_obj.search(newString)
        if match:
            newString = re_obj.sub(replace, newString)

    sr(r"\bот(?!е[цч]|ц)/ѿ")
    sr(r"\bОт(?!е[цч]|ц)/Ѿ")
    sed(
        r"([бвгджзклмнпрстфхцчшщ])\b(?![" + overlines_for_consonants + r"])",
        r"\1ъ"
    )
    sed(
        r"([БВГДЖЗКЛМНПРСТФХЦЧШЩ])\b(?![" + overlines_for_consonants + r"])",
        r"\1Ъ"
    )

    sr(r"У/Ꙋ")

    sr(r"\bꙊ(" + pL + r")/Оу\1")
    sr(r"\bꙊ(" + pU + r")/ОꙊ\1")
    sr(r"\bя/ꙗ")
    sr(r"\bЯ/Ꙗ")
    sr(r"я/ѧ")
    sr(r"Я/Ѧ")
    sr(r"(?<![" + acutes + Kendema + dbl_grave + r"])\bе/є")
    sr(r"(?<![" + acutes + Kendema + dbl_grave + r"])\bЕ/Є")

    sr(r"\bО\b/Ѽ")
    sr(r"\bо\b/ѡ")
    sr(r"\bо҆?/ѻ")
    sr(r"\bО(?!у)/Ѻ")
    sr(r"\b" + unicNarrowO + "?[уꙋ]/ᲂу")

    sr(r"([^Оᲂ])у/\1ꙋ")

    # -ии- -> -їи-
    # TODO: -їѧ & -їа
    sr(r"и҆?([аеєийоѡꙋюѧ])/ї\1")
    sr(r"И҆?([АЕЄИЙОѠꙊЮѦаеєийоѡꙋюѧ])/Ї\1")
    sr(r"\bЇ/І")
    sr(r"\bї/і")

    sr(r"ᲂ+/ᲂ")
    sr(r"ᲂꙋ/ᲂу")

    # Zvatelce for first letter of word
    sed(r"(?<![" + Oxia + Kamora + Kendema + dbl_grave + titles + r"])\b([АЄИІѴѺѠЮꙖ])(?!҆)", r"\1" + Zvatelce, "i")  #
    # sed(r"\b([аєиіѵѻѡюꙗ])҆?", r"\1" + Zvatelce)  #
    sed(r"\bОу҆?", "Оу" + Zvatelce)  # для ук
    sed(unicSmallUk + "҆?", unicSmallUk + Zvatelce)

    """
    Python interprets some diacritics as bound of word
    If word have it already, some regexes below may have wrong matches
    
    TODO: divide diacritic and letters processing,
    and check - if word have diacritic, process only letters.
    It possible to redefine "word", and expand it for diacritic?
    """

    # some words
    sr(r"([Аа]҆)зъ/\1́зъ")
    sr(r"([Аа]҆)ка́?фистъ/\1ка́ѳїстъ")
    sr(r"([Аа]҆)ллилꙋ́?їѧ/\1ллилꙋ́їа")
    sr(r"([Аа]҆)минь/\1ми́нь")
    sr(r"([Аа]҆)ще/\1" + Oxia + "ще")

    sr(r"\bбе́?д([аеносꙋъы])/бѣ́д\1")
    sr(r"\bбе́?л/бѣл")
    sr(r"(?<![" + Zvatelce + r"])\bбе́?л/бѣ́л")
    sr(r"([Бб])лагїй\b/\1лагі́й")
    sr(r"([Бб])лагогове́?йн/\1лагоговѣ́йн")
    sr(r"([Бб])лагодарю\b/\1лагодарю̀")
    sr(r"([Бб])лагодар([иеѧ])(\w+)/\1лагодар\2" + Oxia + r"\3")  # благодарим
    sr(r"([Бб])лагода([рт][^иеѧ])/\1лагода́\2")  # благодарно, благодать
    sr(r"([Бб])ог([аеꙋъ])/\1о́г\2")
    sr(r"([Бб])огороди([чц])/\1огоро́ди\2")
    sr(r"([Бб])огородительниц/\1огороди́тельниц")
    sr(r"([Бб])ож(е|ї[еиюѧ])\b/\1о́ж\2")
    sr(r"([Бб])ожественн/\1оже́ственн")
    sr(r"боле́?зн/болѣ́зн")
    sr(r"бꙋд(етъ|и)/бꙋ́д\1")
    sr(r"бысть/бы́сть")
    sr(r"быша/бы́ша")

    sr(r"\bвек([аиъ])\b/вѣ́к\1")
    sr(r"\bвековъ/вѣкѡ́въ")
    sr(r"\bве́?мъ/вѣ́мъ")
    sr(r"вер(аеоꙋ)/вѣ́р\1")
    sr(r"ве́?цехъ/вѣ́цѣхъ")
    sr(r"взываемъ/взыва́емъ")
    sr(r"([Вв])ладычиц/\1лады́чиц")
    sr(r"возсїѧваетъ/возсїѧва́етъ")
    sr(r"возсїѧ\b/возсїѧ̀")
    sr(r"возсїѧ([йеюя])/возсїѧ́\1")
    sr(r"восп[еѣ]ва́?/воспѣва́")
    sr(r"воспою\b/воспою̀")
    sr("вражї/вра́жї")
    sr(r"всегда\b/всегда̀")
    sr(r"\bвсе́?ми\b/всѣ́ми")
    sr(r"всемꙋ\b/всемꙋ̀")
    sr(r"всемъ/все́мъ")
    sr(r"всехъ/всѣ́хъ")
    sr(r"всеѧ/всеѧ̀")
    sr(r"\bвс([ию])\b/вс\1̀")
    sr(r"\bвсѧ\b/всѧ̑")
    sr(r"всѧк([аиїоꙋъ])/всѧ́к\1")
    sr(r"вта́?йне/вта́йнѣ")

    sr(r"([Гг])оспод([аеиꙋ])\b/\1о́спод\2")
    sr(r"([Гг])осподь/\1оспо́дь")
    sr(r"([Гг])лас(аоеꙋъ)/\1ла́с\1")
    sr(r"гне́?въ/гнѣ́въ")
    sr(r"([Гг])ре́?([схш])/\1рѣ\2")
    sr(r"([Гг])рѣ(хъ|шн\w{2,})/\1рѣ́\2")
    sr(r"грѣш([аеѣи])([вилмнстхшюѧ])/грѣш\1" + Oxia + r"\2")
    sr(r"грѣш([иꙋ])\b(?!["+ acutes +"])/грѣш\1" + Varia)
    sr(r"грѧди\b/грѧдѝ")

    sr(r"даже/да́же")
    sr(r"\bдарꙋ/да́рꙋ")
    sr(r"\b([Дд])е́?в([аеоꙋы]|ств)/\1ѣ́в\2") # ! одева-
    sr(r"\bдень/де́нь")
    sr(r"\bде́?т(и|[еѧ][мхй]ъ?|с[кт])/дѣ́т\1")
    sr(r"детоводи́?т/дѣ́товоди́т")
    sr(r"длѧ\b/длѧ̀")
    sr(r"днесь/дне́сь")
    sr(r"доко́?ле/доко́лѣ")
    sr(r"([Дд])ꙋх(а|ꙋ|ъ|омъ)/\1ꙋ́х\2")
    sr(r"\b([Дд])ꙋша\b/\1ꙋша̀")
    sr(r"\b([Дд])ꙋш([ꙋъ])\b/\1ꙋ́ш\2")

    sr(r"([Єє]҆)гда\b/\1гда̀")
    sr(r"([Єє]҆)го\b/\1гѡ̀")
    sr(r"([Єє]҆)го́?же\b/\1го́же")
    sr(r"([Єє])҆же/\1҆́же")
    sr(r"([Єє])҆й/\1҆́й")
    sr(r"є҆ли́?жды/є҆ли́жды")
    sr(r"([Єє]҆)лисе́?(\w)/\1лиссе́\2")  # var: єлїссе́й
    sr(r"є҆ли́?цы/є҆ли́цы")
    sr(r"([Єє])҆мꙋ\b/\1мꙋ̀")
    sr(r"є҆си\b/є҆сѝ")
    sr(r"є҆сть/є҆́сть")
    sr(r"є҆ще\b/є҆щѐ")
    sr(r"([Єє])҆юже/\1҆́юже")

    sr(r"живꙋщихъ/живꙋ́щихъ")
    sr(r"([Жж])и́?зн([иь])/\1и́зн\2")

    sr(r"([Зз])аповед/\1аповѣд")
    sr(r"зва́?ти/зва́ти")
    sr(r"зве́?зд/ѕвѣзд")
    sr(r"зело/ѕѣлѡ̀")
    sr(r"([Зз])емл([иѧ])\b/\1емл\2" + Varia)
    sr(r"([Зз])е́?млю/\1е́млю")
    sr(r"зениц/зѣ́ниц")
    sr(r"\bзл([аеоꙋы])\b/ѕл\1" + Varia)
    sr(r"зме́?([йюѧ]́?\b|[еи]\w+)/ѕмѣ\1")
    sr(r"ѕмѣй/ѕмѣ́й")  # var: ѕмі́й
    sr(r"зре́?ти\b/зрѣ́ти")

    sr(r"и҆де́?же/и҆дѣ́же")
    sr(r"(І҆|і҆)ере́?/\1ере́")
    sr(r"(И҆|и҆)же/\1́же")
    sr(r"и҆збави/и҆зба́ви")
    sr(r"и҆зрѧ́?дно/и҆зрѧ́днѡ")
    sr(r"(І҆|і҆)исꙋс/\1исꙋ́с")
    sr(r"(І҆|і҆)кон/\1ко́н")
    sr(r"и҆косъ/і҆́косъ")
    sed("И҆косъ", "І҆́косъ", "i")
    sr(r"(И҆|и҆)мже/\1́мже")
    sr(r"(И҆|и҆)мѧ/\1́мѧ")
    sr(r"(І҆|і҆)о/\1ѡ")
    sr(r"(І҆|і҆)ѡвъ/\1́ѡвъ")
    sr(r"И҆рмо́?съ/І҆рмо́съ")
    sr(r"и҆рмо́?съ/і҆рмо́съ")
    sr(r"и҆ссꙋш/и҆зсꙋш")
    sr(r"цел([еєиюѧ]|ьб)/цѣл\1")
    sr(r"и҆сцѣл([еєѧ])́?/и҆сцѣл\1́")
    sr(r"и҆спове́?д/и҆сповѣ́д")
    sr(r"и҆ссо́?п/ѵ҆ссѡ́п")
    sr(r"и҆хъ/и҆́хъ")

    sed("([Кк])ондакъ", r"\1онда́къ", "i")
    sr(r"красн/кра́сн")
    sr(r"красотꙋ\b/красотꙋ̀")
    sr(r"красотою/красото́ю")
    sr(r"([Кк])рестн/\1ре́стн")
    sr(r"кре́?пк(?=\w)/крѣ́пк")
    sr(r"кротк/кро́тк")
    sr(r"([Кк])ꙋпина/\1ꙋпина̀")

    sr(r"([Лл])ик(?=\w\b)/\1и́к")
    sr(r"([Лл])юбв[ие]\b/\1юбвѐ")
    sr(r"([Лл])юбов([їь]ю?)/\1юбо́в\2")
    sr(r"([Лл])юбы\b/\1юбы̀")

    sr(r"([Мм])арї([еиѧю])/\1арі́\2")
    sr(r"([Мм])ати/\1а́ти")
    sr(r"([Мм])атер([нсь])/\1а́тер\2")
    sr(r"([Мм])илосерд/\1илосе́рд")
    sr(r"([Мм])илости/\1и́лости")
    sr(r"мне́?ти\b/мнѣ́ти")
    sr(r"\bмое\b/моѐ")
    sr(r"\bмой\b/мо́й")
    sr(r"моли\b/молѝ")
    sr(r"молитв(?!ословъ)/моли́тв")
    sr(r"моѧ\b/моѧ̀")
    sr(r"([Мм])ꙋчен/\1ꙋ́чен")

    sr("наве́?т(?=\w)/навѣ́т")
    sr(r"\bна([мсш])([аиꙋъ]|ихъ|е(?:[йѧ]|го)?)\b/на́\1\2")  # на́мъ на́шъ на́съ
    sr(r"\b([Нн])ебеса\b/\1ебеса̀")
    sr(r"\b([Нн])ебесн(?=\w)/\1ебе́сн")
    sr(r"\b([Нн])ебо\b/\1е́бо")
    sr(r"неве́?денї/невѣ́денї")
    sr(r"([Нн])его́?же\b/\1егѡ́же")
    sr(r"не́?жн/нѣ́жн")
    sr(r"неизреченн/неизрече́нн")
    sr(r"([Нн])ейже/\1е́йже")
    sr(r"непорочн/непоро́чн")
    sr(r"\b([Нн])ов([аоꙋы][гейюѧ]([оѡ])?)/\1о́в\2")
    sr(r"\b([Нн])о́?вого/\1о́ваго")
    sr(r"нощь/но́щь")
    sr(r"([Нн])ы́?не/\1ы́нѣ")

    sr(r"ѻ҆баче/ѡ҆ба́че")
    sr(r"Ѻ҆баче/Ѡ҆ба́че")
    sr(r"([Ѻѻ]҆)бител/\1би́тел")
    sr(r"ѻ҆блеце́?мсѧ/ѡ҆блеце́мсѧ")
    sr(r"ѻ҆бнов/ѡ҆бнов")
    sr(r"Ѻ҆бнов/Ѡ҆бнов")
    sr(r"(Ѡ҆|ѡ҆)бновѝ?\b/\1бновѝ")
    sed(r"ѻ҆(браз([аеꙋъы]|омъ))\b", r"ѡ"+Iso+r"\1")
    sed(r"Ѻ҆(браз([аеꙋъы]|омъ))\b", r"Ѡ"+Iso+r"\1")
    sr(r"ѻ҆блеко́?ша/ѡ҆блеко́ша")
    sr(r"ѻ҆бре(с?т)/ѡ҆҆брѣ\1")
    sr(r"ѡ҆҆брѣта(?:\w)/ѡ҆҆брѣта́")
    sr(r"ѻ҆девает/ѡ҆дѣва́ет")
    sr(r"ѻ҆зар([еєиѧ]́?)/ѡ҆зар\1")
    sr(r"Ѻ҆зар([еєиѧ]́?)/Ѡ҆зар\1")
    sr(r"(Ѡ҆|ѡ҆)зар([еєѧ])/\1зар\2" + Oxia)
    sr(r"(Ѡ҆|ѡ҆)зари\b/\1зарѝ")
    sr(r"ѻ҆кропи/ѡ҆кропи")
    sr(r"ѻ҆мы́?й/ѡ҆мы́й")
    sr(r"ѻ҆правди́?ша/ѡ҆правди́ша")
    sr(r"ѻ҆чи́?(сти|щ)/ѡ҆чи\1")
    sr(r"Ѻ҆чи́?(сти|щ)/Ѡ҆чи\1")
    sr(r"(Ѡ҆|ѡ҆)чи́?сти/\1чи́сти")

    sr(r"([Пп])а(ки|че)/\1а́\2")
    sr(r"([Пп])е́?(въ|нї|снь)/\1ѣ́\2")
    sr(r"печаль/печа́ль")
    sr(r"([Пп])ла́?ч[ьъ]\b/\1ла́чь")
    sr(r"побежда́?(?=\w)/побѣжда́")
    sr(r"([Пп])окаѧнї/\1окаѧ́нї")
    sr(r"([Пп])окров([аеꙋъ]|омъ)\b/\1окро́в\2")
    sr(r"покрый/покры́й")
    sr(r"([Пп])омилꙋй/\1оми́лꙋй")
    sr(r"([Пп])о́?сле/\1о́слѣ")
    sr(r"предъ/пре́дъ")
    sr(r"преиспещренн/преиспещре́нн")
    sr(r"([Пп])речист/\1речи́ст")
    sr(r"([Пп])рїиди\b/\1рїидѝ")
    sr(r"([Пп])рїиди(\w+)/\1рїиди́\2")
    sr(r"([Пп])ри́?сно\b/\1ри́снѡ")
    sr(r"простира́?/простира́")
    sr(r"Псал(о?м|т)/Ѱал\1")
    sr(r"псал(о?м|т)/ѱал\1")
    sr(r"([Ѱѱ])алом/\1ало́м")
    sr(r"([Ѱѱ])алмопе́?в/\1алмопѣ́в")
    sr(r"([Ѱѱ])алт([иы])р/\1алт\2" + Oxia + r"р")
    sr(r"пꙋтемъ/пꙋте́мъ")

    sr(r"([Рр])ади/\1а́ди")
    sr(r"([Рр])адост([ень])/\1а́дост\2")
    sr(r"([Рр])адꙋй(сѧ|тесь)/\1а́дꙋй\2")
    sr(r"риз([аеоꙋы])/ри́з\1")
    sr(r"([Рр])ꙋсск/\1ꙋ́сск")

    sr(r"([Сс])воеѧ\b/\1воеѧ̀")
    sr(r"([Сс])ве́?т([ъаꙋе]|омъ|л(аѧ|о([ей]|мꙋ)|ꙋю|ый))\b/\1вѣ́т\2")
    sr(r"([Сс])вѧтаѧ/\1вѧта́ѧ")
    sr(r"([Сс])вѧте(й|мъ)/\1вѧте́\2")
    sr(r"([Сс])вѧтїи/\1вѧті́и")
    sr(r"([Сс])вѧто(й|м[ꙋъ])/\1вѧто́\2")
    sr(r"([Сс])вѧтꙋю/\1вѧтꙋ́ю")
    sr(r"([Сс])вѧтыѧ/\1вѧты́ѧ")
    sr(r"свѧщенї([еюѧ])/свѧще́нї\1")
    sr(r"([Сс])его\b/\1его̀")
    sr(r"\b([Сс])ей\b/\1е́й")
    sr(r"селенї/селе́нї")
    sr(r"\bсемъ\b/се́мъ")
    sr(r"сердц(ꙋ|е(мъ)?)/се́рдц\1")
    sr(r"\b([Сс])еѧ\b/\1еѧ̀")
    sr(r"\bсї([еюѧ])\b/сї\1̀")  # "сие сию сия"
    sr(r"([Сс])илꙋан/\1илꙋа́н")
    sr(r"([Сс])ице\b/\1и́це")
    sr(r"\bскорб([иь]\b|ехъ|н)/ско́рб\1")
    sr(r"\bскорбѧ([мщ])/скорбѧ́\1")
    sr(r"([Сс])лав([аоꙋые]|и[вмтх]ъ|лю)\b/\1ла́в\2")
    sr(r"([Сс])лавн([аоꙋые]\w+)\b/\1ла́вн\2")
    sr(r"слезам([иъ])/слеза́м\1")
    sr(r"слез([ыъ])/сле́з\1")
    sr(r"слезн([аоꙋы])/сле́зн\1")
    sr(r"смиренї/смире́нї")
    sr(r"смиренн(?!омꙋд)/смире́нн")
    sr(r"сне́?г(?=\w)/снѣ́г")
    sr(r"страждꙋщ/стра́ждꙋщ")
    sr(r"страданї/страда́нї")
    sr(r"страхъ\b/стра́хъ")
    sr(r"([Сс])офро́?н/\1офрѡ́н")
    sr(r"((со)?х)рани\b/\1ранѝ")
    sr(r"спасенї/спасе́нї")
    sr(r"([Сс])паси\b/\1пасѝ")
    sr(r"([Сс])подоби/\1подо́би")
    sr(r"([Сс])ын([аеꙋъ])/\1ы́н\2")

    sr(r"([Тт])а́?ко\b/\1а́кѡ")
    sr(r"([Тт])а((ко)?же)/\1а́\2")
    sr(r"тайн([аеоꙋы][ейюѧ]?)/та́йн\1")
    sr(r"та́?йнемъ/та́йнѣмъ")
    sr(r"тварь/тва́рь")
    sr(r"([Тт])вое\b/\1воѐ")
    sr(r"([Тт])во(е?ѧ)/\1во\2̀")
    sr(r"([Тт])вое(мꙋ|г[оѡ])/\1вое\2̀")
    sr(r"([Тт])вое([йю])/\1вое́\2")
    sr(r"([Тт])вои([мх])ъ/\1вои́\2ъ")
    sr(r"([Тт])вой/\1во́й")
    sr(r"([Тт])вою/\1вою̀")
    sr(r"([Тт])ебѐ?\b/\1ебѣ̀")
    sr(r"([Тт])е́?мже/\1ѣ́мже")
    sr(r"\bтепл([аоыꙋ][ейюѧ])/те́пл\1")
    sr(r"([Тт])обою/\1обо́ю")
    sr(r"\bтьмѐ?\b/тьмѣ")
    sr(r"\bтьм([аѣꙋы])\b/тьм\1̀")

    sr(r"(ᲂу҆́|ᲂу҆|ᲂу)б[оѡ]/ᲂу҆́бѡ")
    sr(r"([Оᲂ]у҆)миленї/\1миле́нї")
    sr(r"ᲂу҆мъ/ᲂу" + Iso + r"мъ")
    sr(r"ᲂу҆тверди\b/ᲂу҆твердѝ")
    sr(r"([Оᲂ]у҆)теше́?нїе/\1тѣше́нїе")
    sr(r"([Оᲂ]у҆)те́?шите/\1тѣ́шите")
    sr(r"([Оᲂ]у҆)теша́?(\w+)/\1тѣша́\2")

    sr(r"фарисе́?/фарїсе́")

    sr(r"ходиша/ходи́ша")
    sr(r"([Хх])рам/\1ра́м")
    sr(r"([Хх])ристо́?съ/\1рїсто́съ")
    sr(r"([Хх])рист([аеꙋ]́?)\b/\1рїст\2̀")

    sr(r"царск[ао]го/царскагѡ")
    sr(r"([Цц])ар([сь])/\1а́р\2")
    sr(r"([Цц])ар([еє]́?)(\w+)/\1ар\2" + Oxia + r"\3")
    sr(r"([Цц])ар([июѧ]́?)\b/\1ар\2" + Varia)
    sr(r"([Цц])ве́?([лст])/\1вѣ\2")
    sr(r"([Цц])еркв/\1е́ркв")
    sr(r"([Цц])ерковь/\1е́рковь")
    sr(r"([Цц])ерковн/\1ерко́вн")

    sr(r"([Чч])елове́?([кч])/\1еловѣ́\2")
    sr(r"([Чч])еловѣколю́?б/\1еловѣколю́б")
    sr(r"([Чч])естне́?йш/\1естнѣйш")
    sr(r"([Чч])естн([аеєѣоꙋы])(\w+)/\1естн\2́\3")
    sr(r"([Чч])ист([аы]ѧ|о[ейю]|ꙋю)/\1и́ст\2")

    sr(r"ѿкровенї/ѿкрове́нї")
    sr(r"Ѿцемъ/Ѿце́мъ")

    sr(r"(Ю҆|ю҆)же\b/\1́же")

    sr(r"((Ꙗ҆|ꙗ҆)́?)ви\b/\1вѝ")
    sr(r"(Ꙗ҆|ꙗ҆)висѧ/\1ви́сѧ")
    sr(r"(Ꙗ҆|ꙗ҆)́?коже/\1́коже")
    sr(r"(Ꙗ҆|ꙗ҆)́?ко\b/\1́кѡ")
    sr(r"(Ꙗ҆|ꙗ҆)́?же/\1́же")

    sr(r"/0")
    sr(r"/1")
    sr(r"/2")
    sr(r"/3")
    sr(r"/4")
    sr(r"/5")
    sr(r"/6")
    sr(r"/7")
    sr(r"/8")
    sr(r"/9")

    # months
    sr(r"ентѧбрѧ/епте́мврїа")
    sr(r"ктѧбрѧ/ктѡ́врїа")
    sr(r"оѧбрѧ/ое́мврїа")
    sr(r"екабрѧ/еке́мврїа")
    sr(r"ꙗ҆нварѧ/і҆аннꙋа́рїа")
    sr(r"Ꙗ҆нварѧ/І҆аннꙋа́рїа")
    sr(r"евралѧ/еврꙋа́рїа")
    sr(r"([Мм])арта\b/\1а́рта")
    sr(r"прелѧ/прі́лїа")
    sr(r"([Мм])аѧ\b/\1а́їа")
    sr(r"і҆ю([лн])ѧ\b/і҆ꙋ́\1їа")
    sr(r"І҆ю([лн])ѧ\b/І҆ꙋ́\1їа")
    sr(r"([Аа]҆?)вгꙋста/\1"+Iso+r"ѵгꙋста")

    # remove repeating
    sr(Oxia + "+/" + Oxia)
    sr(Varia + "+/" + Varia)
    sr(Zvatelce + "+/" + Zvatelce)

    if istitled:
        sr(r"([Аа]҆)по́?стол/\1пⷭ҇тол")
        sr(r"([Бб])ла́?г/\1л҃г")
        sr(r"([Бб])о́?г([аеꙋъ])/\1г҃\2")
        sr(r"([Бб])огове́?денї/\1г҃овѣ́дѣнї")  # бг҃овѣ́дѣнї
        sr(r"([Бб])огоро́?диц/\1цⷣ")
        sr(r"([Бб])огоро́?дич/\1г҃оро́дич")
        sr(r"([Бб])огороди́?тельниц/\1г҃ороди́тельниц")
        sr(r"([Бб])о́?ж/\1ж҃")
        sr(r"([Вв])лады́?([кч])/\1лⷣ\2")
        sr(r"([Гг])о́?спо́?д/\1дⷭ҇")
        sr(r"([Дд])ѣ́?в([аеоꙋы])/\1в҃\2")
        sr(r"([Дд])ѣ́?вств/\1вⷭ҇тв")
        sr(r"(І҆|і҆)исꙋ́?с/\1и҃с")
        sr(r"([Кк])ре́?ст/\1рⷭ҇т")
        sr(r"([Мм])арі́?([еѧю])/\1р҃і́\2")
        sr(r"([^и][Мм])а́?ти/\1т҃и")
        sr(r"([Мм])а́?тер([нсь])/\1т҃р\2")
        sr(r"([Мм])илосе́?рд/\1лⷭ҇рд")
        sr(r"([Мм])и́?лости/\1лⷭ҇ти")
        sr(r"([Мм])оли́?тв/\1л҃тв")
        sr(r"мꙋдрость/мⷣрость")
        sr(r"([Мм])ꙋ́?чен/\1ч҃н")
        sr(r"([Нн])ы́?не/\1н҃ѣ")
        sr(r"([Пп])реподо́?б(е?н)/\1рпⷣб\2")
        sr(r"при́?снѡ/прⷭ҇нѡ")
        # sr(r"([Пп])роро́?къ/\1рⷪ҇ркъ")
        sr(r"([Сс])вѧ́?т/\1т҃")
        sr(r"се́?рдц/срⷣц")
        sr(r"([Сс])па́?с/\1п҃с")
        sr(r"([Сс])ы́?н([аеꙋъ])/\1н҃\2")
        sr(r"([Хх])р(ї|и)ст/\1рⷭ҇т")
        sr(r"([Чч])еловѣколю́?б/\1л҃вѣколю́б")
        sr(r"([Чч])еловѣ́?([кч])/\1л҃вѣ́\2")
        sr(r"([Чч])е́?стн/\1ⷭ҇тн")
        sr(r"([Чч])и́ст/\1ⷭ҇т")
        sr(r"([Цц])а́?рс/\1рⷭ҇")
        sr(r"([Цц])е́?рк/\1р҃к")

    return newString


def onik_prepare(vDoc, istitled=False):
    """takes oDoc (CurrentComponent. Convert whole text or selected text)"""
    # TODO: флаг istitled заменить на именованный параметр flags
    # для запуска onik_titled и onik_untitled

    # видимый курсор для обработки выделенного текста
    oVC = vDoc.CurrentController.getViewCursor()
    sSel = oVC.getString()  # текст выделенной области
    istitled_flag = istitled

    if sSel == '':  # whole document
        # by paragraph, for preserv it
        oParEnum = vDoc.Text.createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.Paragraph"):
                theString = oPar.getString()  # текст абзаца
                # конвертированный текст абзаца
                newString = onik_search_and_replace(theString, istitled_flag)
                oPar.setString(newString)  # replace with converted

    else:  # selected text
        # TODO: multi-selection (see Capitalise.py)
        # конвертированный текст выделенной области
        new_sSel = onik_search_and_replace(sSel, istitled_flag)
        oVC.setString(new_sSel)  # replace with converted (for selected area)
    return None


def onik_titled(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient and set some titles."""
    # get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    oDoc = desktop.getCurrentComponent()

    onik_prepare(oDoc, True)
    return None

# TODO: def onik_untitled(*args)
# "Раскрыть" титла в тексте.

def onik(*args):
    """Convert text in Ponomar Unicode from modern-russian form to ancient."""
    # get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    oDoc = desktop.getCurrentComponent()

    onik_prepare(oDoc)
    return None


def ucs_convert_from_shell(*args):
    """Convert text with various Orthodox fonts to Ponomar Unicode.
    For runnig from oo-macro from shell
    to pass oDoc (ThisComponent) to py-script as first argument
    $ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"
    """
    oDoc = args[0]
    # обработка всего документа посекционно
    ucs_convert_by_sections(oDoc)

    return None


def ucs_convert_from_office(*args):
    """Convert text with various Orthodox fonts to Ponomar Unicode.
    for running from Libre/Open Office - Menu, toolbar or gui-dialog.
    """
    desktop = XSCRIPTCONTEXT.getDesktop()
    # doc = XSCRIPTCONTEXT.getDocument()
    oDoc = desktop.getCurrentComponent()

    # видимый курсор для обработки выделенного текста
    oVC = oDoc.CurrentController.getViewCursor()
    sSel = oVC.getString()  # текст выделенной области

    if sSel == '':  # whole document
        # обработка всего документа посекционно
        ucs_convert_by_sections(oDoc)

    else:  # selected text
        # TODO: multi-selection (see Capitalise.py)
        oCursor = oVC.Text.createTextCursorByRange(oVC)
        # обработка выделенного фрагмента через текстовый курсор
        ucs_convert_in_oo_text_cursor(oCursor)
        oVC.collapseToEnd()
    # Msg("Done!")
    return None


# button url
# vnd.sun.star.script:onik.py$onik?language=Python&location=user

# lists the scripts, that shall be visible inside OOo. Can be omitted, if
# all functions shall be visible, however here getNewString shall be suppressed
g_exportedScripts = onik, onik_titled, ucs_convert_from_office,  # UCSconvert_from_shell,
