
import json
import wx

try:
    import src.constants as const
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.constants as const

command_data = []

class ExecuteDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Execute commands", size=(600, 300))
        self.parent = parent
        panel = wx.Panel(self)

        self.listcmd = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        btn_add = wx.Button(panel, label="Add")
        btn_remove = wx.Button(panel, label="Remove")
        btn_executecmd = wx.Button(panel, label="Execute")
        btn_savecmds = wx.Button(panel, label="Save")
        btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.listcmd.InsertColumn(0, "Name")
        self.listcmd.InsertColumn(1, "Command")
        self.listcmd.SetColumnWidth(0, 100)
        self.listcmd.SetColumnWidth(1, 400)

        f = open(const.PROJECT_FILE, "r")
        project_json = json.load(f)
        f.close()

        try:
            if(not len(project_json[const.JSON_CMDEXE]) == 0):
                for cmd in project_json[const.JSON_CMDEXE]:
                    self.listcmd.Append([cmd[const.JSON_CMDEXE_NAME], cmd[const.JSON_CMDEXE_CMD]])
        except KeyError:
            pass

        btns_sizer.Add(btn_add, 1, wx.CENTER, 0)
        btns_sizer.Add(btn_remove, 1, wx.CENTER, 0)
        btns_sizer.Add(btn_executecmd, 1, wx.CENTER, 0)
        btns_sizer.Add(btn_savecmds, 1, wx.CENTER, 0)

        panel.Bind(wx.EVT_BUTTON, self.OnAdd, btn_add)
        panel.Bind(wx.EVT_BUTTON, self.OnRemove, btn_remove)
        panel.Bind(wx.EVT_BUTTON, self.OnSave, btn_savecmds)
        panel.Bind(wx.EVT_BUTTON, self.OnExecute, btn_executecmd)
       
        cont = wx.BoxSizer(wx.VERTICAL)
        cont.Add(self.listcmd, 3, wx.ALL, 5)
        cont.Add(btns_sizer, 1, wx.CENTER, 5)
        panel.SetSizerAndFit(cont)
    
    def OnExecute(self, event):
        selected_item = self.listcmd.GetFirstSelected() 
        if(selected_item != -1):
            command = self.listcmd.GetItem(selected_item, 1).GetText()
            wx.Execute(command, flags=wx.EXEC_ASYNC | wx.EXEC_SHOW_CONSOLE, callback=None, env=None)
        else:
            wx.MessageDialog(None, "Select a command to execute in the list", "Select something first!").ShowModal()
    
    def OnRemove(self, event):
        selected_item = self.listcmd.GetFirstSelected() 
        if(selected_item != -1):
            self.listcmd.DeleteItem(selected_item)
        else:
            wx.MessageDialog(None, "Select a command to delete in the list", "Select something first!").ShowModal()
    
    def OnSave(self, event):
        json_cmd_list = []
        for i in range(0, self.listcmd.GetItemCount()):
            json_cmd = {const.JSON_CMDEXE_NAME : self.listcmd.GetItem(i, 0).GetText(), const.JSON_CMDEXE_CMD : self.listcmd.GetItem(i, 1).GetText()}
            json_cmd_list.append(json_cmd)
        
        f = open(const.PROJECT_FILE, "r")
        project_json = json.load(f)
        f.close()

        project_json[const.JSON_CMDEXE] = json_cmd_list

        f = open(const.PROJECT_FILE, "w")
        json.dump(project_json, f, indent=4)
        f.close()
        wx.MessageDialog(None, "The commands are saved in the " + const.PROJECT_FILE + " file.", "Commands Saved!").ShowModal()

    def OnAdd(self, event):
        dialog = ExecuteDialog_AddCommand(self)
        dialog.ShowModal()
        command_data = [dialog.txt_name.GetValue(), dialog.txt_cmd.GetValue()]
        if(len(command_data[0])> 0 and len(command_data[1])> 0):
            self.listcmd.Append(command_data)
    
class ExecuteDialog_AddCommand(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Add a new Execute command", size=(320, 250))
        self.parent = parent
        # self.panel = wx.Panel(self, size=(300, 300))
        main_cont = wx.BoxSizer(wx.VERTICAL)
        cont = wx.BoxSizer(wx.VERTICAL)
        self.txt_name = wx.TextCtrl(self, size=(200, 25))
        self.txt_cmd = wx.TextCtrl(self, size=(200, 100), style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        btn_add = wx.Button(self, label="Add Command")

        self.Bind(wx.EVT_BUTTON, self.OnAdd, btn_add)

        cont.Add(wx.StaticText(self,label="Name"), 1, wx.CENTER | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        cont.Add(self.txt_name, 1, wx.CENTER | wx.LEFT | wx.RIGHT, 5)
        cont.Add(wx.StaticText(self,label="CMD"), 1, wx.CENTER | wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        cont.Add(self.txt_cmd, 1, wx.CENTER | wx.LEFT | wx.RIGHT, 5)
        cont.Add(btn_add, 2, wx.CENTER | wx.LEFT | wx.RIGHT, 10)
        self.SetSizer(cont)
    	
    	
    def OnAdd(self, event):
        self.Close()
