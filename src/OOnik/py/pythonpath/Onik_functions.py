#!/usr/bin/python3
# _*_ coding: utf-8

# import copy
import re
from Regs import *
from Letters import *
from numerals import cu_format_int

# compiled regexes sets
regs_letters_in_word_compiled = []
regs_acutes_compiled = []
regs_titles_set_compiled = []
regs_titles_open_compiled = []

'''
    Общие положения.
    
    Текст в onik-функции приходит в виде обычной строки символов 
    либо отдельным словом (под курсором), либо протяженным текстом  
    (со знаками пунктуации, кавычками и т.д.)
    Надстрочники в словах следуют за буквами. 
    
    Текст разбивается на слова. 
    
    Для обработки слово ("очищенное" от кавычек и пр.), 
    переводится в особый "запакованный" формат, где доступны два "слоя" -
    текстовый, и надстрочников. 
    Напр., слово 'ѻ҆́ч҃е' (отче с исо и титлом) как строка имеет 6 символов:
    ('ѻ', 'Zvatelce', 'Oxia', 'ч', '҃', 'е')
    В формате "пакета" имеем 3 буквы+надстрочник:
    (
        ['ѻ', 'Zvatelce + Oxia'], или ['ѻ', 'Iso'],
        ['ч', 'titlo'],
        ['е']
    )
    Надстрочники:   ['Iso', 'titlo', '' ]
    Текстовый слой: ['ѻ',   'ч',     'е']
    
    Далее "запакованное" слово, или "пакет", обрабатывается в зависимости от поставленной задачи.
    После обработки пакет "распаковывается", т.е. приводится к исходному формату - строка символов,
    надстрочники следуют за буквами.
         
    Ближе к коду:
    Создается объект класса RawWord, 
    слово "очищается" от пред- и -пост символов (метод RawWord.get_text_stripped). 
    Создается объект класса WordPacked (метод RawWord.pack), 
    кот-й в свою очередь состоит 
    из отдельных объектов класса Gramma - буква + надстрочник.
    
    С помощью различных методов RawWord и WordPacked выполняютсмя задачи onik-функций.
    Напр. основная задача перевода текста из русской орфографии в цся 
    (ф-ция get_string_converted) -
    использует метод RawWord.get_converted.
    
    Полученный результат распаковывается (метод WordPacked.unpack),
    к нему присоединяются пре- и -пост фрагменты (кавычки и пр.), 
    и конечный результат возвращается из функции в виде обычного текста.
    
    Некоторые задачи не требуют работы со слоями, в этом случае
    обработка текста обычная (convert_string_with_digits) 
'''


class Gramma:
    # одна буква с надстрочниками и др. атрибутами

    def __init__(self, char, superscript=''):
        # TODO: разобраться с ООП-подходом
        #  уточнить что и как передается и меняется
        self.letter = char  # буква
        self.superscript = superscript  # надстрочник
        # вид ударения ['varia', 'oxia', 'kamora']
        self.acute = self.get_acute()
        self.is_acuted = self.get_acute_flag()  # есть ли знак ударения
        # TODO: ??? м.б. разделить оксию варию и камору?
        self.have_zvatelce = self.get_zvatelce_flag()
        self.have_erok = False  # COMBINED !!!
        self.is_first = False
        self.is_last = False
        self.is_vowel = False  # гласная
        self.is_consonante = False  # согласная
        # ук, от?, ї с кендемой, ѷ ижица с дв. ударением
        self.is_combined = False
        self.titlo = ''  # титло
        self.is_titled = False  # имеет титло
        self.have_superscript = self.get_superscript_flag()

        # TODO: проверка порядка следования для исо и апострофа

    def __eq__(self, other):
        # проверка на равенство двух gramma
        return self.letter == other.letter and self.superscript == other.superscript

    def get_full_list(self):
        # получиь списком букву + надстрочник
        letter_with_superscripts = [self.letter]
        if self.have_superscript:
            letter_with_superscripts.append(self.superscript)
        return letter_with_superscripts

    def get_full_letter(self):
        # получиь строкой букву + надстрочник
        # TODO: использовать self.get_full_list
        #  return ''.join(self.get_full_list)
        letter_with_superscripts = self.letter
        if self.have_superscript:
            letter_with_superscripts += self.superscript
        return letter_with_superscripts

    def get_acute_flag(self):
        # получить признак ударения
        # исо и апостроф включены
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

    def check_vowels(self):
        if self.letter in cu_vowels:
            return True
        return False

    def check_consonants(self):
        if self.letter in cu_consonants:
            return True
        return False

    def de_acute(self):
        # удалить ударение
        if self.superscript in [Iso, Apostrof]:
            self.superscript = Zvatelce
        elif self.superscript in [Oxia, Varia, Kamora]:
            if self.letter in "Ѵѵ":
                self.superscript = dbl_grave
            elif self.letter in "Іі":
                self.superscript = Kendema
            else:
                self.superscript = ''


class WordPacked(list):
    def __init__(self, letters):
        super().__init__(letters)
        # self.unpacked = self.unpack()

    def __str__(self):
        return self.unpack()

    def __eq__(self, other):
        _ret = False  # по умолчанию не равны
        if len(self) != len(other):
            return False
        # если eq все gramma
        i = 0
        for gramma in self:
            _ret = gramma == other[i]
            if not _ret:
                return False
            _ret *= _ret
            i += 1
        return bool(_ret)

    def unpack(self):
        '''
        :return: строка буквы + надстрочники
        '''
        string = ''
        for gramma in self:
            string += gramma.letter
            if gramma.get_superscript_flag():
                string += gramma.superscript

        return string

    def get_text_layer(self):
        '''
        :return: текстовый слой как список '''
        text_layer = []
        for gramma in self:
            text_layer.append(gramma.letter)
        return text_layer

    def get_superscripts_layer(self):
        '''
        :return: слой надстрочников как список'''
        superscripts_layer = []
        for gramma in self:
            if gramma.get_superscript_flag():
                superscripts_layer.append(gramma.superscript)
            else:
                superscripts_layer.append('')
        return superscripts_layer

    def get_text_layer_string(self):
        '''
        :return: текстовый слой как строку'''
        return ''.join(self.get_text_layer())

    def get_text_anacuted(self):
        '''
        :return: текст (строку) без ударений и звательца'''
        anacuted = ''
        for gramma in self:
            anacuted += gramma.letter
            if not (gramma.is_acuted or gramma.have_zvatelce):
                anacuted += gramma.superscript
        return anacuted

    def imposing(self, packet_converted):
        '''
        Совершает послойное наложение двух packet:
        исходного и измененного (converted).

        дете́й + дѣт => дѣте́й
        свѧты́й + ст҃ый => ст҃ы́й

        :param packet_converted: измененный пакет
        :return: результат наложения пакетов.
        '''

        # исходная и измененная строки текстового слоя
        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()

        packet_imposed = self  # результирующий пакет
        for i in range(len(packet_converted)):
            # изменяем текст

            # новая буква-пакет, ее буква и надстрочник
            gramma_converted = packet_converted[i]  # Gramma
            letter_converted = gramma_converted.letter  # буква
            superscript_converted = gramma_converted.superscript  # надстрочник

            char_new = packet_imposed[i].letter
            superscript_new = packet_imposed[i].superscript
            if letter_converted != '':
                packet_imposed[i].letter = letter_converted

            # изменяем надстрочники
            if superscript_converted != '':
                # условия наложения надстрочников (кендема, исо, апостроф)
                # при накладывании кендемы на ударение - ударение не меняется

                # TODO: если у источника звательце у replaced - оксия|вария
                # вариант 1: сразу в regex заменить на Исо|Апостроф
                if not (
                        superscript_new in acutes  # , Iso, Apostrof
                        and superscript_new != ''
                        and superscript_converted == Kendema
                ):
                    # Если у источника исо|апостроф,
                    # и если в правиле стоит замена на Zvatelce, то оставить без изменения
                    if superscript_new in [Iso, Apostrof] and superscript_converted == Zvatelce:
                        packet_imposed[i].superscript = superscript_new
                    else:
                        packet_imposed[i].superscript = superscript_converted

        return packet_imposed

    def imposing_nonequal(self, packet_converted, match, replace_expanded):
        ''' imposing для случая, когда replace != find [и есть ударение]

        :param packet_converted: преобразованный пакет
        :param match: regex match
        :param replace_expanded: match.expand(replace) для \1 \2 \g<name>
        :return: результат наложения пакетов
        '''

        # строки исходная и преобразованная
        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()

        packet_source = self

        replaced_expanded_text = \
            RawWord(replace_expanded).pack().get_text_layer_string()

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
                    packet_source[to_remove_pos].superscript = ''

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
                packet_source.pop(i)
            # print("--- ", packet_source.unpack(), '(после удаления)')
            # print("--- ", packet_converted.unpack(), '(новая)')

            if len(packet_source) == len(packet_converted):
                # применить обычное наложение
                packet_source.imposing(packet_converted)

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
                packet_source.insert_char(i, l)

            if len(packet_source) == len(packet_converted):
                # применить обычное наложение
                packet_source.imposing(packet_converted)

        return packet_source

    def regex_sub(self, regex_tuple):
        '''В исходном пакете совершает замену по regex из полученного кортежа

        :param regex_tuple: кортеж (re_compiled, Replace_part_of_reg_rule)
        :return: пакет с заменой текста
        '''
        # исходная строка
        _string_source = self.get_text_layer_string()
        converted_packet = self

        re_compiled, replace_part = regex_tuple

        # получить новую строку (и сопутств. объект match)
        _string_replaced, match, = \
            get_search_and_replaced(_string_source, re_compiled, replace_part)
        if match:
            # для работы с \1, \2, \g<name>
            replace_expanded = match.expand(replace_part)
            # result of S&R -> to packet
            replaced_packet = \
                RawWord(_string_replaced).pack()
            replaced_expanded_text = \
                RawWord(replace_expanded).pack().get_text_layer_string()
            # impose s&r and source
            # если текст найденного и для замены совпадают по длине
            if len(replaced_expanded_text) == \
                    len(match.group(0)):
                # простое наложение двух пакетов
                converted_packet = \
                    self.imposing(replaced_packet)
            # если текст найденного и для замены НЕ совпадают по длине
            else:
                # сложное наложение двух пакетов
                converted_packet = \
                    self.imposing_nonequal(replaced_packet, match, replace_expanded)

        return converted_packet

    def replace_char(self, find, replace):
        '''
        Поиск и замена буквы в пакете. Все вхождения.
        :param find: буква для поиска
        :param replace: буква для замены
        :return: измененный пакет
        '''
        packet = self
        for gramma in packet:
            if gramma.letter == find:
                gramma.letter = replace
        return packet

    def insert_char(self, pos=0, char='', superscript=''):
        '''
        вставляет в позицию pos букву [с надстрочником]
        :param pos: позиция вставки
        :param char: буква
        :param superscript: надстрочник
        :return: измененный пакет
        '''
        gramma_inserted = RawWord(char).pack()[0]
        gramma_inserted.superscript = superscript
        new_packet = self
        new_packet.insert(pos, gramma_inserted)

        return new_packet

    def append_char(self, char='', superscript=''):
        '''
        вставляет в конец букву [с надстрочником]
        :param char: буква
        :param superscript: надстрочник
        :return: измененный пакет
        '''

        gramma_inserted = RawWord(char).pack()[0]
        gramma_inserted.superscript = superscript
        new_packet = self
        new_packet.append(gramma_inserted)

        return new_packet

    def is_acuted(self):
        '''
        :return: множество ударений в слове.
        Если ошибочно две оксии, то покажет ОДНУ
        '''
        # acute_set = {Oxia, Varia, Kamora}
        # UPD: , Iso, Apostrof
        acute_set = {Oxia, Varia, Kamora, Iso, Apostrof}
        # результат пересечения множеств
        return set(self.get_superscripts_layer()).intersection(acute_set)

    def get_acutes_list(self):
        '''Возвращает список ударений
        для выявления ошибок множеств. ударений

        :return: список ударений
        '''
        acutes_list = []
        for gramma in self:
            if gramma.superscript in [Oxia, Varia, Kamora, Iso, Apostrof]:
                acutes_list.append(gramma.superscript)

        return acutes_list

    def is_letters_number(self):
        '''
        Определяет - является ли слово числом в буквенной записи
        :return: Bool
        '''
        string = self.unpack()
        thousands_re = thousands + '[' + lnum_1_900 + ']'
        # а҃ - ѳ҃ ;  1-9 ;
        if re.search('^[' + lnum_1_9 + ']' + titlo + '$', string, re.U | re.X):
            return True
        # ; а҃і-ѳ҃і;  11-19; 1011-1019
        if re.search('^(' + thousands_re + ')?[' + lnum_1_9 + ']' + titlo + 'і$', string, re.U | re.X):
            return True
        # і҃; 10
        if re.search('^і' + titlo + '$', string, re.U | re.X):
            return True
        # к҃а - ч҃ѳ ; 20 - 99; 1020-1099
        elif re.search('^(' + thousands_re + ')?[' + lnum_20_90 + ']' + titlo + '([' + lnum_1_9 + '])?$', string, re.U | re.X):
            return True
        # р҃-ц҃ ;р҃а..р҃ѳ ; р҃і,р҃к..ц҃ч ; 101-109 ... 901-909; 110,120...990; 1101-1109...1901-1909; 1110,1120...1990
        elif re.search('^(' + thousands_re + ')?[' + lnum_100_900 + ']' + titlo + '([' + lnum_1_90 + '])?$', string, re.U | re.X):
            return True
        # ра҃і ; 111-119 ... 911-919; 1111-1119...1911-1919
        elif re.search('^(' + thousands_re + ')?[' + lnum_100_900 + ']' + '[' + lnum_1_9 + ']' + titlo + 'і$', string, re.U | re.X):
            return True
        # рк҃а цч҃ѳ ; 121-199 ... 921-999; 1121-1199 .. 1921-1999
        elif re.search('^(' + thousands_re + ')?[' + lnum_100_900 + ']' + '[' + lnum_20_90 + ']' + titlo + '[' + lnum_1_9 + ']$', string, re.U | re.X):
            return True
        #  ҂а҃,҂в҃ - ҂ѳ ҃; ҂а҃а - ҂ѳ ҃ц ; 1000,2000-9000; 1001,1002-1010 ... 100100-900 900
        elif re.search('^' + thousands_re + titlo + '(' + lnum_1_900 + ')?$', string, re.U | re.X):
            return True
        else:
            return False


class RawWord:
    # слово (строка) с предшеств. и послед. символами

    def __init__(self, string):
        self.string = str(string)
        self.stripped = self.get_text_stripped()
        self.packet = self.pack()  # WordPacked

    def get_pref_symbols(self):
        # проверка на символы перед буквами - кавычки, кавыки и т.д.
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
        '''
        :return: текст (строка) без пре- и -пост символов
        '''
        stripped = self.string
        stripped = stripped.strip(self.get_pref_symbols())
        stripped = stripped.strip(self.get_post_symbols())
        return stripped

    def get_text_unstripped(self, string):
        '''
        Присоединяет к тексту полученной строки
        пре- и -пост фрагменты
        :param string: строка без пре/пост фрагментов
        :return: "полная" строка
        '''
        unstripped = string
        _pre = self.get_pref_symbols() if self.get_pref_symbols() else ''
        _post = self.get_post_symbols() if self.get_post_symbols() else ''
        return _pre + unstripped + _post

    def pack(self):
        '''
        Разбивает слово string на объекты класса Gramma
        вместе с самой буквой - флаги и значения надстрочников и т.д.

        :return: packed_word
        '''
        packed_word = WordPacked([])
        string = self.get_text_stripped()

        combined_dic = {
            unicCapitalIzhitsaDblGrave: unicCapitalIzhitsa,
            unicSmallIzhitsaDblGrave: unicSmallIzhitsa,
            unicCapitalYi: unicCapitalUkrI,
            unicSmallYi: unicSmallUkrI
        }
        string_length = len(string)

        for i in range(string_length):
            gramma_current = Gramma('')  # текущий gramma
            _char = string[i]  # текущий символ
            if i > 0:
                # предыдущий gramma, начиная с 1
                gramma_prev = packed_word[-1]
            if i == 0:
                gramma_current.is_first = True

            if _char in cu_letters_text:
                # если текущий символ - буква
                gramma_current.letter = _char
                # проверка на слитные с надстрочником символы  ѷ ї
                if _char in combined_dic.keys():
                    gramma_current.letter = combined_dic.get(_char, _char)
                    if _char in [unicCapitalIzhitsaDblGrave, unicSmallIzhitsaDblGrave]:
                        gramma_current.superscript = dbl_grave
                    elif _char in [unicCapitalYi, unicSmallYi]:
                        gramma_current.superscript = Kendema
                    gramma_current.is_combined = True

                packed_word.append(gramma_current)

            elif _char in cu_superscripts:
                # Если текущий символ - надстрочник
                # выставить флаг и занести символ

                # Если у предыдущего символа уже есть надстрочник
                # (исправление ошибок набора - два ударения подряд и т.п.)
                if gramma_prev.have_superscript:
                    # Если текущий символ - часть комбинированного надстрочника
                    # (остальные некорректные надстрочники отбрасываются)
                    #  TODO: проверить: ошибка если оксия после кендимы у i - она должна заменять ее
                    if gramma_prev.have_zvatelce and _char in [Oxia, Varia, Kamora]:
                        # Исо, Апостроф, breve+pokrytie
                        gramma_prev.superscript += _char  # если двойной то добавить к уже имеющемуся
                    elif gramma_prev.superscript in under_pokrytie and _char == pokrytie:
                        # буквенное титло
                        gramma_prev.superscript += _char
                else:
                    gramma_prev.have_superscript = True
                    gramma_prev.superscript = _char

                if _char == Zvatelce:
                    # если звательце,
                    # выставить у предыдущей буквы флаг
                    gramma_prev.have_zvatelce = True

                elif _char in acutes:
                    # если ударение,
                    # выставить у предыдущей буквы флаг и символ ударения
                    gramma_prev.is_acuted = True  # флаг и
                    gramma_prev.acute = _char  # тип ударения
                    # TODO: ??? м.б. разделить оксию варию и камору
                elif _char in titles:
                    # если титло, выставить у предыдущей буквы флаг и титло
                    gramma_prev.is_titled = True
                    gramma_prev.titlo = _char
                elif _char == erok_comb:
                    gramma_prev.have_erok = True
                elif _char == Kendema:
                    gramma_prev.superscript = Kendema
                elif _char == dbl_grave:
                    gramma_prev.superscript = dbl_grave
                    gramma_prev.is_combined = True

            else:
                # остальные символы рассматриваются как буквы
                gramma_current.letter = _char
                # TODO: другие символы: тире, подчеркивание etc
                # TODO: обработка знака "тысяча" (должен быть в self.pref_symbols)
                packed_word.append(gramma_current)

        return packed_word

    def get_converted(self, titles_flag='off'):
        '''Возвращает преобразованное набором конвертеров слово (как unpack-текст с надстрочниками)

         общий подход
         За исключением замен некотрых отдельных букв (ъ, от, у, я)
         1. Получить текст без надстрочников (текстовый слой).
         2. Обработать его поиском и заменой (regex, (str.replace?)).
         TODO: м.б. выражение find в regex также запаковать
          и взять только текстовый слой, чтобы можно было
          указать в find слова как есть с надстрочниками
          напр. с ї
         3. Полученный измененный результат необходимо
         "запаковать" в WordPacked (в нем могут быть надстрочники).
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
            self.replacer_by_regex_compiled_list(regs_letters_in_word_compiled)

        # Ударения
        converted_packet = \
            self.replacer_by_regex_compiled_list(regs_acutes_compiled)

        # Титла
        if titles_flag == 'on':
            # Выставить титла
            converted_packet = \
                self.replacer_by_regex_compiled_list(regs_titles_set_compiled)

        converted_text = \
            self.get_text_unstripped(converted_packet.unpack())

        return converted_text

    def convert_separate_letters(self):
        """В исходном packet конвертирует отдельные буквы"""

        word_packed = self.packet
        c = word_packed.unpack()

        last_symbol = c[-1]

        # ъ в конце
        if last_symbol in cu_before_er:
            # TODO: проблема - предлоги 'В К С' в начале предложения
            # как отличить контекст - строчные или прописные буквы.
            # пока чаще контекст строчных => задать правило regex
            _er = 'ъ' if last_symbol.islower() else 'Ъ'
            word_packed.append(Gramma(_er))

        # е в начале слова
        if word_packed[0].letter == 'е':
            word_packed[0].letter = 'є'
        if word_packed[0].letter == 'Е':
            word_packed[0].letter = 'Є'

        # все у -> ꙋ
        word_packed = word_packed.replace_char('у', 'ꙋ')
        word_packed = word_packed.replace_char('У', 'Ꙋ')
        # ꙋ -> ᲂу
        if word_packed[0].letter == 'ꙋ':
            word_packed.pop(0)
            word_packed.insert(0, Gramma('у'))
            word_packed.insert(0, Gramma(unicNarrowO))
            word_packed[1].superscript = Zvatelce
        if word_packed[0].letter == 'Ꙋ':
            word_packed.pop(0)
            word_packed.insert(0, Gramma('у'))
            word_packed.insert(0, Gramma('О'))
            word_packed[1].superscript = Zvatelce

        # все я -> ѧ
        word_packed = word_packed.replace_char('я', 'ѧ')
        word_packed = word_packed.replace_char('Я', 'Ѧ')
        # е в начале слова
        if word_packed[0].letter == 'ѧ':
            word_packed[0].letter = 'ꙗ'
        if word_packed[0].letter == 'Ѧ':
            word_packed[0].letter = 'Ꙗ'

        return word_packed

    def replacer_by_regex_compiled_list(self, regex_compiled_lists):
        '''Заменяет текст в пакете по всем regexes-правилам из принятого списка

        :param regex_compiled_lists: список compiled regex-правил замен
        (список кортежей (re_compiled, Replace_part_of_reg_rule))
        :return: пакет с примененными regex заменами
        '''

        packet = self.packet
        for regex_tuple in regex_compiled_lists:
            packet = packet.regex_sub(regex_tuple)
        return packet

    def is_acuted(self):
        return self.pack().is_acuted()

    def is_acuted_old(self):
        # факт наличия в слове ударения
        acute_set = {Oxia, Varia, Kamora, Iso, Apostrof}
        superscript_layer = self.pack().get_superscripts_layer()
        # пересечение множеств
        set_of_acutes = set(superscript_layer).intersection(acute_set)
        if set_of_acutes:
            return set_of_acutes
        else:
            return None


def acute_util(string, type_of_operation='change_type'):
    '''Замена ударений в слове

    :param string: слово
    :param type_of_operation: тип операции [change_type, move_right, move_left]  (def=change_type)
    :return: слово с измененным ударением
    '''

    # FIXME: если ударение стоит ошибочно на согласной, то при перемещении - ошибка
    #  стр.893

    raw_word = RawWord(string)
    # сохранить пост и префиксы (для симолов до след. слова)
    word_prefix_part = raw_word.get_pref_symbols() if raw_word.get_pref_symbols() else ''
    word_post_part = raw_word.get_post_symbols() if raw_word.get_post_symbols() else ''

    word_packed = raw_word.pack()
    # new_word_packed = word_packed

    # множество ударений (в идеале - одно ударение в слове)
    # ТОЛЬКО ФАКТ вхождения
    # word_acutes_set = raw_word.is_acuted()
    word_acutes_set = word_packed.is_acuted()
    # список ударений (в идеале - одно ударение в слове)
    word_acutes_list = word_packed.get_acutes_list()

    # print("===", word_acutes_set)
    # print("@@@", word_acutes_list)

    superscript_layer = raw_word.pack().get_superscripts_layer()
    text_layer = raw_word.pack().get_text_layer()

    # длина слова (текстовый слой)
    word_length = len(superscript_layer)

    # если в слове есть ударение
    if word_acutes_set:
        # Если больше одного удаления (нештат)
        # TODO: сделать этот блок проверочным,
        #  т.е. при запуске этих функций
        #  сначала исправляется ошибка, а потом уже работает алгоритм.
        #  в коде: последующий if сделать elif
        # if len(word_acutes_set) > 1:
        if len(word_acutes_list) > 1:
            # - оставить только одно.
            # Можно сделать начальную проверку при работе с ударениями.
            # если ударений > 1 то оставить например, первое,
            # далее его можно перемещать <->
            # Также проверку на варию в середине слова - заменить на оксию.

            # получить индексы гласных под ударением (включая исо и апостроф)
            list_stressed_volwes = []
            gramma_index = 0
            for gramma in word_packed:
                if gramma.is_acuted:
                    list_stressed_volwes.append(gramma_index)
                gramma_index += 1
            # удалить ударение у всех букв, кроме первой
            list_stressed_volwes.pop(0)  # усечь список с началв
            for deleting_index in list_stressed_volwes:
                word_packed[deleting_index].de_acute()

            # обновить слой надстрочников
            superscript_layer = word_packed.get_superscripts_layer()
            # и множество ударений (д.б. только одно)
            # word_acutes_set = word_packed.is_acuted()
            word_acutes_list = word_packed.get_acutes_list()

        # если одно ударение (норма)
        # if len(word_acutes_set) == 1:
        if len(word_acutes_list) == 1:
            # acute_symbol = list(word_acutes_set)[0]
            acute_symbol = word_acutes_list[0]
            # позиция ударения
            acute_index = superscript_layer.index(acute_symbol)
            # ударная гласная
            acuted_letter = text_layer[acute_index]

            # #####################
            # Изменить тип ударения
            if type_of_operation == 'change_type':

                # TODO: уточнить проверку и исправление, если вария посередине слова,
                #  то первый запуск этой функции может исправить эту ошибку.
                #  А последующие соответственно уже будут менять по алгоитму.
                new_acute_symbol = ''
                new_acuted_letter = ''

                # учесть ОУ
                if acute_index == 1 \
                        and acuted_letter in {'У', 'у'} \
                        and acute_symbol in {Iso, Apostrof}:
                    acute_is_onik = True
                else:
                    acute_is_onik = False

                # если ударение в начале слова
                if acute_index == 0 or acute_is_onik:
                    new_acute_symbol = acute_cycler(Iso, Apostrof, acute=acute_symbol)

                # если ударение в конце или в середине слова
                else:
                    # если буквы изменяющиеся для множественного числа
                    acutes_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}

                    # если ударение в КОНЦЕ слова
                    if acute_index == word_length - 1:

                        # если меняется буква в конце слова
                        if acuted_letter in acutes_dic.keys() \
                                or acuted_letter in acutes_dic.values():
                            new_acuted_letter, new_acute_symbol = \
                                acute_cycler(Oxia, Varia, letter=acuted_letter, acute=acute_symbol)
                        # меняется только ударение
                        else:
                            new_acute_symbol = \
                                acute_cycler(Oxia, Varia, Kamora, acute=acute_symbol)

                    # если ударение в середине слова
                    else:
                        # если меняется буква в середине слова
                        if acuted_letter in acutes_dic.keys() \
                                or acuted_letter in acutes_dic.values():

                            # исправление ошибки: если вария в середине слова
                            # TODO: сделать это глобально
                            if acute_symbol == Varia:
                                acute_symbol = Oxia

                            new_acuted_letter, new_acute_symbol = \
                                acute_cycler(Oxia,  letter=acuted_letter, acute=acute_symbol)
                        # меняется только ударение
                        else:
                            new_acute_symbol = \
                                acute_cycler(Oxia, Kamora, acute=acute_symbol)

                # применить новые данные (ударение или букву)
                new_word_packed = word_packed
                if new_acute_symbol:
                    # заменить ударение
                    new_word_packed[acute_index].superscript = new_acute_symbol

                if new_acuted_letter:
                    # заменить букву
                    new_word_packed[acute_index].letter = new_acuted_letter

                # результат - новое слово
                return word_prefix_part + new_word_packed.unpack() + word_post_part

            # @@@@@@@@@@@@@@@@@@@@
            # Переместить ударение
            elif type_of_operation in ['move_right', 'move_left']:
                # некоторый общий код для move_right и move_left

                # Получить список индексов потенциально ударных гласных
                # из текстового слоя
                vowels_indexes_in_word = []  # список индексов
                letter_index = 0
                for gramma in raw_word.pack():
                    if gramma.letter in cu_vowels_for_stressed:
                        vowels_indexes_in_word.append(letter_index)
                    letter_index += 1

                # если есть куда перемещать ударение
                if len(vowels_indexes_in_word) > 1:

                    # определить позицию текущего ударения в списке vowels_indexes_in_word
                    # FIXME: error если ударение стоит на согласной
                    current_position_of_acute_index = vowels_indexes_in_word.index(acute_index)
                    # NOTE: цикличное перемещение по слову
                    new_acute_index = 0
                    if type_of_operation == 'move_right':
                        # учитываем последнюю букву
                        new_acute_index = vowels_indexes_in_word[0] \
                            if current_position_of_acute_index == len(vowels_indexes_in_word) - 1 \
                            else vowels_indexes_in_word[current_position_of_acute_index + 1]

                    elif type_of_operation == 'move_left':
                        # учитываем первую букву
                        new_acute_index = vowels_indexes_in_word[-1] \
                            if current_position_of_acute_index == 0 \
                            else vowels_indexes_in_word[current_position_of_acute_index - 1]

                    if new_acute_index != acute_index:
                        new_word_packed = word_packed
                        new_acuted_letter = new_word_packed[new_acute_index].letter
                        new_acute_symbol = ''

                        # обработать текущую букву acuted_letter
                        # если ударной была 'ѡ' или 'є'
                        # то при смене ударения - менять вид букв?

                        old_acuted_letter = acuted_letter
                        old_acute_symbol = ''

                        # если ижица, то проверить -
                        # без надстрочника (ударения) - согласная
                        if acuted_letter in "Ѵѵ" and acute_symbol != '':
                            old_acute_symbol = dbl_grave

                        # если і
                        if acuted_letter in "Іі":
                            old_acute_symbol = Kendema

                        # НЕ-КАМОРА
                        if acute_symbol in [Oxia, Varia, Iso]:

                            # Текущая первая буква (+ ᲂу) => оставляем только звательце
                            if acute_symbol == Iso:
                                old_acute_symbol = Zvatelce

                            # Новая буква - первая
                            if new_acute_index == 0 \
                                    or (new_acute_index == 1
                                        and new_acuted_letter == 'у'):
                                new_acute_symbol = Iso
                            # Новая буква - последняя
                            elif new_acute_index == word_length-1:
                                new_acute_symbol = Varia
                            # новая буква в середине слова
                            else:
                                new_acute_symbol = Oxia

                        # КАМОРА, мн.ч.
                        elif acute_symbol in [Kamora, Apostrof]:

                            # Текущая первая буква (+ ᲂу) => оставляем только звательце
                            if acute_symbol == Apostrof:
                                old_acute_symbol = Zvatelce

                            # Новая буква - первая (+ ᲂу)
                            if new_acute_index == 0 \
                                    or (new_acute_index == 1
                                        and new_acuted_letter == 'у'):
                                new_acute_symbol = Apostrof
                            else:
                                new_acute_symbol = Kamora

                            # если ударной становится 'о' или 'е' и множ. число то замена на 'ѡ' или 'є'
                            letters_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}
                            # может пригодиться
                            # letters_dic_rev = dict(zip(letters_dic.values(), letters_dic.keys()))
                            if new_acuted_letter in letters_dic.keys():
                                new_acuted_letter = letters_dic.get(new_acuted_letter, '')
                                new_acute_symbol = Oxia

                        # применить изменения
                        new_word_packed[acute_index].letter = old_acuted_letter
                        new_word_packed[acute_index].superscript = old_acute_symbol
                        new_word_packed[new_acute_index].letter = new_acuted_letter
                        new_word_packed[new_acute_index].superscript = new_acute_symbol

                        return word_prefix_part + new_word_packed.unpack() + word_post_part
                        # print(raw_word.get_text_unstripped(new_word_packed.unpack()))
                        # тоже самое, только без использования word_prefix_part и word_post_part

            # вывод результата (если было изменение) -
            # (сейчас реализовано в каждом блоке отдельно)
            # if new_word_packed != word_packed:
            #     return word_prefix_part + new_word_packed.unpack() + word_post_part

    else:
        return None


def acute_cycler(*args, **kwargs):
    '''заменяет ударение и букву.
    "движок" для acute_util (с параметром acute_change)

    :param args: кортеж ударений для выбора (Oxia|Varia|Kamora)
    :param kwargs: letter: буква, acute: текущее ударение (Oxia|Varia|Kamora)
    :return: ударение или (буква, ударение)
    '''

    acute = kwargs.get('acute', '')
    if not acute:
        return None
    letter = kwargs.get('letter', '')
    _lett = ''  # новая буква
    _ac = ''  # новое ударение

    if not args.count(acute):
        return None
    _pos = args.index(acute)

    if not letter:
        _ac = args[0] if _pos == len(args)-1 else args[_pos+1]
        return _ac
    else:
        ac_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}
        ac_dic_rev = dict(zip(ac_dic.values(), ac_dic.keys()))

        # в конце слова
        if len(args) > 1:
            if letter in ac_dic.keys():  # and  acute == (_lett, _ac):
                if acute == Oxia:
                    _ac = args[0] if _pos == len(args) - 1 else args[_pos + 1]
                    _lett = letter
                elif acute == Varia:
                    _ac = acute
                    _lett = ac_dic.get(letter, '')
            elif letter in ac_dic_rev.keys():
                if acute == Varia:
                    _lett = letter
                    _ac = args[0] if _pos == len(args) - 1 else args[_pos + 1]
                elif acute == Oxia:
                    _ac = acute
                    _lett = ac_dic_rev.get(letter, '')

        # в середине слова
        else:
            _ac = acute
            if letter in ac_dic.keys():
                _lett = ac_dic.get(letter, '')
            elif letter in ac_dic_rev.keys():
                _lett = ac_dic_rev.get(letter, '')

        return _lett, _ac


def letters_util(string, type_replace):
    '''Замена букв в слове

    :param string: слово
    :param type_replace: [0,1,2] -
        тип замены (ѻ|ѡ в начале (0) или о|ѡ (1) е|ѣ (2) в конце)
    :return: слово с измененными буквами
    '''

    raw_word = RawWord(string)
    # сохранить пост и префиксы (для симолов до след. слова)
    word_prefix_part = raw_word.get_pref_symbols() if raw_word.get_pref_symbols() else ''
    word_post_part = raw_word.get_post_symbols() if raw_word.get_post_symbols() else ''

    text_layer = raw_word.pack().get_text_layer()

    new_word_packed = raw_word.pack()
    _lett = ''
    letter_index = ''
    if type_replace == 0:
        letter_index = 0  # first letter
        processed_letter = text_layer[0]
        lett_dic = {'ѻ': 'ѡ', 'Ѻ': 'Ѡ'}
        lett_dic_rev = dict(zip(lett_dic.values(), lett_dic.keys()))

        if processed_letter in lett_dic.keys():
            _lett = lett_dic.get(processed_letter, '')
        elif processed_letter in lett_dic.values():
            _lett = lett_dic_rev.get(processed_letter, '')
    elif type_replace > 0:
        letter_index = -1  # last letter
        processed_letter = text_layer[-1]
        if type_replace == 1:
            _lett = letters_cycler('о', 'ѡ', letter=processed_letter)
        elif type_replace == 2:
            _lett = letters_cycler('е', 'ѣ', 'є', letter=processed_letter)

    if _lett:
        new_word_packed[letter_index].letter = _lett

    # return processed_letter
    return word_prefix_part + new_word_packed.unpack() + word_post_part


def letters_cycler(*args, **kwargs):
    '''циклически заменяет букву
    "движок" для letter_util

    :param args: кортеж букв для выбора (е|ѣ|є)
    :param kwargs: letter: буква
    :return: новая буква
    '''

    letter = kwargs.get('letter', '')
    if not args.count(letter):
        return None
    _pos = args.index(letter)
    _lett = args[0] if _pos == len(args) - 1 else args[_pos + 1]
    # cycle = {'е', 'ѣ', 'є'}
    return _lett


def get_search_and_replaced(string_source, re_compiled, replace):
    ''' Производит поиск и замену в строке

    :param string_source: исходная строка
    :param re_compiled: compiled regex (search part)
    :param replace: replace part of regex rule (with \1 \2 etc.)
    :return: (replaced string, match)
    '''

    new_string = string_source  # действует как фильтр
    re_obj = re_compiled

    match = re_obj.search(string_source)
    if match:
        new_string = re_obj.sub(replace, string_source)

    return new_string, match  # кортеж


def make_compiled_regs(tuple_regs):
    '''Компиляция кортежа regex-ов
    кортеж содержит правила (список) [Srch, Repl [,Flag]]

    :param tuple_regs: кортеж правил регулярных выражений из Regs.py
    :return: список кортежей (re_compiled, Replace_part_of_reg_rule)
    '''
    list_compiled = []
    # для каждого regex правила из кортежа
    for reg_rule in tuple_regs:
        # обработка флага regex ('i' - регистронезависимость)
        flags = reg_rule[2] if len(reg_rule) > 2 else ''
        if flags and flags.count('i') > 0:
            re_compiled = re.compile(reg_rule[0], re.U | re.X | re.I)
        else:
            re_compiled = re.compile(reg_rule[0], re.U | re.X)
        list_compiled.append((re_compiled, reg_rule[1]))
    return list_compiled


def get_string_converted(string, titles_flag='off'):
    '''Конвертирует переданную строку
    :type string: str
    :type titles_flag: str
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

    # init lists of compiled regexes

    global regs_letters_in_word_compiled
    global regs_acutes_compiled
    global regs_titles_set_compiled
    global regs_titles_open_compiled

    regs_letters_in_word_compiled = make_compiled_regs(regs_letters_in_word)
    regs_acutes_compiled = make_compiled_regs(regs_acutes)
    regs_titles_set_compiled = make_compiled_regs(regs_titles_set)
    regs_titles_open_compiled = make_compiled_regs(regs_titles_open)

    # шаблоны для поиска надстрочников (титла и остальные)
    pat_titles = r'[' + titles + ']'
    re_titled = re.compile(pat_titles, re.U | re.X)
    pat_superscripts = r'[' + Zvatelce + acutes + ']'
    re_superscript = re.compile(pat_superscripts, re.U | re.X)

    for w in string.split():
        # конвертация отдельного слова
        converted_string = w
        word_is_titled = False

        # TODO: учесть титла в числах
        # Предварительная оработка для раскрытия титла
        if titles_flag == 'open':
            # удалить другие надстрочники
            # (чтобы соответствовать строкам в regex_set)
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
        # TODO: учесть титла в числах
        if titles_flag != 'open' or word_is_titled:
            word = RawWord(w)
            # если строка - число буквами, то не менять
            if not word.pack().is_letters_number():
                converted_string = word.get_converted(titles_flag=titles_flag)

        # обработанные слова - в массив
        strings_converted.append(converted_string)

    # массив в строку
    return ' '.join(strings_converted)


def convert_string_with_digits(string):
    '''В строке выбирает цифры и пытается перевести их в буквы

    :param string: строка с возможными цифрами
    :return: новая строка с возможно преобразованными числами
    '''

    def replacer(m):
        '''Replacer for regex

        :param m: regex match object
        :return: string for replacing
        '''

        try:
            _d = int(m.group())
            if cu_format_int(_d):
                return cu_format_int(_d)
        except ValueError:
            pass

    # Проверка если "жирные" цифры (\uF430 - \uF439)
    bold_digits = {
        '': '0',
        '': '1',
        '': '2',
        '': '3',
        '': '4',
        '': '5',
        '': '6',
        '': '7',
        '': '8',
        '': '9',
    }
    if set(bold_digits.keys()).intersection(set(string)):
        # Замена по словарю
        for _d in bold_digits.keys():
            string = string.replace(_d, bold_digits[_d])

    # поиск чисел и замена на буквы
    pat = r'\d+'
    r = re.compile(pat, re.U)
    if r.search(string):
        return r.sub(replacer, string)


def debug(string):
    # debug only
    return RawWord(string).pack()