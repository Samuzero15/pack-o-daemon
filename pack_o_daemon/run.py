
import traceback
import wx
import os
import sys
import argparse

try:
    import src.main_frame as frame
    import src.constants as const
except ModuleNotFoundError: # If the module is installed and running in the main repo.
    import pack_o_daemon.src.main_frame as frame
    import pack_o_daemon.src.constants as const

def GreetUser():
    name = const.EXENAME
    msg = "Welcome to the " + name + "!"
    msg += "\nA new file has been created"
    msg += "\nto the main directory, it's called "+const.PROJECT_FILE
    msg += "\nconfigure your settings with it, and you're ready"
    msg += "\nto build and play in matter of seconds."
    msg += "\n\nNote: If the antivirus says its a virus, it's a"
    msg += "\nfalse positive, add it to your exceptions."
    msg += "\n\nThis time " + name + " will not start."
    msg += "\nRun it again once you're done with the "+const.PROJECT_FILE+" file."
    dlg = wx.MessageDialog(None, msg, "Welcome!").ShowModal()


def main():
    app = wx.App()
    try:
        if const.FIRST_TIME:
            GreetUser()
            sys.exit()
        frm = frame.Main()
        
    except Exception as e:
        dlg = wx.MessageDialog(None, "Something went wrong!\n" +"\n"+ traceback.format_exc(), "Ah shiet!").ShowModal()
        
        sys.exit()
    app.MainLoop()

if __name__ == '__main__':
    main()

def cli_main():
    parser = argparse.ArgumentParser(description='Pack-O-Daemon, but in Command Line Interface for some quick builds and executions.')
    parser.add_argument('action',  help='Action to do [build, play].')
    args = parser.parse_args()
    print(args)
