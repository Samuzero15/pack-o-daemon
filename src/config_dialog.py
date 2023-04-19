
import os
import traceback
import wx
import json

import src.constants as const
import src.funs_n_cons_2 as utils
import src.form_inputs as form

class ConfigDialog(wx.Dialog):
    def __init__(self, frame):
        wx.Dialog.__init__(self, frame, title="Settings", size=(500, 500))
        self.Centre()
        self.frame = frame
        cont = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        
        self._make_tab_build_flags(nb, frame)
        self._make_tab_build_settings(nb, frame)
        self._make_tab_string_replacer(nb)
        self._make_tab_acs_compilation(nb, frame)
        
        btn_save = wx.Button(panel, label="Save settings")
        
        cont.Add(nb, 2, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        cont.Add(btn_save, 0, wx.DOWN | wx.CENTER, 10)
        panel.SetSizerAndFit(cont)

        self.Bind(wx.EVT_BUTTON, self.OnSave, btn_save)

    def GetBuildFlags(self):
        return self.bf_checks
    

    def _make_tab_build_flags(self, nb, frame):

        tab_build_flags = self.MakeTab(nb, "Build Flags")
        sizer_panel_build_flags = wx.BoxSizer(wx.VERTICAL)
        sizer_checkbox_build_flags = wx.BoxSizer(wx.VERTICAL)
        build_flags = frame.flags
        self.bf_checks = []
        # Add the flags over here
        for i in range(0, len(const.BUILD_FLAGS)):
            tooltip = wx.ToolTip(const.BUILD_FLAGS[i][1])
            self.bf_checks.append(wx.CheckBox(tab_build_flags, label=const.BUILD_FLAGS[i][0]))
            self.bf_checks[i].SetToolTip(tooltip)
            sizer_checkbox_build_flags.Add(self.bf_checks[i], 0, wx.ALL, 5)
            self.bf_checks[i].SetValue(build_flags[i].GetValue())

        sizer_panel_build_flags.Add(sizer_checkbox_build_flags, 0, wx.ALL, 2)
        tab_build_flags.SetSizer(sizer_panel_build_flags)
    
    def _make_tab_build_settings(self, nb, frame):
        tab_bs = self.MakeTab(nb, "Build settings")
        
        self.bs_inputs = []
        i1 = form.InputText(tab_bs, "Name", "name")
        i2 = form.InputText(tab_bs, "Tag", "tag")
        i3 = form.InputText(tab_bs, "Build Directory Name", "build_dir")
        i4 = form.InputComboBox(tab_bs, "Compression Type", "zip_compress_type", _choices=["deflated", "bzip2", "lzma" , "stored"])
        i5 = form.InputTextDir(tab_bs, "Zip Directory Name", "zip_dir", frame.rootdir, "Pick a folder")
        i6 = form.InputList(tab_bs, "Skip File Extentions", "build_skip_files")
        i7 = form.InputListFile(tab_bs, "Add extra files", frame.rootdir, "Any file (*.*) | *.*", "Pick a file", "build_add_files")

        self.bs_inputs.extend([i1, i2, i3, i4, i5, i6, i7])
        for input in self.bs_inputs:
            self.AddToTab(tab_bs, input.sizer)

    def _make_tab_string_replacer(self, nb):
        tab_sr = self.MakeTab(nb, "String Replacer")
        self.sr_inputs = []
        
        string_replacer_list = []
        for key, value in const.ini_prop("string_replacer")["strings_to_replace"].items():
            string_replacer_list.append(form.StringReplacerEntry(key, value["type"], value["content"], value["oneline"]))
        
        i8 = form.InputList_StringReplacer(tab_sr, "Input String replacer",  string_replacer_list)
        i9 = form.InputList(tab_sr, "Apply string replacement on file names in source folders", "files_to_replace", const.ini_prop("string_replacer")["files_to_replace"])
        
        self.sr_inputs.extend([i8, i9])

        self.AddToTab(tab_sr, i9.sizer, 0, wx.LEFT | wx.RIGHT | wx.CENTER | wx.EXPAND, 20)
        self.AddToTab(tab_sr, i8.sizer, 4, wx.ALL | wx.CENTER | wx.EXPAND, 20)

    def _make_tab_acs_compilation(self, nb, frame):
        tab_ac = self.MakeTab(nb, "ACS Compilation")
        self.ac_inputs = []

        i10 = form.InputComboBox(tab_ac, "Compilation Type", "type", "acs_compilation", _choices=["acc", "bcc"])
        i11 = form.InputTextFile(tab_ac, "Executable", "executeable",
                                frame.rootdir, "Executeable file (*.exe;)|*.exe", "Pick a file", "acs_compilation")
        i12 = form.InputText(tab_ac, "Extra parameters for the compiler", "extra_params", "acs_compilation")
    
        self.ac_inputs.extend([i10, i11, i12])
        for input in self.ac_inputs:
            self.AddToTab(tab_ac, input.sizer)

    def OnSave(self, event):
        try:
            s = {}
            for i in self.bs_inputs:
                data = i.GetValue()
                s[data[0]] = data[1]

            checks = []
            for i in range(0,len(self.bf_checks)):
                self.frame.flags[i] = self.bf_checks[i]
                checks.append(self.bf_checks[i].GetValue())
                
            json_buildflags = ("build_flags", checks)

            o = {}
            for i in self.sr_inputs:
                data = i.GetValue()
                o[data[0]] = data[1]
            
            s[json_buildflags[0]] = json_buildflags[1]
            s["string_replacer"] = o

            j = {}
            for i in self.ac_inputs:
                data = i.GetValue()
                j[data[0]] = data[1]

            f = open(const.PROJECT_FILE, "r")
            project_json = json.load(f)
            f.close()

            project_json["build_settings"] = s
            project_json["acs_compilation"] = j

            f = open(const.PROJECT_FILE, "w")
            json.dump(project_json, f, indent=4)
            f.close()
            const.CONFIG_DATA = project_json

            msg = "All the settings are saved in the '" +const.PROJECT_FILE+"' file."
            dlg = wx.MessageDialog(self.frame, msg, "Settings saved on file").ShowModal()
            self.Close()
        except Exception as e:
            dlg = wx.MessageDialog(None, "Something went wrong!\n" +"\n"+ traceback.format_exc(), "Ah shiet!").ShowModal()
        

    
    def MakeTab(self, notebook, title):
        tab = wx.ScrolledWindow(notebook)
        tab.SetScrollbars(1, 5, 300, 400)
        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        tab.SetSizer(tab_sizer)
        notebook.AddPage(tab, title)
        return tab
    
    def AddMultiToTab(self, tab, what=[]):
        for item in what:
            if type(item) == list:
                self.AddToTab(tab, item[0], item[1] or 0, item[2] or None, item[3] or 10)
            else:
                self.AddToTab(tab, item)

    def AddToTab(self, tab, what, proportion = 0,  flags=None, margin = 10):
        if flags == None: flags = wx.LEFT | wx.DOWN | wx.RIGHT | wx.CENTER | wx.EXPAND
        tab.GetSizer().Add(what, proportion, flags, margin)

