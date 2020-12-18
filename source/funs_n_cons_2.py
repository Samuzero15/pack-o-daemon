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

#
# Build main package (as .pk3, a good ol' zip, really)
#
def makepkg(builder, sourcePath, destPath, notxt=False, skipVariableTexts=False):
    destination = destPath + ".pk3"
    wadinfoPath = destPath + ".txt" # just assume this, 'cause we can.

    builder.ui.AddToLog("> Zipping {filename}".format (filename=destination))
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
        builder.ui.AddToLog("> There is no files to zip!\n> Are you sure you setted the directory name correctly for {0}?.".format(destination))
        return None
    
    builder.ui.AddToLog("> {1} files selected. Zipping {0} now.".format (destination, total_files))
    distzip = zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED)
    current = 1
    # And zip'em
    for file in filelist:
        if builder.abort: distzip.close(); return None
        distzip.write(*file)
        printProgress (builder.ui, current, len(filelist), '> Zipped: ', 'files. (' + file[1] + ')')
        current += 1
    
    builder.ui.AddToLog("> {0} Zipped Sucessfully".format(destination))
    return (distzip)
    
# Return if this file should be ignored.
def file_igonre(file):
    should_ignore = False;
    for ext in const.get_skip_filetypes():
        if not (should_ignore): should_ignore = file.endswith(ext);
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
            builder.ui.AddToLog("> buildinfo.txt found, makinig up distribution version.")
            for file in const.VARIABLE_FILES:
                if builder.abort or res == -1: return -1;
                source = sourceDir
                if (file == 'changelog.md'): source = rootDir
                if not os.path.isfile(os.path.join(source,file)):
                    printProgress (builder.ui, current, len(const.VARIABLE_FILES), '> Wrote: ', 'files. [SKIP] (' + file + ')')
                    current += 1
                    continue
                
                res = maketxt(builder, source, destPath, relase, file)
                zip.write(wadinfoPath, file)
                printProgress (builder.ui, current, len(const.VARIABLE_FILES), '> Wrote: ', 'files. (' + file + ')')
                current+=1
        else: builder.ui.AddToLog("> buildinfo.txt not found, skipping versioning.")
    zip.close()
    file_output = makever(builder.ui, relase, rootDir, destPath, notxt, True)
        
    
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
    color = True
    for line in textfile:
        if (lang_print):
            if (line.endswith("\n")): line = line.replace("\n", "")
            if(color):  strchanges += "\\cg-> \\cn" + line + "\c-\\n"
            else:       strchanges += "\\ci-> \\cv" + line + "\c-\\n"
            color = not color
        else:
            strchanges += line
        
    return strchanges

# Copies, and writes versionified files.
def makever(ui, version, sourceDir, destPath, notxt, versioned=False):
    file_output = []
    pk3 = destPath + ".pk3"
    ui.AddToLog("> Setting version to {0} and cleaning up".format(version))
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
def printProgress(ui, iteration, total, prefix = '', suffix = ''):
    ui.gauge.SetRange(total)
    ui.gauge.SetValue(iteration)
    percent = ("{0:.2f}").format(100 * (iteration / float(total)))
    ui.AddToLog(f'{prefix} {percent}% {suffix}')
    # print(f'{prefix} {percent}% {suffix}')

    
# Returns the path, parsing it if is a relative path.
def relativePath (path):
    if('..\\' in path):
        path = os.path.join(os.getcwd(), path)
        path = path.replace('..\\', '')
    return path

# Lil function which it delets deez files.
def remove_files(file_list):
    for f in file_list:
        os.remove(f)

# A powerful function that compiles every single acs library file in the specified directory.
def acs_compile(builder, part):
    rootDir     = part.rootdir
    sourceDir   = part.sourcedir
    partname    = part.name
    
    tools_dir = relativePath(const.ini_prop("acscomp_path", "..\\"));
    acs_dir = os.path.join(rootDir, sourceDir, "acs");
    src_dir = os.path.join(rootDir, sourceDir);
    comp_path = os.path.join(rootDir, tools_dir, const.COMPILER_EXE)
    if not os.path.isfile(comp_path):
        builder.ui.AddToLog("> ACS compiler can't find " + const.COMPILER_EXE + "." + 
        "\nPlease configure the directory on the project.ini file." +
        "\nACS Compilation skipped.")
        return 0
    
    if not os.path.isdir(acs_dir):
        builder.ui.AddToLog("> No ACS folder on {0} exists, creating it now.".format(partname))
        os.mkdir(acs_dir)
    
    tmp_dir = os.path.join(tools_dir, "acscomp_tmp");
    
    # includes = ['-i'] + [tools_dir] """+ ['-i'] + [src_dir]"""
    includes = ['-i'] + [tools_dir] + ['-i'] + [tmp_dir]
    
    # print(includes);
    
    os.chdir(acs_dir);
    # Get rid of the old compiled files, for a clean build.
    builder.ui.AddToLog("> Clearing old compiled ACS for {name}".format(name=partname));
    current = 1;
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: return -1
            if file.endswith(".o"):
               os.remove(os.path.join(root, file));
               printProgress(builder.ui, current, len(files), '> Cleared', '.o files. (' + file + ')')
               current += 1;
    builder.ui.AddToLog("> {name} Old Compiled ACS cleared.".format(name=partname));
    
    os.chdir(src_dir);
    
    # We should detect the acs libraries, those libraries are a must compile.
    fileslist = 0;
    files_copied = []
    files_to_compile = []
    builder.ui.AddToLog("> Preparing to compile ACS for {name} ".format(name=partname));
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: 
                remove_files(files_copied)
                os.rmdir(tmp_dir)
                return -1
            if file.endswith(".acs"):
                # Libraries are our compile target, but the acs library file can import/include some more acs.
                # Either way they must be copied to the acs temporary directory to make it work.
                acsfile = os.path.join(root, file)
                with open(acsfile, "r") as acsfile_reader:
                    if acsfile_reader.read().find("#library") != -1:
                        files_to_compile.append(acsfile)
                        builder.ui.AddToLog("> {0} library file has been targeted".format(file));
                        acsfile_reader.close()
                copy_dest = os.path.join(tmp_dir,file)
                if not os.path.exists(tmp_dir):
                    os.mkdir(tmp_dir)
                files_copied.append(copy_dest)
                copyfile(acsfile, copy_dest)
    
    # The stage is set! Let the compiling-fest begin!
    builder.ui.AddToLog("> Compiling ACS for {name}".format(name=partname));
    current = 0;
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    
    for file in files_to_compile:
        if builder.abort: 
            remove_files(files_copied)
            os.rmdir(tmp_dir)
            return -1
        else:
            # If you have acs files, compile them like libnraries.
            # Small suggestion, if you have an acs file which acts as a function container (through #include) rename the extention to something else, like .ach
            f_target = os.path.join(root, file)
            f_name = os.path.basename(f_target).split('.')[0]
            f_names = os.path.basename(f_target).split('.')[0] + '.' + os.path.basename(f_target).split('.')[1]
            
            compcmd     = [comp_path] + includes + [f_target] + [os.path.join(acs_dir, f_name + '.o')]
            subprocess.call(compcmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, startupinfo=startupinfo)
            current+=1;
            printProgress(builder.ui, current, len(files_to_compile), '> Compiled', 'acs files. (' + f_names + ')')
            # acs_err = os.path.join(rootDir, 'acs.err')
            acs_err = f_target.replace(f_names, 'acs.err')
            # We got an error in the acs script? Stop it, and show the error ASAP.
            if os.path.isfile(acs_err):
                remove_files(files_copied)
                os.rmdir(tmp_dir)
                acs_err_dir = get_file_dir(acs_err)
                os.chdir(acs_err_dir);
                # os.system('cls')
                with open('acs.err', 'rt') as errorlog:
                    builder.ui.AddToLog(errorlog.read())
                    errorlog.close()
                os.remove(os.path.join(acs_err_dir, 'acs.err'))
                builder.ui.AddToLog("> Fix those errors and try again, compilation failed.")
                return -1
            
            # Also stop if the expected file was'nt created.
            if not os.path.isfile(os.path.join(acs_dir, f_name + '.o')):
                remove_files(files_copied)
                os.rmdir(tmp_dir)
                os.chdir(rootDir);
                # os.system('cls')
                if(os.path.isfile(acs_err)): os.remove(acs_err)
                builder.ui.AddToLog("> The expected file was'nt created, compilation failed.")
                return -1
    
    # Job's done here, get back to the root directory and continue with the rest.
    remove_files(files_copied)
    os.rmdir(tmp_dir)
    os.chdir(rootDir)
    builder.ui.AddToLog("> {name} ACS Compiled Sucessfully.".format(name=partname));
    return 0
