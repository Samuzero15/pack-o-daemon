
import wx
import os
import source.main_frame as frame
import source.constants as const

from configparser import ConfigParser

def GreetUser():
    msg = "Welcome to the CacoPacker!"
    msg += "\nA new file has been created"
    msg += "\nto the main directory, it's called project.ini"
    msg += "\nconfigure your settings with it, and you're ready"
    msg += "\nto build and play in matter of seconds."
    msg += "\n\nNote: If the antivirus says its a virus, it's a"
    msg += "\nfalse positive, add it to your exceptions."
    dlg = wx.MessageDialog(None, msg, "First time?").ShowModal()
    
if __name__ == "__main__":
    app = wx.App()
    first_time = const.load_stuff()
    if first_time:
        GreetUser()
    frm = frame.Main().Show(True);
    app.MainLoop()