# Onik
LiberOfiice Extension for Church-Slavonic texts  

<ul>
<li>Convert text in various Orthodox [UCS] fonts to Ponomar Unicode font.</li>  
<li>Convert text from modern-russian form to ancient (some letters, acutes, titles etc).</li>  
</ul>

It can be running as from Open\Libre Office as from command line for hidden batch processing.

**After installing**  

In OOffice available from own Menu and Toolbar.

From shell **ucs converter** can be starting with command:  
``$ soffice --invisible "macro:///OOnik.main.run_ucs_convert_py($PWD/$file_name.odt)"``  
(we should pass full path to oo-macro)

## Availble Orthodox fonts:  
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

Convert text or in selected area, or in whole opened document.