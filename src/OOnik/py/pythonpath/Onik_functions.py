#!/usr/bin/python3
# _*_ coding: utf-8

# import copy
import re
from Regs import *
from Letters import *
from numerals import cu_format_int, cu_parse_int


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
    (ф-ця convert_stripped принимает строку, и функцию коныертации)  
        
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
    # одна буква с надстрочниками и др. атрибутами

    def __init__(self, char, superscript=''):
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
        '''

        # Отдельные буквы ꙋ ᲂу ѡ ѿ ꙗ ѧ є ъ ѽ
        converted_packet = self.convert_separate_letters()

        # Преобразование через imposing

        # Буквы в слове,
        converted_packet = self.replacer_by_regex_compiled_list(regs_letters_in_word_compiled)

        # Ударения
        converted_packet = self.replacer_by_regex_compiled_list(regs_acutes_compiled)

        # Титла
        if titles_flag == 'on':
            # Выставить титла
            converted_packet = converted_packet.replacer_by_regex_compiled_list(regs_titles_set_compiled)

        return converted_packet

    def convert_separate_letters(self):
        """В исходном packet конвертирует отдельные буквы"""

        word_packed = self
        c = word_packed.unpack()

        last_symbol = c[-1]
        # print(last_symbol)
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
        for regex_tuple in regex_compiled_lists:
            packet = self.regex_sub(regex_tuple)
        return packet


class RawWord:
    # слово (unstripped-строка)
    # слова содержат только [знак тысячи]буквы + надстрочники

    def __init__(self, string):
        self.string = str(string)

    def pack(self):
        '''
        Разбивает слово string на объекты класса Gramma
        вместе с самой буквой - флаги и значения надстрочников и т.д.

        :return: packed_word
        '''
        packed_word = WordPacked([])
        string = self.string

        combined_dic = {
            unicCapitalIzhitsaDblGrave: unicCapitalIzhitsa,
            unicSmallIzhitsaDblGrave: unicSmallIzhitsa,
            unicCapitalYi: unicCapitalUkrI,
            unicSmallYi: unicSmallUkrI
        }
        string_length = len(string)

        for i in range(string_length):
            gramma_current = Gramma('')  # текущий gramma
            gramma_prev = Gramma('')  # Предыдущий gramma, начиная с 1
            _char = string[i]  # текущий символ
            if i > 0:
                gramma_prev = packed_word[-1]
            if i == 0:
                gramma_current.is_first = True

            if _char in cu_letters_text or \
                    _char in combined_dic.keys() or \
                    _char == latin_i:
                # Если текущий символ - буква

                # латинское i -> ї
                if _char == latin_i:
                    _char = unicSmallUkrI
                    gramma_current.superscript = Kendema

                gramma_current.letter = _char
                # Проверка на слитные с надстрочником символы  ѷ ї
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
                # выставить флаг и занести символ (к предыдущей букве)

                # Если у предыдущего символа уже есть надстрочник
                # (в том числе исправление ошибок набора - два ударения подряд и т.п.)
                if gramma_prev.have_superscript:
                    # Если текущий символ - часть комбинированного надстрочника,
                    # он добавляется к свое паре (остальные некорректные надстрочники отбрасываются).
                    # TODO: проверить: ошибка если оксия после кендимы у i - она должна заменять ее
                    if gramma_prev.have_zvatelce and _char in [Oxia, Varia, Kamora]:
                        # Исо, Апостроф, breve+pokrytie
                        gramma_prev.superscript += _char  # если двойной то добавить к уже имеющемуся
                    elif gramma_prev.superscript in under_pokrytie and _char == pokrytie:
                        # Буквенное титло
                        gramma_prev.superscript += _char
                else:
                    gramma_prev.have_superscript = True
                    gramma_prev.superscript = _char

                if _char == Zvatelce:
                    # Если звательце, выставить у предыдущей буквы флаг
                    gramma_prev.have_zvatelce = True

                elif _char in acutes:
                    # Если ударение, выставить у предыдущей буквы:
                    gramma_prev.is_acuted = True  # флаг и
                    gramma_prev.acute = _char  # тип ударения
                    # TODO: ??? м.б. разделить оксию варию и камору
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
        converted_packet = self.pack().get_converted(titles_flag)
        return converted_packet.unpack()

    def is_acuted(self):
        return self.pack().is_acuted()


def acute_util(string, type_of_operation='change_type'):
    '''Замена ударений в слове

    :param string: слово
    :param type_of_operation: тип операции [change_type, move_right, move_left]  (def=change_type)
    :return: слово с измененным ударением
    '''

    raw_word = RawWord(string)
    word_packed = raw_word.pack()

    # Множество ударений (в идеале - одно ударение в слове)
    # ТОЛЬКО ФАКТ вхождения
    word_acutes_set = word_packed.is_acuted()
    # Список ударений (в идеале - одно ударение в слове)
    word_acutes_list = word_packed.get_acutes_list()

    superscript_layer = word_packed.get_superscripts_layer()
    text_layer = word_packed.get_text_layer()

    # Длина слова (текстовый слой)
    word_length = len(superscript_layer)

    # Если в слове есть ударение
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

        # Если одно ударение (норма)
        if len(word_acutes_list) == 1:
            acute_symbol = word_acutes_list[0]
            # Позиция ударения
            acute_index = superscript_layer.index(acute_symbol)
            # Ударная гласная
            acuted_letter = text_layer[acute_index]
            # TODO: проверка на гласную и исправление (сдвиг ударения на ближайшую ударную)
            # Получить список индексов потенциально ударных гласных
            # из текстового слоя
            vowels_indexes_in_word = []  # список индексов ударных гласных
            letter_index = 0
            for gramma in word_packed:
                if gramma.letter in cu_vowels_for_stressed:
                    vowels_indexes_in_word.append(letter_index)
                letter_index += 1

            # #####################
            # Изменить тип ударения
            if type_of_operation == 'change_type':

                # TODO: уточнить проверку и исправление, если вария посередине слова,
                #  то первый запуск этой функции может исправить эту ошибку.
                #  А последующие соответственно уже будут менять по алгоитму.
                new_acute_symbol = ''
                new_acuted_letter = ''

                # Учесть ОУ
                if acute_index == 1 \
                        and acuted_letter in {'У', 'у'} \
                        and acute_symbol in {Iso, Apostrof}:
                    acute_is_onik = True
                else:
                    acute_is_onik = False

                # Если ударение в начале слова
                if acute_index == 0 or acute_is_onik:
                    new_acute_symbol = acute_cycler(Iso, Apostrof, acute=acute_symbol)

                # Если ударение в конце или в середине слова
                else:
                    # Если буквы изменяющиеся для множественного числа
                    acutes_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}

                    # Если ударение в КОНЦЕ слова
                    if acute_index == word_length - 1:

                        # Если меняется буква в конце слова
                        if acuted_letter in acutes_dic.keys() \
                                or acuted_letter in acutes_dic.values():
                            new_acuted_letter, new_acute_symbol = \
                                acute_cycler(Oxia, Varia, letter=acuted_letter, acute=acute_symbol)
                        # Меняется только ударение
                        else:
                            new_acute_symbol = \
                                acute_cycler(Oxia, Varia, Kamora, acute=acute_symbol)

                    # Если ударение в середине слова
                    else:
                        # Исправление ошибки: если вария в середине слова
                        # TODO: ??? сделать это глобально
                        if acute_symbol == Varia:
                            acute_symbol = Oxia
                            # new_acute_symbol = Oxia

                        # Если меняется буква в середине слова
                        if acuted_letter in acutes_dic.keys() \
                                or acuted_letter in acutes_dic.values():
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
                # Если ударение ошибочно на согласной, то нужна х.о. согласная
                # поэтому > 0
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
                        if word_packed[-1].check_vowels():
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

    # если нет ударений
    else:
        if type_of_operation == 'move_to_end':
            new_word_packed = word_packed
            # get last letter in word.
            last_letter = new_word_packed[-1]
            # проверить - гласная ли
            if last_letter.check_vowels():
                # set varia for last letter
                last_letter.superscript = Varia
                return new_word_packed.unpack()
            else:
                return None
        else:
            return None


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
    _lett = ''  # новая буква
    _ac = ''  # новое ударение

    if not args.count(acute):
        return None
    _pos = args.index(acute)

    if not letter:
        _ac = args[0] if _pos == len(args) - 1 else args[_pos + 1]
        return _ac
    else:
        ac_dic = {'о': 'ѡ', 'е': 'є', 'О': 'Ѡ', 'Е': 'Є'}
        ac_dic_rev = dict(zip(ac_dic.values(), ac_dic.keys()))

        # В конце слова
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

        # В середине слова
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
    new_word_packed = raw_word.pack()
    text_layer = new_word_packed.get_text_layer()

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
    :param titles_flag: титла - [on|off*|open].
        on - ставить титла.
        off - не ставить (по умолч.)
        open - раскрыть титла.
    :return: прреобразованная строка
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

    regs_letters_in_word_compiled = make_compiled_regs(regs_letters_in_word)
    regs_acutes_compiled = make_compiled_regs(regs_acutes)
    regs_titles_set_compiled = make_compiled_regs(regs_titles_set)
    regs_titles_open_compiled = make_compiled_regs(regs_titles_open)

    # шаблоны для поиска надстрочников (титла и остальные)
    pat_titles = r'[' + titles + ']'
    re_titled = re.compile(pat_titles, re.U | re.X)
    pat_superscripts = r'[' + Zvatelce + acutes + ']'
    re_superscript = re.compile(pat_superscripts, re.U | re.X)

    def convert_one_word(word_string, flags=''):
        # конвертация отдельного слова
        converted_string = word_string
        word_is_titled = False

        # Предварительная оработка для раскрытия титла
        if titles_flag == 'open':
            # удалить другие надстрочники
            # (чтобы соответствовать строкам в regex_set)
            if re_superscript.search(word_string):
                word_string = re_superscript.sub('', word_string)
            # Если в слове есть титло
            if re_titled.search(word_string):
                word_is_titled = True
                for r_obj, replace in regs_titles_open_compiled:
                    if r_obj.search(word_string):
                        word_string = r_obj.sub(replace, word_string)

        # Основная конвертация
        # при опции 'раскрытие титла' обработка только слов с титлами
        if titles_flag != 'open' or word_is_titled:
            raw_word = RawWord(word_string)
            # если строка - число буквами, то не менять
            if not raw_word.pack().is_letters_number():
                converted_string = raw_word.get_converted(titles_flag=titles_flag)

        return converted_string

    return convert_stripped(string, convert_one_word)


def convert_stripped(string, converter, flags=''):
    '''Конвертация unstripped-строки (буквы + пробелы, пунктуация и проч.)

    :param string: исходная строка (unstripped)
    :param converter: функция конвертации одного слова
    :param flags:
    :return: конвертированная unstripped-строка
    '''
    # Разбить строку по словам

    # замена буквы ё
    string = string.replace(unicSmallYo, 'е')

    string_list = ''
    # От начала строки до слова
    pref_pat = r'^(?P<pref_symbols>[^' + cu_letters_with_superscripts + r']+)(?=[' + cu_letters_with_superscripts + r'])'
    re_obj = re.compile(pref_pat, re.U | re.X)
    match = re_obj.search(string)
    first_pre_part = ''
    if match:
        first_pre_part = match.group('pref_symbols')

    # Слово [+промежуток]
    word_pat = r'(?P<one_word>[' + cu_letters_with_superscripts + r']+)(?P<between>[^' + cu_letters_with_superscripts + r']*)'
    regex = re.compile(word_pat, re.U | re.X)

    # ковертировать каждое найденное слово
    if regex.search(string):

        def gen_converted_list():
            for match in regex.finditer(string):
                _word = match.group('one_word')
                _word_cnv = converter(_word, flags)
                if _word_cnv:
                    _word = _word_cnv
                # добавить в список конвертированное слово
                yield _word
                _btw = match.group('between')
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


def convert_ending_i_at_plural(string):
    """Заменяет 'и' на 'ы' в окончаниях для мн.ч.: '-[шщ][ы](ѧ|мъ?)(сѧ)?'

    напр.: боящыяся, идущыя
    :param string: строка
    :return: измененная строка
    """
    pat_singular = r'''
        ([шщ])      # \1
        (?:и|ї)
        (           # \2
          (?:мъ?|ѧ)
          (?:сѧ)?
        )\b
        '''
    pat_plurar = r'''
        ([шщ])      # \1
        ы
        (           # \2
          мъ?
          (?:сѧ)?
        )\b
        '''
    pat_plurar_ya = r'''
        ([шщ])      # \1
        ы
        (           # \2
          ѧ
          (?:сѧ)?
        )\b
        '''
    re_obj_singular = re.compile(pat_singular, re.U | re.X)
    re_obj_plurar = re.compile(pat_plurar, re.U | re.X)
    re_obj_plurar_ya = re.compile(pat_plurar_ya, re.U | re.X)
    match_singular = re_obj_singular.search(string)
    match_plurar = re_obj_plurar.search(string)
    match_plurar_ya = re_obj_plurar_ya.search(string)
    if match_singular:
        return re_obj_singular.sub(r"\1ы\2", string)
    elif match_plurar:
        return re_obj_plurar.sub(r"\1и\2", string)
    elif match_plurar_ya:
        return re_obj_plurar_ya.sub(r"\1ї\2", string)


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


def debug(string):
    # debug only
    return get_string_converted(string)
