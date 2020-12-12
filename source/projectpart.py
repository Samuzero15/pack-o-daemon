import wx
import os
import source.threads as br
import source.funs_n_cons_2 as utils
import source.constants as const

from configparser import ConfigParser

class ProjectPart():
    def __init__(self, name, rootdir):
        
        self.name           = name
        self.rootdir        = rootdir
        self.version        = const.ini_prop("relase",            "v0",     name)
        self.filename       = const.ini_prop("filename",          name,     name)
        self.acscomp        = const.ini_prop("acscomp",             section=name)
        self.sourcedir      = const.ini_prop("sourcedir",         "src",    name)
        self.distdir        = const.ini_prop("distdir",           "dist",   name)
        self.notxt          = const.ini_prop("notxt",               section=name)
        self.skip           = False
    
    
    def GetExpectedPWADS(self, versioned):
        expectfilename = ""
        pwad = []
        if not self.notxt:
            if versioned: expectfilename = self.filename + "_" + self.version + ".pk3"
            else:              expectfilename = self.filename + "_DEV.pk3"
        else: expectfilename = self.filename + ".pk3"
        fullpath = os.path.join(self.rootdir, os.path.join(self.distdir, expectfilename))
        pwad = [utils.get_file_name(fullpath),utils.get_file_dir(fullpath)]
        return pwad
    
    def BuildPart(self, thread, versioned, noacs, current, total):
        output = (0, [])
        # Get the data from the section...
        relase     = self.version
        sourceDir  = self.sourcedir
        distDir    = self.distdir
        fileName   = self.filename
        notxt      = self.notxt
        compileacs = self.acscomp
        rootdir    = self.rootdir
        
        destPath = os.path.join(distDir, fileName)
                
        # Check the flags.
        if (self.skip):
            thread.ui.AddToLog(self.name + " part excluded.")
            output = (0, [])
            return output
        
        # First compile (If the part contains any acs script.)
        res = 0;
        thread.ui.AddToLog("\n({1}/{2})\t\t=== Building {0} === ".format(self.name, current, total));
        if(noacs):
            thread.ui.AddToLog("ACS Compilation skipped")
        elif(compileacs):
            res = utils.acs_compile(thread, self)
            
        # Check if the cancel button is called.
        if thread.abort or res == -1:
            if thread.abort:  fail_reason = br.BUILD_CANCELED
            else:             fail_reason = br.BUILD_ERROR
            output = (fail_reason, [])
            os.chdir(rootdir)
            return output
        
        # After compiling, zip them all.
        # The path does'nt exist? Create it!
        target_path = os.path.join(rootdir, distDir)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
            thread.ui.AddToLog(target_path + " directory created.")
        
        zip = utils.makepkg(thread, sourceDir, destPath, notxt, versioned)
        # Check if the cancel button is called.
        if thread.abort or zip == None:
            if thread.abort:  fail_reason = br.BUILD_CANCELED
            else:             fail_reason = br.BUILD_ERROR
            
            output = (fail_reason, [])
            if(zip is not None): zip.close()
            os.chdir(rootdir)
            return output
        
        files = []
        
        # Versionify if the flag is called.
        if versioned:
            out = utils.make_dist_version(thread, zip, rootdir, sourceDir, destPath, relase, notxt)
            files = out[1]
            if thread.abort or out[0] == -1:
                if thread.abort:  fail_reason = br.BUILD_CANCELED
                else:             fail_reason = br.BUILD_ERROR
                os.chdir(rootdir)
                output = (fail_reason, [])
                return output
        else: 
            zip.close()
            files = utils.makever(thread.ui, "DEV", rootdir, destPath, notxt)
        
        # Part finished! Start the next one.
        output = (0, files)
        
        thread.ui.AddToLog("({1}/{2})\t\t=== {0} finished ===\n".format(self.name, current, total));
        
        return output