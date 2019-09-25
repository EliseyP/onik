# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def MsgBox(prompt: str, buttons=0, title='LibreOffice') -> int:
    """ Displays a dialog box containing a message and returns a value."""
    xScript = _getScript("_MsgBox")
    res = xScript.invoke((prompt, buttons, title), (), ())
    return res[0]


def InputBox(prompt: str, title='LibreOffice', defaultValue='') -> str:
    """ Displays a prompt in a dialog box at which the user can enter text."""
    xScript = _getScript("_InputBox")
    res = xScript.invoke((prompt, title, defaultValue), (), ())
    return res[0]


def Print(message: str):
    """Outputs the specified strings or numeric expressions in a dialog box."""
    xScript = _getScript("_Print")
    xScript.invoke((message,), (), ())


import uno
from com.sun.star.script.provider import XScript


def _getScript(script: str, library='Standard', module='uiScripts') -> XScript:
    sm = uno.getComponentContext().ServiceManager
    mspf = sm.createInstanceWithContext("com.sun.star.script.provider.MasterScriptProviderFactory",
                                        uno.getComponentContext())
    scriptPro = mspf.createScriptProvider("")
    scriptName = "vnd.sun.star.script:" + library + "." + module + "." + script + "?language=Basic&location=application"
    xScript = scriptPro.getScript(scriptName)
    return xScript
