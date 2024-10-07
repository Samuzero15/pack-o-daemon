import json
import os
import datetime
import traceback
import wx

try:
    import src.projectpart as part
except ModuleNotFoundError: # If the module is not installed and running in the main repo.
    import pack_o_daemon.src.projectpart as part
    
from configparser import ConfigParser
from random import randint


PROJECT_FILE = "project.json"

VERSION = (1, 7, 1)
EXENAME = "Pack-o-daemon"

BFLAG_SKIPACSCOMP = 0
BFLAG_MAKEVERSION = 1
BFLAG_PACKPROJECT = 2
BFLAG_BUILDNPLAY = 3
BFLAG_SNAPSHOTVER = 4
BFLAG_SKIPLOGBUILD = 5
BFLAG_SKIPLOGPLAY = 6
BFLAG_QUICKPLAY = 7
BFLAG_HIDEACSSOURCE = 8
BFLAG_CACHEACSLIBS = 9

BUILD_FLAGS = [
    ["Skip ACS Comp", "Skips the ACS compilation process on each project part.\n" +
    "You could check this if you're only doing anything else than ACS scripting."],
    
    ["Make Version", "Tagges all project part files with their specified version tags.\n\n" + 
    "If the pack project flag is activated, the zip file will be tagged too."
    "\nAnd when entering into the play mode, the tagged zips will be targeted to be played."],
    
    ["Pack Project", "All the outputted files will be packed up in a single zip. \n" + 
    "Just in case you want to grab your stuff to take it to somewhere else."],
    
    ["Build-n-Play", "Once the files are built, the game launcher will pop up to test the project"],
    
    ["Snapshot Versioning", "If versioning is true.\n"+
    "Instead of using the config file tag relase, use a date-formatted tag.\n"],

    ["Skip log after Build", "After a build, don't show the build log results."],

    ["Skip log after Play", "After the sourceport is closed, don't show the gamelog results."],

    ["Quick play", "When pressing the play button, skips the play dialog and runs the sourceport with the saved settings."],

    ["Hide ACS Source", "Do not include the compilable ACS sources/libraries into the build."+
     "\nThe files must be cached first, or at least execute the acs compilation at least once to work."],

    ["Cache ACS Libraries", "When compiling ACS scripts, Pack-O-Daemon searchs for new libraries,\n" +
                            "and that takes some time depending on how deep is your file structure\n" +
                            "and how many libraries are referenced in your project.\n\n" +
                            "This flag forces the Pack-O-Daemon to load the ACS libraries only once,\n" + 
                            "and then, stop searching for new libraries in the future.\n\n" + 
                            "Be mindful of this flag when referencing new libraries on ACS."]
]

JSON_PROJPARTS = "project_parts"
JSON_PROJPARTS_RELEASE = "release"
JSON_PROJPARTS_FILENAME = "filename"
JSON_PROJPARTS_ACSCOMP = "acscomp"
JSON_PROJPARTS_SOURCEDIR = "sourcedir"
JSON_PROJPARTS_DISTDIR = "distdir"
JSON_PROJPARTS_NOTXT = "notxt"
JSON_PROJPARTS_SKIPPED = "skipped"

JSON_PLAYSETS = "play_settings"
JSON_PLAYSETS_SOURCEPORTPATH = "sourceport_path"
JSON_PLAYSETS_PWADSBEFORE = "pwads_before"
JSON_PLAYSETS_PWADSAFTER = "pwads_after"
JSON_PLAYSETS_IWADPATH = "iwad_path"
JSON_PLAYSETS_MAP = "map"
JSON_PLAYSETS_EXTRAPARAMS = "extra_params"

JSON_BUILDSETS = "build_settings"
JSON_BUILDSETS_NAME = "name"
JSON_BUILDSETS_TAG = "tag"
JSON_BUILDSETS_ZIPDIR = "zip_dir"
JSON_BUILDSETS_ZIPCOMPRESSTYPE = "zip_compress_type"
JSON_BUILDSETS_BUILDSKIPFILES = "build_skip_files"
JSON_BUILDSETS_BUILDDIR = "build_dir"
JSON_BUILDSETS_BUILDADDFILES = "build_add_files"
JSON_BUILDSETS_BUILDFLAGS = "build_flags"
JSON_BUILDSETS_STRREP = "string_replacer"
JSON_BUILDSETS_STRREP_FILESTOREPLACE = "files_to_replace"
JSON_BUILDSETS_STRREP_STR2REP = "strings_to_replace"
JSON_BUILDSETS_STRREP_STR2REP_TYPE = "type"
JSON_BUILDSETS_STRREP_STR2REP_CONTENT = "content"
JSON_BUILDSETS_STRREP_STR2REP_ONELINE = "oneline"

JSON_ACSCOMP = "acs_compilation"
JSON_ACSCOMP_TYPE = "type"
JSON_ACSCOMP_EXECUTEABLE = "executeable"
JSON_ACSCOMP_GDCCLINKER = "gdcc-linker_exe"
JSON_ACSCOMP_GDCCMAKELIBS = "gdcc-make_libs"
JSON_ACSCOMP_GDCCMAINLIB =  "gdcc-mainlib_name"
JSON_ACSCOMP_GDCCTARGETENGINE =  "gdcc-target_engine"
JSON_ACSCOMP_EXTRAPARAMS = "extra_params"
JSON_ACSCOMP_LIBRARYDIRS =  "library_dirs"

JSON_CMDEXE         = "cmd_execute" 
JSON_CMDEXE_NAME    = "name"
JSON_CMDEXE_CMD     = "cmd"

def make_default_json():
    flag_default_values = []
    for i in range(0, len(BUILD_FLAGS)):
        flag_default_values.append(False)

    json_data = {
        JSON_PROJPARTS : {
            "Source" : {
                JSON_PROJPARTS_RELEASE            : "v0",
                JSON_PROJPARTS_FILENAME          : "my_mod",
                JSON_PROJPARTS_ACSCOMP           : False,
                JSON_PROJPARTS_SOURCEDIR         : "src",
                JSON_PROJPARTS_DISTDIR          : "dist",
                JSON_PROJPARTS_NOTXT             : False,
                JSON_PROJPARTS_SKIPPED           : False
            }
        },
        JSON_PLAYSETS : {
            JSON_PLAYSETS_SOURCEPORTPATH    : "",
            JSON_PLAYSETS_PWADSBEFORE       : [],
            JSON_PLAYSETS_PWADSAFTER        : [],
            JSON_PLAYSETS_IWADPATH          : "",
            JSON_PLAYSETS_MAP               : "MAP01",
            JSON_PLAYSETS_EXTRAPARAMS       : ""
        }, 
        JSON_BUILDSETS : {
            JSON_BUILDSETS_NAME : "my_project",
            JSON_BUILDSETS_TAG : "v0",
            JSON_BUILDSETS_ZIPDIR:   "dist\packed",
            JSON_BUILDSETS_ZIPCOMPRESSTYPE: "",
            JSON_BUILDSETS_BUILDSKIPFILES : [ ".backup1", ".backup2", ".backup3", ".bak", ".dbs"],
            JSON_BUILDSETS_BUILDDIR : "",
            JSON_BUILDSETS_BUILDADDFILES : [],
            JSON_BUILDSETS_BUILDFLAGS : flag_default_values,
            JSON_BUILDSETS_STRREP : {
                JSON_BUILDSETS_STRREP_FILESTOREPLACE : [
                    "Language.txt", 
                    "GAMEINFO.txt", 
                    "changelog.md", 
                    "buildinfo.txt"
                ],
                JSON_BUILDSETS_STRREP_STR2REP : {
                    "_DEV_": {
                        JSON_BUILDSETS_STRREP_STR2REP_TYPE: "tag",
                        JSON_BUILDSETS_STRREP_STR2REP_CONTENT: "",
                        JSON_BUILDSETS_STRREP_STR2REP_ONELINE: False
                    },
                    "_FILE_": {
                        JSON_BUILDSETS_STRREP_STR2REP_TYPE: "file",
                        JSON_BUILDSETS_STRREP_STR2REP_CONTENT: "..\\path\\to\\file.txt",
                        JSON_BUILDSETS_STRREP_STR2REP_ONELINE: False
                    },
                    "XX/XX/XXXX": {
                        JSON_BUILDSETS_STRREP_STR2REP_TYPE: "date",
                        JSON_BUILDSETS_STRREP_STR2REP_CONTENT: "%d/%m/%Y",
                        JSON_BUILDSETS_STRREP_STR2REP_ONELINE: False
                    }
                }
            }
        },
        JSON_ACSCOMP : {
            JSON_ACSCOMP_TYPE: "acc",
            JSON_ACSCOMP_EXECUTEABLE: "acc.exe",
            JSON_ACSCOMP_GDCCLINKER : "gdcc-ld.exe",
            JSON_ACSCOMP_GDCCMAKELIBS : True,
            JSON_ACSCOMP_GDCCMAINLIB : "project",
            JSON_ACSCOMP_GDCCTARGETENGINE : "project",
            JSON_ACSCOMP_EXTRAPARAMS : "",
            JSON_ACSCOMP_LIBRARYDIRS : []
        },
        JSON_CMDEXE : [
			{
				JSON_CMDEXE_NAME :"test",
				JSON_CMDEXE_CMD :"echo 'hello world'"
			}
		]
        
    }
    # Serializing json
    json_object = json.dumps(json_data, indent=4)
    
    # Writing to sample.json
    with open(PROJECT_FILE, "w") as outfile:
        outfile.write(json_object)

# Defaults to the project section.
def ini_prop(what, default=None, section=JSON_BUILDSETS):
    ## data_conf = load_stuff()[0]
    setting = CONFIG_DATA[section].get(what, default)
    # print(setting)
    return setting

def ini_prop_projectparts(what, default=None, section="Source"):
    ## data_conf = load_stuff()[0]
    try:
        setting = CONFIG_DATA[JSON_PROJPARTS][section].get(what, default)
    except KeyError:
        setting = default
    return setting


# Read all sections
def read_parts(rootDir=os.getcwd()):
    project_parts = []
    build_dir = ini_prop(JSON_BUILDSETS_BUILDDIR, section=JSON_BUILDSETS)
    project_dir = None
    if(len(build_dir) != 0):
        project_dir = os.path.join(rootDir, build_dir)
    else:
        project_dir = rootDir
    
    for p in CONFIG_DATA[JSON_PROJPARTS]:
        project_parts.append(part.ProjectPart(p, project_dir))
    return project_parts


accept_msg = [
    "Done",
    "Nice",
    "Alright",
    "Got it",
    "Good"
]

funny_msg = [
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


def get_snapshot_build_tag():
    return datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')

# Get the possible snapshot tag.
SNAPSHOT_LAST = get_snapshot_build_tag()


def get_funny_msg():
    return funny_msg[randint(0, len(funny_msg) - 1)]

def get_accept_msg():
    return accept_msg[randint(0, len(accept_msg) - 1)]


def get_version():
    return  EXENAME + " - Ver. " + str(VERSION[0]) + "." + str(VERSION[1]) + "." + str(VERSION[2])

def get_skip_filetypes():
    return ini_prop(JSON_BUILDSETS_BUILDSKIPFILES, "")

def load_stuff():
    first_time = False
    try:
        try:
            f = open(PROJECT_FILE)
            CONFIG_DATA = json.load(f)
            f.close()
        except:
            make_default_json()
            f = open(PROJECT_FILE)
            CONFIG_DATA = json.load(f)
            f.close()
            first_time = True
        
    except:
        dlg = wx.MessageDialog(None, "Something went wrong (constants.py)!\n" +"\n"+ traceback.format_exc(), "Ah shiet!").ShowModal()
        
    return  CONFIG_DATA, first_time

FIRST_TIME = False
CONFIG_DATA, FIRST_TIME = load_stuff()
