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
import source.constants as const

from configparser import ConfigParser

class PlayDialog(wx.Dialog):
    def __init__(self, parent, play_params=[-1,-1,"","",[]]):
        wx.Dialog.__init__(self, parent, title="Play Project", size=(300, 200))
        self.parent = parent
        self.project_pwads = self.SetUpPwads(parent, play_params[4], parent.flags[1].GetValue())
        pwad_choices = [
        "doom2.wad",
        "doom.wad",
        "heretic.wad",
        "hexen.wad",
        "strife1.wad",
        "chex3.wad",
        "freedoom1.wad",
        "freedoom2.wad"
        ]
        
        sourceport_choices = [
        "Zandronum", 
        "GZDoom", 
        "ZDaemon"
        ]
        
        panel =             wx.Panel(self);
        btn_play =               wx.Button(panel, label="Play Project")
        btn_save =               wx.Button(panel, label="Save Settings")
        self.txt_ctrl_map =      wx.TextCtrl(panel)
        self.txt_ctrl_params =   wx.TextCtrl(panel)
        self.list_sourceports   =  wx.ComboBox(panel, style=wx.CB_READONLY, choices=sourceport_choices)
        self.list_iwads         =  wx.ComboBox(panel, style=wx.CB_READONLY, choices=pwad_choices)
        self.list_pwads         = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.btn_add_pwad            = wx.Button(panel, label="Add")
        self.btn_remove_pwad         = wx.Button(panel, label="Remove")
        self.btn_clear_pwads         = wx.Button(panel, label="Clear")
        self.btn_raise_pwad          = wx.Button(panel, label="Raise")
        self.btn_lower_pwad          = wx.Button(panel, label="Lower")
        
        self.list_pwads.AppendColumn("Name")
        self.list_pwads.AppendColumn("Directory", width=200)
        
        self.Bind(wx.EVT_BUTTON, self.OnPlay, btn_play)
        self.Bind(wx.EVT_BUTTON, self.OnSaveSets, btn_save)
        self.Bind(wx.EVT_BUTTON, self.OnAddPwad,    self.btn_add_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnRemovePwad, self.btn_remove_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnClearPwads, self.btn_clear_pwads)
        self.Bind(wx.EVT_BUTTON, self.OnRaisePwad,  self.btn_raise_pwad)
        self.Bind(wx.EVT_BUTTON, self.OnLowerPwad,  self.btn_lower_pwad)
        
        gsizer_form     = wx.GridSizer(3, 2, 5, 5)
        pwad_btn_sz     = wx.BoxSizer(wx.VERTICAL)
        pwads_sizer     = wx.BoxSizer(wx.HORIZONTAL)
        param_sizer     = wx.BoxSizer(wx.VERTICAL)
        ctrls           = wx.BoxSizer(wx.VERTICAL)
        ctrls2          = wx.BoxSizer(wx.HORIZONTAL)
        cont            = wx.BoxSizer(wx.VERTICAL)
        
        gsizer_form_flags = wx.ALL | wx.CENTER | wx.EXPAND
        
        self.AddFormInput( gsizer_form, panel, "Sourceport:",       self.list_sourceports)
        self.AddFormInput( gsizer_form, panel, "IWad to use:",      self.list_iwads)
        self.AddFormInput( gsizer_form, panel, "Map to play:",      self.txt_ctrl_map)
        self.AddFormInput( param_sizer, panel, "Extra parameters:", self.txt_ctrl_params)
        pwads_sizer.Add (self.list_pwads, 0, gsizer_form_flags)
        pwad_btn_sz.Add (self.btn_add_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_remove_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_clear_pwads, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_raise_pwad, 0, gsizer_form_flags, 2)
        pwad_btn_sz.Add (self.btn_lower_pwad, 0, gsizer_form_flags, 2)
        pwads_sizer.Add (pwad_btn_sz, 0, wx.CENTER, 5)
        
        ctrls.Add(gsizer_form, 0, wx.CENTER, 5)
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
        
    def SetUpPwads(self, parent, pwad_list, versioned=False):
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
            
        if len(pwad_list) == 0:
            # If this is the first time on the play button. Load the INI PWADS and the project pwads
            for pwad in pwads_before:
                pwad_list.append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
            for p in parent.projectparts:
                pwad_list.append(p.GetExpectedPWADS(versioned))
            for pwad in pwads_after:
                pwad_list.append([utils.get_file_name(pwad),utils.get_file_dir(pwad)])
        else:
            # Else, update the project pwads. Depending on the versioned mark.
            index = 0
            for pwadlist in pwad_list:
                for p in parent.projectparts:
                    if pwadlist[0] == p.GetExpectedPWADS(not versioned)[0]:
                        pwad_list[index] = p.GetExpectedPWADS(versioned)
                index += 1
        return pwad_list
    
    def LoadDefaultValues(self, play_params):
        # Load the selected sourceport.
        if play_params[0] != -1: 
            self.list_sourceports.SetSelection      (play_params[0])
        else:
            self.list_sourceports.SetSelection      (const.ini_prop('play_sourceport', 0))
        # Load the selected iwad
        if play_params[1] != -1: 
            self.list_iwads.SetSelection            (play_params[1])
        else:
            self.list_iwads.SetSelection            (const.ini_prop('play_iwad', 0))
        # Load the specified map
        if len(play_params[2]) != 0: 
            self.txt_ctrl_map.SetValue              (play_params[2])
        else:
            self.txt_ctrl_map.SetValue              (const.ini_prop('play_map'))
        # Load the extra parameters
        if len(play_params[3]) != 0: 
            self.txt_ctrl_params.SetValue           (play_params[3])
        else:
            self.txt_ctrl_params.SetValue           (const.ini_prop('play_extraparams'))
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
            sourceport  = self.list_sourceports.GetStringSelection()
            iwad        = self.list_iwads.GetStringSelection()
            test_map    = self.txt_ctrl_map.GetValue()
            ex_params   = self.txt_ctrl_params.GetValue()
            pwads       = self.GetPWADList()
            
            self.parent.play_params = []
            
            self.parent.play_params.append(self.list_sourceports.GetSelection())
            self.parent.play_params.append(self.list_iwads.GetSelection())
            self.parent.play_params.append(test_map)
            self.parent.play_params.append(ex_params)
            self.parent.play_params.append(pwads)
            
            thread.PlayProject(self.parent, sourceport,  iwad, test_map, ex_params, pwads)
            self.Close()
        else:
            msg = "Specify a sourceport and IWAD!"
            dlg = wx.MessageDialog(self.parent, msg, "Hold-up!").ShowModal()
    
    def OnSaveSets(self, event):
        config = ConfigParser()
        config.read("project.ini")
        
        section = "Project"
        config.set(section, "play_sourceport",   str(self.list_sourceports.GetSelection()))
        config.set(section, "play_iwad",         str(self.list_iwads.GetSelection()))
        config.set(section, "play_map",          self.txt_ctrl_map.GetValue())
        config.set(section, "play_extraparams",  self.txt_ctrl_params.GetValue())
        
        
        with open("project.ini", 'w') as configfile:
            config.write(configfile)
        
        msg = "The current play settings are saved in the project.ini file."
        dlg = wx.MessageDialog(self.parent, msg, "Settings saved!").ShowModal()
       
    def GetCurrentSets(self):
        return [self.list_sourceports.GetSelection(), 
        self.list_iwads.GetSelection(), 
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
        directory = ""
        wildcards = "WAD/PK3/PK7 files (*.wad;*.pk3;*.pk7)|*.wad;*.pk3;*.pk7"
        dialog = wx.FileDialog(self, "Choose a PWAD", self.dirname, "", wildcards, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename();
            self.dirname = dialog.GetDirectory();
            if len(filename) != 0: 
                self.list_pwads.Append([filename, self.dirname])
        dialog.Destroy();
        self.UpdatePWADButtons()
    
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
        return  self.list_sourceports.GetSelection() != wx.NOT_FOUND and self.list_iwads.GetSelection() != wx.NOT_FOUND;
