# Onik 

**1.1.63**

![Панель](/src/OOnik/Images/Onik_toolbar.png)

Libre Office расширение для текстов с церковно-славянским языком.  

**В консольном и графическом вариантах:**

- Переводит текст с различными Orthodox [UCS] шрифтами в Ponomar Unicode.
- Переводит текст из современной (или смешанной) орфографии в церковно-славянскую (некоторые буквы, ударения, титла (выставить и раскрыть) и т.д.).  
- Меняет ударение в слове _(оксия, вария, камора, исо, апостроф)_.
- Перемещает ударение (циклически) вправо и влево.
- Преобразует числа в буквы и обратно _(в выделенном)_.
- Меняет буквы  <strong>о, е</strong> <i>(о, омега, е, е-широкое, ять)</i>  в начале и конце слова.
- Меняет _(циклично)_ ударные буквы <strong>и, ї, ѵ</strong> в словах  ми́ръ, мі́ръ, мѵ́ро.
- Меняет _(циклично)_ буквы <strong>и, ї, ы</strong> для мн. и ед. числа: <strong>-щимъ -щымъ</strong> 
- Исправляет варию в конце слова на оксию _(перед частицами или краткими местоимениями)._ 
- Позволяет быстро выставить ударение в слово без оного (для скорости набора).
- Позволяет быстро выставить _варию_ в конец слова.
- Позволяет исправить некоторые ошибки набора.
- Позволяет быстро назначить и удалить _горячие клавиши_.

**Для установки**  

Для Linux требуется установить компонент LibreOffice: *libreoffice-script-provider-python*  
``$ sudo apt-get install libreoffice-script-provider-python``  

**После установки**  

В OOffice конвертеры доступны через собственные меню и панель.  

Обрабатывается либо выделенный текст (доступно мультивыделение), либо весь открытый документ.

Из командной строки (например, для пакетной обработки) **ucs конвертер** может быть запущен подобным образом (необходимо указать полный путь к файлу):  
``$ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"``  



Для тестов или скриптов м.б. использваны py-скрипты c функциями обработки Ponomar-текста:   
``$ onik_run.py 'Фома'``  
``Ѳѡма̀``     
и текстовый фильтр:   
``$ echo 'Фома' |  onik_test.py``  
``Ѳѡма̀``  



### Orthodox шрифты, доступные для конвертации :  
#### UCS

<ul>
<li>Akathistos Ucs    
<li>Hirmos Ucs
<li>Irmologion Ucs
<li>Pochaevsk Ucs
<li>Ostrog Ucs
<li>StaroUspenskaya Ucs
<li>Triodion Ucs
<li><i>и все недекоративные UCS-шрифты</i>   
</ul>  

#### Другие 
<ul>
<li>Hirmos Ponomar TT
<li>Irmologion
<li>Orthodox
<li>OrthodoxLoose
<li>OrthodoxDigits
<li>OrthodoxDigitsLoose
<li>Orthodox.tt Ucs8
<li>Orthodox.tt eRoos
<li>Ustav
<li>Valaam
</ul>


Конвертеры написаны для обработки большого количества документов, в которых церковно-славянские тексты набраны самыми различными (см. выше) ЦСЯ-шрифтами, и оформлены (орфографически) самыми разными способами.  

С Unicode-текстом удобно работать, назначив различным функциям "горячие клавиши".  

Расширение продолжает идею:
https://extensions.libreoffice.org/extensions/church-slavonic-converter

### Работа с инструментами  

#### Конвертация шрифтов

На панели доступны кнопки конвертации - автоматической, и с опциями _(на данный момент показыает список шрифтов, и конвертирует также в автоматическом режиме)._     
![Кнопка конвертации](/src/OOnik/Images/nYat_16.png) &nbsp;&nbsp; ![Кнопка конвертации](/src/OOnik/Images/nYat_red_16.png)  
     
  

**Остальные кнопки - обработка текста со шрифтом Ponomar:**

Перевод текста в современной орфографии в цся _(с титлами и без)_.  
![Русский -> ЦСЯ](/src/OOnik/Images/nAz_16.png) &nbsp;&nbsp;  ![Русский -> ЦСЯ (с титлами)](/src/OOnik/Images/nAz_titled_16.png)  

Раскрыть титла _(в выделенном фрагменте)_.  
![Русский -> ЦСЯ (раскрыть титла)](/src/OOnik/Images/nTitles_open_16.png)  

Числа в буквы и обратно _(в выделенном фрагменте)_.  
![Числа в буквы](/src/OOnik/Images/Digits_16.png)&nbsp;&nbsp; ![Числа в буквы](/src/OOnik/Images/LetToDig_16.png)    

Изменить ударение в слове под курсором  
_(циклически меняется оксия, вария, камора; исо и апостроф.
Учитываются **е** и **о**)_.  
![Изменить ударение](/src/OOnik/Images/Acutes_16.png)  

Переместить ударение влево и вправо в слове под курсором _(циклически)_.  
Учитываются **е** и **о** для мн.ч.  
![Изменить ударение](/src/OOnik/Images/MovAc_L_16.png)&nbsp;&nbsp;
![Изменить ударение](/src/OOnik/Images/MovAc_R_16.png)  

Установить варию для последней буквы (для скорости редактирования).   
![Вария в конце слова](/src/OOnik/Images/Var2End_16.png)

Изменение вида букв **о** в начале слова, а также  **е** и **о** в конце.  
![Буква О в начале слова](/src/OOnik/Images/ChLetStart_16.png)&nbsp;&nbsp; ![Буква О в конце слова](/src/OOnik/Images/ChLetEndO_16.png)&nbsp;&nbsp; ![Буква Е в конце слова](/src/OOnik/Images/ChLetEndE_16.png)  

Замена _(циклическая)_ ударных букв <strong>и, ї, ѵ</strong> в словах  ми́ръ, мі́ръ, мѵ́ро.  
![ми́ръ|мі́ръ|мѵ́ро](/src/OOnik/Images/ChLetI_16.png)

Замена _(циклическая)_ букв <strong>и, ї, ы</strong> для мн. и ед. числа: <strong>-щимъ -щымъ.</strong>  
![-щымъ|-щимъ](/src/OOnik/Images/ChLetPlurI_16.png)

В меню доступны пункты утановки и удаления горячих клавиш.  
![Меню](/src/OOnik/Images/Onik_menu.png)  


##### Горячие  клавиши:  
"CTRL + T": "Русский -> ЦСЯ"  
"CTRL + ALT + T",   "Русский -> ЦСЯ с титлами"  
"CTRL + ALT + SHIFT + T", "Русский -> ЦСЯ раскрыть титла"  
"CTRL + ALT + .", "Изменить ударение"  
"CTRL + ALT + [", "Переместить ударение влево"  
"CTRL + ALT + ]", "Переместить ударение вправо"  
"CTRL + .", "Ударение для слова без оного"  
"CTRL + ALT + Q", "Вария для последней буквы"  
  
"CTRL + ALT + D", "Числа в буквы"    
  
"CTRL + ALT + SHIFT + O", "Изменить буквы О в начале слова"  
"CTRL + ALT + O", "Изменить буквы О в конце слова"  
"CTRL + ALT + P", "Изменить буквы и, і, ы для мн. и ед. числа"  
"CTRL + ALT + I", "Изменить ударные буквы и, і, ѵ в слове"  
"CTRL + ALT + E", "Изменить буквы Е в конце слова"  


##### Для текстов со смешанными языками:
onik-функции обрабатывают весь текст, независимо от языка (шрифта), как ЦСЯ. Если в тексте есть фрагменты на другом языке, можно сильно исказить текст. Отмена действий может не помочь. В подобных случаях необходимо пользоваться обработкой выделенного фрагмента.  

### Проблемы:  

#### При конвертации шрифтов:
- При работе с цветом и более сложным форматированием возможно придется либо убрать форматирование, либо обрабатывать через выделение.  

#### При обработке текста:
- Текст обрабатывается регулярными выражениями, которые могут содержать разного рода неточности и ошибки. Поэтому после обработки возможны неверные ударения и замены букв.    

#### Общие:
- нет обработки текста в таблице (todo).
