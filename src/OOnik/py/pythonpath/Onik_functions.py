#!/usr/bin/python3
# _*_ coding: utf-8

import re
from Regs import *
from Letters import *

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
        packed_imposed = self
        for i in range(len(packet_converted)):
            # изменяем текст

            l = packet_converted[i]
            char_conv = l.char
            super_conv = l.superscript
            super_new = packed_imposed[i].superscript
            char_new = packed_imposed[i].char
            if char_conv != '':
                packed_imposed[i].char = char_conv
            # изменяем надстрочники
            if super_conv != '':
                # условия наложения надстрочников (кендема, исо, апостроф)
                # при накладывании кендемы на ударение - ударение не меняется

                # TODO: если у источника звательце у replaced - оксия|вария
                # вариант 1: сразу в regex заменить на Исо|Апостроф

                if not (
                        super_new in acutes
                        and super_new != ''
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