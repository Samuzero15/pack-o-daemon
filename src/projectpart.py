import wx
import os
import src.threads as br
import src.funs_n_cons_2 as utils
import src.constants as const

import src.acs_comp as acscomp

from configparser import ConfigParser

class ProjectPart():
    def __init__(self, name, rootdir):
        
        self.name           = name
        self.rootdir        = rootdir
        self.version        = const.ini_prop_projectparts("release",            "v0",     name)
        self.filename       = const.ini_prop_projectparts("filename",          name,     name)
        self.acscomp        = const.ini_prop_projectparts("acscomp",             section=name)
        self.sourcedir      = const.ini_prop_projectparts("sourcedir",         "src",    name)
        self.distdir        = const.ini_prop_projectparts("distdir",           "dist",   name)
        self.notxt          = const.ini_prop_projectparts("notxt",               section=name)
        self.skip           = False
    
    
    def GetExpectedPWADS(self, versioned, snapshot, snapshot_tag):
        expectfilename = ""
        pwad = []
        if not self.notxt:
            if versioned: 
                if snapshot: expectfilename = self.filename + "_" + snapshot_tag + ".pk3"
                else:        expectfilename = self.filename + "_" + self.version + ".pk3"
            else:            expectfilename = self.filename + "_DEV.pk3"
        else: expectfilename = self.filename + ".pk3"
        fullpath = os.path.join(self.rootdir, os.path.join(self.distdir, expectfilename))
        #print(fullpath)
        pwad = [utils.get_file_name(fullpath),utils.get_file_dir(fullpath)]
        return pwad
    
    def PartMsg(self, thread, msg):
        thread.ui.AddToLog(msg, 1);
    
    def BuildPart(self, thread, versioned, noacs, snapshot, current, total):
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
        
        os.chdir(rootdir)
        
        # Check the flags.
        if (self.skip):
            self.PartMsg(thread, self.name + " part excluded.")
            output = (0, [])
            return output
        
        # First compile (If the part contains any acs script.)
        res = 0;
        self.PartMsg(thread, "({1}/{2})\t\t=== Building {0} === ".format(self.name, current, total));
        if(noacs):
            self.PartMsg(thread, "ACS Compilation skipped")
        elif(compileacs):
            res = acscomp.acs_compile(thread, self)
            
        # Check if the cancel button is called.
        if thread.abort or res == -1:
            if thread.abort:  fail_reason = br.BUILD_CANCELED
            else:             fail_reason = br.BUILD_ERROR
            output = (fail_reason, [])
            os.chdir(rootdir)
            return output
        
        # After compiling, zip them all.
        # The path does'nt exist? Create it!
        os.chdir(rootdir)
        target_path = os.path.join(rootdir, distDir)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
            self.PartMsg(thread, target_path + " directory created.")
        
        zip = utils.makepkg(thread, sourceDir, destPath, notxt, versioned)
        os.chdir(rootdir)
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
            if snapshot: 
                tag_relase = thread.ui.snapshot_tag
            else:
                tag_relase = relase
            out = utils.make_dist_version(thread, zip, rootdir, sourceDir, destPath, tag_relase, notxt)
            files = out[1]
            if thread.abort or out[0] == -1:
                if thread.abort:  fail_reason = br.BUILD_CANCELED
                else:             fail_reason = br.BUILD_ERROR
                os.chdir(rootdir)
                output = (fail_reason, [])
                return output
        else: 
            zip.close()
            files = utils.makever(thread, "DEV", rootdir, destPath, notxt)
        
        # Part finished! Start the next one.
        output = (0, files)
        
        self.PartMsg(thread, "({1}/{2})\t\t=== {0} finished ===\n".format(self.name, current, total));
        
        return output