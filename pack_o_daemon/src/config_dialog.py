
import os
import traceback
import wx
import json

try:
    import src.constants as const
    import src.funs_n_cons_2 as utils
    import src.form_inputs as form
    import src.acs_comp as acs_comp
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.constants as const
    import pack_o_daemon.src.funs_n_cons_2 as utils
    import pack_o_daemon.src.form_inputs as form
    import pack_o_daemon.src.acs_comp as acs_comp

class ConfigDialog(wx.Dialog):
    def __init__(self, frame):
        wx.Dialog.__init__(self, frame, title="Settings", size=(500, 500))
        self.Centre()
        self.frame = frame
        self.projparts = {}
        cont = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        
        # self._make_tab_build_flags(nb, frame)
        self._make_tab_project_parts(nb, frame)
        self._make_tab_build_settings(nb, frame)
        self._make_tab_string_replacer(nb)
        self._make_tab_acs_compilation(nb, frame)
        
        btn_save = wx.Button(panel, label="Save settings")
        
        cont.Add(nb, 2, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        cont.Add(btn_save, 0, wx.DOWN | wx.CENTER, 10)
        panel.SetSizerAndFit(cont)

        self.Bind(wx.EVT_BUTTON, self.OnSave, btn_save)
    
    def _make_tab_project_parts(self, nb, frame):
        tab_pp = self.MakeTab(nb, "Project Parts")
        self.nb_pp = wx.Notebook(tab_pp)
        for part in frame.projectparts:
            self._make_new_projectpart(part.name)

        self.AddToTab(tab_pp, self.nb_pp, 1, wx.ALL | wx.EXPAND | wx.CENTER)
        self.input_addppart = form.InputText(tab_pp, "Add New Part", "")
        self.btn_addppart = wx.Button(tab_pp, label="Add")
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hori_sizer.Add(self.input_addppart.sizer, 2, wx.ALL | wx.CENTER | wx.EXPAND ,1)
        hori_sizer.Add(self.btn_addppart, 0, wx.ALL | wx.CENTER | wx.EXPAND, 1)
        self.AddToTab(tab_pp, hori_sizer, 0, wx.ALL | wx.CENTER | wx.EXPAND,1)
        self.input_addppart.ctrl.SetValue("")
        self.btn_addppart.Bind(wx.EVT_BUTTON, self._OnAddProjectPart, self.btn_addppart)
    
    def _OnAddProjectPart(self, event):
        unique_name = self.input_addppart.GetValue()[1]
        if len(unique_name) == 0: return
        while(self.__TabExists(self.nb_pp, unique_name)):
            unique_name = unique_name + "_copy"
        self._make_new_projectpart(unique_name)
        self.nb_pp.SetSelection(self.nb_pp.GetPageCount()-1)
        self.nb_pp.FitInside()
    
    def __TabExists(self, nb, tab_name):
        for index in range(nb.GetPageCount()):
            if nb.GetPageText(index) == tab_name:
                return True
        return False

    def _make_new_projectpart(self, name):
        tab_part = self.MakeTab(self.nb_pp, name)
        part_form = [
            form.InputProjPartText(tab_part, "Release", name, const.JSON_PROJPARTS_RELEASE, "v0"),
            form.InputProjPartText(tab_part, "Filename", name, const.JSON_PROJPARTS_FILENAME, name),
            form.InputProjPartText(tab_part, "Source Directory", name, const.JSON_PROJPARTS_SOURCEDIR, "src"),
            form.InputProjPartText(tab_part, "Dist. Directory", name, const.JSON_PROJPARTS_DISTDIR, "dist"),
            form.InputProjPartCheckBox(tab_part, "Enable ACS Compilation", name, const.JSON_PROJPARTS_ACSCOMP, False),
            form.InputProjPartCheckBox(tab_part, "Disable Text Edition?", name, const.JSON_PROJPARTS_NOTXT, False),
        ]
        for input in part_form:
            self.AddToTab(tab_part, input.sizer)
        self.projparts[name] = part_form
        btn_delete = wx.Button(tab_part, label="Delete")
        self.AddToTab(tab_part, btn_delete)
        btn_delete.Bind(wx.EVT_BUTTON, lambda evt, projpart=name: self._OnDeleteProjectPart(evt, projpart), btn_delete)
        tab_part.FitInside()

    def _OnDeleteProjectPart(self, event, projpart):

        if self.nb_pp.GetPageCount() == 1:
            wx.Bell()
            msg = "You can't delete your last Project Part."
            dialog = wx.MessageDialog(self, msg, "Delete Project Part", wx.OK).ShowModal()
            return

        msg = "Deleting a project part will only delete the definition, "
        msg += "not the directory and files, if you need to delete the files too, do it manually."
        msg += "\n\nAre you sure you want to delete this part?"
        dialog = wx.MessageDialog(self, msg, "Delete Project Part", wx.YES_NO | wx.NO_DEFAULT).ShowModal()
        
        if dialog == wx.ID_YES:
            for index in range(self.nb_pp.GetPageCount()):
                if self.nb_pp.GetPageText(index) == projpart:
                    del self.projparts[projpart]
                    # print(self.projparts)
                    self.nb_pp.DeletePage(index)
                    self.nb_pp.SendSizeEvent()
                    break
        

    def _make_tab_build_settings(self, nb, frame):
        tab_bs = self.MakeTab(nb, "Build settings")
        
        self.bs_inputs = [
            form.InputText(tab_bs, "Name", const.JSON_BUILDSETS_NAME),
            form.InputText(tab_bs, "Tag", const.JSON_BUILDSETS_TAG),
            form.InputText(tab_bs, "Build Directory Name", const.JSON_BUILDSETS_BUILDDIR),
            form.InputComboBox(tab_bs, "Compression Type", const.JSON_BUILDSETS_ZIPCOMPRESSTYPE, _choices=["deflated", "bzip2", "lzma" , "stored"]),
            form.InputTextDir(tab_bs, "Zip Directory Name", const.JSON_BUILDSETS_ZIPDIR, frame.rootdir, "Pick a folder"),
            form.InputList(tab_bs, "Skip File Extentions", const.JSON_BUILDSETS_BUILDSKIPFILES),
            form.InputListFile(tab_bs, "Add extra files", frame.rootdir, "Any file (*.*) | *.*", "Pick a file", const.JSON_BUILDSETS_BUILDADDFILES)
        ]
        for input in self.bs_inputs:
            self.AddToTab(tab_bs, input.sizer)

    def _make_tab_string_replacer(self, nb):
        tab_sr = self.MakeTab(nb, "String Replacer")
        self.sr_inputs = []
        
        string_replacer_list = []
        for key, value in const.ini_prop(const.JSON_BUILDSETS_STRREP)[const.JSON_BUILDSETS_STRREP_STR2REP].items():
            string_replacer_list.append(form.StringReplacerEntry(key, value[const.JSON_BUILDSETS_STRREP_STR2REP_TYPE], value[const.JSON_BUILDSETS_STRREP_STR2REP_CONTENT], value[const.JSON_BUILDSETS_STRREP_STR2REP_ONELINE]))
        
        i8 = form.InputList_StringReplacer(tab_sr, "Input String replacer",  string_replacer_list)
        i9 = form.InputList(tab_sr, "Apply string replacement on file names in source folders", const.JSON_BUILDSETS_STRREP_FILESTOREPLACE, const.ini_prop(const.JSON_BUILDSETS_STRREP)[const.JSON_BUILDSETS_STRREP_FILESTOREPLACE])
        
        self.sr_inputs.extend([i8, i9])

        self.AddToTab(tab_sr, i9.sizer, 0, wx.LEFT | wx.RIGHT | wx.CENTER | wx.EXPAND, 20)
        self.AddToTab(tab_sr, i8.sizer, 4, wx.ALL | wx.CENTER | wx.EXPAND, 20)

    def _make_tab_acs_compilation(self, nb, frame):
        self.tab_ac = self.MakeTab(nb, "ACS Compilation")
        comp_types = list(acs_comp.ACS_FLIEEXT_TARGETS.keys())
        self.ac_comp_type_input = form.InputComboBox(self.tab_ac, "Compilation Type", const.JSON_ACSCOMP_TYPE, const.JSON_ACSCOMP, _choices=comp_types)
        self.ac_exe_input = form.InputTextFile(self.tab_ac, "Executable", const.JSON_ACSCOMP_EXECUTEABLE,
                                frame.rootdir, "Executeable file (*.exe;)|*.exe", "Pick the executeable", const.JSON_ACSCOMP)
        self.Bind(wx.EVT_COMBOBOX, self.UpdateACTab, self.ac_comp_type_input.ctrl)
        self.Bind(wx.EVT_TEXT, self.UpdateACTab, self.ac_exe_input.ctrl)

        self.ac_inputs = [self.ac_comp_type_input,self.ac_exe_input,]
        self.ac_gdcc_inputs = [
            form.InputTextFile(self.tab_ac, "(GDCC-C) Linker Executable", const.JSON_ACSCOMP_GDCCLINKER, 
                                frame.rootdir, "Executeable file (*.exe;)|*.exe", "Pick the GDCC's linker executeable", const.JSON_ACSCOMP),
            form.InputCheckBox(self.tab_ac, "(GDCC-C) Include Libc and LibGDCC", const.JSON_ACSCOMP_GDCCMAKELIBS, const.JSON_ACSCOMP),
            form.InputTextFile(self.tab_ac, "(GDCC-C) Makelib Executeable", "gdcc-makelib_exe",
                                frame.rootdir, "Executeable file (*.exe;)|*.exe", "Pick the GDCC's makelib executeable", const.JSON_ACSCOMP),
            form.InputText(self.tab_ac, "(GDCC-C) Project Library Name", const.JSON_ACSCOMP_GDCCMAINLIB, const.JSON_ACSCOMP),
            form.InputComboBox(self.tab_ac, "(GDCC-C) Target Engine", const.JSON_ACSCOMP_GDCCTARGETENGINE, const.JSON_ACSCOMP, ["Zandronum", "ZDoom"])
        ]
        self.ac_inputs += self.ac_gdcc_inputs
        self.ac_inputs += [
            form.InputTextMultiline(self.tab_ac, "Extra parameters for the compiler", const.JSON_ACSCOMP_EXTRAPARAMS, const.JSON_ACSCOMP),
            form.InputListDir(self.tab_ac, "Add acs library", frame.rootdir, "Pick a folder", const.JSON_ACSCOMP_LIBRARYDIRS, const.JSON_ACSCOMP)
        ]
    
        for input in self.ac_inputs:
            self.AddToTab(self.tab_ac, input.sizer)
        
        self.UpdateACTab()
    
    def UpdateACTab(self, event=None):
        comp_type_list = acs_comp.ACS_FLIEEXT_TARGETS
        selected_value = self.ac_comp_type_input.ctrl.GetValue()
        if len(str.strip(self.ac_exe_input.ctrl.GetValue())) > 0:
            self.ac_exe_input.label.SetLabelText("Executeable ("+os.path.split(self.ac_exe_input.ctrl.GetValue())[1]+")")
        else:
             self.ac_exe_input.label.SetLabelText("Executeable")
        self.ac_comp_type_input.label.SetLabelText("Compilation Type (Targets '*"+comp_type_list[selected_value]+"' files.) ")
        if selected_value == 'gdcc-c':
            for input in self.ac_gdcc_inputs:
                if hasattr(input, "label"): input.label.Show()
                if hasattr(input, "btn"): input.btn.Hide()
                input.ctrl.Show()
        else:
            for input in self.ac_gdcc_inputs:
                if hasattr(input, "label"): input.label.Hide()
                if hasattr(input, "btn"): input.btn.Hide()
                input.ctrl.Hide()
        
        self.tab_ac.Layout()
        self.tab_ac.FitInside()

    def OnSave(self, event):
        skip_part_oldvalues = []
        for skip_part in self.frame.skip_parts:
            skip_part_oldvalues.append(skip_part.GetValue())
        
        os.chdir(self.frame.rootdir)
        try:
            p = {}
            for i in self.projparts:
                p[i] = {}
                for j in self.projparts[i]:
                    data = j.GetValue()
                    p[data[0]][data[1]] = data[2]
            s = {}
            for i in self.bs_inputs:
                data = i.GetValue()
                s[data[0]] = data[1]

            o = {}
            for i in self.sr_inputs:
                data = i.GetValue()
                o[data[0]] = data[1]
            
            # s[json_buildflags[0]] = json_buildflags[1]
            s[const.JSON_BUILDSETS_STRREP] = o

            j = {}
            for i in self.ac_inputs:
                data = i.GetValue()
                j[data[0]] = data[1]

            f = open(const.PROJECT_FILE, "r")
            project_json = json.load(f)
            f.close()

            project_json[const.JSON_PROJPARTS] = p
            for k in p.keys():
                project_json[const.JSON_PROJPARTS][k][const.JSON_PROJPARTS_SKIPPED] = False

            for k in s.keys():
                project_json[const.JSON_BUILDSETS][k] = s[k]

            project_json[const.JSON_ACSCOMP] = j

            f = open(const.PROJECT_FILE, "w")
            json.dump(project_json, f, indent=4)
            f.close()
            const.CONFIG_DATA = project_json

            msg = "All the settings are saved in the '" +const.PROJECT_FILE+"' file."
            dlg = wx.MessageDialog(self.frame, msg, "Settings saved on file").ShowModal()

            # Now, update the flags and the project parts.
            self.frame.projectparts = const.read_parts(self.frame.rootdir)
            for fl in self.frame.flags:
                fl.Destroy()
            for sp in self.frame.skip_parts:
                sp.Destroy()
            for buf in self.frame.build_flags:
                buf.Destroy()
            
            self.frame.flags = []
            self.frame.skip_parts = []
            self.frame.build_flags = []

            for child in self.frame.cb_tab.GetChildren():
                child.Destroy()
            self.frame._AddToTab(self.frame.cb_tab, self.frame._build_checkboxes(self.frame.cb_tab))
            self.frame.cb_tab.Layout()
            self.frame.cb_tab.FitInside()
            const.CONFIG_DATA, FIRST_TIME = const.load_stuff()

            # Recover old skip part flag values if they were already checked before.
            for skip_part_id in range(0, min(len(self.frame.skip_parts), len(skip_part_oldvalues))):
                self.frame.skip_parts[skip_part_id].SetValue(skip_part_oldvalues[skip_part_id])

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

