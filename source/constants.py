import os
import datetime
import source.projectpart as part
from configparser import ConfigParser
from random import randint

# I know, they're variables 
# but since you use the program and rarely the ini file... there is'nt a better place.

PROJECT_SECTION = "Project"
PROJECT_FILEINI = "project.ini"

def make_default_ini():
    config = ConfigParser(allow_no_value=True)
    section = PROJECT_SECTION
    config[section] = {}
    config.set(section, "# ..\\ means relative path (hidden in a subfolder in your project)", None)
    config.set(section, "# on dir variables, you only have to name the folder and subfolders without the relative path simbol.", None)
    config.set(section, "# -=(ACS Compilation settings)=-")
    config.set(section, "acscomp_path",     "..\\tools")
    config.set(section, "# No need to set them all, unless you're looking for more compatibility range.", None)
    config.set(section, "# -=(Sourceport settings)=-")
    config.set(section, "zandronum_path",   "?")
    config.set(section, "gzdoom_path",      "?")
    config.set(section, "zdaemon_path",     "?")
    config.set(section, "# -=(Build Settings)=-")
    config.set(section, "# The mentioned files (or file extensions) will be skipped on zipping.")
    config.set(section, "build_skip_files", " .backup1, .backup2, .backup3, .bak, .dbs")
    config.set(section, "build_dir", "")
    # config.set(section, "# The mentioned files are writtable by giving it some template.")
    # config.set(section, "build_variable_files", "")
    config.set(section, "# -=(Package settings)=-")
    config.set(section, "zip_name",      "my_project")
    config.set(section, "zip_dir",       "dist\packed")
    config.set(section, "zip_tag",       "v0")
    config.set(section, "# -=(Play project settings)=-", None)
    config.set(section, "# Add a pre-loaded pwad using comma (,) (e.g. ..\\path\\pwad1.wad, ..\\path\\pwad2.wad).", None)
    config.set(section, "# Add these pwads before adding the project files.", None)
    config.set(section, "play_pwads_before", "")
    config.set(section, "# Same, but after adding the project files.", None)
    config.set(section, "play_pwads_after", "")
    config.set(section, "play_sourceport",  "0")
    config.set(section, "play_iwad",        "0")
    config.set(section, "play_map",         "Map01")
    config.set(section, "play_extraparams", "")
    
    config['Source'] = {
        "relase"            : "v0",
        "filename"          : "my_mod",
        "acscomp"           : "false",
        "sourcedir"         : "src",
        "distdir"           : "dist",
        "notxt"             : "false"
    }
    with open(PROJECT_FILEINI,"w") as configfile:
        config.write(configfile)

# Defaults to the project section.
def ini_prop(what, default=None, section="Project"):
    setting = CONFIG[section].get(what, default)
    if setting.find(',') != -1:
        return setting.split(',')
    elif str_is_int(setting):
        return int(setting)
    elif str_is_bool(setting) is not None:
        return str_is_bool(setting)
    else: return setting

# Read all sections
def read_parts(rootDir=os.getcwd()):
    project_parts = []
    build_dir = ini_prop("build_dir");
    project_dir = None
    if(len(build_dir) != 0):
        project_dir = os.path.join(rootDir, ini_prop("build_dir"))
    else:
        project_dir = rootDir
    
    for p in CONFIG.sections():
        if p != PROJECT_SECTION:
            project_parts.append(part.ProjectPart(p, project_dir))
    return project_parts

# The string is a boolean?
def str_is_bool(stringy):
    test = stringy.lower();
    if(test in ["yes","y","1","true"]):
        return True
    elif(test in ["no","n","0","false"]):
        return False
    return None

# The string is a integer?
def str_is_int(stringy):
    res = False
    try:
        int(stringy)
        res = True
    except ValueError:
        pass
    return res

VERSION = (1, 4, 2)
EXENAME = "Pack-o-daemon"
COMPILER_EXE = "acc.exe"
TODAY = datetime.datetime.now().strftime('%d/%m/%Y')
CONFIG = ConfigParser()
FIRST_TIME = False
# [".backup1", ".backup2", ".backup3", ".bak", ".dbs"]
VARIABLE_FILES = ["Language.txt", "GAMEINFO.txt", "changelog.md", "buildinfo.txt"]
# ini_prop("build_variable_files", [])
# 
SHOWCASE_FILE = ["showcase.txt"]

BUILD_FLAGS = [
    ["Skip ACS Comp", "Skips the ACS compilation process on each project part.\n" +
    "You could check this if you're only doing anything else than ACS scripting."],
    
    ["Make Version", "Tagges all project part files with their specified version tags.\n" + 
    "\nIf the pack project flag is activated, the zip file will be tagged too."
    "\nAnd when entering into the play mode, the tagged zips will be targeted to be played."],
    
    ["Pack Project", "All the outputted files will be packed up in a single zip. \n" + 
    "Just in case you want to grab your stuff to take it to somewhere else."],
    
    ["Build-n-Play", "Once the files are built, the game launcher will pop up to test the project"],
    
    ["Snapshot Ver.", "If versioning is true.\n"+
    "Instead of using the config file tag relase, use a date-formatted tag.\n"]
]

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
    return ini_prop("build_skip_files", "")

def load_stuff():
    first_time = False
    try:
        CONFIG.read(PROJECT_FILEINI)
        if(len(CONFIG) == 1):
            make_default_ini()
            CONFIG.read(PROJECT_FILEINI)
            first_time = True
    except:
        print("Ah shiet.")
    return first_time
    
