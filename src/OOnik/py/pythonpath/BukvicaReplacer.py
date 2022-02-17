# _*_ coding: utf-8

"""
    from: https://github.com/EliseyP/CSL_For_InDesign/tree/main/LettrineBukvicaUCS

    Скрипты для установки буквицы из шрифта Bukvica UCS
    для абзаца с текстом со шрифтом семейства Ponomar Unicode.
    Пока нет Unicode версии этого шрифта,
    совершается подобная замена символов.

    Подразумевается, что курсор находится в абзаце с одним из стилей:
    "Абзац с большой буквицей",
    "Абзац с большой буквицей и надстрочник",
    "Абзац с большой буквицей и два надстрочника",
    Разница - сколько символов занимает собственно буквица.
    Для шрифта Ponomar Unicode надстрочники  отделены от буквы и друг от друга.

    Сам текст абзаца - обычный Unicod текст.
    Большинство символов совпадают, но для некоторых необходима замена.
    Сами стили буквицы д.б. настроены с указанием символьного стиля с гарнитурой Bukvica UCS
    При импорте или наборе текста, при примененных абзацных стилях буквицы,
    необходимость замены видна сразу - неотображаемостью символов непосредственно буквицы
    (буква + надстрочники, если есть).

    Данный скрипт запускается  при помещенном курсоре в такой абзац.
    Происходит замена символов, а также, если изменилось кол-во символов буквицы
    (если, например, замененный символ - единый монограф буква + надстрочник(и) ),
    в таком случае заменяется и стиль абзаца на соответствующий.

    Начальная идея взята:
    http://adobeindesign.ru/2009/03/11/kak-programmno-vydelit-ves-abzac-v-kotorom-stoit-kursor/
    Авторам - благодарность.

    В шрифте Bukvica UCS два вида начертания -
    для прописных и строчных букв (буквы самого текста).
    Данная версия скрипта выставляет начертание для прописных (caps).

    AgripniSoft, ҂вк҃а
"""
from Letters import (
    Zvatelce as Zvatelco,
    Oxia,
    Varia,
    titlo,
    s_under,
    Iso,
    # Apostrof,
    Pokrytie,
    # Kendema,  # ̈
)


class Styles:
    BIG_LETTRINE = "Абзац с большой буквицей"
    BIG_LETTRINE_WITH_SUBSCRIPT = "Абзац с большой буквицей и надстрочник"
    BIG_LETTRINE_WITH_TWO_SUBSCRIPTS = "Абзац с большой буквицей и два надстрочника"
    LETTRINE = "Абзац с буквицей"
    LETTRINE_WITH_SUBSCRIPT = "Абзац с буквицей и надстрочник"
    LETTRINE_WITH_TWO_SUBSCRIPTS = "Абзац с буквицей и два надстрочника"


class StyleSet:
    SMALL = 'small'
    CAPS = 'caps'


# Iso = Zvatelco + Oxia
# Apostrof = Zvatelco + Varia
# ucs_oxia = "1"

# TODO: использовать UCS_Letters.UCS
ucs_zvatelco = "3"
ucs_iso = "4"
# ucs_kendema = "̏"
ucs_accents = [ucs_zvatelco, ucs_iso]
# Полностью несовпадающие символы.
# --------------------------------
# Е е
unic_caps_e = "Є"
unic_caps_e_with_zvatelco = unic_caps_e + Zvatelco
unic_caps_e_with_iso = unic_caps_e + Iso
ucs_caps_e = "Е"
ucs_caps_e_with_zvatelco = ucs_caps_e + ucs_zvatelco
ucs_caps_e_with_iso = ucs_caps_e + ucs_iso
ucs_small_e = "е"
ucs_small_e_with_zvatelco = ucs_small_e + ucs_zvatelco
ucs_small_e_with_iso = ucs_small_e + ucs_iso
# --------------------------------
# Ижица
unic_caps_izhitsa = "Ѵ"
unic_caps_izhitsa_with_zvatelco = unic_caps_izhitsa + Zvatelco
ucs_caps_izhitsa = "V"
ucs_caps_izhitsa_with_zvatelco = ucs_caps_izhitsa + ucs_zvatelco
ucs_small_izhitsa = "v"
ucs_small_izhitsa_with_zvatelco = ucs_small_izhitsa + ucs_zvatelco
# --------------------------------
# Омега
unic_caps_omega = "Ѡ"
unic_caps_omega_with_zvatelco = unic_caps_omega + Zvatelco
ucs_caps_omega = "W"
ucs_caps_omega_with_zvatelco = "Њ"
ucs_small_omega = "w"
ucs_small_omega_with_zvatelco = "њ"
# --------------------------------

# О широкое
unic_caps_o_broad = "Ѻ"
unic_caps_o_broad_with_zvatelco = unic_caps_o_broad + Zvatelco
unic_caps_o_broad_with_iso = unic_caps_o_broad + Iso
# В шрифте нет отдельного символа -> обычное "О".
ucs_caps_o = "О"
ucs_caps_o_with_zvatelco = "N"
ucs_caps_o_with_iso = "Џ"
ucs_small_o = "о"
ucs_small_o_with_zvatelco = "n"
ucs_small_o_with_iso = "џ"
# --------------------------------
# Омега широкое с покрытием
unic_caps_omega_great = "Ѽ"
ucs_caps_omega_great = "Q"
ucs_small_omega_great = "q"
# --------------------------------
# Я йотифированное
unic_caps_ya_iot = "Ꙗ"
unic_caps_ya_iot_with_zvatelco = unic_caps_ya_iot + Zvatelco
unic_caps_ya_iot_with_iso = unic_caps_ya_iot + Iso
ucs_caps_ya_iot = "Я"
ucs_caps_ya_iot_with_zvatelco = "K"
ucs_caps_ya_iot_with_iso = "Ћ"
ucs_small_ya_iot = "я"
ucs_small_ya_iot_with_zvatelco = "k"
ucs_small_ya_iot_with_iso = "ћ"
# --------------------------------
# От
unic_caps_ot = "Ѿ"
ucs_caps_ot = "T"
ucs_small_ot = "t"

# Частично несовпадающие символы.
# --------------------------------
unic_caps_uk = "Оу"
unic_caps_uk_with_zvatelco = unic_caps_uk + Zvatelco
unic_caps_uk_with_iso = unic_caps_uk + Iso
ucs_caps_uk = "У"
ucs_caps_uk_with_zvatelco = "Ў"  # ДУБЛИРУЕТСЯ В СЛОВАРЕ caps_dic
ucs_caps_uk_with_iso = "Ќ"  # ДУБЛИРУЕТСЯ В СЛОВАРЕ caps_dic
ucs_small_uk = "у"
ucs_small_uk_with_zvatelco = "ў"  # ДУБЛИРУЕТСЯ В СЛОВАРЕ small_dic
ucs_small_uk_with_iso = "ќ"  # ДУБЛИРУЕТСЯ В СЛОВАРЕ small_dic
# Вариант для ОУ - монографа.
unic_caps_uk_monograph = "Ꙋ"
unic_caps_uk_monograph_with_zvatelco = unic_caps_uk_monograph + Zvatelco
unic_caps_uk_monograph_with_iso = unic_caps_uk_monograph + Iso
# У
unic_caps_u = "У"
unic_caps_u_with_zvatelco = unic_caps_u + Zvatelco
unic_caps_u_with_iso = unic_caps_u + Iso
# --------------------------------
# А + надстрочники
unic_caps_az = "А"
unic_caps_az_with_zvatelco = unic_caps_az + Zvatelco
unic_caps_az_with_iso = unic_caps_az + Iso
ucs_caps_az = "А"
ucs_caps_az_with_zvatelco = ucs_caps_az + ucs_zvatelco
ucs_caps_az_with_iso = "Ѓ"
ucs_small_az = "а"
ucs_small_az_with_zvatelco = ucs_small_az + ucs_zvatelco
ucs_small_az_with_iso = "ѓ"
# --------------------------------
# Иже + надстрочники
unic_caps_izhe = "И"
unic_caps_izhe_with_zvatelco = unic_caps_izhe + Zvatelco
unic_caps_izhe_with_iso = unic_caps_izhe + Iso
ucs_caps_izhe = "И"
ucs_caps_izhe_with_zvatelco = ucs_caps_izhe + ucs_zvatelco
ucs_caps_izhe_with_iso = ucs_caps_izhe + ucs_iso
ucs_small_izhe = "и"
ucs_small_izhe_with_zvatelco = ucs_small_izhe + ucs_zvatelco
ucs_small_izhe_with_iso = ucs_small_izhe + ucs_iso
# І + надстрочники
unic_caps_i_decimal = "І"
unic_caps_i_decimal_with_zvatelco = unic_caps_i_decimal + Zvatelco
unic_caps_i_decimal_with_iso = unic_caps_i_decimal + Iso
ucs_caps_i_decimal = "I"
ucs_caps_i_decimal_with_zvatelco = "Ї"
ucs_caps_i_decimal_with_iso = "Ј"
ucs_small_i_decimal = "i"
ucs_small_i_decimal_with_zvatelco = "ї"
ucs_small_i_decimal_with_iso = "ј"
# --------------------------------
# Я (юс малый) + надстрочники
unic_caps_ya = "Ѧ"
unic_caps_ya_with_zvatelco = unic_caps_ya + Zvatelco
unic_caps_ya_with_iso = unic_caps_ya + Iso
ucs_caps_ya = "Z"
ucs_caps_ya_with_zvatelco = "Љ"
ucs_caps_ya_with_iso = ucs_caps_ya + ucs_iso
ucs_small_ya = "z"
ucs_small_ya_with_zvatelco = "љ"
ucs_small_ya_with_iso = ucs_small_ya + ucs_iso

caps_dic = {
    unic_caps_e_with_iso: ucs_caps_e_with_iso,
    unic_caps_e_with_zvatelco: ucs_caps_e_with_zvatelco,
    
    unic_caps_izhitsa: ucs_caps_izhitsa,
    unic_caps_izhitsa_with_zvatelco: ucs_caps_izhitsa_with_zvatelco,
    
    unic_caps_omega_with_zvatelco: ucs_caps_omega_with_zvatelco,
    unic_caps_omega_great: ucs_caps_omega_great,
    
    unic_caps_o_broad_with_zvatelco: ucs_caps_o_with_zvatelco,
    unic_caps_o_broad_with_iso: ucs_caps_o_with_iso,
    
    unic_caps_ya_iot_with_zvatelco: ucs_caps_ya_iot_with_zvatelco,
    unic_caps_ya_iot_with_iso: ucs_caps_ya_iot_with_iso,
    
    unic_caps_uk_with_zvatelco: ucs_caps_uk_with_zvatelco,
    unic_caps_uk_with_iso: ucs_caps_uk_with_iso,
    unic_caps_uk_monograph_with_zvatelco: ucs_caps_uk_with_zvatelco,
    unic_caps_uk_monograph_with_iso: ucs_caps_uk_with_iso,
    unic_caps_u_with_zvatelco: ucs_caps_uk_with_zvatelco,
    unic_caps_u_with_iso: ucs_caps_uk_with_iso,
    
    unic_caps_ot: ucs_caps_ot,
    
    unic_caps_az_with_zvatelco: ucs_caps_az_with_zvatelco,
    unic_caps_az_with_iso: ucs_caps_az_with_iso,
    
    unic_caps_izhe_with_zvatelco: ucs_caps_izhe_with_zvatelco,
    unic_caps_izhe_with_iso: ucs_caps_izhe_with_iso,
    unic_caps_i_decimal_with_zvatelco: ucs_caps_i_decimal_with_zvatelco,
    unic_caps_i_decimal_with_iso: ucs_caps_i_decimal_with_iso,
    
    unic_caps_ya_with_zvatelco: ucs_caps_ya_with_zvatelco,
    unic_caps_ya_with_iso: ucs_caps_ya_with_iso,
}

small_dic = {
    unic_caps_e_with_iso: ucs_small_e_with_iso,
    unic_caps_e_with_zvatelco: ucs_small_e_with_zvatelco,

    unic_caps_izhitsa: ucs_small_izhitsa,
    unic_caps_izhitsa_with_zvatelco: ucs_small_izhitsa_with_zvatelco,

    unic_caps_omega_with_zvatelco: ucs_small_omega_with_zvatelco,
    unic_caps_omega_great: ucs_small_omega_great,

    unic_caps_o_broad_with_zvatelco: ucs_small_o_with_zvatelco,
    unic_caps_o_broad_with_iso: ucs_small_o_with_iso,

    unic_caps_ya_iot_with_zvatelco: ucs_small_ya_iot_with_zvatelco,
    unic_caps_ya_iot_with_iso: ucs_small_ya_iot_with_iso,

    unic_caps_uk_with_zvatelco: ucs_small_uk_with_zvatelco,
    unic_caps_uk_with_iso: ucs_small_uk_with_iso,
    unic_caps_uk_monograph_with_zvatelco: ucs_small_uk_with_zvatelco,
    unic_caps_uk_monograph_with_iso: ucs_small_uk_with_iso,
    unic_caps_u_with_zvatelco: ucs_small_uk_with_zvatelco,
    unic_caps_u_with_iso: ucs_small_uk_with_iso,

    unic_caps_ot: ucs_small_ot,

    unic_caps_az_with_zvatelco: ucs_small_az_with_zvatelco,
    unic_caps_az_with_iso: ucs_small_az_with_iso,

    unic_caps_izhe_with_zvatelco: ucs_small_izhe_with_zvatelco,
    unic_caps_izhe_with_iso: ucs_small_izhe_with_iso,
    unic_caps_i_decimal_with_zvatelco: ucs_small_i_decimal_with_zvatelco,
    unic_caps_i_decimal_with_iso: ucs_small_i_decimal_with_iso,

    unic_caps_ya_with_zvatelco: ucs_small_ya_with_zvatelco,
    unic_caps_ya_with_iso: ucs_small_ya_with_iso,
}

ucs_style_number_dic = {
    Styles.BIG_LETTRINE: 1,
    Styles.BIG_LETTRINE_WITH_SUBSCRIPT: 2,
    Styles.BIG_LETTRINE_WITH_TWO_SUBSCRIPTS: 3
}
unic_style_number_dic = {
    Styles.LETTRINE: 1,
    Styles.LETTRINE_WITH_SUBSCRIPT: 2,
    Styles.LETTRINE_WITH_TWO_SUBSCRIPTS: 3
}
ucs_number_style_dic = dict(zip(ucs_style_number_dic.values(), ucs_style_number_dic.keys()))
unic_number_style_dic = dict(zip(unic_style_number_dic.values(), unic_style_number_dic.keys()))

caps_letters_rev = dict(zip(caps_dic.values(), caps_dic.keys()))
small_letters_rev = dict(zip(small_dic.values(), small_dic.keys()))


def get_first_letters_accents_amount(_string) -> int:
    # Возвращает кол-во надстрочников у первой буквы.
    # Текст в Unicode.

    second_symbol = _string[1:2]
    third_symbol = _string[2:3]
    accents_amount = 0

    if second_symbol in [Zvatelco, titlo]:
        accents_amount = 1
        if third_symbol in [Oxia, Varia]:
            accents_amount = 2

    if _string[1:3] == s_under + Pokrytie:
        accents_amount = 2

    if _string[:2] == "Оу":
        if _string[2] == Zvatelco:
            accents_amount = 1
            if _string[2:4] == Iso:
                accents_amount = 2
    return accents_amount


def replace_first_letter_from_unicode_to_bukvica_ucs(
        _string: str = None,
        style_set: str = 'caps') -> [str, [None, str]]:
    """Анализ и замена первой буквы в тексте _string.

    :param _string: текст для обработки
    :param style_set: стиль начертания [ caps | small ]
    :return: new_text, new_style
    """
    if _string is None:
        return None, None

    new_para_style_name = None

    if style_set == StyleSet.CAPS:
        cnv_dic = caps_dic
    elif style_set == StyleSet.SMALL:
        cnv_dic = small_dic
    else:
        return _string, new_para_style_name

    #  Определять кол-во надстрочников.
    amount_symbols_to_convert = 1
    # Анализ первых символов.
    second_symbol = _string[1:2]
    third_symbol = _string[2:3]
    # Второй символ
    if second_symbol in [Zvatelco, titlo, s_under]:
        amount_symbols_to_convert = 2
        if third_symbol in [Oxia, Varia, Pokrytie]:
            amount_symbols_to_convert = 3

    # Анализ надстрочников и соответственное значение
    # amount_symbols_to_convert  'Оу҆́мъ'
    # TODO: учесть случай монографа Ук в исходной строке.
    if _string[:2] == "Оу":
        amount_symbols_to_convert = 2
        if _string[2] == Zvatelco:
            amount_symbols_to_convert = 3
            if _string[2:4] == Iso:
                amount_symbols_to_convert = 4

    if not amount_symbols_to_convert:
        return None, None

    # Символы, на кот-е распространяется стиль "Буквица большая".
    # (буква+надстр-ки)
    symbols_with_bukvica_style = _string[:amount_symbols_to_convert]
    converted_symbols = cnv_dic.get(symbols_with_bukvica_style, symbols_with_bukvica_style)

    tail = _string[amount_symbols_to_convert:]

    delta = len(symbols_with_bukvica_style) - len(converted_symbols)

    new_para_style_name = ucs_number_style_dic[amount_symbols_to_convert - delta]

    return converted_symbols + tail, new_para_style_name


def replace_first_letter_from_bukvica_ucs_to_unicode(_string: str = None) -> [str, [None, str]]:
    """Анализ и замена первой буквы+надстрочники из UCS в Unicode.


    Выодит новую строку и новый стиль.

    !!! Апостроф для Bukvica UCS не предполагается. Везде в UCS - Исо.

    :param _string:
    :return: converted_string, new_style_name
    """
    _out_string = _string
    _first_symbol = _string[0]
    _second_symbol = _string[1]

    # В обратном словаре однозначно определить
    # (устранить последствия усечения дублирования)
    caps_letters_rev[ucs_caps_uk_with_zvatelco] = unic_caps_uk_with_zvatelco
    caps_letters_rev[ucs_caps_uk_with_iso] = unic_caps_uk_with_iso
    small_letters_rev[ucs_small_uk_with_zvatelco] = unic_caps_uk_with_zvatelco
    small_letters_rev[ucs_small_uk_with_iso] = unic_caps_uk_with_iso

    # For searching by first symbol
    caps_first_symbols = [x[0] for x in caps_letters_rev.keys()]
    small_first_symbols = [x[0] for x in small_letters_rev.keys()]

    _dic_rev = {}
    # Определить какой набор caps или small
    if _first_symbol in caps_first_symbols:
        _dic_rev = caps_letters_rev
    elif _first_symbol in small_first_symbols:
        _dic_rev = small_letters_rev

    if _dic_rev:
        # Для несовпадающих букв.
        _for_convert = _first_symbol
        if _second_symbol in ucs_accents:
            _for_convert += _second_symbol
        _converted_symbols = \
            _dic_rev.get(_for_convert, _for_convert)
        _out_string = f'{_converted_symbols + _string[len(_for_convert):]}'

    _amount = get_first_letters_accents_amount(_out_string)
    _style = unic_number_style_dic.get(_amount + 1)
    return _out_string, _style


if __name__ == "__main__":
    _text = [
        'Оу҆́мъ',
        'Оу҆тѣше́нїе',
        'Паче',
        'А҆́зъ',
        'Є҆́же', 'Є҆два',
        'І҆и҃съ',
    ]
    _text_ucs_caps = [
        'Ќмъ',
        'Ўтѣше́нїе',
        'Паче',
        'Ѓзъ',
        'Е4же',
        'Е3два',
        'Їи҃съ',
    ]
    _text_ucs_small = [
        'ќмъ',
        'ўтѣше́нїе',
        'Паче',
        'ѓзъ',
        'е4же',
        'е3два',
        'їи҃съ',
    ]
    for _t in _text_ucs_caps:
        _new_text_list = replace_first_letter_from_bukvica_ucs_to_unicode(_t)
        _new_text = _new_text_list[0]
        style = _new_text_list[1]
        print(f'{style}: {_new_text}')

    for _t in _text_ucs_small:
        replace_first_letter_from_bukvica_ucs_to_unicode(_t)

    # print('_text_ucs = [')
    # for _t in _text:
    #     _new_text = replace_first_letter_for_bukvica_font(_string=_t, style_set=StyleSet.CAPS)
    #     # print(f'{_new_text[1]}\n{_new_text[0]}')
    #     print(f'\t\'{_new_text[0]}\',')
    # print(']')
