# Onik 

**1.1.43**

Libre Office расширение для текстов с церковно-славянским языком.  

**В консольном и графическом вариантах:**

- Переводит текст с различными Orthodox [UCS] шрифтами в Ponomar Unicode.
- Переводит текст из современной (или смешанной) орфографии в церковно-славянскую (некоторые буквы, ударения, титла (выставить и раскрыть) и т.д.).  
- Меняет ударение в слове (оксия, вария, камора, исо, апостроф).
- Перемещает ударение (циклически) вправо и влево.
- Преобразует числа в буквы.
- Меняет буквы  <strong>о, е</strong> <i>(о, омега, е, е-широкое, ять)</i>  в начале и конце слова.


**Для установки**  

Для Linux требуется установить компонент LibreOffice: *libreoffice-script-provider-python*  
``$ sudo apt-get install libreoffice-script-provider-python``  

**После установки**  

В OOffice конвертеры доступны через собственные меню и панель.  

Обрабатывается либо выделенный текст, либо весь открытый документ.

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

Расширение продолжает идею:
https://extensions.libreoffice.org/extensions/church-slavonic-converter

### Работа с инструментами  

#### Конвертация шрифтов

На панели доступны кнопки для автоматической конвертации, и конвертации с опциями  
_(на данный момент показыает список шрифтов, и конвертирует также в автоматическом режиме)._     
![Кнопка конвертации](/src/OOnik/Images/nYat_16.png) &nbsp;&nbsp; ![Кнопка конвертации](/src/OOnik/Images/nYat_red_16.png)  
     
  

**Остальные кнопки - обработка текста со шрифтом Ponomar:**

Перевод текста в современной орфографии в цся _(с титлами и без)_.  
![Русский -> ЦСЯ](/src/OOnik/Images/nAz_16.png) &nbsp;&nbsp;  ![Русский -> ЦСЯ (с титлами)](/src/OOnik/Images/nAz_titled_16.png)  

Раскрыть титла _(в выделенном фрагменте)_.  
![Русский -> ЦСЯ (раскрыть титла)](/src/OOnik/Images/nTitles_open_16.png)  

Числа в буквы.  
![Числа в буквы](/src/OOnik/Images/Digits_16.png)  

Изменить ударение в слове под курсором  
_(циклически меняется оксия, вария, камора; исо и апостроф.
Учитываются **е** и **о**)_.  
![Изменить ударение](/src/OOnik/Images/Acutes_16.png)  

Переместить ударение влево и вправо в слове под курсором _(циклически)_.  
Учитываются **е** и **о** для мн.ч.  
![Изменить ударение](/src/OOnik/Images/MovAc_L_16.png)&nbsp;&nbsp;
![Изменить ударение](/src/OOnik/Images/MovAc_R_16.png)  


Изменение вида букв **о** в начале слова, а также  **е** и **о** в конце.  
![Буква О в начале слова](/src/OOnik/Images/ChLetStart_16.png)&nbsp;&nbsp; ![Буква О в конце слова](/src/OOnik/Images/ChLetEndO_16.png)&nbsp;&nbsp; ![Буква Е в конце слова](/src/OOnik/Images/ChLetEndE_16.png)  


##### Для текстов со смешанными языками:
onik-функции обрабатывают весь текст, независимо от языка, как ЦСЯ. Если в тексте есть фрагменты на другом языке, можно сильно исказить текст. Отмена действий может не помочь. В подобных случаях необходимо пользоваться обработкой выделенного фрагмента.  

### Проблемы:  

#### При конвертации шрифтов:
- При работе с цветом и более сложным форматированием возможно придется либо убрать форматирование, либо обрабатывать через выделение.  

#### При обработке текста:
- Текст обрабатывается регулярными выражениями, которые могут содержать разного рода неточности и ошибки. Поэтому после обработки возможны неверные ударения и замены букв.    

#### Общие:
- нет обработки текста в таблице (todo).
