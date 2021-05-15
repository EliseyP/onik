# _*_ coding: utf-8

"""
UCS-символы
"""


class UCS:
    # Совпадающие символы:
    CAPS_A = 'А'
    CAPS_B = 'Б'
    CAPS_V = 'В'
    CAPS_G = 'Г'
    CAPS_D = 'Д'
    CAPS_E = 'Е'
    CAPS_ZH = 'Ж'
    CAPS_Z = 'З'
    CAPS_DZE = 'Ѕ'
    CAPS_I = 'И'
    CAPS_I_KRATKOE = 'Й'
    CAPS_K = 'К'
    CAPS_L = 'Л'
    CAPS_M = 'М'
    CAPS_N = 'Н'
    CAPS_O = 'О'
    CAPS_P = 'П'
    CAPS_R = 'Р'
    CAPS_S = 'С'
    CAPS_T = 'Т'
    CAPS_F = 'Ф'
    CAPS_HER = 'Х'
    CAPS_CE = 'Ц'
    CAPS_CH = 'Ч'
    CAPS_SH = 'Ш'
    CAPS_CHSH = 'Щ'
    CAPS_HARD_SIGN = 'Ъ'
    CAPS_Y = 'Ы'
    CAPS_SOFT_SIGN = 'Ь'
    CAPS_YU = 'Ю'

    SMALL_A = 'а'
    SMALL_B = 'б'
    SMALL_V = 'в'
    SMALL_G = 'г'
    SMALL_D = 'д'
    SMALL_E = 'е'
    SMALL_E_BROAD = 'є'
    SMALL_ZH = 'ж'
    SMALL_Z = 'з'
    SMALL_ZELO = 'ѕ'
    SMALL_I = 'и'
    SMALL_I_KRATKOE = 'й'
    SMALL_K = 'к'
    SMALL_L = 'л'
    SMALL_M = 'м'
    SMALL_N = 'н'
    SMALL_O = 'о'
    SMALL_P = 'п'
    SMALL_R = 'р'
    SMALL_S = 'с'
    SMALL_T = 'т'
    SMALL_F = 'ф'
    SMALL_HER = 'х'
    SMALL_CE = 'ц'
    SMALL_CH = 'ч'
    SMALL_SH = 'ш'
    SMALL_CHSH = 'щ'
    SMALL_SOFT_SIGN = 'ь'
    SMALL_Y = 'ы'
    SMALL_HARD_SIGN = 'ъ'
    SMALL_YU = 'ю'

    # Несовпадающие символы:
    CAPS_YAT = 'Э'
    CAPS_I_DECIMAL = 'I'
    CAPS_O_BROAD = 'O'
    CAPS_OT = 'T'
    CAPS_OUK = 'U'
    CAPS_OUK_MONOGR = 'У'
    CAPS_O_GREAT = 'Q'
    CAPS_YA_IOTIF = 'Я'
    CAPS_YA = 'Z'
    CAPS_IZHICA = 'V'
    CAPS_OMEGA = 'W'
    CAPS_PSI = 'P'
    CAPS_KSI = 'X'

    SMALL_IZHICA = 'v'
    SMALL_YAT = 'э'
    SMALL_I_DECIMAL = '\u0069'  # without dot (decimal), as base
    SMALL_O_BROAD = 'o'
    SMALL_OMEGA = 'w'
    SMALL_O_GREAT = 'q'
    SMALL_OT = 't'
    SMALL_OUK_MONOGR = 'у'
    SMALL_OUK = 'u'
    SMALL_FITA = 'f'
    SMALL_YA = 'z'
    SMALL_YA_IOTIF = 'я'
    SMALL_PSI = 'p'
    SMALL_KSI = 'x'

    # Монограф.
    CAPS_A_AND_ZVATELCO = 'Ґ'
    CAPS_A_AND_ISO = 'Ѓ'
    CAPS_IZHICA_AND_KENDEMA = 'M'
    CAPS_I_DECIMAL_AND_DOTS = 'І'
    CAPS_I_DECIMAL_AND_ZVATELCO = 'Ї'
    CAPS_I_DECIMAL_AND_ISO = 'Ј'
    CAPS_O_BROAD_AND_ZVATELCO = 'N'
    CAPS_O_BROAD_AND_ISO = 'Џ'
    CAPS_OMEGA_AND_ZVATELCO = 'Њ'
    CAPS_OUK_AND_ISO = 'Ќ'
    CAPS_OUK_AND_ZVATELCO = 'Ў'
    CAPS_YA_AND_ZVATELCO = 'Љ'
    CAPS_YA_IOTIF_AND_ZVATELCO = 'K'
    CAPS_YA_IOTIF_AND_ISO = 'Ћ'

    SMALL_A_AND_ZVATELCO = 'ґ'
    SMALL_A_AND_OXIA = 'a'
    SMALL_A_AND_VARIA = 'A'
    SMALL_A_AND_KAMORA = '†'
    SMALL_A_AND_ISO = 'ѓ'
    SMALL_A_AND_TITLO = '№'
    SMALL_G_AND_TITLO = 'G'
    SMALL_D_AND_TITLO_S = 'D'
    SMALL_E_AND_OXIA = 'e'
    SMALL_E_AND_VARIA = 'E'
    SMALL_YAT_AND_OXIA = 'ё'
    SMALL_YAT_AND_VARIA = 'Ё'
    SMALL_YAT_AND_KAMORA = 'B'
    SMALL_ZH_AND_TITLO = '9'
    SMALL_I_AND_TITLO = '}'
    SMALL_I_DECIMAL_AND_DOTS = '\u0456'  # with dots
    SMALL_I_DECIMAL_AND_ZVATELCO = 'ї'
    SMALL_I_DECIMAL_AND_OXIA = 'j'
    SMALL_I_DECIMAL_AND_VARIA = 'J'
    SMALL_I_DECIMAL_AND_KAMORA = '‡'
    SMALL_I_DECIMAL_AND_ISO = 'ј'
    SMALL_I_DECIMAL_AND_TITLO = '‹'
    SMALL_IZHICA_AND_OXIA = 'Ђ'
    SMALL_IZHICA_AND_KAMORA = '›'
    SMALL_IZHICA_AND_KENDEMA = 'm'
    SMALL_IZHICA_AND_TITLO_G = 'ђ'
    SMALL_L_AND_TITLO = 'l'
    SMALL_L_AND_TITLO_D = 'L'
    SMALL_O_AND_OXIA = '0'
    SMALL_O_BROAD_AND_ZVATELCO = 'n'
    SMALL_O_BROAD_AND_ISO = 'џ'
    SMALL_OMEGA_AND_ZVATELCO = 'њ'
    SMALL_R_AND_TITLO = 'R'
    SMALL_R_AND_TITLO_D = '®'
    SMALL_R_AND_TITLO_S = 'r'
    SMALL_S_AND_TITLO = '©'
    SMALL_T_AND_TITLO = '™'
    SMALL_OUK_MONOGR_AND_OXIA = 'y'
    SMALL_OUK_MONOGR_AND_VARIA = 'Y'
    SMALL_OUK_MONOGR_AND_KAMORA = '{'
    SMALL_OUK_AND_ZVATELCO = 'ў'
    SMALL_OUK_AND_ISO = 'ќ'
    SMALL_HER_AND_TITLO = '¦'
    SMALL_CH_AND_TITLO = '§'
    SMALL_Y_AND_OXIA = 'h'
    SMALL_YA_AND_ZVATELCO = 'љ'
    SMALL_YA_AND_OXIA = 's'
    SMALL_YA_AND_VARIA = 'S'
    SMALL_YA_AND_KAMORA = '‰'
    SMALL_YA_AND_APOSTROF = '|'
    SMALL_YA_IOTIF_AND_ZVATELCO = 'k'
    SMALL_YA_IOTIF_AND_ISO = 'ћ'
    SMALL_YA_IOTIF_AND_APOSTROF = '±'
    SMALL_KSI_AND_TITLO = '…'

    symb_monograph_list = [
        CAPS_A_AND_ZVATELCO,
        CAPS_A_AND_ISO,
        CAPS_IZHICA_AND_KENDEMA,
        CAPS_I_DECIMAL_AND_DOTS,
        CAPS_I_DECIMAL_AND_ZVATELCO,
        CAPS_I_DECIMAL_AND_ISO,
        CAPS_O_BROAD_AND_ZVATELCO,
        CAPS_O_BROAD_AND_ISO,
        CAPS_OMEGA_AND_ZVATELCO,
        CAPS_OUK_AND_ISO,
        CAPS_OUK_AND_ZVATELCO,
        CAPS_YA_AND_ZVATELCO,
        CAPS_YA_IOTIF_AND_ZVATELCO,
        CAPS_YA_IOTIF_AND_ISO,

        SMALL_A_AND_ZVATELCO,
        SMALL_A_AND_OXIA,
        SMALL_A_AND_VARIA,
        SMALL_A_AND_KAMORA,
        SMALL_A_AND_ISO,
        SMALL_A_AND_TITLO,
        SMALL_G_AND_TITLO,
        SMALL_D_AND_TITLO_S,
        SMALL_E_AND_OXIA,
        SMALL_E_AND_VARIA,
        SMALL_YAT_AND_OXIA,
        SMALL_YAT_AND_VARIA,
        SMALL_YAT_AND_KAMORA,
        SMALL_ZH_AND_TITLO,
        SMALL_I_AND_TITLO,
        SMALL_I_DECIMAL_AND_DOTS,
        SMALL_I_DECIMAL_AND_ZVATELCO,
        SMALL_I_DECIMAL_AND_OXIA,
        SMALL_I_DECIMAL_AND_VARIA,
        SMALL_I_DECIMAL_AND_KAMORA,
        SMALL_I_DECIMAL_AND_ISO,
        SMALL_I_DECIMAL_AND_TITLO,
        SMALL_IZHICA_AND_OXIA,
        SMALL_IZHICA_AND_KAMORA,
        SMALL_IZHICA_AND_KENDEMA,
        SMALL_IZHICA_AND_TITLO_G,
        SMALL_L_AND_TITLO,
        SMALL_L_AND_TITLO_D,
        SMALL_O_AND_OXIA,
        SMALL_O_BROAD_AND_ZVATELCO,
        SMALL_O_BROAD_AND_ISO,
        SMALL_OMEGA_AND_ZVATELCO,
        SMALL_R_AND_TITLO,
        SMALL_R_AND_TITLO_D,
        SMALL_R_AND_TITLO_S,
        SMALL_S_AND_TITLO,
        SMALL_T_AND_TITLO,
        SMALL_OUK_MONOGR_AND_OXIA,
        SMALL_OUK_MONOGR_AND_VARIA,
        SMALL_OUK_MONOGR_AND_KAMORA,
        SMALL_OUK_AND_ZVATELCO,
        SMALL_OUK_AND_ISO,
        SMALL_HER_AND_TITLO,
        SMALL_CH_AND_TITLO,
        SMALL_Y_AND_OXIA,
        SMALL_YA_AND_ZVATELCO,
        SMALL_YA_AND_OXIA,
        SMALL_YA_AND_VARIA,
        SMALL_YA_AND_KAMORA,
        SMALL_YA_AND_APOSTROF,
        SMALL_YA_IOTIF_AND_ZVATELCO,
        SMALL_YA_IOTIF_AND_ISO,
        SMALL_YA_IOTIF_AND_APOSTROF,
        SMALL_KSI_AND_TITLO,
    ]

    # Титла.
    TITLO_UPP_BROAD = '\\'
    TITLO_UPP = '&'
    TITLO_S_UPP = 'C'
    TITLO = '7'
    TITLO_V = '+'
    TITLO_G = 'g'
    TITLO_D = 'd'
    TITLO_H = '='
    TITLO_O = 'b'
    TITLO_R = '>'
    TITLO_S = 'c'
    TITLO_HER = '<'
    TITLO_CH = '?'
    TITLO_ZH = '•'
    TITLO_Z = '€'

    symb_titles_upper_list = [
        TITLO_UPP_BROAD,
        TITLO_UPP,
        TITLO_S_UPP,
    ]

    symb_titles_lower_list = [
        TITLO,
        TITLO_V,
        TITLO_G,
        TITLO_D,
        TITLO_H,
        TITLO_O,
        TITLO_R,
        TITLO_S,
        TITLO_HER,
        TITLO_CH,
        TITLO_ZH,
        TITLO_Z,
    ]

    symb_titles_list = [
        symb_titles_upper_list,
        symb_titles_lower_list,
    ]

    # Акценты.
    ZVATELCO_UPP = '#'
    OXIA_UPP = '~'
    VARIA_UPP = '@'
    ISO_UPP = '$'
    APOSTROF_UPP = '%'
    KAMORA_UPP = '^'
    EROK_UPP = '_'
    ZVATELCO = '3'
    OXIA = '1'
    VARIA = '2'
    ISO = '4'
    APOSTROF = '5'
    KAMORA = '6'
    EROK = '8'

    symb_accents_upper_list = [
        ZVATELCO_UPP,
        OXIA_UPP,
        VARIA_UPP,
        ISO_UPP,
        APOSTROF_UPP,
        KAMORA_UPP,
        EROK_UPP,
    ]

    symb_accents_lower_list = [
        ZVATELCO,
        OXIA,
        VARIA,
        ISO,
        APOSTROF,
        KAMORA,
        EROK,
    ]

    symb_accents_list = [
        symb_accents_upper_list,
        symb_accents_lower_list,
    ]

    # Прочие символы.
    THOUTHANDS_SIGN = '¤'
    KAVYKA = '°'

    symb_other_list = [
        THOUTHANDS_SIGN,
        KAVYKA,
    ]

    ucs_to_unicode_mathched_list = [
        # Совпадающие символы:
        CAPS_A,
        CAPS_B,
        CAPS_V,
        CAPS_G,
        CAPS_D,
        CAPS_E,
        CAPS_ZH,
        CAPS_Z,
        CAPS_DZE,
        CAPS_I,
        CAPS_I_KRATKOE,
        CAPS_K,
        CAPS_L,
        CAPS_M,
        CAPS_N,
        CAPS_O,
        CAPS_P,
        CAPS_R,
        CAPS_S,
        CAPS_T,
        CAPS_F,
        CAPS_HER,
        CAPS_CE,
        CAPS_CH,
        CAPS_SH,
        CAPS_CHSH,
        CAPS_HARD_SIGN,
        CAPS_Y,
        CAPS_SOFT_SIGN,
        CAPS_YU,

        SMALL_A,
        SMALL_B,
        SMALL_V,
        SMALL_G,
        SMALL_D,
        SMALL_E,
        SMALL_E_BROAD,
        SMALL_ZH,
        SMALL_Z,
        SMALL_ZELO,
        SMALL_I,
        SMALL_I_KRATKOE,
        SMALL_K,
        SMALL_L,
        SMALL_M,
        SMALL_N,
        SMALL_O,
        SMALL_P,
        SMALL_R,
        SMALL_S,
        SMALL_T,
        SMALL_F,
        SMALL_HER,
        SMALL_CE,
        SMALL_CH,
        SMALL_SH,
        SMALL_CHSH,
        SMALL_SOFT_SIGN,
        SMALL_Y,
        SMALL_HARD_SIGN,
        SMALL_YU,
    ]

    ucs_to_unicode_unmathched_list = [
        # Несовпадающие символы:
        CAPS_YAT,
        CAPS_I_DECIMAL,
        CAPS_O_BROAD,
        CAPS_OT,
        CAPS_OUK,
        CAPS_OUK_MONOGR,
        CAPS_O_GREAT,
        CAPS_YA_IOTIF,
        CAPS_YA,
        CAPS_IZHICA,
        CAPS_OMEGA,
        CAPS_PSI,
        CAPS_KSI,

        SMALL_IZHICA,
        SMALL_YAT,
        SMALL_I_DECIMAL,
        SMALL_O_BROAD,
        SMALL_OMEGA,
        SMALL_O_GREAT,
        SMALL_OT,
        SMALL_OUK_MONOGR,
        SMALL_OUK,
        SMALL_FITA,
        SMALL_YA,
        SMALL_YA_IOTIF,
        SMALL_PSI,
        SMALL_KSI,

        symb_monograph_list,
        symb_titles_list,
        symb_accents_list,
        symb_other_list,
    ]

    all_caps_letters_list = [
        # Совпадающие символы:
        CAPS_A,
        CAPS_B,
        CAPS_V,
        CAPS_G,
        CAPS_D,
        CAPS_E,
        CAPS_ZH,
        CAPS_Z,
        CAPS_DZE,
        CAPS_I,
        CAPS_I_DECIMAL,
        CAPS_I_KRATKOE,
        CAPS_K,
        CAPS_L,
        CAPS_M,
        CAPS_N,
        CAPS_O,
        CAPS_P,
        CAPS_R,
        CAPS_S,
        CAPS_T,
        CAPS_F,
        CAPS_HER,
        CAPS_CE,
        CAPS_CH,
        CAPS_SH,
        CAPS_CHSH,
        CAPS_HARD_SIGN,
        CAPS_Y,
        CAPS_SOFT_SIGN,
        CAPS_YU,

        # Несовпадающие символы:
        CAPS_YAT,
        CAPS_O_BROAD,
        CAPS_OT,
        CAPS_OUK,
        CAPS_OUK_MONOGR,
        CAPS_O_GREAT,
        CAPS_YA_IOTIF,
        CAPS_YA,
        CAPS_IZHICA,
        CAPS_OMEGA,
        CAPS_PSI,
        CAPS_KSI,
    ]

    symb_uppeer_list = [
        symb_titles_upper_list,
        symb_accents_upper_list,
    ]

    split_monograph_dic = {
        CAPS_A_AND_ZVATELCO: CAPS_A + ZVATELCO_UPP,
        CAPS_A_AND_ISO: CAPS_A + ISO_UPP,
        # CAPS_IZHICA_AND_KENDEMA,
        # CAPS_I_DECIMAL_AND_DOTS,
        CAPS_I_DECIMAL_AND_ZVATELCO: CAPS_I_DECIMAL + ZVATELCO_UPP,
        CAPS_I_DECIMAL_AND_ISO: CAPS_I_DECIMAL + ISO_UPP,
        CAPS_O_BROAD_AND_ZVATELCO: CAPS_O_BROAD + ZVATELCO_UPP,
        CAPS_O_BROAD_AND_ISO: CAPS_O_BROAD + ISO_UPP,
        CAPS_OMEGA_AND_ZVATELCO: CAPS_OMEGA + ZVATELCO_UPP,
        CAPS_OUK_AND_ISO: CAPS_OUK + ISO,
        CAPS_OUK_AND_ZVATELCO: CAPS_OUK + ZVATELCO,
        CAPS_YA_AND_ZVATELCO: CAPS_YA + ZVATELCO_UPP,
        CAPS_YA_IOTIF_AND_ZVATELCO: CAPS_YA_IOTIF + ZVATELCO_UPP,
        CAPS_YA_IOTIF_AND_ISO: CAPS_YA_IOTIF + ISO_UPP,

        SMALL_A_AND_ZVATELCO: SMALL_A + ZVATELCO,
        SMALL_A_AND_OXIA: SMALL_A + OXIA,
        SMALL_A_AND_VARIA: SMALL_A + VARIA,
        SMALL_A_AND_KAMORA: SMALL_A + KAMORA,
        SMALL_A_AND_ISO: SMALL_A + ISO,
        SMALL_A_AND_TITLO: SMALL_A + TITLO,
        SMALL_G_AND_TITLO: SMALL_G + TITLO,
        SMALL_D_AND_TITLO_S: SMALL_D + TITLO_S,
        SMALL_E_AND_OXIA: SMALL_E + OXIA,
        SMALL_E_AND_VARIA: SMALL_E + VARIA,
        SMALL_YAT_AND_OXIA: SMALL_YAT + OXIA,
        SMALL_YAT_AND_VARIA: SMALL_YAT + VARIA,
        SMALL_YAT_AND_KAMORA: SMALL_YAT + KAMORA_UPP,
        SMALL_ZH_AND_TITLO: SMALL_ZH + TITLO,
        SMALL_I_AND_TITLO: SMALL_I + TITLO,
        # SMALL_I_DECIMAL_AND_DOTS: ,
        SMALL_I_DECIMAL_AND_ZVATELCO: SMALL_I_DECIMAL + ZVATELCO,
        SMALL_I_DECIMAL_AND_OXIA: SMALL_I_DECIMAL + OXIA,
        SMALL_I_DECIMAL_AND_VARIA: SMALL_I_DECIMAL + VARIA,
        SMALL_I_DECIMAL_AND_KAMORA: SMALL_I_DECIMAL + KAMORA,
        SMALL_I_DECIMAL_AND_ISO: SMALL_I_DECIMAL + ISO,
        SMALL_I_DECIMAL_AND_TITLO: SMALL_I_DECIMAL + TITLO,
        SMALL_IZHICA_AND_OXIA: SMALL_IZHICA + OXIA,
        SMALL_IZHICA_AND_KAMORA: SMALL_IZHICA + KAMORA,
        # SMALL_IZHICA_AND_KENDEMA,
        SMALL_IZHICA_AND_TITLO_G: SMALL_IZHICA + TITLO_G,
        SMALL_L_AND_TITLO: SMALL_L + TITLO,
        SMALL_L_AND_TITLO_D: SMALL_L + TITLO_D,
        SMALL_O_AND_OXIA: SMALL_O + OXIA,
        SMALL_O_BROAD_AND_ZVATELCO: SMALL_O_BROAD + ZVATELCO,
        SMALL_O_BROAD_AND_ISO: SMALL_O_BROAD + ISO,
        SMALL_R_AND_TITLO: SMALL_R + TITLO,
        SMALL_R_AND_TITLO_D: SMALL_R + TITLO_D,
        SMALL_R_AND_TITLO_S: SMALL_R + TITLO_S,
        SMALL_S_AND_TITLO: SMALL_S + TITLO,
        SMALL_T_AND_TITLO: SMALL_T + TITLO,
        # SMALL_OUK_MONOGR_AND_OXIA,  # UGLY NON-KERNED
        # SMALL_OUK_MONOGR_AND_VARIA,  # UGLY NON-KERNED
        # SMALL_OUK_MONOGR_AND_KAMORA,  # UGLY NON-KERNED
        SMALL_OUK_AND_ZVATELCO: SMALL_OUK + ZVATELCO,
        SMALL_OUK_AND_ISO: SMALL_OUK + ISO,
        SMALL_HER_AND_TITLO: SMALL_HER + TITLO,
        SMALL_CH_AND_TITLO: SMALL_CH + TITLO,
        SMALL_YA_AND_ZVATELCO: SMALL_YA + ZVATELCO,
        SMALL_YA_AND_OXIA: SMALL_YA + OXIA,
        SMALL_YA_AND_VARIA: SMALL_YA + VARIA,
        SMALL_YA_AND_KAMORA: SMALL_YA + KAMORA,
        SMALL_YA_AND_APOSTROF: SMALL_YA + APOSTROF,
        SMALL_YA_IOTIF_AND_ZVATELCO: SMALL_YA_IOTIF + ZVATELCO,
        SMALL_YA_IOTIF_AND_ISO: SMALL_YA_IOTIF + ISO,
        SMALL_YA_IOTIF_AND_APOSTROF: SMALL_YA_IOTIF + APOSTROF,
        SMALL_KSI_AND_TITLO: SMALL_KSI + TITLO,
    }
