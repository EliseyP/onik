#!/usr/bin/python3
# _*_ coding: utf-8

# import copy
import re
from Regs import *
from RegsLetters import regs_letters_in_word
from Letters import *
from numerals import cu_format_int, cu_parse_int
from pathlib import Path

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
    (ф-ця convert_stripped принимает строку, и функцию конвертации)  
        
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
    Текст рабивается на слоа+промежутки convert_stripped()
    Функция-конвертер 
        convert_one_word для общей onik-обработки слова
        acute_util для работы с ударениями
        letters_util для работы с начальными и конечными буквами
      
    Создает объект класса RawWord (raw_word = RawWord(string)), 
    Создается объект класса WordPacked (метод RawWord.pack()), 
    кот-й в свою очередь состоит 
    из отдельных объектов класса Gramma - буква + надстрочник.
    
    С помощью различных методов RawWord и WordPacked выполняютсмя задачи onik-функций.
    Напр. основная задача перевода текста из русской орфографии в цся 
    (ф-ция get_string_converted) -
    использует метод RawWord.get_converted() (обертка для WordPacked.get_converted()) 
    
    Полученный результат распаковывается (метод WordPacked.unpack()).
    В ф-ции convert_stripped 
    к нему присоединяются пре- и -пост фрагменты (кавычки и пр.), 
    и конечный результат возвращается из функции в виде обычного текста.
    
    Некоторые задачи не требуют работы со слоями, в этом случае
    обработка текста обычная (convert_string_with_digits, convert_string_letters_to_digits) 
'''


class Gramma:
    # Одна буква с надстрочниками и др. атрибутами.

    def __init__(self, char, superscript=''):
        self.letter = char  # буква
        self.superscript = superscript  # надстрочник
        # вид ударения ['varia', 'oxia', 'kamora']
        self.acute = self.get_acute_symbol()
        self.have_zvatelce = False
        self.have_erok = False  # COMBINED !!!
        # self.is_first = False
        # self.is_last = False
        # self.is_vowel = False  # гласная
        # self.is_consonante = False  # согласная
        # ук, от?, ї с кендемой, ѷ ижица с дв. ударением
        self.is_combined = False
        self.titlo = ''  # титло
        self.is_titled = False  # имеет титло

    def __eq__(self, other):
        # проверка на равенство двух gramma
        return self.letter == other.letter and self.superscript == other.superscript

    def __str__(self):
        return self.get_full_letter_str()

    def __repr__(self):
        return self.get_full_letter_str()

    def get_full_letter_list(self):
        """Получить списком букву + надстрочник"""
        letter_with_superscripts = [self.letter]
        if self.get_superscript_flag():
            letter_with_superscripts.append(self.superscript)
        return letter_with_superscripts

    def get_full_letter_str(self):
        """Получить строкой букву + надстрочник"""
        return ''.join(self.get_full_letter_list())

    def get_acute_flag(self):
        """Получить признак ударения, исо и апостроф включены"""
        for _acute in Oxia, Varia, Kamora:
            if self.superscript.find(_acute) >= 0:
                return True
        return False

    def get_acute_symbol(self):
        """Получить символ ударения"""
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

    def is_letter_vowel(self):
        if self.letter in cu_vowels:
            return True
        return False

    def is_letter_consonant(self):
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

    def __str__(self):
        return self.unpack()

    def __repr__(self):
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
        return ''.join([gramma.get_full_letter_str() for gramma in self])

    def get_text_layer_list(self):
        '''
        :return: текстовый слой как список '''
        return [gramma.letter for gramma in self]

    def get_superscripts_layer_list(self):
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
        return ''.join(self.get_text_layer_list())

    def get_text_anacuted(self):
        '''
        :return: текст (строку) без ударений и звательца'''
        anacuted = ''
        for gramma in self:
            anacuted += gramma.letter
            if not (gramma.get_acute_flag() or gramma.get_zvatelce_flag()):
                anacuted += gramma.superscript
        return anacuted

    def imposing(self, packet_converted):
        '''Совершает послойное наложение двух packet:

        исходного и измененного (converted).

        дете́й + дѣт => дѣте́й
        свѧты́й + ст҃ый => ст҃ы́й

        :param packet_converted: измененный пакет
        :return: результат наложения пакетов.
        '''

        # Исходная и измененная строки текстового слоя
        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()

        packet_imposed = self  # результирующий пакет
        for i, gramma_converted in enumerate(packet_converted):
            # Изменяем текст

            # Новая буква-пакет, ее буква и надстрочник
            letter_converted = gramma_converted.letter  # буква
            superscript_converted = gramma_converted.superscript  # надстрочник

            superscript_new = packet_imposed[i].superscript
            if letter_converted != '':
                packet_imposed[i].letter = letter_converted

            # Изменяем надстрочники
            if superscript_converted != '':
                # Условия наложения надстрочников (кендема, исо, апостроф)

                # При накладывании кендемы на ударение - ударение не меняется
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

        def list_find_match_index_from_start(_s1, _s2):
            """Возвращает индекс последнего совпадающего элемента s1 и s2 с начала.

            :param _s1:
            :param _s2:
            :return:
            """

            matching_index = 0
            for i, _letter in enumerate(_s2):
                if _letter != _s1[i]:
                    return matching_index
                else:
                    matching_index = i
            return matching_index

        def list_find_match_index_from_end(_s1, _s2):
            """Возвращает индекс последнего совпадающего элемента s1 и s2 с конца.

            :param _s1:
            :param _s2:
            :return:
            """

            _s1_rev = list(reversed(_s1))
            _s2_rev = list(reversed(_s2))
            matching_index_end = list_find_match_index_from_start(_s1_rev, _s2_rev)
            if matching_index_end == 0:
                return 0
            elif matching_index_end == len(_s1) - 1:
                return matching_index_end
            else:
                result_index_end = len(_s1) - 1 - matching_index_end
                return result_index_end

        # Строки исходная и преобразованная
        _string = self.get_text_layer_string()
        _string_converted = packet_converted.get_text_layer_string()

        packet_source = self

        replaced_expanded_text = \
            RawWord(replace_expanded).pack().get_text_layer_string()

        # если find > replace (от -> ѿ)
        if len(match.group(0)) > len(replaced_expanded_text):
            # print(f'here {match.group(0)}|{replaced_expanded_text}')

            # Определить кол-во удаляемых символов.
            to_remove_amount = len(match.group(0)) - len(replaced_expanded_text)

            # Определить позицию удаляемых символов.

            # TODO: попробовать оставить фрагмент, в котором есть ударение
            # можно определить метод для поиска и замены с указанием
            # дополнительно - имя группы и позицию в ней символа с ударением
            # fr(find, rerplace, (group_name, pos))
            # fr(r'(?<acute>у)мъ', r'ᲂу҆́мъ', (acute,0))

            # Индекс последнего совпадения строк с начала.
            # TODO: Использовать совпадение F и R также и с конца.
            # list_find_match_index_from_end()
            matching_from_start = list_find_match_index_from_start(match.group(0), replaced_expanded_text)
            if matching_from_start > 0:
                to_remove_start_index = matching_from_start
            else:
                # Удаляются n символов после первого,
                # первый и остальные заменяются обычным наложением
                to_remove_start_index = match.start()

            # Возможен случай, когда ударение исходного фрагмента
            # наложится на новый, когда усечение
            # не затронет саму ударную гласную.
            # (Возможно и для других надстрочников?)
            # Вариант решения - отметить в regex букву
            # именованным сохранением <remove>
            # При обработке удалить перед наложением
            # у этого символа надстрочник.

            # Если в regex указана группа 'remove'
            if match.groupdict():
                if 'remove' in match.groupdict().keys():
                    to_remove_pos = match.start('remove')
                    packet_source[to_remove_pos].superscript = ''

            # Получить список индексов удаляемых эл-в
            to_remove_indexes_list = []
            for i in range(to_remove_amount):
                to_remove_indexes_list.append(to_remove_start_index + 1 + i)
            # Обратить список
            to_remove_indexes_list.reverse()
            # Удалить элементы, начиная с конца
            # (иначе удаление элементов сдвинет последующие индексы)
            for i in to_remove_indexes_list:
                try:
                    packet_source.pop(i)
                except IndexError as e:
                    return

            if len(packet_source) == len(packet_converted):
                # Применить обычное наложение
                packet_source.imposing(packet_converted)

        # Если find < replace (умъ -> ᲂумъ)
        # цель 1: вставить нужное кол-во букв
        # цель 2: сохранить ударение (если оно было в исх. слове)
        # Определить позицию и кол-во вставленных букв.
        # через match.group(0) match.start(0), match.end(0) и replace_expanded
        # если match.group(0) имел ударение:
        #   попробовать найти позицию для ударной буквы в новом фрагменте
        #   попробовать определить автоматически,
        #   по букве, если есть совпадение в процессе сравнивания F & R
        #   попробовать найти совпадение F и R с начала и с конца.
        #   ум -> оум - совпадение с конца.
        #   ум -> оум : накладываем с конца. 'ум' => 'муо'
        #
        if len(match.group(0)) < len(replaced_expanded_text):
            # Определить кол-во добавляемых символов
            to_add_amount = len(replaced_expanded_text) - len(match.group(0))
            # Определить позицию добавляемых символов
            # можно попробовать определить фрагмент с ударением
            to_add_start_index = match.start()
            to_add_indexes_list = []
            for i in range(to_add_amount):
                to_add_indexes_list.append((to_add_start_index + 1 + i, _string_converted[to_add_start_index + 1 + i]))

            # Обратить список
            to_add_indexes_list.reverse()
            # Вставить элементы, начиная с конца
            # (иначе вставка элементов сдвинет последующие индексы)
            for i, l in to_add_indexes_list:
                packet_source.insert_char(i, l)

            if len(packet_source) == len(packet_converted):
                # Применить обычное наложение
                packet_source.imposing(packet_converted)

        return packet_source

    def regex_sub(self, regex_tuple):
        '''В исходном пакете совершает замену по regex из полученного кортежа

        :param regex_tuple: кортеж (re_compiled, Replace_part_of_reg_rule)
        :return: пакет с заменой текста
        '''
        # Исходная строка
        _string_source = self.get_text_layer_string()
        converted_packet = self

        re_compiled, replace_part = regex_tuple

        # Получить новую строку (и сопутств. объект match)
        _string_replaced, match, = \
            get_search_and_replaced(_string_source, re_compiled, replace_part)
        if match:
            # Для работы с \1, \2, \g<name>
            replace_expanded = match.expand(replace_part)
            # Result of S&R -> to packet
            replaced_packet = \
                RawWord(_string_replaced).pack()
            replaced_expanded_text = \
                RawWord(replace_expanded).pack().get_text_layer_string()
            # Impose s&r and source
            # Если текст найденного и для замены совпадают по длине
            if len(replaced_expanded_text) == \
                    len(match.group(0)):
                # Простое наложение двух пакетов
                converted_packet = \
                    self.imposing(replaced_packet)
            # Если текст найденного и для замены НЕ совпадают по длине
            else:
                # Сложное наложение двух пакетов
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

    def replace_superscript(self, find, replace):
        # FIXME: gramma.acute сохраняется неизменной
        #  после, например, "титлования".
        #  При этом gramma.superscript - меняется!
        # Исправить
        packet = self
        for gramma in packet:
            if gramma.superscript == find:
                gramma.superscript = replace
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

    def get_acutes_set(self):
        '''
        :return: множество ударений в слове.
        Если ошибочно две оксии, то покажет ОДНУ
        '''
        acute_set = {Oxia, Varia, Kamora, Iso, Apostrof}
        # результат пересечения множеств
        return set(self.get_superscripts_layer_list()).intersection(acute_set)

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
        '''Определяет - является ли слово числом в буквенной записи.

        :return: Bool
        '''
        # TODO: слово мт҃и
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
        elif re.search('^(' + thousands_re + ')?[' + lnum_20_90 + ']' + titlo + '([' + lnum_1_9 + '])?$', string,
                       re.U | re.X):
            return True
        # р҃-ц҃ ;р҃а..р҃ѳ ; р҃і,р҃к..ц҃ч ; 101-109 ... 901-909; 110,120...990; 1101-1109...1901-1909; 1110,1120...1990
        elif re.search('^(' + thousands_re + ')?[' + lnum_100_900 + ']' + titlo + '([' + lnum_1_90 + '])?$', string,
                       re.U | re.X):
            return True
        # ра҃і ; 111-119 ... 911-919; 1111-1119...1911-1919
        elif re.search('^(' + thousands_re + ')?[' + lnum_100_900 + ']' + '[' + lnum_1_9 + ']' + titlo + 'і$', string,
                       re.U | re.X):
            return True
        # рк҃а цч҃ѳ ; 121-199 ... 921-999; 1121-1199 .. 1921-1999
        elif re.search(
                '^(' + thousands_re + ')?[' + lnum_100_900 + ']' + '[' + lnum_20_90 + ']' + titlo + '[' + lnum_1_9 + ']$',
                string, re.U | re.X):
            return True
        #  ҂а҃,҂в҃ - ҂ѳ ҃; ҂а҃а - ҂ѳ ҃ц ; 1000,2000-9000; 1001,1002-1010 ... 100100-900 900
        elif re.search('^' + thousands_re + titlo + '(' + lnum_1_900 + ')?$', string, re.U | re.X):
            return True
        else:
            return False

    def get_converted(self, titles_flag='off'):
        '''Возвращает преобразованное набором конвертеров слово (как pack-текст с надстрочниками)

         Общий подход:
         За исключением замен некотрых отдельных букв (ъ, от, у, я)
         1. Получить текст без надстрочников (текстовый слой).
         2. Обработать его поиском и заменой (regex, (str.replace?)).
         3. Полученный измененный результат необходимо
         "запаковать" в WordPacked (в нем могут быть надстрочники).
         4. Полученный временный (replaced) пакет
         накладывается отдельно по слоям на исходный пакет
         через imposing(packet_converted)
         результатом будет новый packet (imposed)
        '''

        # Камора при сокращении с титлом перезаписывается в оксию,
        # в соответствии с regex-правилами.
        _kamora_flag: bool = False
        try:
            _pos = self.get_acutes_list().index(Kamora)
        except ValueError:
            pass
        else:
            _kamora_flag = True

        # Отдельные буквы ꙋ ᲂу ѡ ѿ ꙗ ѧ є ъ ѽ.
        converted_packet = self.convert_separate_letters()

        # Преобразование через imposing

        # Буквы в слове.
        converted_packet = self.replacer_by_regex_compiled_list(regs_letters_in_word_compiled)

        # Ударения.
        converted_packet = self.replacer_by_regex_compiled_list(regs_acutes_compiled)

        # Титла.
        if titles_flag == 'on':
            # Выставить титла.
            converted_packet = converted_packet.replacer_by_regex_compiled_list(regs_titles_set_compiled)
            # Восстановление каморы.
            if _kamora_flag:
                _acute_symbol = converted_packet.get_acutes_list()[0]
                converted_packet = converted_packet.replace_superscript(_acute_symbol, Kamora)

        return converted_packet

    def convert_separate_letters(self):
        """В исходном packet конвертирует отдельные буквы"""

        word_packed = self
        last_symbol = word_packed.unpack()[-1]
        # ъ в конце
        # TODO: ъ в конце чисел. При csl2russian происходят некоторые ложные срабатывания.
        if last_symbol in cu_before_er:
            _erok_symbol = 'ъ' if last_symbol.islower() else 'Ъ'
            word_packed.append(Gramma(_erok_symbol))

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
        packet = self
        for regex_tuple in regex_compiled_lists:
            packet = self.regex_sub(regex_tuple)
        return packet

    def get_text_layer_as_ucs(self, split_monograph=False):
        """Получить текстовый слой в UCS виде.
        :param split_monograph: разбивать ли монограф.
        :return: str.
        """
        from UCS_Letters import UCS
        from Ft import unicode_to_ucs_fonttable, unicode_to_ucs_upper_fonttable
        _unic_smalls = "абвгдеєѣжзѕꙁиіѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ"
        _converted_list = []
        uk_flag = False
        _previous_symbol = ''
        for gramma in self:
            full_letter_str = gramma.get_full_letter_str()
            # Если полное совпадение в словаре.
            if full_letter_str in unicode_to_ucs_fonttable.keys():
                ucs_string = unicode_to_ucs_fonttable.get(full_letter_str, full_letter_str)
            # Посимвольная выборка из словаря (кроме исо и апострофа).
            else:
                _letter = full_letter_str[0]
                _superscripts = full_letter_str[1:]
                _ucs_letters = _letter
                _ucs_superscripts = _superscripts

                # Если Ук или ук
                if _letter in (unicNarrowO, unicCapitalO):
                    uk_flag = True
                    _previous_symbol = _letter
                    continue

                if _letter == unicSmallU and uk_flag:
                    _letter = _previous_symbol + _letter
                    uk_flag = False
                    _previous_symbol = ''

                if _superscripts in (Iso, Apostrof):
                    if _letter in cu_cap_letters_text \
                            and _letter not in (unicCapitalUk, unicSmallUk):
                        if _superscripts == Iso:
                            _ucs_superscripts = UCS.ISO_UPP
                        elif _superscripts == Apostrof:
                            _ucs_superscripts = UCS.APOSTROF_UPP
                        _ucs_letters = unicode_to_ucs_fonttable.get(_letter, _letter)
                    elif _letter in _unic_smalls \
                            or _letter in (unicCapitalUk, unicSmallUk):
                        if _superscripts == Iso:
                            _ucs_superscripts = UCS.ISO
                        elif _superscripts == Apostrof:
                            _ucs_superscripts = UCS.APOSTROF

                        if _letter == unicCapitalUk:
                            if _superscripts == Iso:
                                _ucs_letters = UCS.CAPS.OUK_AND_ISO
                                _ucs_superscripts = ''
                        elif _letter == unicSmallUk:
                            if _superscripts == Iso:
                                _ucs_letters = UCS.SMALL.OUK_AND_ISO
                                _ucs_superscripts = ''
                        else:
                            _ucs_letters = unicode_to_ucs_fonttable.get(_letter, _letter)
                # Другие надстрочники
                elif _superscripts not in (Iso, Apostrof):
                    if _letter in cu_cap_letters_text \
                            and _letter not in (unicCapitalUk, unicSmallUk):
                        # Надстрочники для прописных.
                        _ucs_superscripts = unicode_to_ucs_upper_fonttable.get(_superscripts, _superscripts)
                        _ucs_letters = unicode_to_ucs_fonttable.get(_letter, _letter)
                    elif _letter in _unic_smalls \
                            or _letter in (unicCapitalUk, unicSmallUk):
                        # Надстрочники для строчных.
                        _ucs_superscripts = unicode_to_ucs_fonttable.get(_superscripts, _superscripts)

                        # УК и другие надстрочники.
                        if _letter == unicCapitalUk:
                            _ucs_letters = UCS.CAPS.OUK
                            if _superscripts == Zvatelce:
                                _ucs_letters = UCS.CAPS.OUK_AND_ZVATELCO
                                _ucs_superscripts = ''
                        # ук и другие надстрочники.
                        elif _letter == unicSmallUk:
                            _ucs_letters = UCS.SMALL.OUK
                            if _superscripts == Zvatelce:
                                _ucs_letters = UCS.SMALL.OUK_AND_ZVATELCO
                                _ucs_superscripts = ''
                        # Остальные буквы и другие надстрочники
                        else:
                            _ucs_letters = unicode_to_ucs_fonttable.get(_letter, _letter)
                ucs_string = _ucs_letters + _ucs_superscripts

                if full_letter_str in unicode_to_ucs_fonttable.keys():
                    ucs_string = unicode_to_ucs_fonttable.get(full_letter_str, full_letter_str)

            # Пси строчное с титлом - ставить широкое верхнее титло.
            if full_letter_str == unicSmallPsi + Titlo:
                ucs_string = UCS.SMALL.PSI + UCS.TITLO_UPP_BROAD

            # Если нужно отделить надстрочники:
            if split_monograph:
                ucs_string = UCS.split_monograph_dic.get(ucs_string, ucs_string)

            _converted_list.append(ucs_string)

        converted_string = ''.join(_converted_list)

        return converted_string


class RawWord:
    # слово (unstripped-строка)
    # слова содержат только [знак тысячи]буквы + надстрочники

    def __init__(self, string):
        self.string = str(string)

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string

    def pack(self):
        '''Разбивает слово string на объекты класса Gramma

        вместе с самой буквой - флаги и значения надстрочников и т.д.

        :return: packed_word
        '''
        packed_word = WordPacked([])
        string = self.string

        for i, _char in enumerate(string):
            gramma_current = Gramma('')  # текущий gramma
            gramma_prev = Gramma('')  # Предыдущий gramma, начиная с 1
            if i > 0:
                # Потенциальная проблема:
                # В текущую ф-цию pack() может поступить некорректная строка
                # начинающаяся например с надстрочника (или двух).
                # Это происходит, если вышестоящая разбивка на pre_part и word_part
                # разбили слово по символу не входящим в определенный здесь набор
                # цся букв (например "Э"). Соответственно, если после такого
                # "неизвестноого" символа стоят надстрочники, они попадут в текущ-ю
                # ф-цию в начале string
                # Но дальнейшие операции расчитывают на то, что надстрочники
                # следуют только за буквами, и надстрочник "помещается"
                # в предшеств-ю Gramma.
                # Варианты решения: Проверка
                # (Исходить из того что на выходе должен быть packed =>
                # надстрочники на этом этапе точно потеряются)
                # В packed должно попасть все после этих надстрочников
                # 1. Выше уровнем при разборе через regexp
                #   (Точно) сохранится надстрочник(и)
                #   UPD: реализовано.
                # 2. В этом блоке через if packed_word:
                # Надстрочник(-и) при этом не сохраняются
                if packed_word:
                    gramma_prev = packed_word[-1]

            # elif i == 0:
            #     gramma_current.is_first = True

            # Если текущий символ - буква
            if _char in cu_letters_text or \
                    _char == latin_i or \
                    _char in combined_monosymbols_dic:
                # латинское i -> ї
                if _char == latin_i:
                    _char = unicSmallUkrI
                    gramma_current.superscript = Kendema

                gramma_current.letter = _char
                # Проверка на слитные с надстрочником символы  ѷ ї
                if _char in combined_monosymbols_dic:
                    gramma_current.letter = combined_monosymbols_dic.get(_char, _char)[0]
                    gramma_current.superscript = combined_monosymbols_dic.get(_char, _char)[1]
                    gramma_current.is_combined = True

                packed_word.append(gramma_current)

            # Если текущий символ - надстрочник
            elif _char in cu_superscripts:
                # выставить флаг и занести символ (к предыдущей букве)

                # Если у предыдущего символа уже есть надстрочник
                # (в том числе исправление ошибок набора - два ударения подряд и т.п.)
                if gramma_prev.get_superscript_flag():
                    # Если текущий символ - часть комбинированного надстрочника,
                    # он добавляется к свое паре (остальные некорректные надстрочники отбрасываются).
                    if gramma_prev.get_zvatelce_flag() and _char in [Oxia, Varia, Kamora]:
                        # (Звательце+Камора = breve+pokrytie)
                        # Исо, Апостроф, breve+pokrytie
                        gramma_prev.superscript += _char  # если двойной то добавить к уже имеющемуся
                    elif gramma_prev.superscript in under_pokrytie and _char == pokrytie:
                        # Буквенное титло
                        gramma_prev.superscript += _char
                    elif gramma_prev.superscript == Kendema and _char == Oxia:
                        # ошибка если оксия после кендимы у i - она должна заменять ее
                        gramma_prev.superscript = _char
                else:
                    # gramma_prev.have_superscript = True
                    gramma_prev.superscript = _char

                # Установка дополн-х свойств
                # (основные уже выставлены .letter и .superscript)
                if _char == Zvatelce:
                    # Если звательце, выставить у предыдущей буквы флаг
                    gramma_prev.have_zvatelce = True
                elif _char in acutes:
                    # Если ударение, выставить у предыдущей буквы:
                    gramma_prev.acute = _char  # тип ударения
                elif _char in titles:
                    # Если титло, выставить у предыдущей буквы флаг и титло
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
                # Остальные символы рассматриваются и добавляются как буквы
                gramma_current.letter = _char
                # TODO: ??? обработка знака "тысяча" (должен быть в self.pref_symbols)
                packed_word.append(gramma_current)

        return packed_word

    def get_converted(self, titles_flag='off'):
        _pack = self.pack()
        # Если строка - число буквами, то не менять.
        if not _pack.is_letters_number():
            converted_packet = _pack.get_converted(titles_flag)
            return converted_packet.unpack()
        else:
            return None

    def get_ucs_string(self, split_monograph=False):
        """Получить строку UCS.

        :param split_monograph: разбивать грамму на букву+надстрочник
        :return: str
        """
        _pack = self.pack()
        converted_string = _pack.get_text_layer_as_ucs(
            split_monograph=split_monograph)
        return converted_string


def acute_util(string, type_of_operation='change_type'):
    '''Замена ударений в слове

    :param string: слово
    :param type_of_operation: тип операции [change_type, move_right, move_left]  (def=change_type)
    :return: слово с измененным ударением
    '''

    raw_word = RawWord(string)
    word_packed = raw_word.pack()

    # если нет ударений
    if not word_packed.get_acutes_set():
        if type_of_operation == 'move_to_end':
            new_word_packed = word_packed
            # get last letter in word.
            last_letter = new_word_packed[-1]
            # проверить - гласная ли
            if last_letter.is_letter_vowel():
                # set varia for last letter
                last_letter.superscript = Varia
                return new_word_packed.unpack()
            else:
                return None
        else:
            # Если нет ударений, но подразумевается что после вставки оно будет изменено,
            # то выставить ударение для первой гласной, чтобы дальнейшие ф-ции
            # изменили его или его положение.
            # (Если нужно только вставить оксию на первой гласной,
            # можно вызвать ф-цию add_oxia_for_unacuted_word_handler())
            _string = add_oxia_for_unacuted_word_handler(string)
            # Новое word_packed для работы функций
            word_packed = RawWord(_string).pack()

    # Список ударений (в идеале - одно ударение в слове)
    word_acutes_list = word_packed.get_acutes_list()

    superscript_layer = word_packed.get_superscripts_layer_list()
    text_layer = word_packed.get_text_layer_list()
    # print(f'== {text_layer}')

    # Длина слова (текстовый слой)
    word_length = len(superscript_layer)

    # Если в слове есть ударение
    if word_packed.get_acutes_set():
        # Если больше одного удаления (нештат)
        if len(word_acutes_list) > 1:
            # Оставить только одно (первое)

            # получить индексы гласных под ударением (включая исо и апостроф)
            list_stressed_volwes = []
            for gramma_index, gramma in enumerate(word_packed):
                if gramma.get_acute_flag():
                    list_stressed_volwes.append(gramma_index)

            # удалить ударение у всех букв, кроме первой
            list_stressed_volwes.pop(0)  # усечь список с началв
            for deleting_index in list_stressed_volwes:
                word_packed[deleting_index].de_acute()

            # обновить слой надстрочников
            superscript_layer = word_packed.get_superscripts_layer_list()
            # и множество ударений (д.б. только одно)
            word_acutes_list = word_packed.get_acutes_list()

        # Если одно ударение (норма)
        if len(word_acutes_list) == 1:
            acute_symbol = word_acutes_list[0]
            # Позиция ударения
            acute_index = superscript_layer.index(acute_symbol)
            # Ударная гласная
            acuted_letter = text_layer[acute_index]
            # Получить список индексов потенциально ударных гласных
            # из текстового слоя
            vowels_indexes_in_word = []  # список индексов ударных гласных
            for letter_index, gramma in enumerate(word_packed):
                if gramma.letter in cu_vowels_for_stressed:
                    vowels_indexes_in_word.append(letter_index)

            # #####################
            # Изменить тип ударения
            if type_of_operation == 'change_type':

                new_acute_symbol = ''
                new_acuted_letter = ''

                # Учесть ОУ
                if acute_index == 1 \
                        and acuted_letter in {'У', 'у'} \
                        and acute_symbol in {Iso, Apostrof}:
                    acuted_is_onik = True
                else:
                    acuted_is_onik = False

                # Если ударение в начале слова
                if acute_index == 0 or acuted_is_onik:
                    new_acute_symbol = acute_cycler(Iso, Apostrof, acute=acute_symbol)

                # Если ударение в конце или в середине слова
                else:
                    # Если буквы изменяющиеся для множественного числа
                    changing_letters_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}

                    # Если ударение в КОНЦЕ слова
                    if acute_index == word_length - 1:

                        # Если меняется буква в конце слова
                        if acuted_letter in changing_letters_dic.keys() \
                                or acuted_letter in changing_letters_dic.values():
                            new_acuted_letter, new_acute_symbol = \
                                acute_cycler(Oxia, Varia, letter=acuted_letter, acute=acute_symbol)
                        # Меняется только ударение
                        else:
                            new_acute_symbol = \
                                acute_cycler(Oxia, Varia, Kamora, acute=acute_symbol)

                    # Если ударение в середине слова
                    else:
                        # Исправление ошибки: если вария в середине слова
                        if acute_symbol == Varia:
                            acute_symbol = Oxia

                        # Если меняется буква в середине слова
                        if acuted_letter in changing_letters_dic.keys() \
                                or acuted_letter in changing_letters_dic.values():
                            # исправление ошибки набора, когда вместо е-широкого или омеги - камора
                            if acute_symbol == Kamora:
                                acute_symbol = Oxia

                            new_acuted_letter, new_acute_symbol = \
                                acute_cycler(Oxia, letter=acuted_letter, acute=acute_symbol)
                        # Меняется только ударение
                        else:
                            new_acute_symbol = \
                                acute_cycler(Oxia, Kamora, acute=acute_symbol)

                # Применить новые данные (ударение или букву)
                new_word_packed = word_packed
                if new_acute_symbol:
                    # Заменить ударение
                    new_word_packed[acute_index].superscript = new_acute_symbol

                if new_acuted_letter:
                    # Заменить букву
                    new_word_packed[acute_index].letter = new_acuted_letter

                # Результат - новое слово
                return new_word_packed.unpack()

            # @@@@@@@@@@@@@@@@@@@@
            # Переместить ударение
            elif type_of_operation in ['move_right', 'move_left', 'move_to_end']:
                # некоторый общий код для move_right и move_left

                # Если есть куда перемещать ударение
                # Если ударение ошибочно на согласной, то нужна х.о. гласная
                # поэтому > 0
                current_position_of_acute_index = 0
                if len(vowels_indexes_in_word) > 0:
                    acute_above_vowel = True
                    # Определить позицию текущего ударения в списке vowels_indexes_in_word
                    if acuted_letter in cu_vowels_for_stressed:
                        current_position_of_acute_index = vowels_indexes_in_word.index(acute_index)

                    # Если ударение стоит на согласной
                    else:
                        acute_above_vowel = False
                        # Найти ближайшую ударную гласную
                        b = f = acute_index  # backward & forward indexes
                        while f < word_length or b >= 0:
                            b -= 1
                            f += 1
                            # Move backward
                            if text_layer[b] in cu_vowels_for_stressed:
                                current_position_of_acute_index = vowels_indexes_in_word.index(b)
                                break
                            # Move forward
                            elif text_layer[f] in cu_vowels_for_stressed:
                                current_position_of_acute_index = vowels_indexes_in_word.index(f)
                                break

                    # цикличное перемещение по слову
                    new_acute_index = 0
                    if type_of_operation == 'move_right':
                        # Учитываем последнюю букву
                        if current_position_of_acute_index == \
                                len(vowels_indexes_in_word) - 1:
                            new_acute_index = vowels_indexes_in_word[0]
                        else:
                            # Случай, если в слове одна ударная гласная, и ударение ошибочно не над ней
                            if not acute_above_vowel and len(vowels_indexes_in_word) == 1:
                                current_position_of_acute_index = -1  # чтобы выйти на первую гласную
                            new_acute_index = vowels_indexes_in_word[current_position_of_acute_index + 1]

                    elif type_of_operation == 'move_left':
                        # Учитываем первую букву
                        new_acute_index = vowels_indexes_in_word[-1] \
                            if current_position_of_acute_index == 0 \
                            else vowels_indexes_in_word[current_position_of_acute_index - 1]

                    elif type_of_operation == 'move_to_end':
                        # если последняя буква - гласная
                        if word_packed[-1].is_letter_vowel():
                            # новый позиция для ударения - последняя буква
                            new_acute_index = word_length - 1

                    if new_acute_index != acute_index:
                        new_word_packed = word_packed
                        new_acuted_letter = new_word_packed[new_acute_index].letter
                        new_acute_symbol = ''

                        # Обработать текущую букву acuted_letter
                        # если ударной была 'ѡ' или 'є'
                        # то при смене ударения - менять вид букв?

                        old_acuted_letter = acuted_letter
                        old_acute_symbol = ''

                        # Если ижица, то проверить -
                        # без надстрочника (ударения) - согласная
                        if acuted_letter in "Ѵѵ" and acute_symbol != '':
                            old_acute_symbol = dbl_grave

                        # Если і
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
                            elif new_acute_index == word_length - 1:
                                new_acute_symbol = Varia
                            # Новая буква в середине слова
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

                            # Если ударной становится 'о' или 'е' и множ. число то замена на 'ѡ' или 'є'
                            letters_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}
                            if new_acuted_letter in letters_dic.keys():
                                new_acuted_letter = letters_dic.get(new_acuted_letter, '')
                                new_acute_symbol = Oxia

                        # Применить изменения
                        new_word_packed[acute_index].letter = old_acuted_letter
                        new_word_packed[acute_index].superscript = old_acute_symbol
                        new_word_packed[new_acute_index].letter = new_acuted_letter
                        new_word_packed[new_acute_index].superscript = new_acute_symbol

                        # return word_prefix_part + new_word_packed.unpack() + word_post_part
                        return new_word_packed.unpack()
                    # Исправление ошибочной оксии в конце
                    elif new_acute_index == acute_index and acute_symbol == Oxia:
                        new_word_packed = word_packed
                        new_word_packed[acute_index].superscript = Varia
                        return new_word_packed.unpack()


def acute_cycler(*args, **kwargs):
    '''Заменяет ударение и букву.

    "движок" для acute_util (с параметром acute_change)

    :param args: кортеж ударений для выбора (Oxia|Varia|Kamora)
    :param kwargs: letter: буква, acute: текущее ударение (Oxia|Varia|Kamora)
    :return: ударение или (буква, ударение)
    '''

    acute = kwargs.get('acute', '')
    if not acute:
        return None
    letter = kwargs.get('letter', '')
    new_letter = ''
    new_acute = ''

    if not args.count(acute):
        return None
    _pos = args.index(acute)

    if not letter:
        new_acute = args[0] if _pos == len(args) - 1 else args[_pos + 1]
        return new_acute
    else:
        changing_letters_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}
        changing_letters_dic_rev = \
            dict(zip(changing_letters_dic.values(), changing_letters_dic.keys()))

        # В конце слова
        if len(args) > 1:
            if letter in changing_letters_dic.keys():
                if acute == Oxia:
                    new_acute = args[0] if _pos == len(args) - 1 else args[_pos + 1]
                    new_letter = letter
                elif acute == Varia:
                    new_acute = acute
                    new_letter = changing_letters_dic.get(letter, '')
            elif letter in changing_letters_dic_rev.keys():
                if acute == Varia:
                    new_letter = letter
                    new_acute = args[0] if _pos == len(args) - 1 else args[_pos + 1]
                elif acute == Oxia:
                    new_acute = acute
                    new_letter = changing_letters_dic_rev.get(letter, '')

        # В середине слова
        else:
            new_acute = acute
            if letter in changing_letters_dic.keys():
                new_letter = changing_letters_dic.get(letter, '')
            elif letter in changing_letters_dic_rev.keys():
                new_letter = changing_letters_dic_rev.get(letter, '')

        return new_letter, new_acute


def letters_util(string, type_replace):
    '''Замена букв в слове

    :param string: слово
    :param type_replace: [0,1,2] -
        тип замены (ѻ|ѡ в начале (0) или о|ѡ (1) е|ѣ (2) в конце)
    :return: слово с измененными буквами
    '''

    # TODO: заменить числовые значения type_replace на осмысленные строковые
    raw_word = RawWord(string)
    new_word_packed = raw_word.pack()
    text_layer = new_word_packed.get_text_layer_list()

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
    elif type_replace in [1, 2]:
        letter_index = -1  # last letter
        processed_letter = text_layer[-1]
        if type_replace == 1:
            _lett = letters_cycler('о', 'ѡ', letter=processed_letter)
        elif type_replace == 2:
            _lett = letters_cycler('е', 'ѣ', 'є', letter=processed_letter)
    elif type_replace == 3:
        # ударные буквы [и ї ѷ]
        _index = 0
        for _gramma in new_word_packed:
            if _gramma.get_acute_flag():
                processed_letter = _gramma.letter
                if processed_letter in ['и', 'і', 'ѵ']:
                    letter_index = _index
                    _lett = letters_cycler('и', 'і', 'ѵ', letter=processed_letter)
                    break
            _index += 1
    elif type_replace == 4:
        # Ударные е є ѣ
        _index = 0
        for _gramma in new_word_packed:
            if _gramma.get_acute_flag():
                processed_letter = _gramma.letter
                if processed_letter in ['е', 'є', 'ѣ']:
                    letter_index = _index
                    _lett = letters_cycler('е', 'ѣ', 'є', letter=processed_letter)
                    break
            _index += 1

    if _lett:
        new_word_packed[letter_index].letter = _lett

    return new_word_packed.unpack()


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

    def _gen_compiled_list():
        # для каждого regex правила из кортежа
        for reg_rule in tuple_regs:
            # обработка флага regex ('i' - регистронезависимость)
            flags = reg_rule[2] if len(reg_rule) > 2 else ''
            if flags and flags.count('i') > 0:
                re_compiled = re.compile(reg_rule[0], re.U | re.X | re.I)
            else:
                re_compiled = re.compile(reg_rule[0], re.U | re.X)

            yield re_compiled, reg_rule[1]

    return list(_gen_compiled_list())


def get_string_converted(string, titles_flag='off'):
    '''Конвертирует переданную строку
    :type string: str
    :type titles_flag: str
    :param string: строка (параграфа)
    :param titles_flag: титла - [on|off*|open|onlyopen].
        on - ставить титла.
        off - не ставить (по умолч.)
        open - раскрыть титла.
        onlyopen - только раскрыть титла (для csl2russian)
    :return: преобразованная строка
    '''
    # try:
    #     # try load cython compiled .so
    #     from getstrcnv import get_string_converted as _g
    #     return _g(string, titles_flag='off')
    # except:  # ModuleNotFoundError
    # init lists of compiled regexes
    global regs_letters_in_word_compiled
    global regs_acutes_compiled
    global regs_titles_set_compiled
    global regs_titles_open_compiled

    if not regs_letters_in_word_compiled:
        regs_letters_in_word_compiled = make_compiled_regs(regs_letters_in_word)
    if not regs_acutes_compiled:
        regs_acutes_compiled = make_compiled_regs(regs_acutes)
    if not regs_titles_set_compiled and titles_flag == 'on':
        regs_titles_set_compiled = make_compiled_regs(regs_titles_set)
    if not regs_titles_open_compiled and titles_flag in ['open', 'onlyopen']:
        regs_titles_open_compiled = make_compiled_regs(regs_titles_open)

    # шаблоны для поиска надстрочников (титла и остальные)
    pat_titles = r'[' + titles + ']'
    re_titled = re.compile(pat_titles, re.U | re.X)
    pat_superscripts = r'[' + Zvatelce + acutes + ']'
    re_superscript = re.compile(pat_superscripts, re.U | re.X)
    pat_acutes_without_kamora = r'[' + Oxia + Varia + dbl_grave + ']'
    re_acutes_without_kamora = re.compile(pat_acutes_without_kamora, re.U | re.X)

    def convert_one_word(word_string: str, flags=''):
        # конвертация отдельного слова
        converted_string = word_string
        word_is_titled: bool = False
        word_have_camora: bool = False

        # TODO:
        # Проблема: при конвертации в гражд-й шрифт:
        # При раскрытии титла если происходит полная конвертация,
        # то теряется ударение (некоторые автоматически выставляются после)
        # Если не проводить полную конвертацию, то ударения мешают раскрытию титла (некоторых)
        # (в reg-правилах нет ударений)

        if word_string.find(Kamora) != -1:
            word_have_camora = True

        # Предварительная обработка для раскрытия титла
        if titles_flag in ['open', 'onlyopen']:
            # Удалить другие надстрочники
            # (чтобы соответствовать строкам в regex_set)
            # UPD_1: проблема! UPD: но не для onlyopen (сохранить ударения!)
            if re_superscript.search(word_string):  # and not titles_flag == 'onlyopen':
                word_string = re_superscript.sub('', word_string)
            # Если в слове есть титло
            if re_titled.search(word_string):
                word_is_titled = True
                for r_obj, replace in regs_titles_open_compiled:
                    if r_obj.search(word_string):
                        word_string = r_obj.sub(replace, word_string)

        # Для csl2russian не проводить конвертацию, только раскрыть титла. См. todo_выше
        # if titles_flag == 'onlyopen':
        #     return word_string

        # Основная конвертация
        # при опции 'раскрытие титла' обработка только слов с титлами.
        if titles_flag not in ['open', 'onlyopen'] or word_is_titled:
            raw_word = RawWord(word_string)
            _converted_string = raw_word.get_converted(titles_flag=titles_flag)
            if word_have_camora:
                if re_acutes_without_kamora.search(_converted_string):
                    _converted_string = re_acutes_without_kamora.sub(Kamora, _converted_string)

            if _converted_string:
                converted_string = _converted_string

        return converted_string

    return convert_unstripped(string=string, converter=convert_one_word, flags='')


def convert_unstripped(string, converter, flags=''):
    '''Конвертация unstripped-строки (буквы + пробелы, пунктуация и проч.)

    :param string: исходная строка (unstripped)
    :param converter: функция конвертации одного слова
    :param flags:
    :return: конвертированная unstripped-строка
    '''
    # Разбить строку по словам

    # замена буквы ё
    string = string.replace(unicSmallYo, 'е')

    # От начала строки до слова
    pref_pat = (
        r'^(?P<pref_symbols>[^' + cu_letters_with_superscripts + r']+)'
        r'(?=[' + cu_letters_with_superscripts + r'])')
    re_obj = re.compile(pref_pat, re.U | re.X)
    match = re_obj.search(string)
    first_pre_part = ''
    if match:
        first_pre_part = match.group('pref_symbols')

    # Слово [+промежуток]
    word_pat = (
        r'(?P<one_word>[' + cu_letters_with_superscripts + r']+)'
        r'(?P<between>[^' + cu_letters_with_superscripts + r']*)'
    )
    regex = re.compile(word_pat, re.U | re.X)

    # ковертировать каждое найденное слово
    if regex.search(string):

        def gen_converted_list():
            for _match in regex.finditer(string):
                _word = _match.group('one_word')
                # Проверка: если слово все же начинается с надстрочников,
                # сохранить их.
                unnormal_leading_superscripts = ''
                if _word[0] in cu_superscripts:
                    unnormal_leading_superscripts = _word[0]
                    try:
                        if _word[1] in cu_superscripts:
                            unnormal_leading_superscripts = _word[:2]
                    except IndexError as e:
                        pass

                # Передать в конвертер строку без анормальных надстрочников
                # если они есть
                _word_cnv = \
                    converter(_word[len(unnormal_leading_superscripts):], flags)
                if _word_cnv:
                    # # Если слово содержит камору,
                    # то, например, после сокращения в титло
                    # ударение меняется на оксию (в соответствии с правилами в regs).
                    # if _word[-1] == Oxia:
                    #     print(f'+++ OXIA: {_word}')

                    # Присоединить анормальные надстрочники, если они были.
                    _word = unnormal_leading_superscripts + _word_cnv
                # добавить в список конвертированное слово
                yield _word
                _btw = _match.group('between')
                if _btw:
                    # промежутки оставить как есть
                    yield _btw

        # собрать список с конвертированными словами в строку
        out = first_pre_part + ''.join(gen_converted_list())
    else:
        out = string
    return out


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
        for _d in bold_digits:
            string = string.replace(_d, bold_digits[_d])

    # поиск чисел и замена на буквы
    pat = r'\d+'
    r = re.compile(pat, re.U)
    if r.search(string):
        return r.sub(replacer, string)


def convert_string_letters_to_digits(string):
    out = string
    try:
        out = cu_parse_int(string)
    except:
        pass
    return out


def convert_varia2oxia(string):
    # слово оканчивающееся на варию, затем пробел, затем частица
    pat = r'(\B[аеєѣиоѡꙋыюѧ])' + Varia + \
          r'\s+(же|бо|ли|[МмТт][ѧи]|сѧ|си|ны|вы)' + \
          '(?:[' + Oxia + Varia + r'])?(' + cu_non_letters_with_superscripts + ')'
    re_obj = re.compile(pat, re.U | re.X)
    match = re_obj.search(string)
    if match:
        return re_obj.sub(r"\1" + Oxia + r" \2\3", string)


def convert_pluralis(string, flags=None):
    """Заменяет 'и' на 'ы' в окончаниях для мн.ч.: '-[шщ][ы](ѧ|мъ?)(сѧ)?'

    напр.: боящыяся, идущыя.
    Также последняя 'о' на 'ѡ' в окончаниях -ѡвъ -ѡмъ для мн.ч. род. и дат. падежей.
    и другие варианты.
    напр.: апо́столѡмъ (дат.п.) и апо́столѡвъ (род.п.)
    Также последняя е в слове -> є (и обратно).
    напр.: моле́нїѧ <-> молє́нїѧ
    :param string: строка
    :param flags: для унификации
    :return: измененная строка
    """
    class Lett:
        SINGLE_O = 'о'
        PLURAL_O = 'ѡ'
        SINGLE_E = 'е'
        PLURAL_E = 'є'
        all_tuple = (SINGLE_O, PLURAL_O, SINGLE_E, PLURAL_E)

    lett = Lett()
    pat_singular_i = r'''
        ([шщ])      # \1
        (?:и|ї)
        (           # \2
          (?:мъ?|ѧ)
          (?:сѧ)?
        )
        $
        '''
    sub_singular_i = r"\1ы\2"

    pat_plural_i = r'''
        ([шщ])      # \1
        ы
        (           # \2
          мъ?
          (?:сѧ)?
        )
        $
        '''
    sub_plural_i = r"\1и\2"

    pat_plural_i_ya = r'''
        ([шщ])      # \1
        ы
        (           # \2
          ѧ
          (?:сѧ)?
        )
        $
        '''
    sub_plural_i_ya = r"\1ї\2"

    pat_singular_o = r'''
        о
        ([^о]+)
        $
        '''
    sub_singular_o = r"ѡ\1"

    pat_plural_o = r'''
        ([^ѡ])
        ѡ
        ([^ѡ]+)
        $
        '''
    sub_plural_o = r'\1о\2'

    pat_singular_e = r'''
        е
        ([^е]+)
        $
        '''
    sub_singular_e = r"є\1"

    pat_plural_e = r'''
        ([^є])
        є
        ([^є]+)
        $
        '''
    sub_plural_e = r'\1е\2'

    re_obj_singular_i = re.compile(pat_singular_i, re.U | re.X)
    re_obj_plural_i = re.compile(pat_plural_i, re.U | re.X)
    re_obj_plural_i_ya = re.compile(pat_plural_i_ya, re.U | re.X)

    re_obj_singular_o = re.compile(pat_singular_o, re.U | re.X)
    re_obj_plural_o = re.compile(pat_plural_o, re.U | re.X)

    re_obj_singular_e = re.compile(pat_singular_e, re.U | re.X)
    re_obj_plural_e = re.compile(pat_plural_e, re.U | re.X)

    match_singular_i = re_obj_singular_i.search(string)
    match_plural_i = re_obj_plural_i.search(string)
    match_plural_i_ya = re_obj_plural_i_ya.search(string)

    match_singular_o = re_obj_singular_o.search(string)
    match_plural_o = re_obj_plural_o.search(string)

    match_singular_e = re_obj_singular_e.search(string)
    match_plural_e = re_obj_plural_e.search(string)

    def get_fist_letter_from_end(_string):
        string_rev_list = reversed(list(_string))
        for _lett in string_rev_list:
            if _lett in Lett.all_tuple:
                return _lett

    re_and_subs_dic = {
        Lett.SINGLE_E: (re_obj_singular_e, sub_singular_e),
        Lett.PLURAL_E: (re_obj_plural_e, sub_plural_e),
        Lett.SINGLE_O: (re_obj_singular_o, sub_singular_o),
        Lett.PLURAL_O: (re_obj_plural_o, sub_plural_o),
    }

    # Буквы и, ї, ы.
    if match_singular_i:
        return re_obj_singular_i.sub(sub_singular_i, string)
    elif match_plural_i:
        return re_obj_plural_i.sub(sub_plural_i, string)
    elif match_plural_i_ya:
        return re_obj_plural_i_ya.sub(sub_plural_i_ya, string)
    # Буквы е, є, о, ѡ.
    elif match_singular_e or match_plural_e or match_singular_o or match_plural_o:
        # Из всех возможных букв е, є, о, ѡ получить первую с конца.
        first_letter_from_end = get_fist_letter_from_end(string)
        re_and_subs = re_and_subs_dic.get(first_letter_from_end)
        if re_and_subs:
            _re_obj, _subs = re_and_subs
            return _re_obj.sub(_subs, string)


def add_oxia_for_unacuted_word_handler(string):
    """Выставляет ударение (оксию) для слова без ударения

    Ударение ставится для первой гласной.
    :param string: исходное слово
    :return: слово с ударением
    """
    _acutes_list = [Oxia, Varia, Kamora]

    def is_word_acuted(_string):
        # Проверка - есть ли уже ударение в слове.
        _acutes_set = set(_acutes_list)
        _word_set = set(string)
        if _word_set.intersection(_acutes_list):
            return True
        else:
            return False

    def get_first_vowel_from_word(_string):
        for _i, _char in enumerate(_string):
            if _char in cu_vowels_for_stressed:
                return _i, _char
        return None, None

    if not is_word_acuted(string):
        _acute = Oxia
        acuted_index, acuted_letter = get_first_vowel_from_word(string)
        if acuted_letter:
            if acuted_index == len(string) - 1:
                _acute = Varia
            # Если слово однобуквенное (и возможно со звательцем) и не ['и', 'є', 'ю', 'ѧ'],
            # ничего не делать.
            if (len(string) == 1 or (len(string) == 2 and string[1] == Zvatelce)) \
                    and acuted_letter not in ['и', 'є', 'ю', 'ѧ']:
                return None

            # Если есть звательце, то вставить ударение после него а не после символа.
            if len(string) > 1 \
                    and acuted_index != len(string) - 1 \
                    and string[acuted_index+1] == Zvatelce:
                # Если слово однобуквенное (и возможно со звательцем) и из ['и', 'є', 'ю', 'ѧ']
                if (len(string) == 1 or (len(string) == 2 and string[1] == Zvatelce)) \
                        and acuted_letter in ['и', 'є', 'ю', 'ѧ']:
                    _acute = Varia
                return string[:acuted_index+2] + _acute + string[acuted_index+2:]

            # случаи ѷ ї  - надстрочник заменяется на ударение.
            if len(string) > 1 and string[acuted_index:acuted_index+2] in ['ї', 'ѷ', 'Ї', 'Ѷ']:
                return string[:acuted_index + 1] + _acute + string[acuted_index + 2:]

            # Слово начинается с 'Оу' + Zvatelce - пропустить О
            if string[:3] == 'Оу' + Zvatelce:
                return string[:3] + _acute + string[3:]

            # Все остальные случаи
            return string[:acuted_index+1] + _acute + string[acuted_index+1:]

    return None


def csl_to_russian(csl_string, save_acute=False):
    """Конвертирует csl шрифт в русский гражданский.
    
    :param csl_string: строка csl текста.
    :param save_acute: сохранять ли ударения? (Нет.) 
    :return: строка конвертированного текста.
    """

    def csl_lett2dig(_word, flags=''):
        # В одном слове - поиск цся-чисел и перевод их в цифры.
        out_digits = _word
        # Анализ (частичный)
        titlo_index = _word.find(titlo)
        if len(_word) > 6:
            return
        # Тысячи 1-7
        letters_thouthands = \
            [unicSmallA, unicSmallVe, unicSmallGhe, unicSmallDe, unicSmallUkrIe, unicSmallZe, unicSmallDze]
        if _word.startswith(thousands) and _word[1] not in letters_thouthands:
            return
        if titlo_index == -1:
            return None

        res = convert_string_letters_to_digits(_word)

        if res:
            out_digits = str(res)
        return out_digits

    ru_string = csl_string

    # Раскрыть все титла.
    ru_string = get_string_converted(ru_string, titles_flag='onlyopen')

    # Удалить все тв.знаки в конце слова.
    ru_string = ru_string.replace(erok, 'ъ')
    ru_string = ru_string.replace(erok_comb, 'ъ')
    r = re.compile(r'(\w+)ъ\b', re.U)
    match = r.search(ru_string)
    if match:
        ru_string = r.sub(r"\1", ru_string)

    # Буквы - в цифры. Пословная обработка текста.
    ru_string = convert_unstripped(ru_string, csl_lett2dig)

    # Все ударения - в оксию.
    ru_string = ru_string.replace(Varia, Oxia)
    ru_string = ru_string.replace(Kamora, Oxia)

    # FIXME: ижица со звательцем = 'и'

    # Создать обратный словарь для csl букв.
    replace_dic = {
        # Удалить все узкие о - (для разбивки по границам слов)
        unicNarrowO: '',
        unicCapitalYat: 'Е',
        unicSmallYat: 'е',
        unicCapitalUkrIe: 'Е',
        unicSmallUkrIe: 'е',
        unicCapitalDze: 'З',
        unicSmallDze: 'з',
        unicCapitalUkrI + Kendema: 'И',
        unicSmallUkrI + Kendema: 'и',
        unicCapitalYi: 'И',
        unicSmallYi: 'и',
        unicSmallUkrIWithDotComb: 'и',
        # Учесть значение в зависимости от надстрочников - [ ѵ ѷ ѵ́]
        unicSmallIzhitsaDblGrave: 'и',
        unicCapitalIzhitsa + Oxia: 'И',
        unicCapitalIzhitsa + Zvatelce: 'И',
        unicSmallIzhitsa + Oxia: 'и',
        unicSmallIzhitsa + Zvatelce: 'и',
        unicCapitalIzhitsa + dbl_grave: 'И',
        unicSmallIzhitsa + dbl_grave: 'и',
        unicCapitalRoundOmega: 'О',
        unicSmallRoundOmega: 'о',
        unicCapitalOmega: 'О',
        unicSmallOmega: 'о',
        unicCapitalBroadOmega: 'О',
        unicSmallBroadOmega: 'о',
        unicCapitalOmegaTitled: 'О',
        unicSmallOmegaTitled: 'о',
        unicCapitalOt: 'От',
        unicSmallOt: 'от',
        unicCapitalUk: 'У',
        unicCapitalMonogrUk: 'У',
        unicSmallMonogrUk: 'у',
        unicCapitalFita: 'Ф',
        unicSmallFita: 'ф',
        unicCapitalLittleYus: 'Я',
        unicSmallLittleYus: 'я',
        unicCapitalIotifA: 'Я',
        unicSmallIotifA: 'я',
        unicCapitalPsi: 'Пс',
        unicSmallPsi: 'пс',
        unicCapitalKsi: 'Кс',
        unicSmallKsi: 'кс',
    }
    for rep_src, rep_dst in replace_dic.items():
        ru_string = ru_string.replace(rep_src, rep_dst)

    # Второй проход.
    replace_dic_two = {
        Zvatelce: '',
        unicCapitalUkrI: 'И',
        unicSmallUkrI: 'и',
        unicCapitalIzhitsa: 'В',
        unicSmallIzhitsa: 'в',
    }
    for rep_src, rep_dst in replace_dic_two.items():
        ru_string = ru_string.replace(rep_src, rep_dst)

    # Удалить ударения (если без ударений).
    if not save_acute:
        ru_string = ru_string.replace(Oxia, '')

    return ru_string


def unicode_to_ucs(unicode_string, split_monograph=False):
    """Конвертировать unicode строку в ucs кодировку.

    :param unicode_string:
    :param split_monograph: разбивать ли монографы.
    :return: ucs str.
    """
    # from Ft import unicode_to_ucs_fonttable
    # ucs_string = unicode_string
    raw_word = RawWord(unicode_string)
    ucs_string = raw_word.get_ucs_string(split_monograph=split_monograph)
    return ucs_string


def get_text_from_file(file_name, flags=None):
    # Для вывода в kile (выделенный текст помещается во временный файл).
    _p = Path(file_name)
    if not _p.exists():
        print('Not exists!')
        return None
    with open(_p) as _f:
        out = _f.read()
    if out:
        return out[:-1]


def debug(string):
    # debug only
    return get_string_converted(string)
