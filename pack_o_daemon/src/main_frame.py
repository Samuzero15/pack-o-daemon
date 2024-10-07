import re
import traceback

import wx
import os
import sys
import datetime
import time
import platform
import json

try:
    import src.threads as thread
    import src.funs_n_cons_2 as utils
    import src.projectpart as part
    import src.play_dialog as pd
    import src.result_dialog as rd
    import src.reports_dialog as rep
    import src.config_dialog as cd
    import src.constants as const
    import src.execute_dialog as exe
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.threads as thread
    import pack_o_daemon.src.funs_n_cons_2 as utils
    import pack_o_daemon.src.projectpart as part
    import pack_o_daemon.src.play_dialog as pd
    import pack_o_daemon.src.result_dialog as rd
    import pack_o_daemon.src.reports_dialog as rep
    import pack_o_daemon.src.config_dialog as cd
    import pack_o_daemon.src.constants as const
    import pack_o_daemon.src.execute_dialog as exe

import wx.lib.agw.hyperlink as hl
# from wx.adv import Animation, AnimationCtrl, NotificationMessage, TaskBarIcon, wxEVT_TASKBAR_BALLOON_CLICK
import wx.adv as adv

#--------------------------------------------------------------#

class MyTaskBarIcon(adv.TaskBarIcon):
    def __init__(self, frame):
        adv.TaskBarIcon.__init__(self)

        self.frame = frame

        self.SetIcon(frame.icon, 'Pack-o-Daemon')

        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=1)
        self.Bind(wx.EVT_MENU, self.OnTaskBarDeactivate, id=2)
        self.Bind(wx.EVT_MENU, self.frame.OnBuild, id=3)
        self.Bind(wx.EVT_MENU, self.frame.OnLog, id=4)
        self.Bind(wx.EVT_MENU, self.frame.OnPlay, id=5)
        self.Bind(wx.EVT_MENU, self.frame.OnConfig, id=6)
        self.Bind(wx.EVT_MENU, self.frame.OnExecute, id=8)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=9)
        
        for i in range(0, len(const.BUILD_FLAGS)):
            self.Bind(wx.EVT_MENU, self.OnChangeFlag(i), id=(10+i))

    def CreatePopupMenu(self):
        menu = wx.Menu()
        
        menu.Append(3, 'Build')
        menu.Append(4, 'Log')
        menu.Append(5, 'Play')
        menu.Append(6, 'Settings')
        menu.Append(8, 'Execute')
        menu.AppendSeparator()
        menu.Append(1, 'Show')
        menu.Append(2, 'Hide')
        menu.Append(9, 'Close')

        if not self.frame.builder is None:
            menu.SetLabel(3, 'Abort')
            menu.Enable(5, False)
            menu.Enable(6, False)
            menu.Enable(7, False)
            menu.Enable(8, False)
            menu.Enable(10, False)

        if not self.frame.btn_log.IsEnabled():
            menu.Enable(4, False)
            menu.SetLabel(4, "No log")

        return menu

    def OnChangeFlag(self, which):
        def OnClick(event):
            self.frame.flags[which].SetValue(not self.frame.flags[which].GetValue())
        return OnClick

    def OnTaskBarClose(self, event):
        self.frame.Close()
        self.Destroy()

    def OnTaskBarActivate(self, event):
        if not self.frame.IsShown():
            self.frame.Show()

    def OnTaskBarDeactivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()

class Main(wx.Frame):
    def __init__(self):
        
        self.rootdir = os.getcwd()
        
        self.lastlog = []
        self.alllogs = {}
        self.builder = None
        self.play_params = [-1,-1,"","",[], [], []]
        self.projectparts = const.read_parts(self.rootdir)
        self.response = -1
        self.snapshot_tag = const.get_snapshot_build_tag()
        self.snapshot_tag_last = self.snapshot_tag
        self.acs_err_dialog = None
        self.notif = adv.NotificationMessage()
        
        self.CACOGIF_SPIN = adv.Animation(utils.get_source_img("caco_spin.gif"))
        self.CACOGIF_FAIL = adv.Animation(utils.get_source_img("caco_fail.gif"))
        self.CACOGIF_OKAY = adv.Animation(utils.get_source_img("caco_success.gif"))
        
        self.icon = wx.Icon(utils.get_source_img("HEADA1.png"), wx.BITMAP_TYPE_ANY)
        self.taskbar = MyTaskBarIcon(self)

        # self.SetIcon(wx.Icon('./bitmaps/web.png', wx.BITMAP_TYPE_PNG), 'Task bar icon')
        
        
        if(len(self.projectparts) == 0):
            msg = "There are no project parts in this project!"
            wx.MessageDialog(None, msg, "Missing Project Parts").ShowModal()
            sys.exit()
            
        wx.Frame.__init__(self, None, title=const.EXENAME, size=(275, 400))
        self.sb = wx.StatusBar()
        self.sb.Create(self, id=wx.ID_ANY, style=wx.STB_DEFAULT_STYLE, name="Test Me")
        
        self.panel = wx.Panel(self)
        self.flags = []
        self.log = []
        self.skip_parts = []
        self.build_flags = []
        
        self.btn_build = wx.Button(self.panel,label="Build")
        self.btn_play = wx.Button(self.panel,label="Play")
        self.btn_log = wx.Button(self.panel,label="No Log")
        self.notebook = wx.Notebook(self.panel,size=(100, 300), style=wx.NB_BOTTOM)

        self.btn_log.Disable()
        
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        btnsSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        btnsSizer2 = wx.BoxSizer(wx.VERTICAL)
        linksSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.cb_tab = self._MakeTab(self.notebook, "Flags")
        self._AddToTab(self.cb_tab, self._build_checkboxes(self.cb_tab))

        tab = self._MakeTab(self.notebook, "Log files")
        self._AddToTab(tab, self._build_logfiles_list(tab))
        tab = self._MakeTab(self.notebook, "Reports")
        self._AddToTab(tab,  rep.ReportsDialog(tab, self))
        tab = self._MakeTab(self.notebook, "More")
        self._AddToTab(tab, self._build_more_buttons(tab, btnsSizer2), wx.CENTER, 3)
        self._AddToTab(tab, wx.StaticLine(tab), margin=2)
        self._AddToTab(tab, self._build_links(tab, linksSizer))

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.gauge = wx.Gauge(self.panel)
        
        btnsSizer1  = self._build_buttons(btnsSizer1)

        panelSizer.Add(self.notebook, 3, wx.CENTER | wx.ALL | wx.EXPAND, 5)
        panelSizer.Add(btnsSizer1, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 5)
        panelSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        panelSizer.Add(self.gauge, 0, wx.CENTER | wx.ALL | wx.EXPAND, 5)
        panelSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        #panelSizer.Add(btnsSizer2, 0, wx.CENTER | wx.LEFT | wx.RIGHT , 5)
        
        topSizer = wx.BoxSizer(wx.VERTICAL)
        txt_version = wx.StaticText(self.panel, label=const.get_version())
        self.cacodemon = adv.AnimationCtrl(self.panel, -1, self.CACOGIF_SPIN)

        topSizer.Add(self.cacodemon, 0, wx.ALL | wx.CENTER, 2)
        topSizer.Add(txt_version, 0, wx.ALL | wx.CENTER, 2)
        topSizer.Add(panelSizer, 0, wx.ALL | wx.CENTER | wx.EXPAND, 5)
        # topSizer.Add(linksSizer, 0, wx.ALL | wx.EXPAND | wx.CENTER, 2)
        
        self.panel.SetSizerAndFit(topSizer)
        self.sb.SetStatusText("Ready")
        self.Centre(wx.BOTH)
        self.SetStatusBar(self.sb)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT,  ord('b'), self.btn_build.GetId()),
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT,  ord('l'), self.btn_log.GetId()),
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT,  ord('p'), self.btn_play.GetId()),
        ])
        self.SetAcceleratorTable(accel_tbl)
        """
        icon = wx.EmptyIcon()
        pyinstaller run.py --onefile -w --name CacoPacker -i "icon.ico" --add-data "icon.ico"
        icon.CopyFromBitmap(wx.Bitmap("icon.ico", wx.BITMAP_TYPE_ANY))
        """
        self.SetIcon(self.icon)
        self.Show(True)
    
    def _MakeTab(self, notebook, title):
        tab = wx.ScrolledWindow(notebook)
        tab.SetScrollbars(1, 5, 300, 400)
        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        tab.SetSizer(tab_sizer)
        notebook.AddPage(tab, title)
        return tab
    
    def _AddToTab(self, tab, what, proportion=0,  flags=None, margin = 10):
        if flags == None: flags = wx.LEFT | wx.DOWN | wx.RIGHT | wx.CENTER | wx.EXPAND
        tab.GetSizer().Add(what, proportion, flags, margin)
    
    def _build_logfiles_list(self, parent):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.logfiles = wx.ListCtrl(parent, style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LC_NO_HEADER, size=(180, 100))
        self.logfiles.InsertColumn(0, "")
        self.logfiles.SetColumnWidth(0, 180)
        sizer.Add(self.logfiles, 0, wx.CENTER | wx.LEFT | wx.RIGHT | wx.EXPAND)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)
        btn_delete = wx.Button(parent, label="Delete")
        btn_clear = wx.Button(parent, label="Clear")
        sizer_btn.Add(btn_delete, 1, wx.ALL | wx.EXPAND)
        sizer_btn.Add(btn_clear, 1, wx.ALL | wx.EXPAND)
        sizer.Add(sizer_btn, 0, wx.CENTER | wx.LEFT | wx.RIGHT)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._OnLogFileView, self.logfiles)
        self.Bind(wx.EVT_BUTTON, self._OnDeleteLogFile, btn_delete)
        self.Bind(wx.EVT_BUTTON, self._OnClearLogFiles, btn_clear)
        return sizer
    
    def _OnClearLogFiles(self, e):
        self.logfiles.DeleteAllItems()

    def _OnDeleteLogFile(self, e):
        selected = self.logfiles.GetFirstSelected()
        if selected != -1:
            filename = self.logfiles.GetItem(selected, 0).GetText()
            self.logfiles.DeleteItem(selected)
            del self.alllogs[filename]
    
    def _OnLogFileView(self, e):
        selected = self.logfiles.GetFirstSelected()
        if selected != -1:
            filename = self.logfiles.GetItem(selected, 0).GetText()
            rd.ResultDialog(self, self.alllogs[filename]["header"], self.alllogs[filename]["content"], filename).ShowModal()
    
    def _build_links(self, parent, sizer):
        hyper1 = hl.HyperLinkCtrl(parent, -1, "GitHub",
                                  URL="https://github.com/Samuzero15/pack-o-daemon")
        hyper1.SetToolTip(wx.ToolTip("The Pack-O-Daemon Git Hub repository!"))
        hyper1.EnableRollover(True)
        
        hyper2 = hl.HyperLinkCtrl(parent, -1, "Discord",
                                  URL="https://discord.gg/s3eWNxe")
        hyper2.SetToolTip(wx.ToolTip("Samu's Chambers Discord.\nTalk to the author here too."))
        hyper2.EnableRollover(True)
        
        hyper3 = hl.HyperLinkCtrl(parent, -1, "Patch Notes")
        hyper3.SetToolTip(wx.ToolTip("What's new in this version?"))
        hyper3.AutoBrowse(False)
        
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnChangelog, hyper3)
        sizer.Add(hyper1, 0, wx.CENTER | wx.ALL | wx.EXPAND, 3)
        sizer.Add(hyper2, 0, wx.CENTER | wx.ALL | wx.EXPAND, 3)
        sizer.Add(hyper3, 0, wx.CENTER | wx.ALL | wx.EXPAND, 3)
        return sizer

    def _build_checkboxes(self, parent):
        sizer =  wx.BoxSizer(wx.VERTICAL)
        self.skip_parts = []
        self.build_flags = []
        skip_parts_labels = ["Skip " + part.name for part in self.projectparts]
        sizer.Add(wx.StaticText(parent, label="Skip Build on..."), 0, wx.CENTER, 2)
        for i in range(0, len(skip_parts_labels)):
            checkbox = wx.CheckBox(parent, label=skip_parts_labels[i])
            self.skip_parts.append(checkbox)
            sizer.Add(self.skip_parts[i], 0, wx.ALL, 2)
        i = 0
        for p in self.projectparts:
            self.skip_parts[i].SetValue(p.skip)
            i += 1

        sizer.Add(wx.StaticText(parent, label="Build Flags..."), 0, wx.CENTER, 2)
        build_flags = const.ini_prop(const.JSON_BUILDSETS_BUILDFLAGS)
        if(build_flags is None): build_flags = [False for i in range(len(const.BUILD_FLAGS))]
        for i in range(0, len(const.BUILD_FLAGS)):
            self.flags.append(wx.CheckBox(parent, label=const.BUILD_FLAGS[i][0]))
            self.flags[i].SetToolTip(wx.ToolTip(const.BUILD_FLAGS[i][1]))
            # self.flags[i].Hide()
            if i in range(0, len(build_flags)):
                self.flags[i].SetValue(build_flags[i])
            sizer.Add(self.flags[i], 0, wx.ALL, 2)
        save_btn = wx.Button(parent, label="Save Flags")
        self.Bind(wx.EVT_BUTTON, self.OnClickSaveFlagsButton, save_btn)
        sizer.Add(save_btn, 0, wx.CENTER, 2)

        return sizer

    def OnClickSaveFlagsButton(self, event):
        # Load the json file
        f = open(const.PROJECT_FILE, "r")
        project_json = json.load(f)
        f.close()

        # Save the skip flags
        i = 0
        for p in self.projectparts:
            project_json[const.JSON_PROJPARTS][p.name][const.JSON_PROJPARTS_SKIPPED] = self.skip_parts[i].GetValue()
            i += 1

        # Save the build flags
        checks = []
        for i in range(0,len(self.flags)):
            checks.append(self.flags[i].GetValue())
        project_json[const.JSON_BUILDSETS][const.JSON_BUILDSETS_BUILDFLAGS] = checks

        # Commit
        f = open(const.PROJECT_FILE, "w")
        json.dump(project_json, f, indent=4)
        f.close()

        msg = "Flags saved in the '" +const.PROJECT_FILE+"' file."
        dlg = wx.MessageDialog(self, msg, "Settings saved on file").ShowModal()

    def _build_buttons(self, sizer):
    
        self.Bind(wx.EVT_BUTTON, self.OnBuild, self.btn_build)
        self.Bind(wx.EVT_BUTTON, self.OnPlay, self.btn_play)
        self.Bind(wx.EVT_BUTTON, self.OnLog, self.btn_log)
        thread.EVT_BUILDRESULT(self,self.OnBuildResult)
        thread.EVT_PLAYRESULT(self,self.OnPlayResult)
        thread.EVT_STATUSMESSAGE(self,self.AddToLog)
        
        sizer.Add(self.btn_build, 1, wx.CENTER, 2)
        sizer.Add(self.btn_log, 1, wx.CENTER, 2)
        sizer.Add(self.btn_play, 1, wx.CENTER, 2)
    
        return sizer

    def _build_more_buttons(self, tab, sizer):

        self.btn_config = wx.Button(tab,label="Settings")
        self.btn_execute = wx.Button(tab, label="Execute")

        self.Bind(wx.EVT_BUTTON, self.OnConfig, self.btn_config)
        self.Bind(wx.EVT_BUTTON, self.OnExecute, self.btn_execute)
        
        sizer.Add(self.btn_config, 1, wx.CENTER | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(self.btn_execute, 1, wx.CENTER | wx.TOP | wx.BOTTOM, 2)
    
        return sizer
    
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    ### ------ ### ------ ### ------ ### ------ ### ------ ### 
    
    def OnChangelog(self, e):
        msg = ""
        print(os.path.split(os.path.dirname(__file__))[0])
        changelog_path = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'changelog.md')#utils.resource_path(os.path.join(".", "changelog.md"))
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
    
    def AddToLog(self, event, order=0):
        t = datetime.datetime.now()
        order=event.order
        msg = event.data
        #print("Order: ", (str)(order),", Msg: ", msg)
        try:
         self.sb.SetStatusText(msg)
         #self.sb.SetStatusText(msg)
        except Exception as e:
         print(traceback.format_exc())
        self.log.append( "["+ t.strftime('%H:%M:%S') +']'+'-'*order + ">  " + msg);
        #print("I'm done adding the message")
       
        
    def OnConfig(self, e):
        config = cd.ConfigDialog(self)
        config.ShowModal()
        # Restart the program.
    
    def OnBuild(self, e):
        self.cacodemon.SetAnimation(self.CACOGIF_SPIN)
        self.cacodemon.Play()
        self.response = -1
        # self.builder = None
        if self.builder is None:
            if self.flags[const.BFLAG_MAKEVERSION].GetValue() and self.flags[const.BFLAG_SNAPSHOTVER].GetValue():
                self.snapshot_tag_last = self.snapshot_tag
                self.snapshot_tag = const.get_snapshot_build_tag()
            index = 0
            for p in self.projectparts:
                p.skip = self.skip_parts[index].GetValue()
                index+=1
            self.ToggleFlags(False)
            self.btn_build.SetLabel("Abort")
            self.btn_play.Disable()
            self.btn_execute.Disable()
            self.btn_config.Disable()
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
        
        noacs =     self.flags[const.BFLAG_SKIPACSCOMP].GetValue()
        versioned = self.flags[const.BFLAG_MAKEVERSION].GetValue()
        packed =    self.flags[const.BFLAG_PACKPROJECT].GetValue()
        play_it =   self.flags[const.BFLAG_BUILDNPLAY].GetValue()
        snapshot =  self.flags[const.BFLAG_SNAPSHOTVER].GetValue()
        cachedacs = self.flags[const.BFLAG_CACHEACSLIBS].GetValue()
        acshide =   self.flags[const.BFLAG_HIDEACSSOURCE].GetValue()
        
        completed = sucess == thread.BUILD_SUCCESS
        failure = sucess == thread.BUILD_CANCELED or sucess == thread.BUILD_ERROR

        if completed:
            self.cacodemon.SetAnimation(self.CACOGIF_OKAY)
            self.cacodemon.Play()
        
        if failure:
            self.cacodemon.SetAnimation(self.CACOGIF_FAIL)
            self.cacodemon.Play()
        
        nopart = []
        skip_a_part = False
        for part in self.projectparts:
            if part.skip: 
                nopart.append(part.skip) 
                skip_a_part = True
            
        result = ""
        title = ""
        self.notif.SetFlags(wx.ICON_INFORMATION)
        if(platform.platform() == "Windows"):
         self.notif.UseTaskBarIcon(self.taskbar)
        
        if(not skip_a_part and not (noacs or versioned or packed or play_it)): 
            if completed: 
                title = "Full build completed."
                self.notif.SetTitle("Full build completed.")
            elif failure: 
                title = "Full build interrupted."
                self.notif.SetTitle("Full build interrupted.")
        else: 
            if(completed): 
                title = "Build completed with the following flags."
                self.notif.SetTitle("Build completed!")
            elif failure: 
                title = "Build interrupted with the following flags."
                self.notif.SetTitle("Build Interrupted!")
            for part in self.projectparts:
                if part.skip:
                    title += "\n -) " + part.name + " part skipped."
            
        if(noacs):  title += "\n -) ACS compilation skipped."
        if(versioned):  title += "\n -) Tagged to the respective versions.";
        if(packed):
            zipfilename = ""
            zip_name = const.ini_prop(const.JSON_BUILDSETS_NAME, 'project')
            zip_tag =  const.ini_prop(const.JSON_BUILDSETS_TAG, 'v0')
            if(versioned): 
                if(snapshot):
                    zipfilename = zip_name + "_" + self.snapshot_tag;
                else: 
                    zipfilename = zip_name + "_" + zip_tag + '.zip';
            else:          
                zipfilename = zip_name + "_DEV.zip";
            title += "\n -) Packed-up in file: " + zipfilename
        if(sucess == thread.BUILD_SKIPPED): title = "Build Interrupted. \nAll the project parts are skipped, unmark the skip flags and try again."
        if(play_it): title += "\n -) The project will run once you close this window."
        if(cachedacs): title += "\n -) ACS Compilation has been done with preloaded dependencies."
        if(acshide): title += "\n -) ACS sources are not included in this build."

        title += "\nRead the log for more details."

        self.notif.SetMessage("Check all the details in the log.")
        # self.Bind(adv.wxEVT_NOTIFICATION_MESSAGE_CLICK, self.OnLog, self.notif)
        # self.notif.AddAction(self.btn_log.GetId(), "View Log Output")
        self.notif.Show(timeout=adv.NotificationMessage.Timeout_Auto)
        
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
            wx.PostEvent(self, thread.StatusBarEvent("Project build stopped, caused by an error."))
            self.gauge.SetValue(0)
            self.gauge.SetRange(0)
        elif sucess == thread.BUILD_CANCELED:
            wx.PostEvent(self, thread.StatusBarEvent("Project build canceled, by user will."))
            self.gauge.SetValue(0)
            self.gauge.SetRange(0)
            
        elif sucess == thread.BUILD_SUCCESS: 
            wx.PostEvent(self, thread.StatusBarEvent("Project build finished."))
            self.gauge.SetValue(1)
            self.gauge.SetRange(1)
        
        
        result = self.ReportResults(sucess)
        
        self.btn_log.Enable()
        self.btn_log.SetLabel("Log")
        self.btn_build.SetLabel("Build")
        self.btn_build.Enable()
        self.btn_play.Enable()
        self.btn_execute.Enable()
        self.btn_config.Enable()
        self.ToggleFlags(True)
        
        
        # And to top it off, do a dialog!
        self.lastlog = [result[0], result[1]]
        filename =  "buildlog_"+ (datetime.datetime.now().strftime("%d%m%y_%H%M%S"))+".txt"
        newlogfile = {filename: {"header":result[0], "content":result[1]}}
        self.alllogs.update(newlogfile)
        self.logfiles.Append([filename])
        self.builder = None
        if (not self.flags[const.BFLAG_SKIPLOGBUILD].GetValue()):
            rd.ResultDialog(self, result[0], result[1], filename).ShowModal()
        if (self.flags[const.BFLAG_BUILDNPLAY].GetValue() and sucess == thread.BUILD_SUCCESS):
            self.PlayNow(event)
        

    def OnPlayResult(self, event):
        self.btn_log.Enable()
        self.btn_log.SetLabel("Log")
        header = "The game closed \nHere it is the following output."
        self.lastlog = [header, event.data]
        filename =  "playlog_"+ (datetime.datetime.now().strftime("%d%m%y_%H%M%S"))+".txt"
        newlogfile = {filename: {"header":header, "content":event.data}}
        self.alllogs.update(newlogfile)
        self.logfiles.Append([filename])
        
        if (not self.flags[const.BFLAG_SKIPLOGPLAY].GetValue()):
            rd.ResultDialog(self, header, event.data, filename).ShowModal()

    def ACSErrorOutput(self, output):
        if self.acs_err_dialog is None:
            self.response = -1
            self.acs_err_dialog = rd.ACSErrorDialog(self, output)
            self.acs_err_dialog.ShowModal()
            # self.acs_err_dialog.Destroy()
            self.acs_err_dialog = None
        # acs_err_dialog.Destroy()
    
    
    def PlayNow(self, e):
        dialog = pd.PlayDialog(self, self.play_params)
        dialog.OnPlay(e)
        self.play_params = dialog.GetCurrentSets()
        
    def OnPlay(self, e):
        try:
            dialog = pd.PlayDialog(self, self.play_params)
            if not self.flags[const.BFLAG_QUICKPLAY].GetValue(): dialog.ShowModal()
            else :                           dialog.OnPlay(e)
            self.play_params = dialog.GetCurrentSets()
        except Exception as e:
            dlg = wx.MessageDialog(None, "Something went wrong!\n" +"\n"+ traceback.format_exc(), "Ah shiet!").ShowModal()
        # saves the temporary settings while you're on the program. (Not saved to the ini)
    
    def OnLog(self, e):
        rd.ResultDialog(self, self.lastlog[0], self.lastlog[1]).ShowModal()

    def OnClose(self, event):
        self.taskbar.RemoveIcon()
        self.taskbar.Destroy()
        self.Destroy()

        if self.notif.Close():
            self.notif.Destroy()
    
    def OnShowMeUp(self, event):
        if not self.IsShown():
            self.Show()
    
    def OnExecute(self, event):
        exe.ExecuteDialog(self).ShowModal()
