import wx

class ResultDialog(wx.Dialog):
    def __init__(self, parent, header, results, _title="Results"):
        wx.Dialog.__init__(self, parent, title=_title, size=(450, 500))
        self.Centre()
        
        cont = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self);
        label = wx.StaticText(panel, label=header)
        txt = wx.TextCtrl(panel, value=results, style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.TE_READONLY)
        btn = wx.Button(panel, label="Alright, got it, thanks.")
        
        self.Bind(wx.EVT_BUTTON, self.OnClick, btn)
        
        cont.Add(label, 0, wx.ALL, 2)
        cont.Add(txt, 2, wx.ALL | wx.EXPAND | wx.CENTER, 4)
        cont.Add(btn, 0, wx.CENTER | wx.ALL, 2)
        panel.SetSizerAndFit(cont)
    
    def OnClick(self, event):
        self.Close();