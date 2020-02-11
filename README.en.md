# Onik

**1.1.58**

Libre Office Extension for Church-Slavonic texts  

<ul>
<li>Convert text in various Orthodox [UCS] fonts to Ponomar Unicode font.</li>  
<li>Convert text from modern russian orthography to church-slavonic (some letters, acutes, titles (set and open) etc).</li>  
<li>Changes acute in word (oxia, varia, kamora, iso, apostrof).</li>  
<li>Convert numerals to letters</li>
<li>Changes first and last letters <strong>о, е</strong> <i>(o, omega, e, e-wide, yat)</i> of the word.</li>
</ul>

**Requirements**  

For Linux you should install LibreOffice component: *libreoffice-script-provider-python*  
``$ sudo apt-get install libreoffice-script-provider-python``  

**After installing:**  

In LOffice both converters available from own Menu and Toolbar.

From shell **ucs converter** can be starting (f.e. for batch processing) with command (full path is required):  
``$ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"``  


Text is processed either in the selected fragment, or in the whole opened document.

There are some py-scripts for testing or scripting:  
``$ onik_run.py 'Фома'``  
``Ѳѡма̀``   
and text filter:    
``$ echo 'Фома' |  onik_test.py``  
``Ѳѡма̀``  

### Availble Orthodox fonts for converting:  
<ul>
<li>Akathistos Ucs    
<li>Hirmos Ucs
<li>Irmologion Ucs
<li>Pochaevsk Ucs
<li>Ostrog Ucs
<li>StaroUspenskaya Ucs
<li>Triodion Ucs
<li><i>and all non-decorative UCS fonts  
</ul>  

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


This continues the idea:  
https://extensions.libreoffice.org/extensions/church-slavonic-converter
