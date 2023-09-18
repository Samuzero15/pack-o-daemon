""" All the needed threads to let the program not freeze as the typical asshole """
import wx
import os
import threading
import subprocess
import time
import pack_o_daemon.src.funs_n_cons_2 as utils
import pack_o_daemon.src.result_dialog as rd
import zipfile
import pack_o_daemon.src.constants as const

# Define notification event for thread completion
EVT_BUILDRESULT_ID = wx.NewId()
EVT_PLAYRESULT_ID = wx.NewId()
EVT_STATUSMESSAGE_ID = wx.NewId()

# Some extra constants.
BUILD_SUCCESS = 1
BUILD_CANCELED = 0
BUILD_ERROR = -1
BUILD_SKIPPED = -2

def EVT_BUILDRESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_BUILDRESULT_ID, func)
    
def EVT_PLAYRESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_PLAYRESULT_ID, func)

def EVT_STATUSMESSAGE(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_STATUSMESSAGE_ID, func)

class StatusBarEvent(wx.PyEvent):
    def __init__(self, data, order=0):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_STATUSMESSAGE_ID)
        self.data = data
        self.order = order

class BuildResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_BUILDRESULT_ID)
        self.data = data

class BuildProject(threading.Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        
        self.ui = notify_window
        self.abort = False
        self.start()
        

    def run(self):
        """Run Worker Thread."""
        
        # First for all, check the main flags
        noacs = self.ui.flags[const.BFLAG_SKIPACSCOMP].GetValue();
        versioned = self.ui.flags[const.BFLAG_MAKEVERSION].GetValue();
        packed = self.ui.flags[const.BFLAG_PACKPROJECT].GetValue();
        snapshot = self.ui.flags[const.BFLAG_SNAPSHOTVER].GetValue();
        
        
        # Make sure you're on the working directory where you will start the build.
        rootdir = self.ui.rootdir
        # print("Root dir: " + rootdir)
        #print("My root dir is: " + rootdir)
        os.chdir(rootdir)
        
        parts = self.ui.projectparts
        
        current = 1
        total = len(parts)
        
        for part in parts:
            if part.skip: total -= 1
        
        if total == 0: 
         wx.PostEvent(self.ui, BuildResultEvent(BUILD_SKIPPED))
         return
        
        output = (0,[])
        files_to_pack = []
        # Good, now start.
        
        for part in parts:
            # print("execute script!")
            output = part.BuildPart(self, versioned, noacs, snapshot, current, total)
            if not part.skip: current += 1
            if output[0] != 0 or self.abort:
                wx.PostEvent(self.ui, BuildResultEvent(output[0]))
                return
            files_to_pack.extend(output[1]);
            
        # Files are built, now, we should pack them if flagged to do so.
        
        if packed:
            
            os.chdir(rootdir)
            
            distDir  = const.ini_prop('zip_dir',  'dist\packed');
            filename = const.ini_prop('name', 'project');

            distDir = os.path.join(const.ini_prop('build_dir',  rootdir), distDir)
            
            if not os.path.exists(distDir):
                os.mkdir(distDir)
                msg = distDir + " directory created to allocate the packed projects."
                wx.PostEvent(self.ui, StatusBarEvent(msg))
                # self.ui.AddToLog(distDir + " directory created to allocate the packed projects.")
                    
            if versioned: 
                if snapshot : filename += "_" + self.ui.snapshot_tag + '.zip'
                else        : filename += "_" + const.ini_prop('tag','v0') + '.zip'
            else        : filename += "_" + "DEV" + '.zip'
            
            
            destination = os.path.join(distDir, filename)
            distzip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
            current = 1
            for file in files_to_pack:
                if self.abort: distzip.close(); return None
                os.chdir(file[0])
                distzip.write(file[1])
                utils.printProgress (self, current, len(files_to_pack), 'Packed: ', 'files. (' + file[1] + ')')
                current += 1
                
            distzip.close()
            # self.ui.AddToLog("{0} Packed up Sucessfully".format(filename))
            msg = "{0} Packed up Sucessfully".format(filename)
            wx.PostEvent(self.ui, StatusBarEvent(msg))
            # print(file_list)
        
        os.chdir(rootdir)
        wx.PostEvent(self.ui, BuildResultEvent(BUILD_SUCCESS))

    def call_abort(self):
        self.abort = True

class PlayResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PLAYRESULT_ID)
        self.data = data

class PlayProject(threading.Thread):
    """This thread will just run the project! """
    def __init__(self, notify_window, sourceport, iwad, test_map, ex_params, pwads):
        threading.Thread.__init__(self)
        self.ui = notify_window
        self.sourceport = sourceport
        self.iwad       = iwad
        self.test_map   = test_map
        self.ex_params  = ex_params
        self.pwads      = pwads
        self.start()

    def run(self):
        
        exe_path = os.path.dirname(utils.relativePath(self.sourceport))
        iwad_path = utils.relativePath(self.iwad)
        sourceport_path = utils.relativePath(self.sourceport)
        
        if exe_path == '?' or not os.path.isdir(exe_path): 
            msg = "Could'nt find " + self.sourceport
            msg += "\nCheck the path in the "+const.PROJECT_FILE+", override sourceport_path, and try again."
            dlg = wx.MessageDialog(self.ui, msg, "Running error").ShowModal()
            return
        
        os.chdir(exe_path)
        
        pwadlist = []
        for pwad in self.pwads:
            pwadlist.extend(["-file"] + [os.path.join(pwad[1], pwad[0])])
            # -stdout
        
        fullcmd     = [sourceport_path, "-iwad", iwad_path, '+map', self.test_map] + pwadlist + self.ex_params.split() + ["-stdout"]
        
        """
        fullcmd     = ["zandronum.exe", "-iwad", "doom2.wad" , "-file", std_path]
        subprocess.call(fullcmd+ filelist + ['+map', map_test])
        """
        # print(fullcmd)
        p = subprocess.Popen(fullcmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        out, err = p.communicate()
            
        os.chdir(self.ui.rootdir)
        wx.PostEvent(self.ui, PlayResultEvent(out.decode("ansi")))
        
        
