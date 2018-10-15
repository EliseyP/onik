# Onik
Libre Ofiice Extension for Church-Slavonic texts  

<ul>
<li>Convert text in various Orthodox [UCS] fonts to Ponomar Unicode font.</li>  
<li>Convert text from modern russian orthography to church-slavonic (some letters, acutes, titles etc).</li>  
</ul>

**After installing:**  

In OOffice both converters available from own Menu and Toolbar.

From shell **ucs converter** can be starting (f.e. for batch processing) with command (full path is required):  
``$ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"``  


Text is processed either in the selected fragment, or in the whole opened document.

## Availble Orthodox fonts for converting:  
<ul> 
<li>Hirmos Ponomar TT</li>
<li>Hirmos Ucs</li>
<li>Irmologion</li>
<li>Irmologion Ucs</li>
<li>Orthodox</li>
<li>OrthodoxDigits</li>
<li>OrthodoxDigitsLoose</li>
<li>OrthodoxLoose</li>
<li>Orthodoxtt eRoos</li>
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

This continues the idea:  
https://extensions.libreoffice.org/extensions/church-slavonic-converter