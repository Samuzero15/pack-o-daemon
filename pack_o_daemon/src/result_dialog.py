import os
import wx
import wx.stc as stc
import datetime
try:
    import src.constants as c
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.constants as c

class ResultDialog(wx.Dialog):
    def __init__(self, parent, header, results, filename="pack-o-daemon_log.txt", _title="Results", ):
        wx.Dialog.__init__(self, parent, title=_title, size=(450, 500))
        self.Centre()
        
        cont = wx.BoxSizer(wx.VERTICAL)
        cont_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = wx.Panel(self)
        label = wx.StaticText(panel, label=header)
        self.txt = stc.StyledTextCtrl(panel)
        btn = wx.Button(panel, label=c.get_accept_msg())
        btn_copy = wx.Button(panel, label="Copy to clipboard")
        btn_save = wx.Button(panel, label="Save to File")
        self.wrap = wx.CheckBox(panel, label="W. Wrap")
        self.filename = filename
        self.txt.SetText(results)
        self.txt.SetReadOnly(True)
        font = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.txt.StyleSetFont(0, font)

        cont_btn.Add(btn, 0, wx.CENTER | wx.ALL, 5)
        cont_btn.Add(btn_copy, 0, wx.CENTER | wx.ALL, 5)
        cont_btn.Add(btn_save, 0, wx.CENTER | wx.ALL, 5)
        
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        self.Bind(wx.EVT_BUTTON, self.onCopy, btn_copy)
        self.Bind(wx.EVT_BUTTON, self.onSave, btn_save)
        self.Bind(wx.EVT_CHECKBOX, self.OnWrap, self.wrap)
        
        cont.Add(label, 0, wx.ALL, 2)
        cont.Add(self.txt, 2, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        cont.Add(self.wrap, 0, wx.ALL | wx.CENTER, 1)
        cont.Add(cont_btn, 0, wx.CENTER | wx.ALL, 5)
        panel.SetSizerAndFit(cont)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_ALT | wx.ACCEL_SHIFT,  ord('c'), btn_copy.GetId()),
            (wx.ACCEL_ALT | wx.ACCEL_SHIFT,  ord('s'), btn_save.GetId()),
            (wx.ACCEL_NORMAL,  wx.WXK_RETURN, btn.GetId()),
        ])
        self.SetAcceleratorTable(accel_tbl)
    
    def OnClick(self, event):
        self.Close();
    
    def OnWrap(self, event):
        self.txt.SetWrapMode(self.wrap.GetValue())

    def onCopy(self, event):
        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText(self.txt.GetValue())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.dataObj)
            wx.TheClipboard.Close()
            wx.MessageBox("Results Copied to the clipboard!", "Copied!")
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")
            
    def onSave(self, event):
        try:
            dlg = wx.FileDialog(self, "Save to file:", ".", self.filename, "Text (*.txt)|*.txt", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if (dlg.ShowModal() == wx.ID_OK):
                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()
                f = open(os.path.join(self.dirname, self.filename), 'w')
                f.write(self.txt.GetValue())
                f.close()
                wx.MessageBox("Results saved in "+os.path.join(self.dirname, self.filename)+"!", "Saved!")
            dlg.Destroy()
        except:
            print("fuck")


class TabText(wx.Panel):
    def __init__(self, parent, title, text):
        wx.Panel.__init__(self, parent)
        cont = wx.BoxSizer(wx.VERTICAL)
        
        self.title =    title[title.find("[")+1:title.find("]")]
        self.ver =      title[title.find("#")+3:title.find("[")]
        self.text =     text.replace("\t* ", "*) ").replace("\n", "\n\n")
        
        t1 = wx.StaticText(self, label=self.title)
        t2 = wx.TextCtrl(self, value=self.text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        font2 = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        t1.SetFont(font1)
        t2.SetFont(font2)
        cont.Add(t1, 0, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        cont.Add(t2, 2, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        self.SetSizer(cont)
        

class ChangelogDialog(wx.Dialog):
    def __init__(self, parent, tab_data):
        self.parent = parent
        wx.Dialog.__init__(self, parent, title="Patch Notes", size=(400, 400))
        
        # print(tab_data)
        # print(tab_data[0])
        panel = wx.Panel(self);
        cont = wx.BoxSizer(wx.VERTICAL)
        
        btn = wx.Button(panel, label=c.get_funny_msg())
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        
        nb = wx.Notebook(panel)
        for data in tab_data:
            tab = TabText(nb, data[0], data[1])
            nb.AddPage(tab, tab.ver)
        
        cont.Add(nb, 2, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        cont.Add(btn, 0, wx.SOUTH | wx.CENTER, 10)
        panel.SetSizer(cont)
        self.Centre()
    
    def OnClick(self, event):
        self.Close();

class ACSErrorDialog(wx.Dialog):
    def __init__(self, parent, results, _title="ACS Output"):
        wx.Dialog.__init__(self, parent, title=_title, size=(400, 300))
        self.parent = parent
        self.result = 0
        self.Centre()
        
        cont = wx.BoxSizer(wx.VERTICAL)
        btns = wx.BoxSizer(wx.HORIZONTAL)
        
        panel = wx.Panel(self);
        txt = wx.TextCtrl(panel, value=results, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        txt.SetFont(font)
        btn1 = wx.Button(panel, label="Retry")
        btn2 = wx.Button(panel, label="Abort")
        
        self.Bind(wx.EVT_BUTTON, self.OnRetry, btn1)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, btn2)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        btns.Add(btn1, 0, wx.CENTER | wx.ALL, 2)
        btns.Add(btn2, 0, wx.CENTER | wx.ALL, 2)
        
        cont.Add(txt, 1, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        cont.Add(btns, 0, wx.CENTER | wx.ALL, 5)
        panel.SetSizerAndFit(cont)
    
    def OnRetry(self, event):
        self.parent.response = 1
        self.Close();
    
    def OnAbort(self, event):
        self.parent.response = 0
        self.Close();
    
    def OnClose(self, event):
        if(self.parent.response == -1): self.parent.response = 0
        self.Destroy()
    
    
