import wx
import wx.stc as stc
import source.constants as c

class ResultDialog(wx.Dialog):
    def __init__(self, parent, header, results, _title="Results"):
        wx.Dialog.__init__(self, parent, title=_title, size=(450, 500))
        self.Centre()
        
        cont = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self);
        label = wx.StaticText(panel, label=header)
        self.txt = stc.StyledTextCtrl(panel)
        btn = wx.Button(panel, label=c.get_accept_msg())
        self.wrap = wx.CheckBox(panel, label="W. Wrap")
        
        self.txt.SetText(results)
        self.txt.SetReadOnly(True)
        font = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.txt.StyleSetFont(0, font)
        
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        self.Bind(wx.EVT_CHECKBOX, self.OnWrap, self.wrap)
        
        cont.Add(label, 0, wx.ALL, 2)
        cont.Add(self.txt, 2, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        cont.Add(self.wrap, 0, wx.ALL | wx.CENTER, 1)
        cont.Add(btn, 0, wx.CENTER | wx.ALL, 5)
        panel.SetSizerAndFit(cont)
    
    def OnClick(self, event):
        self.Close();
    
    def OnWrap(self, event):
        self.txt.SetWrapMode(self.wrap.GetValue())

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
        
        
        # txt = wx.TextCtrl(panel, value="Yeet", size=(250,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        
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
    
    