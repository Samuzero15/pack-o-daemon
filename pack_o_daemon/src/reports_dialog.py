
import os
import wx
import wx.stc as stc
import mimetypes
from pathlib import Path
import collections
from typing import Union

try:
    import src.constants as c
    import src.funs_n_cons_2 as utils
    import src.result_dialog as rd
    from src.zdoom_ednums import Zdoom_EdNums
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.constants as c
    import pack_o_daemon.src.funs_n_cons_2 as utils
    import pack_o_daemon.src.result_dialog as rd
    from pack_o_daemon.src.zdoom_ednums import Zdoom_EdNums


class ReportsDialog(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)
        self.main = frame
        cont = wx.BoxSizer(wx.VERTICAL)

        btn_reportactors = wx.Button(self, label="Actors List")
        btn_reportdoomednums = wx.Button(self, label="DoomEdNums List")
        btn_reportfiledirstruct = wx.Button(self, label="Directory Structure")
        btn_reportfilecount = wx.Button(self, label="File Count")
        btn_report_doomednumcmp_doom = wx.Button(self, label="Doom")
        btn_report_doomednumcmp_doom2 = wx.Button(self, label="Doom 2")
        btn_report_doomednumcmp_heretic = wx.Button(self, label="Heretic")
        btn_report_doomednumcmp_hexen = wx.Button(self, label="Hexen")
        btn_report_doomednumcmp_strife = wx.Button(self, label="Strife")
        btn_report_doomednumcmp_chex = wx.Button(self, label="Chex Quest")

        doomednum_btn_sizer = wx.GridSizer(2, 0, 0)

        doomednum_btn_sizer.AddMany([
            (btn_report_doomednumcmp_doom, 0, wx.ALL | wx.EXPAND, 1),
            (btn_report_doomednumcmp_doom2, 0, wx.ALL | wx.EXPAND, 1),
            (btn_report_doomednumcmp_heretic, 0, wx.ALL | wx.EXPAND, 1),
            (btn_report_doomednumcmp_hexen, 0, wx.ALL | wx.EXPAND, 1),
            (btn_report_doomednumcmp_strife, 0, wx.ALL | wx.EXPAND, 1),
            (btn_report_doomednumcmp_chex, 0, wx.ALL | wx.EXPAND, 1)
        ])

        text = wx.StaticText(parent, label="Compare IWAD's DoomEdNums")
        cont.AddMany([
            (btn_reportactors, 0, wx.ALL | wx.EXPAND, 1),
            (btn_reportdoomednums, 0, wx.ALL | wx.EXPAND, 1),
            (btn_reportfiledirstruct, 0, wx.ALL | wx.EXPAND, 1),
            (btn_reportfilecount, 0, wx.ALL | wx.EXPAND, 1)
        ])
        cont.Add(text, 0, wx.ALL | wx.EXPAND, 1)
        cont.Add(doomednum_btn_sizer, 0, wx.ALL | wx.EXPAND, 1)
        

        self.Bind(wx.EVT_BUTTON, self.OnReportActors, btn_reportactors)
        self.Bind(wx.EVT_BUTTON, self.OnReportDoomednums, btn_reportdoomednums)
        self.Bind(wx.EVT_BUTTON, self.OnReportFileDirectoryStructure, btn_reportfiledirstruct)
        self.Bind(wx.EVT_BUTTON, self.OnReportFileCount, btn_reportfilecount)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Doom": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_doom)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Doom 2": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_doom2)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Heretic": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_heretic)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Hexen": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_hexen)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Strife": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_strife)
        self.Bind(wx.EVT_BUTTON, lambda evt, temp="Chex Quest": self.OnCompareReplacements(evt, temp), btn_report_doomednumcmp_chex)

        self.SetSizerAndFit(cont)
    
    def OnCompareReplacements(self, event, iwad_doomednums):
        reportdata = ""
        data = ""
        parts_actors = []
        title = "Here it is the results of the actor replacements for the project."
        for part in self.main.projectparts:
            dir_path = os.path.join(part.rootdir, part.sourcedir)
            utils.ActorList = []
            utils.Decorate_searchForActors(dir_path)
            parts_actors.extend(utils.ActorList)
        
        replaced_actors = []
        for doomednum, iwad_actor in Zdoom_EdNums[iwad_doomednums].items():
            for actor in parts_actors:
                if(actor["doomednum"] == doomednum or actor["replaces"] == iwad_actor):
                    replaced_actors.append({"doomEdNum": doomednum, "original": iwad_actor, "replaced_by": actor["actor"]})
        
        
        data = "///////////////////// Actors replaced in a "+iwad_doomednums+" Mod //////////////////////////\n"
        if (len(replaced_actors) == 0): data += "No replaced actors detected."
        else:
            for rep_actor in replaced_actors:
                data += "("+ (str)(rep_actor["doomEdNum"]) +")> " + rep_actor["original"] + " replaced by " + rep_actor["replaced_by"] + "\n"
        reportdata += data 
        rd.ResultDialog(self.main, title, reportdata).ShowModal()

    def count_files_by_extension(self, directory_path: Union[str, Path],include_subdirectories=False) -> dict:
        """Counts the different extensions of all directory files (optionally
        includes files from subdirectories too). Returns a dictionary with keys
        for file extensions and values for extension count."""
        if include_subdirectories:
            directory_files = Path(directory_path).rglob("*")
        else:
            directory_files = Path(directory_path).glob("*")
        all_suffixes = [''.join(file_path.suffixes) for file_path in directory_files
                        if file_path.is_file() and file_path.suffix]
        return collections.Counter(all_suffixes)

    def OnReportFileCount(self, event):
        reportdata = ""
        title = "Here it is the file count of the project."
        for part in self.main.projectparts:
            dir_path = os.path.join(part.rootdir, part.sourcedir)
            count = 0
            data = ""
            for path, dirs, files in os.walk (dir_path):
                for file in files:
                    count += 1
            data += "Files in " + part.name + " : " + ((str)(count)) + " files.\n"

            ext_counts = self.count_files_by_extension(dir_path, True)
            for extension, count in ext_counts.items():
                data += f"'{extension}': {count} files.\n"

            reportdata = reportdata + data 
        rd.ResultDialog(self.main, title, reportdata).ShowModal()

    def OnReportFileDirectoryStructure(self, event):
        reportdata = ""
        title = "Here it is the file structure of the project."
        header = "File Directory Structure"
        for part in self.main.projectparts:
            dir_path = os.path.join(part.rootdir, part.sourcedir)
            data = ""
            data = "///////////////////// "+ header +" ON "+ part.name +" START //////////////////////////\n"
            for path, dirs, files in os.walk (dir_path):
                for file in files:
                    path_file = os.path.join(path, file)
                    path_file = path_file.replace(os.path.join(self.main.rootdir, c.ini_prop(const.JSON_BUILDSETS_BUILDDIR, section=c.JSON_BUILDSETS)), "...")
                    
                    data+= path_file + "\n"
            data += "///////////////////// "+ header +" ON "+ part.name +" END //////////////////////////"
            reportdata = reportdata + data 
        rd.ResultDialog(self.main, title, reportdata).ShowModal()

    def OnReportDoomednums(self, event):
        reportdata = ""
        title = "Here it is a list of DoomEdNums in the current project."
        header = "DoomEdNum List"
        for part in self.main.projectparts:
            dir_path = os.path.join(part.rootdir, part.sourcedir)
            utils.ActorList = []
            count = 0
            utils.Decorate_searchForActors(dir_path)
            utils.ActorList = list({v['actor']:v for v in utils.ActorList}.values())

            data = "///////////////////// "+ header +" ON "+ part.name +" START //////////////////////////\n"
            if len(utils.ActorList) == 0: 
                data += "No Actors or Classes with DoomEdNums detected.\n"
                data += "///////////////////// "+ header +" ON "+ part.name +" END //////////////////////////"
                reportdata = reportdata + data 
                continue

            utils.ActorList.sort(key=lambda x: x["doomednum"])
            for actor in utils.ActorList:
                if(actor["doomednum"] > 0 ): data += utils.Decorate_ActorDoomEdNum(actor) + "\n"
            data += "///////////////////// "+ header +" ON "+ part.name +" END //////////////////////////"
            reportdata = reportdata + data 
        os.chdir(self.main.rootdir)
        rd.ResultDialog(self.main, title, reportdata).ShowModal()

    def OnReportActors(self, event):
        reportdata = ""
        title = "Here it is a list of actors separated by files in the current project."
        header = "Actor List"
        for part in self.main.projectparts:
            dir_path = os.path.join(part.rootdir, part.sourcedir)
            utils.ActorList = []
            count = 0
            utils.Decorate_searchForActors(dir_path)
            utils.ActorList = list({v['actor']:v for v in utils.ActorList}.values())
            data = "///////////////////// "+ header +" ON "+ part.name +" START //////////////////////////\n"

            if len(utils.ActorList) == 0: 
                data += "No Actors or Classes detected.\n"
                data += "///////////////////// "+ header +" ON "+ part.name +" END //////////////////////////"
                reportdata = reportdata + data 
                continue

            utils.ActorList.sort(key=lambda x: x["doomednum"])
            lastfile = ""
            for actor in utils.ActorList:
                if(lastfile != (actor["path"] + "\\" + actor["file"])):
                    lastfile = actor["path"] + "\\" + actor["file"]
                    data += "\nIn: '" + lastfile + "'\n"
                data += utils.Decorate_ActorToString(actor) + "\n"
            data += "///////////////////// "+ header +" ON "+ part.name +" END //////////////////////////"
            reportdata = reportdata + data 
        os.chdir(self.main.rootdir)
        rd.ResultDialog(self.main, title, reportdata).ShowModal()
