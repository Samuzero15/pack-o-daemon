import json
import wx
import os
import threading
import time
import sys
import subprocess
import zipfile
import pack_o_daemon.src.threads as thread
import pack_o_daemon.src.funs_n_cons_2 as utils
import pack_o_daemon.src.projectpart as part
import pack_o_daemon.src.constants as const

from configparser import ConfigParser

class PlayDialog(wx.Dialog):
    def __init__(self, parent, play_params=[-1,-1,"","",[]]):
        wx.Dialog.__init__(self, parent, title="Play Project", size=(300, 200))
        self.parent = parent
        self.project_pwads = self.SetUpPwads(parent, play_params[4])
        
        panel =             wx.Panel(self);
        btn_play =               wx.Button(panel, label="Play Project")
        btn_save =               wx.Button(panel, label="Save Settings")
        self.txt_ctrl_map =      wx.TextCtrl(panel)
        self.txt_ctrl_params =   wx.TextCtrl(panel)
        """
        self.list_sourceports   =  wx.ComboBox(panel, style=wx.CB_READONLY, choices=sourceport_choices)
        self.list_iwads         =  wx.ComboBox(panel, style=wx.CB_READONLY, choices=pwad_choices)
        """

        self.txt_sourceport =   wx.TextCtrl(panel)
        self.btn_sourceport =   wx.Button(panel)
        self.txt_iwad =         wx.TextCtrl(panel)
        self.btn_iwad =         wx.Button(panel)
        
        self.list_pwads         = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        self.btn_add_pwad            = wx.Button(panel)
        self.btn_remove_pwad         = wx.Button(panel)
        self.btn_clear_pwads         = wx.Button(panel)
        self.btn_raise_pwad          = wx.Button(panel)
        self.btn_lower_pwad          = wx.Button(panel)

        self.btn_add_pwad.SetToolTip("Add Pwad")
        self.btn_remove_pwad.SetToolTip("Remove Pwad")
        self.btn_clear_pwads.SetToolTip("Clear all Pwads")
        self.btn_raise_pwad.SetToolTip("Raise Pwad")
        self.btn_lower_pwad.SetToolTip("Lower Pwad")
        self.btn_sourceport.SetToolTip("Explore")
        self.btn_iwad.SetToolTip("Explore")

        self.btn_iwad.SetBitmap(wx.Bitmap(utils.get_source_img("explore.png")))
        self.btn_sourceport.SetBitmap(wx.Bitmap(utils.get_source_img("explore.png")))
        self.btn_add_pwad.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_add.png")))
        self.btn_remove_pwad.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_remove.png")))
        self.btn_clear_pwads.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_clear.png")))
        self.btn_raise_pwad.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_up.png")))
        self.btn_lower_pwad.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_down.png")))

        self.list_pwads.AppendColumn("Name")
        self.list_pwads.AppendColumn("Directory", width=200)
        
        self.Bind(wx.EVT_BUTTON, self.OnPlay, btn_play)
        self.Bind(wx.EVT_BUTTON, self.OnSaveSets, btn_save)
        self.Bind(wx.EVT_BUTTON, self.OnAddPwad,    self.btn_add_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnRemovePwad, self.btn_remove_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnClearPwads, self.btn_clear_pwads)
        self.Bind(wx.EVT_BUTTON, self.OnRaisePwad,  self.btn_raise_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnLowerPwad,  self.btn_lower_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnExploreSourceport,    self.btn_sourceport)
        self.Bind(wx.EVT_BUTTON, self.OnExploreIwad,    self.btn_iwad)
        
        gsizer_form     = wx.GridSizer(3, 2, 5, 5)
        pwad_btn_sz     = wx.BoxSizer(wx.VERTICAL)
        pwads_sizer     = wx.BoxSizer(wx.HORIZONTAL)
        sourceport_sizer     = wx.BoxSizer(wx.HORIZONTAL)
        iwad_sizer      = wx.BoxSizer(wx.HORIZONTAL)
        param_sizer     = wx.BoxSizer(wx.VERTICAL)
        ctrls           = wx.BoxSizer(wx.VERTICAL)
        ctrls2          = wx.BoxSizer(wx.HORIZONTAL)
        cont            = wx.BoxSizer(wx.VERTICAL)
        
        gsizer_form_flags = wx.ALL | wx.CENTER | wx.EXPAND 
        
        # self.AddFormInput( gsizer_form, panel, "Sourceport:",       self.list_sourceports)
        # self.AddFormInput( gsizer_form, panel, "IWad to use:",      self.list_iwads)
        
        sourceport_sizer.Add(self.txt_sourceport, 3, wx.LEFT | wx.RIGHT)
        sourceport_sizer.Add(self.btn_sourceport, 1, wx.LEFT | wx.RIGHT)
        iwad_sizer.Add(self.txt_iwad, 3, wx.LEFT | wx.RIGHT)
        iwad_sizer.Add(self.btn_iwad, 1, wx.LEFT | wx.RIGHT)
        self.AddFormInput( param_sizer, panel, "Sourceport:",       sourceport_sizer)
        self.AddFormInput( param_sizer, panel, "IWad:",             iwad_sizer)
        self.AddFormInput( param_sizer, panel, "Map to play:",      self.txt_ctrl_map)
        self.AddFormInput( param_sizer, panel, "Extra parameters:", self.txt_ctrl_params)
        pwads_sizer.Add (self.list_pwads, 0, gsizer_form_flags)
        pwad_btn_sz.Add (self.btn_add_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_remove_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_clear_pwads, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_raise_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_lower_pwad, 0, gsizer_form_flags, 2)
        pwads_sizer.Add (pwad_btn_sz, 0, wx.CENTER, 5)
        
        ctrls.Add(param_sizer, 0, gsizer_form_flags, 5)
        ctrls.Add(wx.StaticLine(panel), 0, gsizer_form_flags, 5);
        ctrls.Add(pwads_sizer, 0, gsizer_form_flags, 5)
        
        ctrls2.Add(btn_play, 0, wx.LEFT | wx.RIGHT, 20)
        ctrls2.Add(btn_save, 0, wx.LEFT | wx.RIGHT, 20)
        
        cont.Add(ctrls, 0, gsizer_form_flags, 5)
        cont.Add(wx.StaticLine(panel), 0, gsizer_form_flags, 5);
        cont.Add(ctrls2, 0, wx.CENTER | wx.ALL, 10)
        
        self.dirname = parent.rootdir;
        
        panel.SetSizerAndFit(cont)
        self.Fit()
        self.CentreOnParent()
        self.LoadDefaultValues(play_params)
        self.UpdatePWADButtons()
        
    def SetUpPwads(self, parent, pwad_list):
        versioned = parent.flags[const.BFLAG_MAKEVERSION].GetValue()
        snapshot = parent.flags[const.BFLAG_SNAPSHOTVER].GetValue()
        snapshot_tag = parent.snapshot_tag
        snapshot_tag_last = parent.snapshot_tag_last
        
        # Read the INI file, and get the required pwads.
        pwads_before_json = const.ini_prop('pwads_before', section="play_settings")
        pwads_before = []
        for path in pwads_before_json:
            filepath = utils.relativePath(path)
            if os.path.isfile(filepath):
                pwads_before.append(filepath)
        
        pwads_after_json = const.ini_prop('pwads_after', section="play_settings")
        pwads_after = []
        for path in pwads_after_json:
            filepath = utils.relativePath(path)
            if os.path.isfile(filepath):
                pwads_after.append(filepath)
            
        if len(pwad_list) == 0:
            # If this is the first time on the play button. Load the INI PWADS and the project pwads
            for pwad in pwads_before:
                pwad_list.append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
            for p in parent.projectparts:
                pwad_list.append(p.GetExpectedPWADS(versioned, snapshot, snapshot_tag))
            for pwad in pwads_after:
                pwad_list.append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
        else:
            # Else, update the project pwads. Depending on the versioned mark.
            index = 0
            for pwadlist in pwad_list:
                for p in parent.projectparts:
                    
                    dev_ver = p.GetExpectedPWADS(False, False, "")
                    relase_ver = p.GetExpectedPWADS(True, False, "")
                    snap_ver = p.GetExpectedPWADS(True, True, snapshot_tag)
                    snap_ver_last = p.GetExpectedPWADS(True, True, snapshot_tag_last)
                    '''
                    print("Develop version: " + dev_ver[0])
                    print("Relase version: " + relase_ver[0])
                    print("Snap version expected: " + snap_ver[0])
                    print("Last Snap version expected: " + snap_ver_last[0])
                    print("Current set: " + pwadlist[0])
                    '''
                    if(versioned):
                        if (snapshot):
                            if pwadlist[0] == dev_ver[0] or pwadlist[0] == relase_ver[0] or pwadlist[0] == snap_ver_last[0]:
                                pwad_list[index] = snap_ver
                        else:
                            if pwadlist[0] == dev_ver[0] or pwadlist[0] == snap_ver[0] or pwadlist[0] == snap_ver_last[0]:
                                pwad_list[index] = relase_ver
                    else:
                        if pwadlist[0] == relase_ver[0] or pwadlist[0] ==  snap_ver[0] or pwadlist[0] == snap_ver_last[0]:
                            pwad_list[index] = dev_ver
                index += 1
        return pwad_list
    
    def LoadDefaultValues(self, play_params):

        # Load the selected sourceport.
        if play_params[0] != -1: 
            self.txt_sourceport.SetValue      (play_params[0])
        else:
            self.txt_sourceport.SetValue      (const.ini_prop('sourceport_path', section="play_settings"))
        # Load the selected iwad
        if play_params[1] != -1: 
            self.txt_iwad.SetValue            (play_params[1])
        else:
            self.txt_iwad.SetValue            (const.ini_prop('iwad_path', section="play_settings"))
        
        # Load the specified map
        if len(play_params[2]) != 0: 
            self.txt_ctrl_map.SetValue              (play_params[2])
        else:
            self.txt_ctrl_map.SetValue              (const.ini_prop('map', section="play_settings"))
        # Load the extra parameters
        if len(play_params[3]) != 0: 
            self.txt_ctrl_params.SetValue           (play_params[3])
        else:
            self.txt_ctrl_params.SetValue           (const.ini_prop('extra_params', section="play_settings"))
        # And load the pwads.
        if len(play_params[4]) != 0: 
            self.project_pwads = play_params[4]
            self.SetPWADList                        (play_params[4])
    
    def AddFormInput(self, sizer, panel, input_label, input_comp):
        form_flags = wx.CENTER | wx.EXPAND
        sizer.Add(wx.StaticText(panel, label=input_label), 0, form_flags)
        sizer.Add(input_comp, 0, form_flags)
    
    def OnPlay(self, event): 
        # Simply saves the temporary settings, and runs the play thread.
        if self.IsValidInput():

            sourceport  = self.txt_sourceport.GetValue()
            iwad        = self.txt_iwad.GetValue()
            test_map    = self.txt_ctrl_map.GetValue()
            ex_params   = self.txt_ctrl_params.GetValue()
            pwads       = self.GetPWADList()
            
            self.parent.play_params = []
            self.parent.play_params.append(sourceport)
            self.parent.play_params.append(iwad)
            self.parent.play_params.append(test_map)
            self.parent.play_params.append(ex_params)
            self.parent.play_params.append(pwads)
            
            thread.PlayProject(self.parent, sourceport, iwad, test_map, ex_params, pwads)
            self.Close()
        else:
            msg = "Specify a sourceport and IWAD!"
            dlg = wx.MessageDialog(self.parent, msg, "Hold-up!").ShowModal()
    
    def OnSaveSets(self, event):
        with open(const.PROJECT_FILE, "r+") as jsonFile:
            data = json.load(jsonFile)

            data["play_settings"]["sourceport_path"] = self.txt_sourceport.GetValue()
            data["play_settings"]["iwad_path"] = self.txt_iwad.GetValue()
            data["play_settings"]["map"] = self.txt_ctrl_map.GetValue()
            data["play_settings"]["extra_params"] = self.txt_ctrl_params.GetValue()

            jsonFile.seek(0)  # rewind
            json.dump(data, jsonFile, indent=4)
            jsonFile.truncate()
        msg = "The current play settings are saved in the "+const.PROJECT_FILE+" file."
        wx.MessageDialog(self.parent, msg, "Settings saved!").ShowModal()        
       
    def GetCurrentSets(self):
        return [self.txt_sourceport.GetValue(),
        self.txt_iwad.GetValue(),
        self.txt_ctrl_map.GetValue(),  
        self.txt_ctrl_params.GetValue(), 
        self.project_pwads]
    
    def GetPWADList(self):
        # Retrives all pwads, with filename and directory separated.
        count = self.list_pwads.GetItemCount()
        pwads = []
        for row in range(count):
            pwad_file = self.list_pwads.GetItem(row).GetText()
            pwad_dir  = self.list_pwads.GetItem(row, 1).GetText()
            pwads.append([pwad_file, pwad_dir])
        
        return pwads
    
    def UpdatePWADButtons(self):
        if self.list_pwads.GetItemCount() > 1:
            self.btn_remove_pwad.Enable()
            self.btn_raise_pwad.Enable()
            self.btn_lower_pwad.Enable()
            self.btn_clear_pwads.Enable()
        elif self.list_pwads.GetItemCount() > 0:
            self.btn_remove_pwad.Enable()
            self.btn_raise_pwad.Disable()
            self.btn_lower_pwad.Disable()
            self.btn_clear_pwads.Disable()
        else:
            self.btn_remove_pwad.Disable()
            self.btn_raise_pwad.Disable()
            self.btn_lower_pwad.Disable()
            self.btn_clear_pwads.Disable()
    
    def SetPWADList(self, pwad_list):
        # From a given pwad_list, add these.
        all_pwads = []
        all_pwads.extend(pwad_list)
        for pwad in all_pwads:
            filepath = os.path.join(pwad[1], pwad[0])
            if os.path.isfile(filepath):
                self.list_pwads.Append([pwad[0], pwad[1]])
            else:
                msg = pwad[0] + " is missing.\nThe file was not added to the PWAD List\nIf this file is generated from your project, re-build it."
                dlg = wx.MessageDialog(self.parent, msg, "Missing PWAD").ShowModal()
    
    def OnAddPwad(self, event):
        # Ask for a file, and add it to the file list
        filename = ""
        wildcards = "WAD/PK3/PK7 files (*.wad;*.pk3;*.pk7)|*.wad;*.pk3;*.pk7"
        dialog = wx.FileDialog(self, "Choose a PWAD", self.dirname, "", wildcards, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename();
            self.dirname = dialog.GetDirectory();
            if len(filename) != 0: 
                self.list_pwads.Append([filename, self.dirname])
        dialog.Destroy();
        self.UpdatePWADButtons()
    
    def OnExploreIwad(self, event):
        # Ask for a file, and add it to the file list
        filename = ""
        wildcards = "WAD file (*.wad;)|*.wad"
        dialog = wx.FileDialog(self, "Choose a IWAD", self.dirname, "", wildcards, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename();
            self.dirname = dialog.GetDirectory();
            if len(filename) != 0: 
                self.txt_iwad.SetValue(self.dirname + os.path.sep + filename)
        dialog.Destroy();
    
    def OnExploreSourceport(self, event):
        # Ask for a file, and add it to the file list
        filename = ""
        wildcards = "Executeable file (*.exe;)|*.exe"
        dialog = wx.FileDialog(self, "Choose a Sourceport", self.dirname, "", wildcards, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename();
            self.dirname = dialog.GetDirectory();
            if len(filename) != 0: 
                self.txt_sourceport.SetValue(self.dirname + os.path.sep + filename)
        dialog.Destroy();
    
    def OnRemovePwad(self, event):
        # If you have something selected, delete it.
        sel = self.list_pwads.GetFirstSelected()
        if sel != -1: self.list_pwads.DeleteItem(sel)
        self.UpdatePWADButtons()
    
    def OnClearPwads(self, event):
        # Nuff said.
        self.list_pwads.DeleteAllItems()
        self.UpdatePWADButtons()
    
    def OnLowerPwad(self, event):
        # Lowers the PWAD on the file list, making this file to be loaded with less priority.
        select_id = self.list_pwads.GetFirstSelected()
        if select_id == -1: return;
        count = self.list_pwads.GetItemCount()
        selected = []
        switchme = []
        tmp = []
        if select_id < count - 1:
            switch_id = self.list_pwads.GetItem(select_id+1).GetId()
            switchme.append(self.list_pwads.GetItem(select_id+1).GetText())
            switchme.append(self.list_pwads.GetItem(select_id+1, 1).GetText())
            selected.append(self.list_pwads.GetItem(select_id).GetText())
            selected.append(self.list_pwads.GetItem(select_id, 1).GetText())
            tmp.append(switchme[0])
            tmp.append(switchme[1])
            
            self.list_pwads.SetItem(switch_id, 0, selected[0])
            self.list_pwads.SetItem(switch_id, 1, selected[1])
            self.list_pwads.SetItem(select_id, 0, tmp[0])
            self.list_pwads.SetItem(select_id, 1, tmp[1])
            self.list_pwads.Select(switch_id)
    
    def OnRaisePwad(self, event):
        # Raises the PWAD on the file list, making this file to be loaded with more priority.
        select_id = self.list_pwads.GetFirstSelected()
        if select_id == -1: return;
        count = self.list_pwads.GetItemCount()
        selected = []
        switchme = []
        tmp = []
        if select_id >= 1:
            switch_id = self.list_pwads.GetItem(select_id-1).GetId()
            switchme.append(self.list_pwads.GetItem(select_id-1).GetText())
            switchme.append(self.list_pwads.GetItem(select_id-1, 1).GetText())
            selected.append(self.list_pwads.GetItem(select_id).GetText())
            selected.append(self.list_pwads.GetItem(select_id, 1).GetText())
            tmp.append(switchme[0])
            tmp.append(switchme[1])
            
            self.list_pwads.SetItem(switch_id, 0, selected[0])
            self.list_pwads.SetItem(switch_id, 1, selected[1])
            self.list_pwads.SetItem(select_id, 0, tmp[0])
            self.list_pwads.SetItem(select_id, 1, tmp[1])
            self.list_pwads.Select(switch_id)
            
    
    def IsValidInput(self):
        sourceport_path = utils.relativePath(self.txt_sourceport.GetValue())
        return os.path.isdir(os.path.dirname(sourceport_path))
