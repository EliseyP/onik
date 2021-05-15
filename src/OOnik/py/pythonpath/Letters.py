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
unicCapitalG = '\u0413'  # Г
unicSmallG = '\u0433'  # г
unicCapitalD = '\u0414'  # Д
unicSmallD = '\u0434'  # д
unicNarrowD = '\u1C81'  # ᲁ
# ---------------------------------------
unicCapitalIe = '\u0415'  # Е
unicSmallIe = '\u0435'  # е
unicCapitalUkrIe = '\u0404'  # Є
unicSmallUkrIe = '\u0454'  # є
unicCapitalYat = '\u0462'  # Ѣ
unicSmallYat = '\u0463'  # ѣ
# ---------------------------------------
unicCapitalZh = '\u0416'  # Ж
unicSmallZh = '\u0436'  # ж

# ---------------------------------------
unicCapitalI = '\u0418'  # И
unicSmallI = '\u0438'  # и
unicCapitalUkrI = '\u0406'  # I
unicSmallUkrI = '\u0456'  # i without dot (decimal), as base
unicSmallUkrIWithDotComb = '\uE926'  # i with dot
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
# unicCapitalIotifA = '\u0656'  # Ꙗ
# unicSmallIotifA = '\u0657'  # ꙗ
unicCapitalIotifA = '\uA656'  # Ꙗ
unicSmallIotifA = '\uA657'  # ꙗ
unicCapitalLittleYus = '\u0466'  # Ѧ
unicSmallLittleYus = '\u0467'  # ѧ
unicCapitalIotifLittleYus = '\u0468'  # Ѩ
unicSmallIotifLittleYus = '\u0469'  # ѩ
unicCapitalYa = '\u042F'  # Я
unicSmallYA = '\u044F'  # я
# ---------------------------------------
unicCapitalA = '\u0410'  # А
unicCapitalZhe = '\u0416'  # Ж
unicSmallA = '\u0430'  # а
unicSmallVe = '\u0432'  # в
unicSmallGhe = '\u0433'  # г
unicSmallDe = '\u0434'  # д
unicSmallZhe = '\u0436'  # ж
unicSmallZe = '\u0437'  # з
unicSmallEl = '\u043B'  # л
unicCapitalPsi = '\u0470'  # Ѱ
unicSmallPsi = '\u0471'  # ѱ
unicSmallEr = '\u0440'  # р
unicSmallEs = '\u0441'  # с
unicSmallTe = '\u0442'  # т
unicSmallHa = '\u0445'  # х
unicSmallChe = '\u0447'  # ч
unicCapitalDze = '\u0405'  # Ѕ
unicSmallDze = '\u0455'  # ѕ
unicCapitalKsi = '\u046E'  # Ѯ
unicSmallKsi = '\u046F'  # ѯ

# ----------------------------
CircledCrossPommee = '\U0001F540'  # 🕀
CrossPommeeWithHalfCircleBelow = '\U0001F541'  # 🕁
CrossPommee = '\U0001F542'  # 🕂
NotchedLeftSemicircleWithThreeDots = '\U0001F543'   # 🕃
NotchedRightSemicircleWithThreeDots = '\U0001F544'   # 🕄
SymbolForMarksChapter = '\U0001F545'   # 🕅

# ----------------------------


# Потенциальная проблема:
# если в тексте будут встречаться незанесенные моно-символы буква+надстрочник,
# то на данный момент они будут рассматриваться как часть промежутка в слове,
# наравне с пробелами, пунктуацией и прочим.
# Соответственно, будут искажения всего слова по границе таких символов.
# Решение: расширить класс букв cu_letters_with_superscripts, по крайней мере при разбивке на части.
# Далее возможны проблемы в ф-ции pack(), - соответственно обработать ситуацию и там.
# unicSmallMonogrUkAndZvatelce = unicSmallMonogrUk + Zvatelce  # 
# unicSmallYatAndOxia = unicSmallYat + Oxia  # 
# unicSmallYatAndVaria = unicSmallYat + Varia  # 
# unicSmallYatAndKamora = unicSmallYat + Zvatelce  # 
# unicSmallYeruAndKamora = unicSmallYeru + Zvatelce  # 

unicSmallYeru = '\u044B'  # ы
unicSmallMonogrUkAndZvatelce = '\uE8E5'  # 
unicSmallYatAndOxia = '\uE901'  # 
unicSmallYatAndVaria = '\uE903'  # 
unicSmallYatAndKamora = '\uE904'  # 
unicSmallYeruAndKamora = '\uE928'  # 
# Some variants while converting

# Orthodox.tt eRoos	: chr(&H0456) і ->  chr(&HE926)
# Valaam			: chr(&H0152) Œ	->  chr(&HE926)
unicSmallUkrIWithDot = unicSmallYi  # i -> ї

Dagger = CrossOrthodox  # † -> ☦

unicSmallYo = '\u0451'  # ё

UnicodeFont = "Ponomar Unicode"

kavyka = '\uA67E'
dbl_grave = '\u030F'  # in ѷ
acutes = Oxia + Varia + Kamora + dbl_grave
erok_comb = '\u033E'  # д̾
Erok = erok_comb
thousands = '\u0482'  # ҂
erok = '\u2E2F'  # дⸯ
titlo = '\u0483'  # а҃
pokrytie = '\u0487'
b_under = '\u2DE0'
v_under = '\u2DE1'
g_under = '\u2DE2'
d_under = '\u2DE3'
zh_under = '\u2DE4'
z_under = '\u2DE5'
k_under = '\u2DE6'
l_under = '\u2DE7'
m_under = '\u2DE8'
n_under = '\u2DE9'
o_under = '\u2DEA'
p_under = '\u2DEB'
r_under = '\u2DEC'
s_under = '\u2DED'
t_under = '\u2DEE'
x_under = '\u2DEF'
c_under = '\u2DF0'
ch_under = '\u2DF1'
sh_under = '\u2DF2'
shch_under = '\u2DF3'
f_under = '\u2DF4'
st_under = '\u2DF5'
a_under = '\u2DF6'
e_under = '\u2DF7'
y_under = '\u2DF9'
yat_under = '\u2DFA'

titlo_v = v_under + pokrytie
titlo_g = g_under + pokrytie
titlo_d = d_under
titlo_n = n_under + pokrytie
titlo_o = o_under + pokrytie
titlo_r = r_under + pokrytie
titlo_s = s_under + pokrytie
titlo_ch = ch_under + pokrytie

titlo_zh = zh_under
titlo_z = z_under
titlo_t = t_under
titlo_st = st_under
titlo_x = x_under

# буквы под покрытием: "бвгджзклмнолрстхцчшщаеуѣ"
# FIXME: если еще неизвестная буква под титлом, то ошибка

# under_pokrytie = '[\u2DE1\u2DE2\u2DE3\u2DEA\u2DEC\u2DED\u2DF1]'
under_pokrytie_list = [
    b_under,
    v_under,
    g_under,
    d_under,
    zh_under,
    z_under,
    k_under,
    l_under,
    m_under,
    n_under,
    o_under,
    p_under,
    r_under,
    s_under,
    t_under,
    x_under,
    c_under,
    ch_under,
    sh_under,
    shch_under,
    f_under,
    titlo_st,
    a_under,
    e_under,
    y_under,
    yat_under,
]
under_pokrytie = '[' + ''.join(under_pokrytie_list) + ']'

titles = titlo + titlo_v + titlo_g + titlo_d + titlo_o + titlo_r + titlo_s + titlo_x + titlo_ch + titlo_n
overlines_for_consonants = \
    titles + erok_comb  # + erok
overlines_for_vowels = acutes + Zvatelce + Kendema

latin_i = "i"  # для слова мip

combined_monosymbols_dic = {
    unicCapitalIzhitsaDblGrave: (unicCapitalIzhitsa, dbl_grave),
    unicSmallIzhitsaDblGrave: (unicSmallIzhitsa, dbl_grave),
    unicCapitalYi: (unicCapitalUkrI, Kendema),
    unicSmallYi: (unicSmallUkrI, Kendema),
    unicSmallUkrIWithDotComb: (unicSmallUkrI, Kendema),
    unicSmallMonogrUkAndZvatelce: (unicSmallMonogrUk, Zvatelce),
    unicSmallYatAndOxia: (unicSmallYat, Oxia),
    unicSmallYatAndVaria: (unicSmallYat, Varia),
    unicSmallYatAndKamora: (unicSmallYat, Kamora),
    unicSmallYeruAndKamora: (unicSmallYeru, Kamora),
}

cu_before_er = "[БВГДЖЗКЛМНПРСТФѲХЦЧШЩбвгджзклмнпрстфѳхцчшщ]"
# UPD: удаение Ї (поскольку это І + Kendema)
cu_cap_letters = \
    "АБВГДЕЄѢЖЗЅꙀИІѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦЧШЩЪЫЬЮѦꙖЯѮѰ" + unicCapitalIzhitsaDblGrave + unicCapitalYi
# UPD: удаление ї (поскольку это і + Kendema)
cu_small_letters = \
    "абвгдеєѣжзѕꙁиіѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ" + \
    unicNarrowO + unicNarrowD + erok + \
    unicSmallIzhitsaDblGrave + unicSmallYi
cu_cap_letters_text = \
    "АБВГДЕЄѢЖЗЅꙀИІѴЙКЛМНОѺѠѾꙌѼПРСТꙊУФѲХЦЧШЩЪЫЬЮѦꙖЯѮѰ"
cu_small_letters_text = \
    "абвгдеєѣжзѕꙁиіѵйклмноѻѡѿꙍѽпрстꙋуфѳхцчшщъыьюѧꙗяѯѱ" + unicNarrowO + unicNarrowD + erok
cu_letters = cu_cap_letters + cu_small_letters
cu_letters_text = cu_cap_letters_text + cu_small_letters_text
cu_superscripts = overlines_for_vowels + overlines_for_consonants
cu_letters_with_superscripts = (
    cu_letters +
    cu_superscripts +
    thousands +
    latin_i +
    'э' +
    ''.join(combined_monosymbols_dic.keys())
)
cu_non_letters = '[^' + cu_letters + ']'
cu_non_letters_with_superscripts = '[^' + cu_letters_with_superscripts + ']'

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
