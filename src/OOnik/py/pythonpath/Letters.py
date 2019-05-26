# _*_ coding: utf-8

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

dbl_grave = '\u030F'  # in ѷ
acutes = Oxia + Varia + Kamora + dbl_grave
erok_comb = '\u033E'  # д̾
Erok = erok_comb
thousands = '\u0482'  # ҂
erok = '\u2E2F'  # дⸯ
titlo = '\u0483'  # а҃
pokrytie = '\u0487'
titlo_v = '\u2DE1' + pokrytie
titlo_g = '\u2DE2' + pokrytie
titlo_d = '\u2DE3'
titlo_o = '\u2DEA' + pokrytie
titlo_r = '\u2DEC' + pokrytie
titlo_s = '\u2DED' + pokrytie
# буквы под покрытием: "вгдорс"
under_pokrytie = '[\u2DE1\u2DE2\u2DE3\u2DEA\u2DEC\u2DED]'
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
cu_letters_with_superscripts = cu_letters + cu_superscripts +thousands
cu_non_letters = '[^' + cu_letters + ']'

lnum_1_9 = "авгдєѕзиѳ"
lnum_20_90 = "клмнѯѻпч"
lnum_10_90 = "і" + lnum_20_90
lnum_100_900 = "рстуфхѱѿц"
lnum_1_90 = lnum_1_9 + lnum_10_90
lnum_1_900 = lnum_1_90 + lnum_100_900

# согласные
cu_consonants = "БВГДЖЗЅꙀЙКЛМНПРСТФѲХЦЧШЩЪЬѮѰ" + "бвгджзѕꙁйклмнпрстфѳхцчшщъьѯѱ"
# гласные
cu_vowels = "АЕЄѢИІѴОѺѠꙌѼꙊУЫЭЮѦꙖЯаеєѣиіѵоѻѡꙍѽꙋуыэюѧꙗя" + unicNarrowO
# потенциально ударные гласные
cu_vowels_for_stressed = "АЕЄѢИІѴОѺѠꙊУЫЭЮѦꙖЯаеєѣиіѵоѻѡꙋуыэюѧꙗя"
cu_doubles = "Ѿѿ"
