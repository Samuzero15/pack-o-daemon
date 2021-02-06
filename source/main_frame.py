import wx
import os
import threading
import time
import sys
import subprocess
import zipfile
import datetime
import source.threads as thread
import source.funs_n_cons_2 as utils
import source.projectpart as part
import source.play_dialog as pd
import source.result_dialog as rd
import source.constants as const

import wx.lib.agw.hyperlink as hl

from configparser import ConfigParser

#--------------------------------------------------------------#

class Main(wx.Frame):
    def __init__(self):
        
        self.rootdir = os.getcwd();
        self.lastlog = []
        self.builder = None
        self.play_params = [-1,-1,"","",[], [], []]
        self.projectparts = const.read_parts(self.rootdir)
        self.response = -1
        
        if(len(self.projectparts) == 0):
            msg = "There is no project parts in this project!"
            dlg = wx.MessageDialog(None, msg, "Missing Project Parts").ShowModal()
            sys.exit()
            
        wx.Frame.__init__(self, None, title=const.EXENAME, size=(400, 250))
        self.sb = self.CreateStatusBar()
        
        self.panel = wx.Panel(self)
        self.flags = []
        self.log = []
        self.skip_parts = []
        skip_parts_labels = []
        for part_lbl in self.projectparts:
            skip_parts_labels.append("Skip " + part_lbl.name);
        
        self.btn_build = wx.Button(self.panel,label="Build");
        self.btn_play = wx.Button(self.panel,label="Play");
        self.btn_log = wx.Button(self.panel,label="No Log");
        self.btn_log.Disable()
        
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsSizer = wx.BoxSizer(wx.VERTICAL)
        checkSizer = wx.BoxSizer(wx.VERTICAL)
        ctrlsSizer = wx.BoxSizer(wx.VERTICAL)
        linksSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        linksSizer = self._build_links(linksSizer)
        checkSizer = self._build_checkboxes(checkSizer, skip_parts_labels)
        btnsSizer  = self._build_buttons(btnsSizer)
        
        self.gauge = wx.Gauge(self.panel)
        
        panelSizer.Add(checkSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 10)
        panelSizer.Add(btnsSizer, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 10)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        txt_version = wx.StaticText(self.panel, label=const.get_version())
        cacodemon = wx.StaticBitmap(self, -1, wx.Bitmap(utils.get_source_img("HEADA1.png"), wx.BITMAP_TYPE_ANY))
        topSizer.Add(cacodemon, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(txt_version, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(panelSizer, 0, wx.ALL | wx.CENTER, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(self.gauge, 0, wx.CENTER | wx.ALL | wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(linksSizer, 0, wx.ALL | wx.EXPAND | wx.CENTER, 2)
        
        self.panel.SetSizerAndFit(topSizer)
        self.sb.SetStatusText("Ready")
        self.Fit()
        self.Centre(wx.BOTH)
        """
        icon = wx.EmptyIcon()
        pyinstaller run.py --onefile -w --name CacoPacker -i "icon.ico" --add-data "icon.ico"
        icon.CopyFromBitmap(wx.Bitmap("icon.ico", wx.BITMAP_TYPE_ANY))
        """
        self.SetIcon(wx.Icon(utils.get_source_img("HEADA1.png"), wx.BITMAP_TYPE_ANY))
    
    def _build_links(self, sizer):
        panel2 = wx.Panel(self.panel, -1)
        hyper1 = hl.HyperLinkCtrl(panel2, -1, "Git Hub", pos=(25,0),
                                  URL="https://github.com/Samuzero15/pack-o-daemon")
        hyper1.SetToolTip(wx.ToolTip("The Pack-O-Daemon Git Hub repository!"))
        hyper1.EnableRollover(True)
        
        hyper2 = hl.HyperLinkCtrl(panel2, -1, "Discord", pos=(90,0),
                                  URL="#")
        hyper2.SetToolTip(wx.ToolTip("Samu's Chambers Discord.\nTalk to the author here too."))
        hyper2.EnableRollover(True)
        
        hyper3 = hl.HyperLinkCtrl(panel2, -1, "Patch Notes", pos=(150,0))
        hyper3.SetToolTip(wx.ToolTip("What's new in this version?"))
        hyper3.AutoBrowse(False)
        
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnChangelog, hyper3)
        
        sizer.Add(panel2, 0, wx.CENTER | wx.ALL, 1)
        
        return sizer
    
    def _build_checkboxes(self, sizer, skip_parts_labels):
        sizer.Add(wx.StaticText(self.panel, label="Skip Build on..."), 0, wx.CENTER, 2)
        for i in range(0, len(skip_parts_labels)):
            self.skip_parts.append(wx.CheckBox(self.panel, label=skip_parts_labels[i]))
            sizer.Add(self.skip_parts[i], 0, wx.ALL, 2)
        
        sizer.Add(wx.StaticText(self.panel, label="Build Flags"), 0, wx.CENTER, 2)
        for i in range(0, len(const.BUILD_FLAGS)):
            tooltip = wx.ToolTip(const.BUILD_FLAGS[i][1])
            self.flags.append(wx.CheckBox(self.panel, label=const.BUILD_FLAGS[i][0]))
            self.flags[i].SetToolTip(tooltip);
            sizer.Add(self.flags[i], 0, wx.ALL, 2)
        
        return sizer
    
    def _build_buttons(self, sizer):
    
        self.Bind(wx.EVT_BUTTON, self.OnBuild, self.btn_build);
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.btn_play);
        self.Bind(wx.EVT_BUTTON, self.OnLog, self.btn_log);
        thread.EVT_BUILDRESULT(self,self.OnBuildResult)
        thread.EVT_PLAYRESULT(self,self.OnPlayResult)
        
        sizer.Add(self.btn_build, 1, wx.CENTER, 2)
        sizer.Add(self.btn_log, 1, wx.CENTER, 2)
        sizer.Add(self.btn_play, 1, wx.CENTER, 2)
    
        return sizer
    
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    
    def OnChangelog(self, e):
        msg = ""
        changelog_path = utils.resource_path(os.path.join(".", "changelog.md"))
        allchanges = []
        try:
            change_ver = ""
            titled_ver = ""
            copy_it = False 
            with open(changelog_path, "rt") as file:
                for line in file.readlines():
                    if(line.startswith("## ")): 
                        if(copy_it): allchanges.append((titled_ver, change_ver))
                        titled_ver = line
                        change_ver = ""
                        copy_it = True
                    else:
                        if(copy_it):
                            change_ver += line
                        
            allchanges.append((titled_ver, change_ver))
            dlg = rd.ChangelogDialog(self, allchanges).ShowModal()
        except Exception as e:
            msg = "Failed to show the changelog!\n" + str(e)
            dlg = wx.MessageDialog(None, msg, "Oh noes!").ShowModal()
    
    def ClearLog(self):
        self.log = [];
    
    def AddToLog(self, msg, order=0):
        time = datetime.datetime.now()
        self.sb.SetStatusText(msg)
        self.log.append( "["+ time.strftime('%H:%M:%S') +']'+'-'*order + ">  " + msg);
    
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
        play_it =   self.flags[3].GetValue();
        
        completed = sucess == thread.BUILD_SUCCESS
        failure = sucess == thread.BUILD_CANCELED or sucess == thread.BUILD_ERROR
        
        nopart = []
        skip_a_part = False;
        for part in self.projectparts:
            if part.skip: 
                nopart.append(part.skip) 
                skip_a_part = True
            
        
        result = ""
        title = ""
        if(not skip_a_part and not (noacs or versioned or packed or play_it)): 
            if completed: title = "Full build completed."
            elif failure: 
                title = "Full build interrupted."
        else: 
            if(completed): 
                title = "Build completed with the following flags."
            elif failure: 
                title = "Build interrupted with the following flags."
            for part in self.projectparts:
                if part.skip:
                    title += "\n -) " + part.name + " part skipped."
            
        if(noacs):  title += "\n -) ACS compilation skipped."
        if(versioned):  title += "\n -) Tagged to the respective versions.";
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
        if(play_it): title += "\n -) The project will run once you close this window."
        
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
        if (self.flags[3].GetValue()):
            self.PlayNow(event)
        

    def OnPlayResult(self, event):
        self.btn_log.Enable()
        self.btn_log.SetLabel("Log")
        header = "The game closed \nHere it is the following output."
        self.lastlog = [header, event.data]
        dialog = rd.ResultDialog(self, header, event.data).ShowModal()
    
    def ACSErrorOutput(self, output):
        self.response = -1
        acs_err_dialog = rd.ACSErrorDialog(self,output)
        acs_err_dialog.ShowModal()
        # acs_err_dialog.Destroy()
    
    
    def PlayNow(self, e):
        dialog = pd.PlayDialog(self, self.play_params)
        dialog.OnPlay(e)
        self.play_params = dialog.GetCurrentSets()
    
    def OnPlay(self, e):
        dialog = pd.PlayDialog(self, self.play_params)
        dialog.ShowModal()
        self.play_params = dialog.GetCurrentSets()
        # saves the temporary settings while you're on the program. (Not saved to the ini)
    
    def OnLog(self, e):
        rd.ResultDialog(self, self.lastlog[0], self.lastlog[1]).ShowModal()