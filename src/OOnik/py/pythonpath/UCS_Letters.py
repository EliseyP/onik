# _*_ coding: utf-8

"""
UCS-символы
"""


class UCS:
    class CAPS:
        # Совпадающие символы:
        A = 'А'
        B = 'Б'
        V = 'В'
        G = 'Г'
        D = 'Д'
        E = 'Е'
        ZH = 'Ж'
        Z = 'З'
        DZE = 'Ѕ'
        IZHE = 'И'
        I_KRATKOE = 'Й'
        K = 'К'
        L = 'Л'
        M = 'М'
        N = 'Н'
        ON = 'О'
        P = 'П'
        R = 'Р'
        S = 'С'
        T = 'Т'
        F = 'Ф'
        HER = 'Х'
        CE = 'Ц'
        CH = 'Ч'
        SH = 'Ш'
        CHSH = 'Щ'
        HARD_SIGN = 'Ъ'
        Y = 'Ы'
        SOFT_SIGN = 'Ь'
        YU = 'Ю'

        # Несовпадающие символы:
        YAT = 'Э'
        I_DECIMAL = 'I'
        O_BROAD = 'O'
        OT = 'T'
        OUK = 'U'
        OUK_MONOGR = 'У'
        O_GREAT = 'Q'
        YA_IOTIF = 'Я'
        YA = 'Z'  # Юс малый
        IZHICA = 'V'
        OMEGA = 'W'
        PSI = 'P'
        KSI = 'X'

        # Монограф.
        A_AND_ZVATELCO = 'Ґ'
        A_AND_ISO = 'Ѓ'
        IZHICA_AND_KENDEMA = 'M'
        I_DECIMAL_AND_DOTS = 'І'
        I_DECIMAL_AND_ZVATELCO = 'Ї'
        I_DECIMAL_AND_ISO = 'Ј'
        O_BROAD_AND_ZVATELCO = 'N'
        O_BROAD_AND_ISO = 'Џ'
        OMEGA_AND_ZVATELCO = 'Њ'
        OUK_AND_ISO = 'Ќ'
        OUK_AND_ZVATELCO = 'Ў'
        YA_AND_ZVATELCO = 'Љ'
        YA_IOTIF_AND_ZVATELCO = 'K'
        YA_IOTIF_AND_ISO = 'Ћ'

    class SMALL:
        # Совпадающие символы:
        A = 'а'
        B = 'б'
        V = 'в'
        G = 'г'
        D = 'д'
        E = 'е'
        E_BROAD = 'є'
        ZH = 'ж'
        ZELO = 'ѕ'
        Z = 'з'
        IZHE = 'и'
        I_KRATKOE = 'й'
        K = 'к'
        L = 'л'
        M = 'м'
        N = 'н'
        ON = 'о'
        P = 'п'
        R = 'р'
        S = 'с'
        T = 'т'
        F = 'ф'
        HER = 'х'
        CE = 'ц'
        CH = 'ч'
        SH = 'ш'
        CHSH = 'щ'
        SOFT_SIGN = 'ь'
        Y = 'ы'
        HARD_SIGN = 'ъ'
        YU = 'ю'

        # Несовпадающие символы:
        IZHICA = 'v'
        YAT = 'э'
        I_DECIMAL = '\u0069'  # without dot (decimal), as base
        O_BROAD = 'o'
        OMEGA = 'w'
        O_GREAT = 'q'
        OT = 't'
        OUK_MONOGR = 'у'
        OUK = 'u'
        FITA = 'f'
        YA = 'z'  # Юс малый
        YA_IOTIF = 'я'
        PSI = 'p'
        KSI = 'x'

        # Монограф.
        A_AND_ZVATELCO = 'ґ'
        A_AND_OXIA = 'a'
        A_AND_VARIA = 'A'
        A_AND_KAMORA = '†'
        A_AND_ISO = 'ѓ'
        A_AND_TITLO = '№'
        G_AND_TITLO = 'G'
        D_AND_TITLO_S = 'D'
        E_AND_OXIA = 'e'
        E_AND_VARIA = 'E'
        YAT_AND_OXIA = 'ё'
        YAT_AND_VARIA = 'Ё'
        YAT_AND_KAMORA = 'B'
        ZH_AND_TITLO = '9'
        IZHE_AND_TITLO = '}'
        I_DECIMAL_AND_DOTS = '\u0456'  # with dots
        I_DECIMAL_AND_ZVATELCO = 'ї'
        I_DECIMAL_AND_OXIA = 'j'
        I_DECIMAL_AND_VARIA = 'J'
        I_DECIMAL_AND_KAMORA = '‡'
        I_DECIMAL_AND_ISO = 'ј'
        I_DECIMAL_AND_TITLO = '‹'
        IZHICA_AND_OXIA = 'Ђ'
        IZHICA_AND_KAMORA = '›'
        IZHICA_AND_KENDEMA = 'm'
        IZHICA_AND_TITLO_G = 'ђ'
        L_AND_TITLO = 'l'
        L_AND_TITLO_D = 'L'
        O_AND_OXIA = '0'
        O_BROAD_AND_ZVATELCO = 'n'
        O_BROAD_AND_ISO = 'џ'
        OMEGA_AND_ZVATELCO = 'њ'
        R_AND_TITLO = 'R'
        R_AND_TITLO_D = '®'
        R_AND_TITLO_S = 'r'
        S_AND_TITLO = '©'
        T_AND_TITLO = '™'
        OUK_MONOGR_AND_OXIA = 'y'
        OUK_MONOGR_AND_VARIA = 'Y'
        OUK_MONOGR_AND_KAMORA = '{'
        OUK_AND_ZVATELCO = 'ў'
        OUK_AND_ISO = 'ќ'
        HER_AND_TITLO = '¦'
        CH_AND_TITLO = '§'
        Y_AND_OXIA = 'h'
        YA_AND_ZVATELCO = 'љ'
        YA_AND_OXIA = 's'
        YA_AND_VARIA = 'S'
        YA_AND_KAMORA = '‰'
        YA_AND_APOSTROF = '|'
        YA_IOTIF_AND_ZVATELCO = 'k'
        YA_IOTIF_AND_ISO = 'ћ'
        YA_IOTIF_AND_APOSTROF = '±'
        KSI_AND_TITLO = '…'

    symb_monograph_list = [
        CAPS.A_AND_ZVATELCO,
        CAPS.A_AND_ISO,
        CAPS.IZHICA_AND_KENDEMA,
        CAPS.I_DECIMAL_AND_DOTS,
        CAPS.I_DECIMAL_AND_ZVATELCO,
        CAPS.I_DECIMAL_AND_ISO,
        CAPS.O_BROAD_AND_ZVATELCO,
        CAPS.O_BROAD_AND_ISO,
        CAPS.OMEGA_AND_ZVATELCO,
        CAPS.OUK_AND_ISO,
        CAPS.OUK_AND_ZVATELCO,
        CAPS.YA_AND_ZVATELCO,
        CAPS.YA_IOTIF_AND_ZVATELCO,
        CAPS.YA_IOTIF_AND_ISO,

        SMALL.A_AND_ZVATELCO,
        SMALL.A_AND_OXIA,
        SMALL.A_AND_VARIA,
        SMALL.A_AND_KAMORA,
        SMALL.A_AND_ISO,
        SMALL.A_AND_TITLO,
        SMALL.G_AND_TITLO,
        SMALL.D_AND_TITLO_S,
        SMALL.E_AND_OXIA,
        SMALL.E_AND_VARIA,
        SMALL.YAT_AND_OXIA,
        SMALL.YAT_AND_VARIA,
        SMALL.YAT_AND_KAMORA,
        SMALL.ZH_AND_TITLO,
        SMALL.IZHE_AND_TITLO,
        SMALL.I_DECIMAL_AND_DOTS,
        SMALL.I_DECIMAL_AND_ZVATELCO,
        SMALL.I_DECIMAL_AND_OXIA,
        SMALL.I_DECIMAL_AND_VARIA,
        SMALL.I_DECIMAL_AND_KAMORA,
        SMALL.I_DECIMAL_AND_ISO,
        SMALL.I_DECIMAL_AND_TITLO,
        SMALL.IZHICA_AND_OXIA,
        SMALL.IZHICA_AND_KAMORA,
        SMALL.IZHICA_AND_KENDEMA,
        SMALL.IZHICA_AND_TITLO_G,
        SMALL.L_AND_TITLO,
        SMALL.L_AND_TITLO_D,
        SMALL.O_AND_OXIA,
        SMALL.O_BROAD_AND_ZVATELCO,
        SMALL.O_BROAD_AND_ISO,
        SMALL.OMEGA_AND_ZVATELCO,
        SMALL.R_AND_TITLO,
        SMALL.R_AND_TITLO_D,
        SMALL.R_AND_TITLO_S,
        SMALL.S_AND_TITLO,
        SMALL.T_AND_TITLO,
        SMALL.OUK_MONOGR_AND_OXIA,
        SMALL.OUK_MONOGR_AND_VARIA,
        SMALL.OUK_MONOGR_AND_KAMORA,
        SMALL.OUK_AND_ZVATELCO,
        SMALL.OUK_AND_ISO,
        SMALL.HER_AND_TITLO,
        SMALL.CH_AND_TITLO,
        SMALL.Y_AND_OXIA,
        SMALL.YA_AND_ZVATELCO,
        SMALL.YA_AND_OXIA,
        SMALL.YA_AND_VARIA,
        SMALL.YA_AND_KAMORA,
        SMALL.YA_AND_APOSTROF,
        SMALL.YA_IOTIF_AND_ZVATELCO,
        SMALL.YA_IOTIF_AND_ISO,
        SMALL.YA_IOTIF_AND_APOSTROF,
        SMALL.KSI_AND_TITLO,
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
        CAPS.A,
        CAPS.B,
        CAPS.V,
        CAPS.G,
        CAPS.D,
        CAPS.E,
        CAPS.ZH,
        CAPS.Z,
        CAPS.DZE,
        CAPS.IZHE,
        CAPS.I_KRATKOE,
        CAPS.K,
        CAPS.L,
        CAPS.M,
        CAPS.N,
        CAPS.ON,
        CAPS.P,
        CAPS.R,
        CAPS.S,
        CAPS.T,
        CAPS.F,
        CAPS.HER,
        CAPS.CE,
        CAPS.CH,
        CAPS.SH,
        CAPS.CHSH,
        CAPS.HARD_SIGN,
        CAPS.Y,
        CAPS.SOFT_SIGN,
        CAPS.YU,

        SMALL.A,
        SMALL.B,
        SMALL.V,
        SMALL.G,
        SMALL.D,
        SMALL.E,
        SMALL.E_BROAD,
        SMALL.ZH,
        SMALL.Z,
        SMALL.ZELO,
        SMALL.IZHE,
        SMALL.I_KRATKOE,
        SMALL.K,
        SMALL.L,
        SMALL.M,
        SMALL.N,
        SMALL.ON,
        SMALL.P,
        SMALL.R,
        SMALL.S,
        SMALL.T,
        SMALL.F,
        SMALL.HER,
        SMALL.CE,
        SMALL.CH,
        SMALL.SH,
        SMALL.CHSH,
        SMALL.SOFT_SIGN,
        SMALL.Y,
        SMALL.HARD_SIGN,
        SMALL.YU,
    ]

    ucs_to_unicode_unmathched_list = [
        # Несовпадающие символы:
        CAPS.YAT,
        CAPS.I_DECIMAL,
        CAPS.O_BROAD,
        CAPS.OT,
        CAPS.OUK,
        CAPS.OUK_MONOGR,
        CAPS.O_GREAT,
        CAPS.YA_IOTIF,
        CAPS.YA,
        CAPS.IZHICA,
        CAPS.OMEGA,
        CAPS.PSI,
        CAPS.KSI,

        SMALL.IZHICA,
        SMALL.YAT,
        SMALL.I_DECIMAL,
        SMALL.O_BROAD,
        SMALL.OMEGA,
        SMALL.O_GREAT,
        SMALL.OT,
        SMALL.OUK_MONOGR,
        SMALL.OUK,
        SMALL.FITA,
        SMALL.YA,
        SMALL.YA_IOTIF,
        SMALL.PSI,
        SMALL.KSI,

        symb_monograph_list,
        symb_titles_list,
        symb_accents_list,
        symb_other_list,
    ]

    all_caps_letters_list = [
        # Совпадающие символы:
        CAPS.A,
        CAPS.B,
        CAPS.V,
        CAPS.G,
        CAPS.D,
        CAPS.E,
        CAPS.ZH,
        CAPS.Z,
        CAPS.DZE,
        CAPS.IZHE,
        CAPS.I_DECIMAL,
        CAPS.I_KRATKOE,
        CAPS.K,
        CAPS.L,
        CAPS.M,
        CAPS.N,
        CAPS.ON,
        CAPS.P,
        CAPS.R,
        CAPS.S,
        CAPS.T,
        CAPS.F,
        CAPS.HER,
        CAPS.CE,
        CAPS.CH,
        CAPS.SH,
        CAPS.CHSH,
        CAPS.HARD_SIGN,
        CAPS.Y,
        CAPS.SOFT_SIGN,
        CAPS.YU,

        # Несовпадающие символы:
        CAPS.YAT,
        CAPS.O_BROAD,
        CAPS.OT,
        CAPS.OUK,
        CAPS.OUK_MONOGR,
        CAPS.O_GREAT,
        CAPS.YA_IOTIF,
        CAPS.YA,
        CAPS.IZHICA,
        CAPS.OMEGA,
        CAPS.PSI,
        CAPS.KSI,
    ]

    symb_uppeer_list = [
        symb_titles_upper_list,
        symb_accents_upper_list,
    ]

    split_monograph_dic = {
        CAPS.A_AND_ZVATELCO: CAPS.A + ZVATELCO_UPP,
        CAPS.A_AND_ISO: CAPS.A + ISO_UPP,
        # CAPS.IZHICA_AND_KENDEMA,
        # CAPS.I_DECIMAL_AND_DOTS,
        CAPS.I_DECIMAL_AND_ZVATELCO: CAPS.I_DECIMAL + ZVATELCO_UPP,
        CAPS.I_DECIMAL_AND_ISO: CAPS.I_DECIMAL + ISO_UPP,
        CAPS.O_BROAD_AND_ZVATELCO: CAPS.O_BROAD + ZVATELCO_UPP,
        CAPS.O_BROAD_AND_ISO: CAPS.O_BROAD + ISO_UPP,
        CAPS.OMEGA_AND_ZVATELCO: CAPS.OMEGA + ZVATELCO_UPP,
        CAPS.OUK_AND_ISO: CAPS.OUK + ISO,
        CAPS.OUK_AND_ZVATELCO: CAPS.OUK + ZVATELCO,
        CAPS.YA_AND_ZVATELCO: CAPS.YA + ZVATELCO_UPP,
        CAPS.YA_IOTIF_AND_ZVATELCO: CAPS.YA_IOTIF + ZVATELCO_UPP,
        CAPS.YA_IOTIF_AND_ISO: CAPS.YA_IOTIF + ISO_UPP,

        SMALL.A_AND_ZVATELCO: SMALL.A + ZVATELCO,
        SMALL.A_AND_OXIA: SMALL.A + OXIA,
        SMALL.A_AND_VARIA: SMALL.A + VARIA,
        SMALL.A_AND_KAMORA: SMALL.A + KAMORA,
        SMALL.A_AND_ISO: SMALL.A + ISO,
        SMALL.A_AND_TITLO: SMALL.A + TITLO,
        SMALL.G_AND_TITLO: SMALL.G + TITLO,
        SMALL.D_AND_TITLO_S: SMALL.D + TITLO_S,
        SMALL.E_AND_OXIA: SMALL.E + OXIA,
        SMALL.E_AND_VARIA: SMALL.E + VARIA,
        SMALL.YAT_AND_OXIA: SMALL.YAT + OXIA,
        SMALL.YAT_AND_VARIA: SMALL.YAT + VARIA,
        SMALL.YAT_AND_KAMORA: SMALL.YAT + KAMORA_UPP,
        SMALL.ZH_AND_TITLO: SMALL.ZH + TITLO,
        SMALL.IZHE_AND_TITLO: SMALL.IZHE + TITLO,
        # SMALL.I_DECIMAL_AND_DOTS: ,
        SMALL.I_DECIMAL_AND_ZVATELCO: SMALL.I_DECIMAL + ZVATELCO,
        SMALL.I_DECIMAL_AND_OXIA: SMALL.I_DECIMAL + OXIA,
        SMALL.I_DECIMAL_AND_VARIA: SMALL.I_DECIMAL + VARIA,
        SMALL.I_DECIMAL_AND_KAMORA: SMALL.I_DECIMAL + KAMORA,
        SMALL.I_DECIMAL_AND_ISO: SMALL.I_DECIMAL + ISO,
        SMALL.I_DECIMAL_AND_TITLO: SMALL.I_DECIMAL + TITLO,
        SMALL.IZHICA_AND_OXIA: SMALL.IZHICA + OXIA,
        SMALL.IZHICA_AND_KAMORA: SMALL.IZHICA + KAMORA,
        # SMALL.IZHICA_AND_KENDEMA,
        SMALL.IZHICA_AND_TITLO_G: SMALL.IZHICA + TITLO_G,
        SMALL.L_AND_TITLO: SMALL.L + TITLO,
        SMALL.L_AND_TITLO_D: SMALL.L + TITLO_D,
        SMALL.O_AND_OXIA: SMALL.ON + OXIA,
        SMALL.O_BROAD_AND_ZVATELCO: SMALL.O_BROAD + ZVATELCO,
        SMALL.O_BROAD_AND_ISO: SMALL.O_BROAD + ISO,
        SMALL.R_AND_TITLO: SMALL.R + TITLO,
        SMALL.R_AND_TITLO_D: SMALL.R + TITLO_D,
        SMALL.R_AND_TITLO_S: SMALL.R + TITLO_S,
        SMALL.S_AND_TITLO: SMALL.S + TITLO,
        SMALL.T_AND_TITLO: SMALL.T + TITLO,
        # SMALL.OUK_MONOGR_AND_OXIA,  # UGLY NON-KERNED
        # SMALL.OUK_MONOGR_AND_VARIA,  # UGLY NON-KERNED
        # SMALL.OUK_MONOGR_AND_KAMORA,  # UGLY NON-KERNED
        SMALL.OUK_AND_ZVATELCO: SMALL.OUK + ZVATELCO,
        SMALL.OUK_AND_ISO: SMALL.OUK + ISO,
        SMALL.HER_AND_TITLO: SMALL.HER + TITLO,
        SMALL.CH_AND_TITLO: SMALL.CH + TITLO,
        SMALL.YA_AND_ZVATELCO: SMALL.YA + ZVATELCO,
        SMALL.YA_AND_OXIA: SMALL.YA + OXIA,
        SMALL.YA_AND_VARIA: SMALL.YA + VARIA,
        SMALL.YA_AND_KAMORA: SMALL.YA + KAMORA,
        SMALL.YA_AND_APOSTROF: SMALL.YA + APOSTROF,
        SMALL.YA_IOTIF_AND_ZVATELCO: SMALL.YA_IOTIF + ZVATELCO,
        SMALL.YA_IOTIF_AND_ISO: SMALL.YA_IOTIF + ISO,
        SMALL.YA_IOTIF_AND_APOSTROF: SMALL.YA_IOTIF + APOSTROF,
        SMALL.KSI_AND_TITLO: SMALL.KSI + TITLO,
    }
