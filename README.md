# Onik 

**1.1.27**

Libre Office расширение для текстов с церковно-славянским языком.  

**В консольном и графическом вариантах:**
<ul>
<li>Переводит текст с различными Orthodox [UCS] шрифтами в Ponomar Unicode.</li>  
</ul>

**В графическом варианте:**
<ul>
<li>Переводит текст из современной (или смешанной) орфографии в церковно-славянскую (некоторые буквы, ударения, титла (выставить и раскрыть) и т.д.).</li>
<li>Меняет ударение в слове (оксия, вария, камора, исо, апостроф).</li>  
<li>Преобразует числа в буквы</li>
<li>Меняет буквы  <strong>о, е</strong> <i>(о, омега, е, е-широкое, ять)</i>  в начале и конце слова. </li>
</ul>

**Для установки**  

Для Linux требуется установить компонент LibreOffice: *libreoffice-script-provider-python*  
``$ sudo apt-get install libreoffice-script-provider-python``  

**После установки**  

В OOffice конвертеры доступны через собственные меню и панель.

Из командной строки (например, для пакетной обработки) **ucs конвертер** может быть запущен подобным образом (необходимо указать полный путь к файлу):  
``$ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"``  


Обрабатывается либо выделенный текст, либо весь открытый документ.

### Orthodox шрифты, доступные для конвертации :  
<ul> 
<li>Hirmos Ponomar TT</li>
<li>Hirmos Ucs</li>
<li>Irmologion</li>
<li>Irmologion Ucs</li>
<li>Orthodox</li>
<li>OrthodoxDigits</li>
<li>OrthodoxDigitsLoose</li>
<li>OrthodoxLoose</li>
<li>Orthodox.tt eRoos</li>
<li>Orthodox.tt ieERoos</li>
<li>Orthodox.tt ieUcs8</li>
<li>Orthodox.tt ieUcs8 Caps</li>
<li>Orthodox.tt Ucs8</li>
<li>Orthodox.tt Ucs8 Caps</li>
<li>Orthodox.tt Ucs8 Caps tight</li>
<li>Orthodox.tt Ucs8 tight</li>
<li>Triodion ieUcs</li>
<li>Triodion Ucs</li>
<li>Ustav</li>
<li>Valaam</li>
</ul>  


Конвертеры написаны для обработки большого количества документов, в которых церковно-славянские тексты набраны самыми различными (см. выше) ЦСЯ-шрифтами, и оформлены (орфографически) самыми разными способами.  

Расширение продолжает идею:
https://extensions.libreoffice.org/extensions/church-slavonic-converter
