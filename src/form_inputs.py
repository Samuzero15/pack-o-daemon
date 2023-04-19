import wx
import os
import src.constants as const
import src.funs_n_cons_2 as utils

class InputComboBox():
    def __init__(self, panel, _label, json_entry, category="build_settings", _choices=[]):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(panel, label=_label)
        self.ctrl =  wx.ComboBox(panel, choices=_choices,style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.json_entry = json_entry
        self.ctrl.SetValue(const.ini_prop(json_entry, "value", category))
        self.sizer.Add(self.label,1,wx.ALL | wx.EXPAND)
        self.sizer.Add(self.ctrl,0,wx.ALL | wx.EXPAND)
    
    def GetValue(self):
        return (self.json_entry, self.ctrl.GetValue())

class InputText():
    def __init__(self, panel, _label, json_entry, category="build_settings"):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(panel, label=_label)
        self.ctrl = wx.TextCtrl(panel)
        self.json_entry = json_entry
        self.ctrl.SetValue(const.ini_prop(json_entry, "value", category))
        self.sizer.Add(self.label,1,wx.ALL | wx.EXPAND)
        self.sizer.Add(self.ctrl,0,wx.ALL | wx.EXPAND)
    
    def GetValue(self):
        return (self.json_entry, self.ctrl.GetValue())

class InputTextFile():
    def __init__(self, panel, _label, json_entry, rootdir, wildcards, title, category="build_settings"):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.StaticText(panel, label=_label)
        self.ctrl = wx.TextCtrl(panel)
        self.btn = wx.Button(panel)
        self.dirname = rootdir 
        self.panel = panel
        self.wildcards = wildcards
        self.title = title
        self.json_entry = json_entry

        self.ctrl.SetValue(const.ini_prop(json_entry, "value", category))
        self.btn.SetBitmap(wx.Bitmap(utils.get_source_img("explore.png")))
        self.btn.SetToolTip("Explore")

        hori_sizer.Add(self.ctrl,2,wx.ALL | wx.EXPAND)
        hori_sizer.Add(self.btn,0,wx.ALL | wx.EXPAND)

        self.sizer.Add(self.label,1,wx.ALL | wx.EXPAND)
        self.sizer.Add(hori_sizer,0,wx.ALL | wx.EXPAND)

        panel.Bind(wx.EVT_BUTTON, self.OnClick, self.btn)
    
    def OnClick(self, e):
        dialog = wx.FileDialog(self.panel, self.title, self.dirname, "", self.wildcards, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
            if len(filename) != 0: 
                self.ctrl.SetValue(self.dirname + os.path.sep)
        dialog.Destroy()

    def GetValue(self):
        return (self.json_entry, self.ctrl.GetValue())

class InputTextDir():
    def __init__(self, panel, _label, json_entry, rootdir, title, category="build_settings"):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.StaticText(panel, label=_label)
        self.ctrl = wx.TextCtrl(panel)
        self.btn = wx.Button(panel)
        self.dirname = rootdir 
        self.panel = panel
        self.title = title
        self.json_entry = json_entry

        self.btn.SetBitmap(wx.Bitmap(utils.get_source_img("explore.png")))
        self.btn.SetToolTip("Explore")
        self.ctrl.SetValue(const.ini_prop(json_entry, "value", category))

        hori_sizer.Add(self.ctrl,2,wx.ALL | wx.EXPAND)
        hori_sizer.Add(self.btn,0,wx.ALL)

        self.sizer.Add(self.label,1,wx.ALL | wx.EXPAND)
        self.sizer.Add(hori_sizer,0,wx.ALL | wx.EXPAND)

        panel.Bind(wx.EVT_BUTTON, self.OnClick, self.btn)
    
    def OnClick(self, e):
        dialog = wx.DirDialog(self.panel, self.title, self.dirname, wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            if len(dialog.GetPath()) != 0: 
                self.ctrl.SetValue(dialog.GetPath())
        dialog.Destroy()

    def GetValue(self):
        return (self.json_entry, self.ctrl.GetValue())

class InputList():
    def __init__(self, panel, _label, json_entry, items=None, category="build_settings"):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.StaticText(panel, label=_label)
        self.text_add = wx.TextCtrl(panel)
        self.btn_add = wx.Button(panel)
        self.btn_remove = wx.Button(panel)
        self.list = wx.ListBox(panel, style=wx.LB_MULTIPLE | wx.LB_HSCROLL, size=wx.Size(200, 100))
        self.panel = panel
        self.json_entry = json_entry
        if type(items) == list:
            self.items = items
        else:  
            self.items = const.ini_prop(json_entry, "value", category)
        

        for i in range(0, len(self.items)):
            self.list.Append(self.items[i])

        self.btn_add.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_add.png")))
        self.btn_add.SetToolTip("Add")
        self.btn_remove.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_remove.png")))
        self.btn_remove.SetToolTip("Remove")

        hori_sizer.Add(self.text_add,2,wx.ALL | wx.EXPAND)
        hori_sizer.Add(self.btn_add,0,wx.ALL)
        hori_sizer.Add(self.btn_remove,0,wx.ALL)

        self.sizer.Add(self.label,0,wx.ALL | wx.EXPAND)
        self.sizer.Add(self.list, 2, wx.ALL | wx.EXPAND)
        self.sizer.Add(hori_sizer,0,wx.ALL | wx.EXPAND)

        panel.Bind(wx.EVT_BUTTON, self.OnAdd, self.btn_add)
        panel.Bind(wx.EVT_BUTTON, self.OnRemove, self.btn_remove)
    
    def OnAdd(self, e):
        text_to_add = str(self.text_add.GetValue()).strip()
        if len(text_to_add):
            self.items.append(text_to_add)
            self.list.Append(text_to_add)
            self.text_add.SetValue("")

    def OnRemove(self, e):
        delete = [i for i in self.list.GetSelections() if self.list.IsSelected(i)]
        for i in reversed(delete):
            del self.items[i]
            self.list.Delete(i)

    def GetValue(self):
        return (self.json_entry, self.items)

class InputListFile():
    def __init__(self, panel, _label, rootdir, wildcards, title, json_entry, category="build_settings"):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        h_s = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(panel, label=_label)
        self.btn_add = wx.Button(panel)
        self.btn_remove = wx.Button(panel)
        self.list = wx.ListBox(panel, style=wx.LB_MULTIPLE | wx.LB_HSCROLL,size=wx.Size(200, 100))
        self.panel = panel
        self.json_entry = json_entry
        self.items = const.ini_prop(json_entry, "value", category)
        self.dirname = rootdir
        self.title = title
        self.wildcard = wildcards

        for i in range(0, len(self.items)):
            self.list.Append(self.items[i])

        self.btn_add.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_add.png")))
        self.btn_add.SetToolTip("Add")
        self.btn_remove.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_remove.png")))
        self.btn_remove.SetToolTip("Remove")

        buttons_sizer.Add(self.btn_add,0,wx.ALL | wx.EXPAND)
        buttons_sizer.Add(self.btn_remove,0,wx.ALL | wx.EXPAND)

        h_s.Add(self.list, 3, wx.ALL | wx.EXPAND)
        h_s.Add(buttons_sizer, 1, wx.ALL | wx.EXPAND)

        self.sizer.Add(self.label,0,wx.ALL | wx.EXPAND)
        self.sizer.Add(h_s, 2, wx.ALL | wx.EXPAND)

        panel.Bind(wx.EVT_BUTTON, self.OnAdd, self.btn_add)
        panel.Bind(wx.EVT_BUTTON, self.OnRemove, self.btn_remove)
    
    def OnAdd(self, e):
        dialog = wx.FileDialog(self.panel, self.title, self.dirname, "", self.wildcard, wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
            if len(filename) != 0: 
                self.items.append(self.dirname + os.path.sep + filename)
                self.list.Append(self.dirname + os.path.sep + filename)
        dialog.Destroy()

    def OnRemove(self, e):
        delete = [i for i in self.list.GetSelections() if self.list.IsSelected(i)]
        for i in reversed(delete):
            del self.items[i]
            self.list.Delete(i)
    
    def GetValue(self):
        return (self.json_entry, self.items)

class StringReplacerEntry():
    def __init__(self, string, type, content, oneline):
        self.string = string
        self.type = type
        self.content = content
        self.oneline = oneline
    
    def toArray(self):
        return [self.string, self.type, self.content, self.oneline]
    
    def toJSON(self):
        return (self.string, { "type" : self.type, "content": self.content, "oneline": self.oneline})

class InputList_StringReplacer():
    def __init__(self, panel, _label, items=[]):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label = wx.StaticText(panel, label=_label)
        self.btn_add = wx.Button(panel)
        self.btn_remove = wx.Button(panel)
        self.btn_save = wx.Button(panel)
        self.list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.panel = panel
        self.json_entry = "strings_to_replace"
        self.items = items

        self.list.InsertColumn(0, "String")
        self.list.InsertColumn(1, "Replace Type")
        self.list.InsertColumn(2, "Replace Content")
        self.list.InsertColumn(3, "Format to 1 line?")

        self.list.SetColumnWidth(2, 150)

        for i in range(0, len(self.items)):
            self.list.Append(self.items[i].toArray())

        self.btn_add.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_add.png")))
        self.btn_add.SetToolTip("Add")
        self.btn_save.SetBitmap(wx.Bitmap(utils.get_source_img("edit.png")))
        self.btn_save.SetToolTip("Overwrite")
        self.btn_remove.SetBitmap(wx.Bitmap(utils.get_source_img("pwad_remove.png")))
        self.btn_remove.SetToolTip("Remove")

        sc = wx.BoxSizer(wx.VERTICAL)
        sl = wx.BoxSizer(wx.VERTICAL)
        sf = wx.BoxSizer(wx.HORIZONTAL)

        self.string = wx.TextCtrl(panel)
        self.type = wx.ComboBox(panel, choices=["label", "tag", "file" ,"date"],style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.content = wx.TextCtrl(panel)
        self.oneline = wx.CheckBox(panel)
        self.oneline.SetToolTip("This works only for file types.")

        sl.AddMany([(wx.StaticText(panel, label="String"), 0, wx.BOTTOM , 10), 
                    (wx.StaticText(panel, label="Type"), 0,wx.TOP | wx.BOTTOM, 8), 
                    (wx.StaticText(panel, label="Content"),0, wx.TOP | wx.BOTTOM , 8), 
                    (wx.StaticText(panel, label="Inline Format?"), 0, wx.TOP , 10)])
        
        sc.AddMany([(self.string, 0,  wx.ALL | wx.EXPAND, 5),
                    (self.type, 0,  wx.ALL | wx.EXPAND, 5),
                    (self.content, 0, wx.ALL | wx.EXPAND, 5),
                    (self.oneline, 0,  wx.ALL | wx.EXPAND, 5)])


        sf.Add(sl, 1, wx.LEFT | wx.TOP, 5)
        sf.Add(sc, 3, wx.ALL | wx.EXPAND, 0)

        hori_sizer.Add(self.btn_add,1,wx.ALL | wx.EXPAND)
        hori_sizer.Add(self.btn_save,1,wx.ALL | wx.EXPAND)
        hori_sizer.Add(self.btn_remove,1,wx.ALL | wx.EXPAND)

        self.sizer.Add(self.label,0,wx.ALL | wx.EXPAND)
        self.sizer.Add(self.list, 1, wx.ALL | wx.EXPAND)
        self.sizer.Add(hori_sizer,0,wx.ALL | wx.EXPAND)
        self.sizer.Add(wx.StaticText(panel, label="Double click to a list element to copy the properties."), 0, wx.ALL | wx.EXPAND)
        self.sizer.Add(sf,0, wx.CENTER | wx.ALL, 10)

        panel.Bind(wx.EVT_BUTTON, self.OnAdd, self.btn_add)
        panel.Bind(wx.EVT_BUTTON, self.OnSave, self.btn_save)
        panel.Bind(wx.EVT_BUTTON, self.OnRemove, self.btn_remove)
        panel.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEdit, self.list)
    
    def GetValue(self):
        json_stuff = {}
        for j in self.items:
            value = j.toJSON()
            json_stuff[value[0]] = value[1]

        return (self.json_entry, json_stuff)

    def OnAdd(self, e):
        data = [self.string.GetValue(), self.type.GetValue(), self.content.GetValue(), self.oneline.GetValue()]
        if len(data[0]) != 0:
            self.list.Append(data)
            self.items.append(StringReplacerEntry(data[0], data[1], data[2], data[3]))
            self.string.SetValue("")
            self.type.SetValue("")
            self.content.SetValue("")
            self.oneline.SetValue(False)

    def OnSave(self, e):
        data = [self.string.GetValue(), self.type.GetValue(), self.content.GetValue(), "True" if self.oneline.GetValue() else "False"]
        selected = self.list.GetFirstSelected()
        if len(data[0]) != 0 and selected != -1:
            selected = self.list.GetFirstSelected()
            self.items[selected] = StringReplacerEntry(data[0], data[1], data[2], data[3] == "True")
            self.list.SetItem(selected, 0, data[0])
            self.list.SetItem(selected, 1, data[1])
            self.list.SetItem(selected, 2, data[2])
            self.list.SetItem(selected, 3, data[3])
            self.string.SetValue("")
            self.type.SetValue("")
            self.content.SetValue("")
            self.oneline.SetValue(False)

    def OnEdit(self, e):
        selected = self.list.GetFirstSelected()
        if selected != -1:
            self.string.SetValue(self.list.GetItem(selected, 0).GetText())
            self.type.SetValue(self.list.GetItem(selected, 1).GetText())
            self.content.SetValue(self.list.GetItem(selected, 2).GetText())
            self.oneline.SetValue(self.list.GetItem(selected, 3).GetText() == "True")

    def OnRemove(self, e):
        selected = self.list.GetFirstSelected()
        if selected != -1:
            self.list.DeleteItem(selected)
            del self.items[selected]
