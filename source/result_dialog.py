import wx
import wx.stc as stc
from random import randint

class ResultDialog(wx.Dialog):
    def __init__(self, parent, header, results, _title="Results"):
        wx.Dialog.__init__(self, parent, title=_title, size=(450, 500))
        self.Centre()
        
        cont = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self);
        label = wx.StaticText(panel, label=header)
        self.txt = stc.StyledTextCtrl(panel)
        btn = wx.Button(panel, label="Alright, got it, thanks.")
        self.wrap = wx.CheckBox(panel, label="W. Wrap")
        
        self.txt.SetText(results)
        self.txt.SetReadOnly(True)
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
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

class MSGDialog(wx.Dialog):
    def __init__(self, parent, msg, _title):
        self.parent = parent
        wx.Dialog.__init__(self, parent, title=_title, size=(300, 250))
        
        cont = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self);
        txt = wx.TextCtrl(panel, value=msg, size=(250,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        funny_msgs = [
            "Okie-Dokie",
            "Iz Nice",
            "Sexelent!",
            "*Aproval Hisses*",
            "Good Stuff",
            "Cool",
            "Not bad",
            "EPIC",
            "What?",
            "UwU",
            "AAAAAAAA",
            "Why are you reading this?"
        ]
        
        btn = wx.Button(panel, label=funny_msgs[randint(0, len(funny_msgs)-1)])
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        
        cont.Add(txt, 2, wx.CENTER | wx.EXPAND | wx.ALL, 10)
        cont.Add(btn, 0, wx.CENTER | wx.ALL, 5)
        panel.SetSizerAndFit(cont)
        self.Fit()
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
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
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
    
    