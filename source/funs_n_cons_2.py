# Constants and useful functions.

import os
import sys
import threading
import zipfile
import datetime
import subprocess
import wx
from configparser import ConfigParser
import source.constants as const
from glob import iglob
from shutil import copyfile

def process_msg(builder, msg):
    builder.ui.AddToLog(msg, 2)

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
            if not (file_igonre(file) or file == "buildinfo.txt" or (skipVariableTexts and file_placeholder(file))): # special exceptions
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
    
    process_msg(builder, "{1} files selected. Zipping {0} now.".format (destination, total_files))
    distzip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
    current = 1
    # And zip'em
    for file in filelist:
        if builder.abort: distzip.close(); return None
        distzip.write(*file)
        printProgress (builder, current, len(filelist), 'Zipped: ', 'files. (' + file[1] + ')')
        current += 1
    
    process_msg(builder, "{0} Zipped Sucessfully".format(destination))
    return (distzip)
    
# Return if this file should be ignored.
def file_igonre(file):
    should_ignore = False;
    # print(const.get_skip_filetypes());
    for ext in const.get_skip_filetypes():
        # print(ext.strip(" "))
        if not (should_ignore): should_ignore = file.endswith(ext.strip(" "));
        else: break;
    return should_ignore;
    
# Return if this file is a placeholding file.
def file_placeholder(file):
    should_ignore = False;
    for f in const.VARIABLE_FILES:
        if not (should_ignore): should_ignore = (file == f);
        else: break;
    return should_ignore;

# Calls any resource within the executable program.
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_source_img(img):
    return resource_path(os.path.join("source/imgs", img));

#
# Make a distribution version
#
def make_dist_version(builder, zip, rootDir, sourceDir, destPath, relase, notxt):
    res = 0
    if not notxt: 
        wadinfoPath = destPath + ".txt"
        current = 1
        if(os.path.isfile(os.path.join(sourceDir, 'buildinfo.txt'))):
            # Get all writeable files and replace them with the version and time.
            process_msg(builder, "buildinfo.txt found, makinig up distribution version.")
            for file in const.VARIABLE_FILES:
                if builder.abort or res == -1: return -1;
                source = sourceDir
                if (file == 'changelog.md'): source = rootDir
                if not os.path.isfile(os.path.join(source,file)):
                    printProgress (builder, current, len(const.VARIABLE_FILES), '> Wrote: ', 'files. [SKIP] (' + file + ')')
                    current += 1
                    continue
                
                res = maketxt(builder, source, destPath, relase, file)
                zip.write(wadinfoPath, file)
                printProgress (builder, current, len(const.VARIABLE_FILES), '> Wrote: ', 'files. (' + file + ')')
                current+=1
        else: process_msg(builder, "buildinfo.txt not found, skipping versioning.")
    zip.close()
    file_output = makever(builder, relase, rootDir, destPath, notxt, True)
        
    
    return (res, file_output)

# Replaces the lines from the template files.
def maketxt(builder, sourcePath, destPath, version, filetemplate):
    textname = os.path.join(sourcePath, filetemplate)
    destname = destPath + ".txt"
    
    aborted = False
    
    sourcefile = open (textname, "rt")
    textfile = open (destname, "wt")
    for line in sourcefile:
        
        if builder.abort: aborted == True; break;
        line = line.replace('x.x.x', version)
        line = line.replace('_SHOWCASE_', print_showcase_changes (filetemplate == "Language.txt"))
        line = line.replace('_DEV_', version)
        line = line.replace('XX/XX/XXXX', const.TODAY)
        textfile.write(line)
    
    textfile.close()
    sourcefile.close()
    
    return 0 + -1*aborted

# Writes the changes to the lines and yeeah, thats it.
def print_showcase_changes (lang_print=False):
    textfile = open (relativePath ("showcase.txt"), "rt")
    changes = [];
    strchanges = "";
    # color = True
    for line in textfile:
        if (lang_print):
            if (line.endswith("\n")): line = line.replace("\n", "#")
            
            strchanges += line
        else:
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
    return os.path.basename(path).split('.')[0] + "." + os.path.basename(path).split('.')[1]

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
