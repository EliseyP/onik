from Letters import *

# Наборы регулярных выражений вида:
# [find, replace [, flags] ]
# компилируются перед запуском основной функции

# Буквы в словах: ѿ, ѡ, ѵ, ѣ, etc

VA = r'\g<0>' + Varia
OX = r'\g<0>' + Oxia
IS = r'\g<0>' + Iso
GKA = r'\g<0>' + Kamora
GAP = r'\g<0>' + Apostrof
ER = r'\1' + Erok
# GER = r'\g<0>' + Erok
# ZG = r'\g<0>'

# список исключений для ѿ
# или наоборот, перечислить ѿ ?
ot_letters_at_start_of_word = r'''
    (?!
        е?ц
        | е?ч(?!аѧн)
        # | да[нт]
        # | враща
        # | врещи
        # | в[еѣ][тщ]
        # | жен
        | зд[еѣ]
        | иш
        #| крове # ѿкрове́нїе
        | орван
        | расль
        | реб
        | ри\b
        | рет
        | ро[кчц]
        | ѧгч
    )
'''

regs_letters_in_word = (
    [r'\bот' + ot_letters_at_start_of_word, r'ѿ'],
    [r'\bОт' + ot_letters_at_start_of_word, r'Ѿ'],

    [r'\b(ѿ)ъ\b', r'\1', 'i'],

    [r'ейш', r'ѣйш'],

    # безпло́дный безкрайнїй безсм҃ртный
    [r'бес(?=[кпстцчшщ])', r'без'],

    [r'\bОу(?=[' + cu_cap_letters + r']+)', r'ОꙊ'],  # УМ -> ОꙊ҆МЪ
    [r'\bО\b', r'Ѽ'],  # как правило - обращение
    [r'\bо\b', r'ѡ'],
    [r'\bо', r'ѻ'],
    [r'\bО(?!у)', r'Ѻ'],

    [  # ᲂꙋ -> ᲂу (для исправления ошибок набора)
        # проблема: узкое о
        # на границе слова '\bᲂ' не работает
        # условно \b = не буквы (ноль или больше)
        # все не-буквы попадают в pref и post
        # и вырезаются (с сохранением) в начале,
        # поэтому можно (конкретно для этого случая) использовать
        # ^ - начало строки
        # Вариант:  cu_non_letter + '*' + unicNarrowO + '?ꙋ'
        r'^' + unicNarrowO + 'ꙋ', 'ᲂу'],


    [  # -ии- -> -їи-
        # TODO: -їѧ & -їа
        r'и(?=[аеєийоѡꙋюѧ])', r'ї'],

    [r'И(?=[АЕЄИЙОѠꙊЮѦаеєийоѡꙋюѧ])', r'І'],
    [r'ᲂ+', r'ᲂ'],

    # Zvatelce for first letter of word
    [r'^([АЄИІѴѠЮꙖаєиіѻѡюꙗ]|Ѻ(?!ꙋ))', r'\1' + Zvatelce],

    # Исправление ошибочного парсинга
    # слово начинается с прописной У
    # У -> Ꙋ -> Оу -> Ѻꙋ
    [r'Ѻꙋ', r'Оу'],


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ааа aaa

    [r'(аар)о(?=н)', r'\1ѡ', 'i'],
    [r'(аерм)о(?=н)', r'\1ѡ', 'i'],
    [r'(ака)фи(?=ст)', r'\1ѳї', 'i'],
    [r'(але)кс', r'\1ѯ', 'i'],
    [r'(амв)о(?=н)', r'\1ѡ', 'i'],
    [r'(ант)и(?=х)', r'\1ї', 'i'],
    [r'(апостольст)е(?=й)', r'\1ѣ', 'i'],
    [r'(а)ф(?=анас)', r'\1ѳ', 'i'],
    [r'(а)фо(?=н)', r'\1ѳѡ', 'i'],
    #

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ббб bbb

    [r'\b(б)е(?=д[аеносꙋъы])', r'\1ѣ', 'i'],

    # -бѣг- -бѣж-
    [r'''  
        (
            \b(?:
                из|при|ѿ|на
            )?
            |^ᲂу
        )
        бе
        (?=
            (
                г
                |ж(?!д) # ! убежден-
            )
            [аеилноꙋъ]
        )
        ''',
        r'\1бѣ'],

    [r'(безм)е(?=(р|ст)н)', r'\1ѣ', 'i'],

    [r'(\b|^[Оᲂ]у)бел', r'\1бѣл', 'i'],
    [r'\bбес(?=[аиноѡꙋы])', r'бѣс'],
    [r'\b(б)е\b', r'\1ѣ', 'i'],
    [r'\b(б)е(?=сте\b)', r'\1ѣ', 'i'],
    [r'\b(б)е(?=х(ом)?ъ\b)', r'\1ѣ', 'i'],
    [r'\b(б)е(?=ша\b)', r'\1ѣ', 'i'],
    [r'\b(бд)е(?=[нт])', r'\1ѣ', 'i'],
    [r'(благогов)е(?=й?н)', r'\1ѣ', 'i'],
    [r'(благодарн)о\b', r'\1ѡ', 'i'],
    [r'(благод)е(?=тел)', r'\1ѣ', 'i'],
    [r'(богов)е(?=ден)', r'\1ѣ', 'i'],
    [r'\b(боз)е\b', r'\1ѣ', 'i'],
    [r'(бол)е(?=зн)', r'\1ѣ', 'i'],
    [r'(бран)е(?=х)', r'\1ѣ', 'i'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ввв vvv

    # ========================
    #   вѣд вѣж вѣм вѣт вѣс вѣщ
    #   -вѣд-
    [r'''
        \b(не|из|(за|ис|про)?по)?
        вед (?=[аиноыꙋь])
        ''',
        r'\1вѣд', 'i'],
    [r'(\bзапов)е(?=де([мх]ъ|й))', r'\1ѣ', 'i'],
    [r'''
    \b(бого|тайно|не(до)?|ᲂу|предꙋ?)?
    вед(?=е)
    (?!
        е
        (
         м?сѧ
         |ни
         |наг[оѡ]
         |т[еъ]
         |тсѧ
         |ши
        )\b
    )
    ''',
     r'\1вѣд', 'i'],

    [r'\b((не|тайно)?в)ѣде(?=ні)', r'\1ѣдѣ', 'i'],
    [r'\b(сердцев)е(?=дче)', r'\1ѣ', 'i'],

    #   -вѣж-
    [r'\b(не)?ве(?=ж)', r'\1вѣ'],

    #   -вѣм-
    [r'''
        \b((?:ис)?по)?
        ([Вв])ем
        (?=[ыъ])
        ''',
        r'\1\2ѣм'],

    #   -вѣс-
    [r'\b(не|со|благо)?вес(?=и\b|т)', r'\1вѣс'],
    [r'\b(возв)е(?=ст(?!и\b))', r'\1ѣ'],  # ! возвести

    #   -вѣт-
    [r''' 
        \b([Зз]а|из|ѻт|ꙋ|на|со)
        вет
        (?=[ълнаеиоѡꙋы])
        ''',
        r'\1вѣт'],
    [r'(в)е(?=ті[иѧ])', r'\1ѣ'],

    #   -вѣщ-
    [r'''
        (?<!кле)
        вещ
        (?!
            # ! вещи, вещество
            (
                [иь]\b
                | [еє]([ймх]|ств)
                | ам[иъ]\b
                | ь?ми\b
            )
            # \b
        )
        ''',
     r'вѣщ'],
    # ---- вѣд вѣж вѣм вѣт вѣс вѣщ ----

    [r'\bвезде\b', r'вездѣ'],

    # ========================
    # вѣк- вѣц- вѣч-
    [r'\b(в)е(?=к[аеиꙋъ](ми)?\b)', r'\1ѣ'],
    [r'\b(в)еко(?=въ)', r'\1ѣкѡ'],
    [r'веце(?=(хъ)?)', r'вѣцѣ'],
    [r'(в)е(?=че?н)', r'\1ѣ'],
    # ------------------------

    [r'(?<!пер)(в)ен(?=е?[чц])', r'\1ѣн', 'i'],
    [r'(\b(не|[ѿвѕ]|благо)?в)ер(?=[аеиноꙋыѧ])', r'\1ѣр', 'i'],
    [r'ветв', r'вѣтв'],
    [r'вет(е?р)', r'вѣт\1'],

    [r'\b(вид)е\b', r'\1ѣ', 'i'],
    [r'(вид)е(?!е[цн]ъ)', r'\1ѣ', 'i'],
    # [r'\b((нена)?в)идені', r'\1идѣнї', 'i'],

    [r'\b(в)ин(?=[аеоꙋ]\b|оград)', r'\1їн', 'i'],
    [r'\bвиссон', r'вѵ́ссон'],
    [r'\b(вкꙋп)е\b', r'\1ѣ'],
    [r'([Вв])ладими(?=р)', r'\1ладимї'],
    [r'вменѧ', r'вмѣнѧ'],
    [r'(вождел)е', r'\1ѣ'],

    [r'возде(?=(ва)?ти|е[мтш]|хшю)', r'воздѣ'],
    [r'(возд)е(?=в[аш])', r'\1ѣ'],
    [r'(возд)е(?=ж)', r'\1ѣ'],

    [r'(в)осп[еѣ]ва', r'\1оспѣва', 'i'],
    [r'(во)с(ста)', r'\1з\2', 'i'],
    [r'врач[ьъ]', r'врачь'],
    [r'\b(в)се(?=(м[иъ]|хъ)\b)', r'\1сѣ', 'i'],
    [r'\b(вскор)е\b', r'\1ѣ', 'i'],
    [r'втайне', r'втайнѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ггг ggg

    [r'([Гг])ефсиман', r'\1еѳсїман'],
    [r'(([Гг])еѳсімані)ѧ', r'\g<1>а'],
    [r'(([Гг])еѳсіманійст)ей', r'\g<1>ѣй'],
    [r'([Гг])олгоф', r'\1олгоѳ'],

    [r'([Гг])нев', r'\1нѣв'],
    [r'([Гг]ласн)о\b', r'\1ѡ'],
    [r'горет', r'горѣт'],

    [r'([Гг])ресех', r'\1рѣсѣх'],
    [r'([Гг])ре(?=[схш])', r'\1рѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ддд ddd

    [r'''
        \b
        (присно)?
        (д)ев
        (?=[аеоꙋы]|ств|ическ)
        ''',
        r'\1\2ѣв', 'i'],

    [r'\bдет(?!=инец)', r'дѣт'],
    [r'издетска', r'издѣтска'],
    [r'дел(?=[оаꙋъ])', r'дѣл'],

    # дѣѧнїѧ ! ѳаддеѧ і҆ꙋдеѧ
    [r'(?<!дд|іꙋ)([Дд])еѧ', r'\1ѣѧ'],
    # дѣю ! надеждею і҆ꙋдею
    [r'(?<![аеꙋ]ж|іꙋ)([Дд])ею', r'\1ѣю'],

    [r'([Дд])иве(?=ев)', r'\1ивѣ'],
    [r'([Дд])ивно\b', r'\1ивнѡ'],
    [r'([Дд])іонисі', r'\1їѻнѵсї'],
    [r'([Дд])іоскор', r'\1їѻскор'],
    [r'\bдне\b', r'днѣ'],
    [r'добродетел', r'добродѣтел'],
    [r'([Дд])околе', r'\1околѣ'],
    [r'([Дд])оселе', r'\1оселѣ'],
    [r'\b([Дд])ꙋсе\b', r'\1ꙋсѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # еее eee

    [r'(є)в(?=ангел)', r'\1ѵ', 'i'],
    [r'(є)в(?=фрафовъ)', r'\1ѵ', 'i'],
    [r'(є)вхарист', r'\1ѵхарїст', 'i'],
    [r'(є)го\b', r'\1гѡ', 'i'],  # Род: єгѡ Вин.: єго
    [r'(є)ги(?=пе?т)', r'\1гѵ', 'i'],  # Род: єгѡ Вин.: єго
    [r'(є)лисе(?=\w)', r'\1лиссе', 'i'],  # var: єлїссей
    [r'(є)пи(?=скоп)', r'\1пї', 'i'],  # var: єлїссей

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # жжж

    [r'(жал)е(?=[велнстюѧ])', r'\1ѣ'],
    [r'(жел)е', r'\1ѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ззз zzz

    [r'([Зз])авес', r'\1авѣс'],
    [r'Звезд', r'Ѕвѣзд'],
    [r'звезд', r'ѕвѣзд'],
    [r'звер(?!ж)', r'ѕвѣр'],
    [r'\b([Зз])де(?=(сь)?\b)', r'\1дѣ'],
    [r'\b([Гг])де\b', r'\1дѣ'],

    [r'зел\b', r'ѕѣлѡ'],
    [r'\bЗело\b', r'Ѕѣлѡ'],
    [r'\bзело\b', r'ѕѣлѡ'],
    [r'Зельне', r'Ѕѣльнѣ'],
    [r'зельне', r'ѕѣльнѣ'],
    [r'Зельн', r'Ѕѣльн'],
    [r'зельн', r'ѕѣльн'],

    [r'зениц', r'зѣниц'],
    [r'(?<!же)зл(?=об)', r'ѕл'],
    [r'\bЗолъ\b', r'Ѕолъ'],
    [r'\bзолъ\b', r'ѕолъ'],
    [r'\b(?<!же)зл(?=[еѣіоꙋы]|а(?![зтцчщ]|га))', r'ѕл'],
    [r'зме(?=[йюѧ]\b|[еи]\w+)', r'ѕмѣ'],
    [r'змі(?=[йюѧ]\b|[еи]\w+)', r'ѕмї'],

    # [r'(пр[ие])?зре(?=тш|ні|\b)', r'\1зрѣ'],
    # [r'(пр[ие])зре(?=[влнстхш]|\b)', r'\1зрѣ'],
    # -зрѣ-
    [r'(?<!во)(з)ре(?=в(?![нѣ])|[лнстхш]|\b)', r'\1рѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # иии iii

    [r'Іакинф', r'Ѵакінѳ'],
    [r'іакинф', r'ѵакінѳ'],
    [r'([Іі])аков', r'\1акѡв'],
    [r'идеже', r'идѣже'],
    [r'И(?=зраил)', r'І'],
    [r'и(?=зраил)', r'і'],
    [r'изрѧдно\b', r'изрѧднѡ'],
    [r'\bикон', r'ікѡн'],
    [r'\bИкон', r'Ікѡн'],
    [r'и(?=косъ)', r'і'],
    [r'И(?=косъ)', r'І', 'i'],
    [r'\b([Ии])ме(?![нт])', r'\1мѣ'],
    [r'([Іі])о(?=ан|аким|в|на|сиф|ил|ота)', r'\1ѡ'],
    [r'([Іі])ордан', r'\1ѻрдан'],
    [r'И(?=пакои)', r'Ѵ'],
    [r'и(?=пакои)', r'ѵ'],
    [r'И(?=постас)', r'Ѵ'],
    [r'и(?=постас)', r'ѵ'],
    [r'И(?=рмос)', r'І'],
    [r'и(?=рмос)', r'і'],
    [r'иссоп', r'ѵссѡп'],
    [r'исцелен', r'исцѣлен'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ккк kkk

    [r'\b([Кк])ако\b', r'\1акѡ'],
    [r'\b([Кк])амо\b', r'\1амѡ'],
    [r'([Кк])ано(?=н(?!ар))', r'\1анѡ'],
    [r'([Кк])ивот', r'\1ївѡт'],
    [r'([Кк])ирилл', r'\1ѷрїлл'],
    [r'\b([Кк])оле(?=н)', r'\1олѣ'],
    [r'крепк', r'крѣпк'],
    [r'крѣпко', r'крѣпкѡ'],
    [r'([Кк])репост', r'\1рѣпост'],
    [r'([Кк]рестн)е(?=й)', r'\1ѣ'],
    [r'([Кк]р)и(?=стал)', r'\1ѷ'],
    [r'([Кк]рил)е(?=(хъ)?\b)', r'\1ѣ'],
    [r'(кꙋп)е(?=л)', r'\1ѣ', 'i'],
    [r'(кꙋпн)о\b', r'\1ѡ', 'i'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ллл lll

    # лепо боголепный великолѣ́пїе
    [r'''
        \b
        (
            (
                б
                (
                    (о|ла|л҃)г
                    |г҃
                )о
                |велико 
            )?
            л
        )
        е(?=пн?[иіоы])
        ''', r'\1ѣ', 'i'],

    [r'\b(не|ѻб|раз)?лен(?=ь|ив|ост|ѧщ|ен)', r'\1лѣн'],
    [r'\bлес(?=[аъ])', r'лѣс'],
    [r'\bлестви(?=[чц])', r'лѣстви'],
    [r'\bлето', r'лѣто'],
    [r'\b([Лл])итꙋрг', r'\1їтꙋрг'],
    [r'\b([Лл])иті', r'\1їтї'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ммм mmm

    [r'\b(из|от)?мер(?=[аеыꙋ]\b|ил)', r'\1мѣр'],
    [r'мест(?=[аеѣоꙋ]\b)', r'мѣст'],
    [r'(нет)[еѣ](сновм)е(?=сти)', r'\1ѣ\2ѣ'],

    [r'''
        ( # \1
          (
            (не)?в
            |без
            |на
          )?
          м
        ) # \1
        е
        (?=
            ст(и[влмстхш]|н[аѣоѡꙋы]|е[нх]ъ)
        )
        ''', r'\1ѣ'],
    [r'(вм)ещ(?=[сш]|[ае])', r'\1ѣщ', 'i'],

    [r'\b([Мм])е(?=сѧц)', r'\1ѣ'],
    # всемїрный надмїрный
    [r'\b((все|над)м)и(?=рн)', r'\1ї', 'i'],
    [r'\b([Мм])и(?=хаил)', r'\1ї'],

    # [r'\bм' + latin_i + r'(?=р)', r'мї', 'i'],
    [r'\bми(?=р(с[кт]|ѧн))', r'мї', 'i'],
    [r'\b(м)и(?=ро\b|ронос)', r'\1ѵ', 'i'],

    [r'\b([Мм])не\b', r'\1нѣ'],
    [r'\b((со)?[Мм])не(?=ти\b|ні)', r'\1нѣ'],
    [r'\b([Мм])оисе', r'\1ѡѷсе'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ннн nnn

    [r'надеѧ(?=ніе|тисѧ)', r'надѣѧ'],
    [r'надею(?=щі|с)', r'надѣю'],
    [r'намерен', r'намѣрен'],
    [r'([Нн]ебес)е(?=хъ)', r'\1ѣ'],
    [r'([Нн])евест', r'\1евѣст'],
    [r'([Нн])егоже\b', r'\1егѡже'],

    # нѣгдѣ
    [r'\b([Нн])егде\b', r'\1ѣгдѣ'],

    [r'([Нн])едел', r'\1едѣл'],
    [r'недр', r'нѣдр'],
    [r'\b((?:все)?н)е(?=жн)', r'\1ѣ', 'i'],
    [r'([Нн])ѣжно\b', r'\1ѣжнѡ'],

    # нѣкто нѣкогда нѣкїй
    [r'\b([Нн])е(?=к(огда|то|ій)\b)', r'\1ѣ'],
    [r'\b([Нн])е(?=котор)', r'\1ѣ'],

    # нѣ́мы
    [r'\bне(?=м([аіоꙋы]\w|ы)\b)', r'нѣ'],

    [r'\b([Нн]епрестанн)о', r'\1ѡ'],
    [r'\bнераде(?=ні)', r'нерадѣ'],
    [r'\b([Нн])еси\b', r'\1ѣси'],
    [r'\b([Нн])есм(?=[ыь]\b)', r'\1ѣсм'],
    [r'\b([Нн])ест(?=[еь]\b)', r'\1ѣст'],
    [r'\b([Нн])е(?=что\b)', r'\1ѣ'],

    # нїкола́й
    [r'([Нн])икол(?!иже)', r'\1їкол'],
    [r'([Нн])ыне', r'\1ынѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ооо ooo

    # TODO:
    # ѻ в середине слова праѻтє́цъ
    [r'оо(?!тв|з)', r'оѻ'],

    [r'Ѻ(?=баче)', r'Ѡ'],
    [r'ѻ(?=баче)', r'ѡ'],

    [r'ѻбе(?=сити)', r'ѡбѣ'],
    [r'ѻбе(?=т)', r'ѻбѣ'],
    [r'ѻбе(?=ща)', r'ѻбѣ'],

    [r'ѻ(?=блада)', r'ѡ'],
    [r'ѻ(?=блача)', r'ѡ'],
    [r'ѻ(?=блег)', r'ѡ'],
    [r'ѻ(?=бле[кцчщ])', r'ѡ'],
    [r'ѻ(?=блист)', r'ѡ'],
    [r'ѻ(?=блоб)', r'ѡ'],
    [r'ѻ(?=блож)', r'ѡ'],
    [r'ѻ(?=блѧз)', r'ѡ'],

    [r'Ѻ(?=бнов)', r'Ѡ'],
    [r'ѻ(?=бнов)', r'ѡ'],

    [r'\bѺ(?=бож)', r'Ѡ'],
    [r'\bѻ(?=бож)', r'ѡ'],

    [r'Ѻ(?=браз)', r'Ѡ'],
    # [r'((?<!о)[ѻо])браз', r'ѡбраз'],
    # [r'(из)?[ѻо]браз', r'\1ѡбраз'],
    # [r'оѻбра([зжщ])', r'оѡбра\1'],
    [r'[ѻо](?=бра[зжщ])', r'ѡ'],

    [r'ѻ(?=брад)', r'ѡ'],
    [r'ѻ(?=брат)', r'ѡ'],
    [r'ѻ(?=бращ)', r'ѡ'],
    [r'ѻбре(?=[лст])', r'ѡбрѣ'],
    [r'ѻ(?=бремен)', r'ѡ'],
    [r'ѻ(?=брѧщ)', r'ѡ'],

    [r'ѻ(?=бстоѧ)', r'ѡ'],

    [r'ѻб(ы|ъи)м(?=[аеиꙋ])', r'ѡбъим'],
    [r'ѻб(ы|ъи)д(?=[еиоꙋ])', r'ѡбъид'],
    [r'ѻб(ы|ъи)ти', r'ѡбъити'],

    [r'ѻ(?=бъѧ[вдлстхш])', r'ѡ'],
    [r'ѻ(?=бъем)', r'ѡ'],
    [r'Ѻ(?=бъем)', r'Ѡ'],
    [r'ѻ(?=бꙋр)', r'ѡ'],
    [r'ѻ(?=бꙋѧ)', r'ѡ'],

    [r'ѻглавлен', r'ѡглавлен'],

    [r'ѻде(?=ва[еюѧ]|ющ|ѧ)', r'ѡдѣ'],
    [r'ѻ(?=ж[ежир])', r'ѡ'],
    [r'Ѻ(?=зар[еєиѧ])', r'Ѡ'],
    [r'ѻ(?=зар[еєиѧ])', r'ѡ'],
    [r'ѻ(?=кропи)', r'ѡ'],
    [r'Ѻ(?=крест)', r'Ѡ'],
    [r'ѻ(?=крест)', r'ѡ'],
    [r'Ѻ(?=каѧ)', r'Ѡ'],
    [r'ѻ(?=каѧ)', r'ѡ'],
    [r'ѻл[ѧе]дене(?=вш)', r'ѡлѧденѣ'],
    [r'Ѻ(?=мы\w)', r'Ѡ'],  # ѡ҆мы́й
    [r'ѻ(?=мы\w)', r'ѡ'],

    [r'\bѺ(?=ро(си|ша))', r'Ѡ'],
    [r'\bѻ(?=ро(си|ша))', r'ѡ'],
    [r'ѻ(?=правд)', r'ѡ'],
    [r'Ѻсен', r'Ѡсѣн'],
    [r'ѻсен', r'ѡсѣн'],
    [r'пріосен', r'прїѡсѣн'],
    [r'Ѻ(?=свѧ[тщ])', r'Ѡ'],
    [r'ѻ(?=свѧ[тщ])', r'ѡ'],
    [r'Ѻ(?=скверн)', r'Ѡ'],
    [r'ѻ(?=скверн)', r'ѡ'],
    [r'Ѻ(?=скорб)', r'Ѡ'],
    [r'ѻ(?=скорб)', r'ѡ'],
    [r'Ѻскꙋде', r'Ѡскꙋдѣ'],
    [r'ѻскꙋде', r'ѡскꙋдѣ'],
    [r'Ѻ(?=став)', r'Ѡ'],
    [r'ѻ(?=став)', r'ѡ'],
    [r'ѻ(?=сꙋ)', r'ѡ'],

    # [r'ѻт(?=жен)', r'ѿ'],
    [r'([Ѿѿ])о(?=нюдꙋже)', r'\1ѻ'],
    [r'([Ѿѿ]сел)е\b', r'\1ѣ'],
    [r'ѻт(?=чаѧн)', r'ѿ'],
    [r'([Ѻѻ])тцевъ', r'\1тцєвъ'],
    [r'([Ѿѿ])ъѧтъ', r'\1ѧтъ'],
    [r'([Ѿѿ])(ъи|ы)ми\b', r'\1ими'],

    [r'Ѻ(?=чи(сти|щ))', r'Ѡ'],
    [r'ѻ(?=чи(сти|щ))', r'ѡ'],

    [r'(ѻчес)е(?=[мх]ъ)', r'\1ѣ', 'i'],

    # ѡ в середине слова
    [r'нео(?=слаб)', r'неѡ'],
    [r'нео(?=сꙋ)', r'неѡ'],

    # ѿ в середине слова
    [r'\bнеот(?=вратн|стꙋп)', r'неѿ'],
    [r'\bнеотъ(?=емлем)', r'неѿ'],

    # ѻ в середине слова
    [r'(без)о(?=пас|чьст)', r'\1ѻ'],
    [r'(во|все)о(?=рꙋж)', r'\1ѻ'],
    [r'(все)о(?=бщ|каѧ)', r'\1ѻ'],
    [r'((пре)?из)о(?=бил)', r'\1ѻ'],
    [r'(не)о(?=бита|бы[кч]|пал)', r'\1ѻ'],
    [r'(пра)о(?=т)', r'\1ѻ'],
    [r'(прі)о(?=бщ)', r'\1ѻ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ппп ppp

    # пѣти
    [r'\b([Пп])е(ні|сн|ти|л(?!аг))', r'\1ѣ\2'],
    [r'(сладкоп)есн', r'\1ѣсн'],

    [r'\b(в)сепе(?=т)', r'\1сепѣ', 'i'],
    [r'''  
        (
            вос        # воспѣти
            |[зн]а       # напѣвъ
            |ѿ          # ѿпѣванїе
            |пр[иое]    # припѣвъ
            |псалмо  
            |р[ао]с     # распѣвъ
            |с          # спѣлъ
        )
        пе([влт])       # пѣти
        ''', r'\1пѣ\2', 'i'],

    [r'(восп)е(?=(ша)?\b)', r'\1ѣ'],

    [r'([Пп])лач[ьъ]\b', r'\1лачь'],
    [r'\bпьѧ(?=н)', r'пїѧ'],
    [r'\bплен', r'плѣн'],
    [r'побе(?=ж?д)', r'побѣ'],

    [r'(повел)е(?=[влнстшх])', r'\1ѣ'],

    [r'([Пп])онедельник', r'\1онедѣльник'],
    [r'([Пп]орф)и(?=р)', r'\1ѷ'],
    [r'([Пп])осе(?=[тщ])', r'\1осѣ'],
    [r'([Пп])осле(?=(жд[еи])?\b)', r'\1ослѣ'],
    [r'([Пп]охот)е(?=[внт])', r'\1ѣ'],
    [r'преждео(?=свѧщ)', r'преждеѡ', 'i'],
    [r'пререкан', r'прерѣкан'],
    [r'прилеж(?=а|н)', r'прилѣж'],
    [r'присещ', r'присѣщ'],
    [r'([Пп])рисно\b', r'\1риснѡ'],
    [r'([Пп])роки(?=м)', r'\1рокї'],

    [r'Псал(?=о?м|т)', r'Ѱал'],
    [r'псал(?=о?м|т)', r'ѱал'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ррр rrr

    [r'(\bр)абовъ\b', r'\1абѡвъ', 'i'],
    [r'([Рр]аввꙋн)и\b', r'\1ї'],
    [r'([Рр])азве\b', r'\1азвѣ'],
    [r'реза', r'рѣза'],
    [r'(раз|ѿ)реш', r'\1рѣш', 'i'],
    # разумѣ-
    [r'разꙋме(?!нъ)', r'разꙋмѣ'],

    # рѣка
    [r'\bрек(?=[аеѣи])', r'рѣк'],
    [r'\bрек(?=(ꙋ|ою?)\b)', r'рѣк'],

    # рѣчь
    [r'\bреч(?=[иь]|ам[иъ]\b)', r'рѣч'],

    [r'(\bрꙋц)е\b', r'\1ѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ссс sss

    [r'([Рр])осс', r'\1ѡсс'],

    [r'([Сс])аваоф', r'\1аваѡѳ'],
    [r'([Сс])ветле(?=[ей])', r'\1вѣтлѣ'],
    [r'([Сс])ве(?=[тщ])', r'\1вѣ'],
    [r'([Сс])вире(?=л)', r'\1вирѣ'],
    [r'([Сс])вѧтемъ', r'\1вѧтѣмъ'],
    [r'([Сс]вѧт)е(?=й\b)', r'\1ѣ'],
    [r'семо', r'сѣмо'],

    [r'([Сс])е(?=веръ)', r'\1ѣ'],
    [r'([Сс])е(вер)е\b', r'\1ѣ\2ѣ'],

    [r'(с)е(дал(е|ь)н)', r'\1ѣ\2', 'i'],

    [r'\bсен(?=[иіь])', r'сѣн'],
    [r'\bсено', r'сѣно'],
    [r'([Сс])ерафи', r'\1ерафі'],
    [r'''
        \b
        сет
        (?=([иь]|ію)\b|ѧм)
        ''', r'сѣт'],

    [r'(сквоз)е\b', r'\1ѣ', 'i'],
    [r'([Сс])лаве', r'\1лавѣ'],
    [r'([Сс])лед', r'\1лѣд'],
    [r'([Сс])леп', r'\1лѣп'],

    [r'''
        \bстен #
        (?!  # ! стенать
            а([нт][иіь]|ющ)
            |ѧ
        )
        ''', r'стѣн'],

    [r'\b([Сс])илꙋан', r'\1їлꙋан'],
    [r'\b([Сс])іон', r'\1їѡн'],
    [r'сиречь', r'сирѣчь'],

    [r'\b([Сс])корбе(?=ти|ні|л|вый)', r'\1корбѣ'],
    [r'\b([Сс])коро\b', r'\1корѡ'],

    [r'сне(?=[гж])', r'снѣ'],
    [r'([Сс]оборн)е(?=й)', r'\1ѣ'],
    [r'совест', r'совѣст'],
    [r'([Сс])овет', r'\1овѣт'],
    [r'([Сс])огре', r'\1огрѣ'],
    [r'([Сс])офрон', r'\1офрѡн'],
    [r'\b([Сс])тих', r'\1тїх'],
    [r'\b(с)тіховне\b', r'\1тїховнѣ'],
    # [r'([Сс])тихир', r'\1тїхир'],
    [r'(ср)е(?=тен)', r'\1ѣ', 'i'],
    [r'([Сс]ꙋбб)от', r'\1ѡт'],
    [r'([Сс])ыновъ', r'\1ынѡвъ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ттт ttt

    [r'([Тт])ако\b', r'\1акѡ'],
    [r'тайнемъ', r'тайнѣмъ'],
    # [r'([Тт])ебе\b', r'\1ебѣ'],  # ? в Дат. Предложн
    [r'\b([Тт])ел(?=[аоꙋ]|е(с[аеин]|х)?)', r'\1ѣл'],
    [r'([Тт])е(?=ми(жд?е)?)', r'\1ѣ'],
    [r'([Тт])е(?=мже)', r'\1ѣ'],
    [r'([Тт]епл)е', r'\1ѣ'],
    [r'([Тт]ерп)е', r'\1ѣ'],
    [r'\b([Тт])е(?=хъ)', r'\1ѣ'],
    [r'([Тт]л)е(?=н[інъ]|т[иь])', r'\1ѣ'],
    [r'([Тт]ишин)е\b', r'\1ѣ'],
    [r'\bтьме\b', r'тьмѣ'],
    [r'\bтокмо\b', r'токмѡ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ууу uuu

    # граница слова для ᲂу :
    # (\b - для `ᲂ' не работает)
    # (?<=\W)ᲂу
    # или (?<=(\W))?ᲂу - И для начала строки
    # или ^ᲂу - только для начала строки
    # (в *этом* модуле ᲂу всегда должен оказаться
    # в начале строки, т.к.
    # - обрабатывается отдельное слово
    # без предшествующих буквам символов)
    # [r'^([Оᲂ]у)б[оѡ]\b', r'\1бѡ'],
    [r'^([Оᲂ]у)зре', r'\1зрѣ'],
    [r'((ꙋ|^[Оᲂ]у)мн)о\b', r'\1ѡ'],
    [r'^([Оᲂ]у)кре', r'\1крѣ'],
    [r'^([Оᲂ]у)те(?=[хш])', r'\1тѣ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ффф fff

    [r'\bФавор', r'Ѳавѡр'],
    [r'\bфавор', r'ѳавѡр'],
    [r'фарисе', r'фарїсе'],
    [r'Фиміам', r'Ѳѷмїам'],
    [r'фиміам', r'ѳѷмїам'],
    # Ѳѡма̀
    [r'\bФом(?=\w)', r'Ѳѡм'],
    [r'\bфом(?=\w)', r'ѳѡм'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ххх hhh

    [r'([Хх]ерꙋв)и(?=м)', r'\1ї'],

    [r'([Хх])леб', r'\1лѣб'],
    [r'([Хх])рист', r'\1рїст'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ццц ccc

    [r'царск[ао]го', r'царскагѡ'],
    [r'([Цц])ве(?=[лст])', r'\1вѣ'],
    [r'цел(?=[еєиоюѧ]|ьб)', r'цѣл'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ччч

    [r'([Чч])елове(?=[кч])', r'\1еловѣ'],
    [r'([Чч])естнейш', r'\1естнѣйш'],
    [r'(чин)о(?=въ)', r'\1ѡ', 'i'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # яяя

    [r'([Ꙗꙗ])ве\b', r'\1вѣ'],
    [r'([Ꙗꙗ])ко\b', r'\1кѡ'],

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ОСТАЛЬНОЕ

    # чаще Въ чем ВЪ
    [r'\b([ВКС])Ъ\b', r'\1ъ'],

    # -ного -> -наго # кроме: ѻ҆дногѡ̀ ѻ҆́ного
    [r'((?<![дѻ])н)о(?=г[оѡ]\b)', r'\1а'],

    # -него -> -нѧго # кроме: него
    [r'(\Bн)е(?=г[оѡ]\b)', r'\1ѧ'],

    # -нного -> -ннаго
    [r'(нн)о(?=г[оѡ]\b)', r'\1а'],

    # -еннѣмъ: неизрече́ннѣмъ ᲂу҆́треннѣмъ
    [r'(енн)е(?=мъ\b)', r'\1ѣ'],

    # -нѣй - сначала все
    [r'\Bне(?=й\b)', r'нѣ'],

    # -ней - исключениѧ
    [r'''
        \b
        (
          ба|бас|бол[еѣ]з|бра|верх|(не)?вечер|господ|голен|д|днеш|єле|зад|зд[еѣ]ш|и|ѵме|іри|каз|ки|кѵри|ко|лім|милосты|нын[еѣ]ш|перст|пламен|прежд?|п[еѣ]с|сви|ран|саже|ста|степе|хана
        )
        нѣ(?=й\b)
        ''', r'\1не'],

    [r'', r'0'],
    [r'', r'1'],
    [r'', r'2'],
    [r'', r'3'],
    [r'', r'4'],
    [r'', r'5'],
    [r'', r'6'],
    [r'', r'7'],
    [r'', r'8'],
    [r'', r'9'],

    # months
    [r'ентѧбрѧ', r'ептемврїа'],
    [r'ктѧбрѧ', r'ктѡврїа'],
    [r'оѧбрѧ', r'оемврїа'],
    [r'екабрѧ', r'екемврїа'],
    [r'ꙗнварѧ', r'іаннꙋарїа'],
    [r'Ꙗнварѧ', r'Іаннꙋарїа'],
    [r'евралѧ', r'еврꙋарїа'],
    [r'([Мм])арта\b', r'\1арта'],
    [r'прелѧ', r'прілїа'],
    [r'\b([Мм])аѧ\b', r'\1аїа'],
    [r'([Іі])ю([лн])ѧ\b', r'\1ꙋ\2їа'],
    [r'([Аа])вгꙋста', r'\1ѵгꙋста'],
)
