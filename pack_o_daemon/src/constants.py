import json
import os
import datetime
import traceback
import wx

import pack_o_daemon.src.projectpart as part
from configparser import ConfigParser
from random import randint


PROJECT_FILE = "project.json"

VERSION = (1, 6, 2)
EXENAME = "Pack-o-daemon"

BUILD_FLAGS = [
    ["Skip ACS Comp", "Skips the ACS compilation process on each project part.\n" +
    "You could check this if you're only doing anything else than ACS scripting."],
    
    ["Make Version", "Tagges all project part files with their specified version tags.\n" + 
    "\nIf the pack project flag is activated, the zip file will be tagged too."
    "\nAnd when entering into the play mode, the tagged zips will be targeted to be played."],
    
    ["Pack Project", "All the outputted files will be packed up in a single zip. \n" + 
    "Just in case you want to grab your stuff to take it to somewhere else."],
    
    ["Build-n-Play", "Once the files are built, the game launcher will pop up to test the project"],
    
    ["Snapshot Versioning", "If versioning is true.\n"+
    "Instead of using the config file tag relase, use a date-formatted tag.\n"],

    ["Skip log after Build", "After a build, don't show the buildlog results."],

    ["Skip log after Play", "After the sourceport is closed, don't show the gamelog results."],

    ["Quick play", "When pressing the play button, skips the play dialog and runs the sourceport with the saved settings."]
]

def make_default_json():
    flag_default_values = []
    for i in range(0, len(BUILD_FLAGS)):
        flag_default_values.append(False)

    json_data = {
        "project_parts" : {
            "Source" : {
                "release"            : "v0",
                "filename"          : "my_mod",
                "acscomp"           : False,
                "sourcedir"         : "src",
                "distdir"           : "dist",
                "notxt"             : False
            }
        },
        "play_settings" : {
            "sourceport_path" : "",
            "pwads_before" : [],
            "pwads_after" : [],
            "iwad_path" : "",
            "map" : "MAP01",
            "extra_params" : ""
        }, 
        "build_settings" : {
            "name" : "my_project",
            "tag" : "v0",
            "zip_dir":   "dist\packed",
            "zip_compress_type": "",
            "build_skip_files" : [ ".backup1", ".backup2", ".backup3", ".bak", ".dbs"],
            "build_dir" : "",
            "build_add_files" : [],
            "build_flags": flag_default_values,
            "string_replacer" : {
                "files_to_replace" : [
                    "Language.txt", 
                    "GAMEINFO.txt", 
                    "changelog.md", 
                    "buildinfo.txt"
                ],
                "strings_to_replace": {
                    "_DEV_": {
                        "type": "tag",
                        "content": "",
                        "oneline": False
                    },
                    "_FILE_": {
                        "type": "file",
                        "content": "..\\path\\to\\file.txt",
                        "oneline": False
                    },
                    "XX/XX/XXXX": {
                        "type": "date",
                        "content": "%d/%m/%Y",
                        "oneline": False
                    }
                }
            }
        },
        "acs_compilation" : {
            "type": "acc",
            "executeable": "acc.exe",
            "extra_params" : ""
        },
        "cmd_execute" : [
			{
				"name":"test",
				"cmd":"echo 'hello world'"
			}
		]
        
    }
    # Serializing json
    json_object = json.dumps(json_data, indent=4)
    
    # Writing to sample.json
    with open(PROJECT_FILE, "w") as outfile:
        outfile.write(json_object)

# Defaults to the project section.
def ini_prop(what, default=None, section="build_settings"):
    ## data_conf = load_stuff()[0]
    setting = CONFIG_DATA[section].get(what, default)
    # print(setting)
    return setting

def ini_prop_projectparts(what, default=None, section="Source"):
    ## data_conf = load_stuff()[0]
    setting = CONFIG_DATA["project_parts"][section].get(what, default)
    return setting


# Read all sections
def read_parts(rootDir=os.getcwd()):
    project_parts = []
    build_dir = ini_prop("build_dir", section="build_settings")
    project_dir = None
    if(len(build_dir) != 0):
        project_dir = os.path.join(rootDir, build_dir)
    else:
        project_dir = rootDir
    
    for p in CONFIG_DATA["project_parts"]:
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
    return ini_prop("build_skip_files", "")

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
