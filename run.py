
import wx
import os
import sys
import src.main_frame as frame
import src.constants as const

from configparser import ConfigParser

def GreetUser():
    name = const.EXENAME
    msg = "Welcome to the " + name + "!"
    msg += "\nA new file has been created"
    msg += "\nto the main directory, it's called project.ini"
    msg += "\nconfigure your settings with it, and you're ready"
    msg += "\nto build and play in matter of seconds."
    msg += "\n\nNote: If the antivirus says its a virus, it's a"
    msg += "\nfalse positive, add it to your exceptions."
    msg += "\n\nThis time " + name + " will not start."
    msg += "\nRun it again once you're done with the project.ini file."
    dlg = wx.MessageDialog(None, msg, "Welcome!").ShowModal()
    
if __name__ == "__main__":
    app = wx.App()
    try:
        first_time = const.load_stuff()
        if first_time:
            GreetUser()
            sys.exit()
        frm = frame.Main().Show(True);
        
    except Exception as e:
        dlg = wx.MessageDialog(None, "Something went wrong! Error Message:\n" + str(e), "Ah shiet!").ShowModal()
        sys.exit()
    app.MainLoop()