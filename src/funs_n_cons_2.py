# Constants and useful functions.

import os
from pathlib import Path
import re
import sys
import threading
import traceback
import zipfile
import datetime
import subprocess
import wx
from configparser import ConfigParser
import src.constants as const
import src.threads as thr
from glob import iglob
from shutil import copyfile

def process_msg(builder, msg):
    #builder.ui.AddToLog(msg, 2)
    wx.PostEvent(builder.ui, thr.StatusBarEvent(msg,2))

#
# Build main package (as .pk3, a good ol' zip, really)
#
def makepkg(builder, sourcePath, destPath, notxt=False, skipVariableTexts=False):
    destination = destPath + ".pk3"
    wadinfoPath = destPath + ".txt" # just assume this, 'cause we can.

    process_msg(builder, "Zipping {filename}".format (filename=destination))
    filelist = []
    current = 1
    total_files = 0
    # Count the files...
    basepath = sourcePath.split(os.sep)
    for path, dirs, files in os.walk (sourcePath):
        
        for file in files:
            if builder.abort: return None
            if not (file_igonre(file) or (skipVariableTexts and file_placeholder(file))): # special exceptions
            # Remove sourcepath from filenames in zip
                total_files += 1
                splitpath = path.split(os.sep)
                splitpath = splitpath[len(basepath):]
                splitpath.append(file)
                name = os.path.join(*splitpath)
                filelist.append((os.path.join (path, file), name,))
    
    if total_files == 0:
        process_msg(builder, "There is no files to zip!\nAre you sure you setted the directory name correctly for {0}?.".format(destination))
        return None
    
    compress_type = str(const.ini_prop("zip_compress_type")).lower()
    compress_type_str = ""
    
    if compress_type == "bzip2":          compress_type = zipfile.ZIP_BZIP2; compress_type_str="BZip2"
    elif compress_type == "lzma":       compress_type = zipfile.ZIP_LZMA; compress_type_str="LZMA"
    elif compress_type == "stored":     compress_type = zipfile.ZIP_STORED; compress_type_str="Stored"
    else:                               compress_type = zipfile.ZIP_DEFLATED; compress_type_str="Deflate"

    process_msg(builder, "{1} files selected. Zipping {0} now. Format compression: '{2}'".format (destination, total_files, compress_type_str))

    distzip = zipfile.ZipFile(destination, "w", compress_type)
    current = 1
    # And zip'em
    for file in filelist:
        if builder.abort: distzip.close(); return None
        distzip.write(*file)
        printProgress (builder, current, len(filelist), 'Zipped: ', 'files. (' + file[1] + ')')
        current += 1
    
    additional_files = const.ini_prop("build_add_files")
    current = 1
    process_msg(builder, "Adding the extra files. {0} extra files to be added.".format(len(additional_files)))
    for file in additional_files:
        try:
            path2file = os.path.join(relativePath(file))
            dirName = os.path.dirname(path2file)
            file_to_copy = os.path.basename(path2file)
            os.chdir(dirName)
            distzip.write(file_to_copy)
            printProgress (builder, current, len(additional_files), 'Zipped: ', 'files. (' + file + ')')
        except:
            process_msg(builder, "File '{0}' Not found, skipping to next file.".format(file))
        current += 1
    
    process_msg(builder, "{0} Zipped Sucessfully".format(destination))
    return (distzip)
    
# Return if this file should be ignored.
def file_igonre(file):
    should_ignore = False
    # print(const.get_skip_filetypes());
    for ext in const.get_skip_filetypes():
        # print(ext.strip(" "))
        if not (should_ignore): should_ignore = file.endswith(ext.strip(" "))
        else: break
    return should_ignore
    
# Return if this file is a placeholding file.
def file_placeholder(file):
    should_ignore = False
    for f in const.ini_prop("string_replacer")["files_to_replace"]:
        if not (should_ignore): should_ignore = (file == f)
        else: break
    return should_ignore

# Calls any resource within the executable program.
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_source_img(img):
    return resource_path(os.path.join("src/imgs", img))

#
# Make a distribution version
#
def make_dist_version(builder, zip, rootDir, sourceDir, destPath, relase, notxt):
    res = 0
    if not notxt: 
        wadinfoPath = destPath + ".txt"
        current = 1
        #if(os.path.isfile(os.path.join(sourceDir, 'buildinfo.txt'))):
            # Get all writeable files and replace them with the version and time.
            # process_msg(builder, "buildinfo.txt found, making up distribution version.")
        variable_files = const.ini_prop("string_replacer")["files_to_replace"]
        for file in variable_files:
            if builder.abort or res == -1: return -1
            source = sourceDir
            # if (file == 'changelog.md'): source = rootDir
            if not os.path.isfile(os.path.join(source,file)):
                printProgress (builder, current, len(variable_files), '> Wrote: ', 'files. [SKIP] (' + file + ')')
                current += 1
                continue
            
            res = maketxt(builder, source, destPath, relase, file)
            zip.write(wadinfoPath, file)
            printProgress (builder, current, len(variable_files), '> Wrote: ', 'files. (' + file + ')')
            current+=1
        # else: process_msg(builder, "buildinfo.txt not found, skipping versioning.")
    zip.close()
    file_output = makever(builder, relase, rootDir, destPath, notxt, True)
        
    
    return (res, file_output)

# Replaces the lines from the template files.
def maketxt(builder, sourcePath, destPath, version, filetemplate):
    textname = os.path.join(sourcePath, filetemplate)
    destname = destPath + ".txt"
    
    aborted = False
    strings_to_replace = const.ini_prop("string_replacer")["strings_to_replace"]
    
    #print(strings_to_replace)
    # Check the string replacer keys in case of file types. And notifies the user if the path from one of them is missing.
    for key, value in strings_to_replace.items():
        if builder.abort: aborted == True; break
        if value["type"] == "file" and not os.path.isfile(relativePath(value["content"])):
            process_msg (builder, "(String Repleacer) File '{0}' not found.".format(relativePath(value["content"])))

    sourcefile = open (textname, "rt")
    textfile = open (destname, "wt")
    for line in sourcefile:
        if builder.abort: aborted == True; break
        for key, value in strings_to_replace.items():
            if builder.abort: aborted == True; break
            if value["type"] == "tag":
                line = line.replace(key, version)
            elif value["type"] == "file":
                try:
                    file_to_copy = open (relativePath(value["content"]), "rt")
                    content = file_to_copy.read()
                    if value["oneline"] is not None and value["oneline"] == True:
                        content = format_singleline (content)
                    line = line.replace(key, content)
                    file_to_copy.close()
                except Exception as e:
                    dlg = wx.MessageDialog(None, "Something went wrong!\n" +"\n"+ traceback.format_exc(), "Ah shiet!").ShowModal()
                    
            elif value["type"] == "date":
                line = line.replace(key, datetime.datetime.now().strftime(value["content"]))
            else:
                line = line.replace(key, value["content"])
        textfile.write(line)
    textfile.close()
    sourcefile.close()
    # print("write in file: " + destname)
    # print(key, value["type"], value["content"])
    #line = line.replace(key, value["content"])
    
    return 0 + -1*aborted

# Reformat the string up to one line., thats it.
def format_singleline (textfile):
    strchanges = ""
    # color = True
    for line in textfile:
        if (line.endswith("\n")): line = line.replace("\n", "\\n")
        strchanges += line

    return strchanges

# Copies, and writes versionified files.
def makever(builder, version, sourceDir, destPath, notxt, versioned=False):
    file_output = []
    pk3 = destPath + ".pk3"
    process_msg(builder, "Setting version to {0} and cleaning up".format(version))
    if not notxt:
        txt_path = os.path.join(sourceDir,destPath + ".txt")
        pk3_ver = destPath + "_" + version + ".pk3"
        txt = destPath + ".txt"
        txt_ver  = destPath + "_" + version + ".txt"
        
        copyfile(pk3, pk3_ver)
        os.remove(pk3)
        file_output.append(get_file_dir_name(os.path.join(sourceDir, pk3_ver)))
        
        if(versioned and os.path.isfile(txt_path)): 
            copyfile(txt, txt_ver)
            os.remove(txt)
            file_output.append(get_file_dir_name(os.path.join(sourceDir, txt_ver)))
    
    if len(file_output) == 0: 
        file_output.append(get_file_dir_name(os.path.join(sourceDir,  pk3)))
    
    return(file_output)

# Returns both parts in a 2 speced array.
def get_file_dir_name(path):
    return [get_file_dir(path), get_file_name(path)]

#Returns the directory from the given file path
def get_file_dir (path):
    return path.replace(get_file_name(path), '')

# Returns the name from the given file path
def get_file_name (path):
    return Path(path).name
    # return os.path.basename(path).split('.')[0] + "." + os.path.basename(path).split('.')[1]

# Updates the GUI gauge bar.
def printProgress(builder, iteration=-1, total=10, prefix = '', suffix = ''):
    if(iteration == -1):
        builder.ui.gauge.Pulse()
    else:
        builder.ui.gauge.SetRange(total)
        builder.ui.gauge.SetValue(iteration)
        percent = ("{0:.2f}").format(100 * (iteration / float(total)))
        process_msg(builder, f'{prefix} {percent}% {suffix}')
    # print(f'{prefix} {percent}% {suffix}')

    
# Returns the path, parsing it if is a relative path.
def relativePath (path):
    if('..\\' in path):
        path = os.path.join(os.getcwd(), path)
        path = path.replace('..\\', '')
    return path

def getFileName(path):
    if os.path.isfile(path):
        filename = path.split(os.sep)
        filename = filename[len(filename)-1:]
        return filename[0]
    return False

ActorList = []

def Decorate_ActorToString(actor):
    linenumber = (str)(actor["line"])
    defname = actor["actor"]
    parentname = (" : " + actor["inherits"]) if len(actor["inherits"]) > 0 else ""
    replacedname = (" replaces " + actor["replaces"]) if len(actor["replaces"]) > 0 else ""
    doomednum = (" " + (str)(actor["doomednum"])) if actor["doomednum"] > 0 else ""

    return linenumber +": " +defname + parentname + replacedname + doomednum

def Decorate_ActorDoomEdNum(actor):
    defname = actor["actor"]
    doomednum = (str)(actor["doomednum"])

    return "(" + doomednum + ") --> " + defname

def Decorate_searchForActors(path_search, file_search = "decorate", extension = False):
     filecompare = ""
     for path, dirs, files in os.walk (path_search):
        for file in files:
            # 
            if extension == True: filecompare = file.lower()
            else: filecompare = str.lower(file.split(".")[0])
            
            # print (filecompare == file_search)
            if(filecompare == file_search):
                line_count = 1
                current_file = file_search
                f = open(os.path.join(path, file), "r")
                
                # Search for next include line.
                for line in f.readlines():
                    isactorline = re.search("^Actor", line, re.IGNORECASE) or re.search("^Class", line, re.IGNORECASE)
                    if(isactorline is not None):
                        # REGEXS
                        # GetActor (first index) : 
                        # print("Found actor line : '" + isactorline.string + "'")
                        actorline = isactorline.string
                        actorline = actorline.split("//", 1)[0]
                        actorline = actorline.replace('\n', "")
                        actorline = actorline.replace('\t', "")
                        actorline = actorline.split("{", 1)[0]
                        replaceactor = ""
                        parentactor = ""
                        doomednum = 0

                        definedactor = re.search('(?:actor *)([" \w\d]+)', actorline, re.IGNORECASE)
                        if (definedactor is not None):
                            definedactor = definedactor.group(1)
                            parentactor = re.search("(?:: *)([ \w\d]+)", actorline)
                            parentactor = parentactor.group(1) if parentactor is not None else ""
                            replaceactor = re.search("(?:replaces *)([ \w\d]+)", actorline)
                            replaceactor = replaceactor.group(1) if replaceactor is not None else ""
                            doomednumregex = re.search("(?: +)([\d]+)", actorline)
                            doomednum = (int)(doomednumregex.group(1)) if doomednumregex is not None else 0
                            
                            path = path.replace(path_search, "...")
                            ActorList.append({"path":path, "file":current_file, "line":line_count,
                                            "actor":definedactor, "inherits":parentactor, "replaces":replaceactor, "doomednum":doomednum})
                        
                        # list_add += "'"+actorline+"', defined actor = '" + definedactor + "', parentactor = '" + parentactor + "', replaceactor = '" + replaceactor + "'\n"
                    
                    isincludeline = re.search("^#include", line, re.IGNORECASE)
                    if(isincludeline is not None):
                        includeline = isincludeline.string.split("\"")[1]
                        includefile = includeline.split("/")
                        includefile_name = includefile[len(includefile)-1:][0]
                        Decorate_searchForActors(path_search, includefile_name, True)
                    
                    line_count+=1
                    
                # for line in f:
                    # print(line)

                f.close()