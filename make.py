import subprocess
import sys
import yaml
import os

from pack_o_daemon.src.constants import VERSION
import yaml

## Update metadata.
metadata = {
    "Version": (str)(VERSION[0]) + "." + (str)(VERSION[1]) + "." + (str)(VERSION[2]),
    "CompanyName" : "none",
    "FileDescription": "A little helper tool for your doom directory based mod.",
    "InternalName" : "Pack O Daemon",
    "LegalCopyright" : "© Cacodemon sprites are from Doom and belongs to ID Software. All rights reserved.",
    "OriginalFilename" : "pack-o-daemon.exe",
    "ProductName" : "Pack O Daemon",
    "Translation" : [
        {
            "langID": 0,
            "charsetID" : 1200
        },
        {
            "langID": 1033,
            "charsetID" : 1252
        }
    ]
}

with open('metadata.yml', 'w') as file:
    yaml.dump(metadata, file)

# Now, execute pyinstaller.

startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def make_exe_build(bit):
    cmd = ["pyinstaller"] + ["pack_o_daemon/run.py"] + ["-w"] + ["--onefile"] + ["--name"] + ["pack-o-daemon_" + (str)(VERSION[0]) + "." + (str)(VERSION[1]) + "." + (str)(VERSION[2]) + "-" + bit] + ["-i"] + ["icon.ico"] + ["--add-data"] + ["pack_o_daemon/src/*.*;pack_o_daemon/src"] + ["--add-data"] + ["pack_o_daemon/src/imgs/*.*;pack_o_daemon/src/imgs"] + ["--add-data"] + ["pack_o_daemon/changelog.md;pack_o_daemon/"] + ["--version-file=file_version_info.txt"]
    return cmd

is_64bits = sys.maxsize > 2**32

arch = "32bit"
if is_64bits:
    arch = "64bit"

commands = [
    ["create-version-file"] + ["metadata.yml"] + ["--outfile"] + ["file_version_info.txt"],
    make_exe_build(arch)
]
for cmd in commands:
    print (cmd)
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, startupinfo=startupinfo)
    out, err = p.communicate()
    if(len(out)>0):print(out)
    if(len(err)>0):print(err)

            