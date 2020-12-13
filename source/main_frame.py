import wx
import os
import threading
import time
import sys
import subprocess
import zipfile
import source.threads as thread
import source.funs_n_cons_2 as utils
import source.projectpart as part
import source.play_dialog as pd
import source.result_dialog as rd
import source.constants as const

from configparser import ConfigParser

#--------------------------------------------------------------#

class Main(wx.Frame):
    def __init__(self):
        
        self.rootdir = os.getcwd();
        self.lastlog = []
        self.builder = None
        self.play_params = [-1,-1,"","",[], [], []]
        self.projectparts = const.read_parts(self.rootdir)
        
        if(len(self.projectparts) == 0):
            msg = "There is no project parts in this project!"
            dlg = wx.MessageDialog(None, msg, "Missing Project Parts").ShowModal()
            sys.exit()
            
        wx.Frame.__init__(self, None, title=const.EXENAME, size=(300, 250))
        self.sb = self.CreateStatusBar()
        
        
        self.panel = wx.Panel(self)
        self.flags = []
        self.skip_parts = []
        self.log = []
        flags_labels = ["Skip ACS Comp.", "Make Version", "Pack Project"]
        skip_parts_labels = []
        for part_lbl in self.projectparts:
            skip_parts_labels.append("Skip " + part_lbl.name);
        
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsSizer = wx.BoxSizer(wx.VERTICAL)
        checkSizer = wx.BoxSizer(wx.VERTICAL)
        ctrlsSizer = wx.BoxSizer(wx.VERTICAL)
        
        checkSizer.Add(wx.StaticText(self.panel, label="Skip Build Process on"), 0, wx.CENTER, 2)
        for i in range(0, len(skip_parts_labels)):
            self.skip_parts.append(wx.CheckBox(self.panel, label=skip_parts_labels[i]))
            checkSizer.Add(self.skip_parts[i], 0, wx.ALL, 2)
        
        checkSizer.Add(wx.StaticText(self.panel, label="Build Flags"), 0, wx.CENTER, 2)
        for i in range(0, len(flags_labels)):
            self.flags.append(wx.CheckBox(self.panel, label=flags_labels[i]))
            checkSizer.Add(self.flags[i], 0, wx.ALL, 2)
        
        
        self.btn_build = wx.Button(self.panel,label="Build");
        self.btn_play = wx.Button(self.panel,label="Play");
        self.btn_log = wx.Button(self.panel,label="No Log");
        self.btn_log.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.OnBuild, self.btn_build);
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.btn_play);
        self.Bind(wx.EVT_BUTTON, self.OnLog, self.btn_log);
        thread.EVT_BUILDRESULT(self,self.OnBuildResult)
        thread.EVT_PLAYRESULT(self,self.OnPlayResult)
        
        self.gauge = wx.Gauge(self.panel, range=10)
        
        btnsSizer.Add(self.btn_build, 1, wx.CENTER, 2)
        btnsSizer.Add(self.btn_log, 1, wx.CENTER, 2)
        btnsSizer.Add(self.btn_play, 1, wx.CENTER, 2)
        
        panelSizer.Add(checkSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 10)
        panelSizer.Add(btnsSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 10)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        txt_version = wx.StaticText(self.panel, label=const.get_version())
        cacodemon = wx.StaticBitmap(self, -1, wx.Bitmap(utils.get_source_img("HEADA1.png"), wx.BITMAP_TYPE_ANY))
        topSizer.Add(cacodemon, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(txt_version, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(panelSizer, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5);
        topSizer.Add(self.gauge, 0, wx.CENTER | wx.ALL | wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5);
        
        self.panel.SetSizerAndFit(topSizer)
        self.sb.SetStatusText("Ready")
        # The play.py and build.py script.
        
        self.Fit()
        self.Centre(wx.BOTH)
        """
        icon = wx.EmptyIcon()
        pyinstaller run.py --onefile -w --name CacoPacker -i "icon.ico" --add-data "icon.ico"
        icon.CopyFromBitmap(wx.Bitmap("icon.ico", wx.BITMAP_TYPE_ANY))
        """
        self.SetIcon(wx.Icon(utils.get_source_img("HEADA1.png"), wx.BITMAP_TYPE_ANY))
    
    def ClearLog(self):
        self.log = [];
    
    def AddToLog(self, msg):
        self.sb.SetStatusText(msg)
        self.log.append(msg);
    
    def OnBuild(self, e):
        if self.builder is None:
            index = 0
            for p in self.projectparts:
                p.skip = self.skip_parts[index].GetValue()
                index+=1
            self.ToggleFlags(False)
            self.btn_build.SetLabel("Abort")
            self.btn_play.Disable()
            self.ClearLog()
            self.builder = thread.BuildProject(self)
        else:
            self.builder.call_abort()
            self.btn_build.SetLabel("Aborting...")
            self.btn_build.Disable()
    
    def ToggleFlags(self, state):
        for i in self.flags:
            if state: 
                i.Enable()
            else:     
                i.Disable()
        for i in self.skip_parts:
            if state: 
                i.Enable()
            else:     
                i.Disable()
    
    def ReportResults(self, sucess):
        
        noacs =     self.flags[0].GetValue();
        versioned = self.flags[1].GetValue();
        packed =    self.flags[2].GetValue();
        
        nopart = []
        skip_a_part = False;
        for part in self.projectparts:
            if part.skip: 
                nopart.append(part.skip) 
                skip_a_part = True
            
        
        result = ""
        title = ""
        if(not skip_a_part): 
            if(sucess == thread.BUILD_SUCCESS): title = "Full build completed."
            elif sucess == thread.BUILD_CANCELED or sucess == thread.BUILD_ERROR: 
                title = "Full build interrupted."
        else:
            if(sucess == thread.BUILD_SUCCESS): title = "Build completed with the following flags."
            elif sucess == thread.BUILD_CANCELED or sucess == thread.BUILD_ERROR: 
                title = "Build interrupted with the following flags."
            for part in self.projectparts:
                if part.skip:
                    title += "\n -) " + part.name + " part skipped."
            if(noacs):  title += "\n -) ACS compilation skipped."
        
        if(versioned):  title += "\n -) Setted version: " + const.ini_prop('zip_tag', 'v0');
        if(packed):
            zipfilename = ""
            zip_name = const.ini_prop('zip_name', 'project')
            zip_tag =  const.ini_prop('zip_tag', 'v0')
            if(versioned): 
                zipfilename = zip_name + "_" + zip_tag + '.zip';
            else:          
                zipfilename = zip_name + "_DEV.zip";
            title += "\n -) Packed-up in file: " + zipfilename
        if(sucess == thread.BUILD_SKIPPED): title = "Build Interrupted. \nAll the project parts are skipped, unmark the skip flags and try again."
        
        title += "\nRead the log for more details."
        
        result += "\n------------------------------------------------------------"
        result += "\n\t==== Log Start ===="
        result += "\n------------------------------------------------------------\n"
        
        if len(self.log) == 0:
            result += "No log outputted.\n"
        else:
            for msg in self.log:
                result += msg + "\n";
                
        result += "------------------------------------------------------------"
        result += "\n\t==== Log End ===="
        result += "\n------------------------------------------------------------"
        
        return (title, result)

    def OnBuildResult(self, event):
        result = ""
        title = ""
        
        sucess = event.data
        
        if sucess == thread.BUILD_ERROR: 
            self.AddToLog("Project build stopped, caused by an error.")
            self.gauge.SetValue(0)
            self.gauge.SetRange(0)
        elif sucess == thread.BUILD_CANCELED:
            self.AddToLog("Project build canceled, by user will.")
            self.gauge.SetValue(0)
            self.gauge.SetRange(0)
            
        elif sucess == thread.BUILD_SUCCESS: 
            self.AddToLog("Project build finished.")
            self.gauge.SetValue(1)
            self.gauge.SetRange(1)
        
        
        result = self.ReportResults(sucess)
        
        self.btn_log.Enable()
        self.btn_log.SetLabel("Log")
        self.btn_build.SetLabel("Build")
        self.btn_build.Enable()
        self.btn_play.Enable()
        self.ToggleFlags(True)
        
        
        # And to top it off, do a dialog!
        dialog = rd.ResultDialog(self, result[0], result[1]).ShowModal()
        self.lastlog = [result[0], result[1]]
        self.builder = None

    def OnPlayResult(self, event):
        self.btn_log.Enable()
        self.btn_log.SetLabel("Log")
        header = "The game closed \nHere it is the following output."
        self.lastlog = [header, event.data]
        dialog = rd.ResultDialog(self, header, event.data).ShowModal()
        
    
    def OnPlay(self, e):
        versioned = self.flags[1].GetValue()
        # Read the INI file, and get the required pwads.
        pwads_before_ini = const.ini_prop('play_pwads_before')
        pwads_before = []
        for path in pwads_before_ini:
            filepath = utils.relativePath(path)
            if os.path.isfile(filepath):
                pwads_before.append(filepath)
        
        pwads_after_ini = const.ini_prop('play_pwads_after')
        pwads_after = []
        for path in pwads_after_ini:
            filepath = utils.relativePath(path)
            if os.path.isfile(filepath):
                pwads_after.append(filepath)
            
        if len(self.play_params[4]) == 0:
            # If this is the first time on the play button. Load the INI PWADS and the project pwads
            for pwad in pwads_before:
                self.play_params[4].append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
            for p in self.projectparts:
                self.play_params[4].append(p.GetExpectedPWADS(versioned))
            for pwad in pwads_after:
                self.play_params[4].append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
        else:
            # Else, update the project pwads. Depending on the versioned mark.
            index = 0
            for pwadlist in self.play_params[4]:
                for p in self.projectparts:
                    if pwadlist[0] == p.GetExpectedPWADS(not versioned)[0]:
                        self.play_params[4][index] = p.GetExpectedPWADS(versioned)
                index += 1
                
        pd.PlayDialog(self, self.play_params).ShowModal()
    
    def OnLog(self, e):
        rd.ResultDialog(self, self.lastlog[0], self.lastlog[1]).ShowModal()