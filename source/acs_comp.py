
import os
import sys
import subprocess
import wx
import source.funs_n_cons_2 as utils
import source.constants as const
from glob import iglob
from shutil import copyfile, rmtree


ACS_T_LIBRARY = "LIBRARY"
ACS_T_IMPORT =  "IMPORT"
ACS_T_INCLUDE = "INCLUDE"

def acs_dict_token(word):
    tokens = {
        "#library" : ACS_T_LIBRARY,
        "#import" : ACS_T_IMPORT,
        "#include" : ACS_T_INCLUDE,
    }
    return tokens.get(word, None)

class Token():
    def __init__(self, token_type, token_value=None):
        self.t_type = token_type
        self.t_value = token_value
    
    def to_string(self):
        if(self.t_value): return "[" + self.t_type + "," + self.t_value + "]"
        return "[" + self.t_type + "]"

def acs_parse_tokens(text):
    # Little parser which it looks up for the proper keywords.
    word = ""
    word_list = []
    for c in range(len(text)):
        char = text[c]
        if((char == '\n' or char == ' ') and len(word) != 0):
            
            word = word.replace("\t", "")
            word = word.replace("\n", "")
            word = word.replace(" ", "")
            word = word.lower()
            if(len(word) != 0): word_list.append(word)
            word = ""
        else:
            word += char 
    token_mode = 0
    token_type = "TOKEN"
    tokens = []
    for w in word_list:
        if(token_mode == 0):
            token_type = acs_dict_token(w);
            if(not (token_type is None)):
                token_mode = 1
        else:
            mytoken = Token(token_type, w);
            tokens.append(mytoken)
            token_mode = 0;
    return tokens

# This function will check the acs file for any dependencies needed to let this file work.
def acs_check_library_and_dependencies(builder):
    dependencies = []
    libraries = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".acs"):
                acsfile = os.path.join(root, file)
                try:
                    with open(acsfile, "r") as acsfile_reader:
                        text = acsfile_reader.read()
                        for t in acs_parse_tokens(text):        
                            if (t.t_type == ACS_T_INCLUDE or t.t_type == ACS_T_IMPORT):
                                dependencies.append(t.t_value.replace("\"", ""))
                            elif t.t_type == ACS_T_LIBRARY:
                                libraries.append(t.t_value.replace("\"", "") + ".acs")
                        acsfile_reader.close()
                except FileNotFoundError:
                    pass
    dependencies = set(dependencies)
    is_library = True
    libraries = set(libraries)
    
    # print ("Library dependencies: {0}".format(dependencies))
    
    all_dependencies = acs_check_extra_dependencies(dependencies)
    #  print ("All needed are: {0}".format(all_dependencies))
    builder.ui.AddToLog("> All needed are: {0}".format(all_dependencies))
    builder.ui.AddToLog("> ACS Compilation Dependencies updated.")
    return (all_dependencies, libraries)

def acs_check_extra_dependencies(dependencies=[]):
    total_dependencies = dependencies.copy()
    
    for d in dependencies:
        total_dependencies = total_dependencies.union(acs_file_dependency_check(d, total_dependencies))
    return total_dependencies

def acs_file_dependency_check(target_file, dependencies=[]):
    new_dependencies = set([])
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file == target_file:
                acsfile = os.path.join(root, file)
                try:
                    with open(acsfile, "r") as acsfile_reader:
                        text = acsfile_reader.read()
                        for t in acs_parse_tokens(text):        
                            if (t.t_type == ACS_T_INCLUDE or t.t_type == ACS_T_IMPORT):
                                new_dependencies.add(t.t_value.replace("\"", ""))
                        acsfile_reader.close()
                except FileNotFoundError:
                    pass
    
    # print ("Dependencies in {0} are: {1}".format(target_file, new_dependencies))
    
    if len(new_dependencies) > 0:
        # print ("Detecting inner dependencies for {0}".format(target_file))
        extra_dependencies = acs_check_extra_dependencies(new_dependencies)
        # print ("Found inner dependencies for file {0}: {1}".format(target_file, extra_dependencies))
        dependencies = dependencies.union(new_dependencies)
        dependencies = dependencies.union(extra_dependencies)
        # print(extra_dependencies)
        
    
    return dependencies

def acs_update_compilable_files(builder, partname, tmp_dir, get_files_to_compile=False):
    acs_comp_dependencies =  acs_check_library_and_dependencies(builder)
    # print(acs_comp_dependencies)
    
    files_copied = []
    files_to_compile = []
    builder.ui.AddToLog("> Checking for ACS script dependencies for {name} ".format(name=partname));
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: 
                rmtree(tmp_dir)
                return -1
            
                # Copy the dependencies and libraries to the temporary file
            if (file in acs_comp_dependencies[1]) or (file in acs_comp_dependencies[0]):
                acsfile = os.path.join(root, file)
                copy_dest = os.path.join(tmp_dir,file)
                if (file in acs_comp_dependencies[1]):
                    files_to_compile.append(file)
               
                files_copied.append(copy_dest)
                copyfile(acsfile, copy_dest)
    if get_files_to_compile: return files_to_compile

# A powerful function that compiles every single acs library file in the specified directory.
def acs_compile(builder, part):
    rootDir     = part.rootdir
    sourceDir   = part.sourcedir
    partname    = part.name
    
    tools_dir = utils.relativePath(const.ini_prop("acscomp_path", "..\\"));
    acs_dir = os.path.join(rootDir, sourceDir, "acs");
    src_dir = os.path.join(rootDir, sourceDir);
    comp_path = os.path.join(tools_dir, const.COMPILER_EXE)
    # print(comp_path)
    if not os.path.isfile(comp_path):
        builder.ui.AddToLog("> ACS compiler can't find " + const.COMPILER_EXE + "." + 
        "\nPlease configure the directory on the project.ini file." +
        "\nACS Compilation skipped.")
        return 0
    
    if not os.path.isdir(acs_dir):
        builder.ui.AddToLog("> No ACS folder on {0} exists, creating it now.".format(partname))
        os.mkdir(acs_dir)
    
    tmp_dir = os.path.join(tools_dir, "acscomp_tmp");
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    else:
        rmtree(tmp_dir)
        os.mkdir(tmp_dir)
    
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
               utils.printProgress(builder.ui, current, len(files), '> Cleared', '.o files. (' + file + ')')
               current += 1;
    builder.ui.AddToLog("> {name} Old Compiled ACS cleared.".format(name=partname));
    
    os.chdir(src_dir);
    files_to_compile = acs_update_compilable_files(builder, partname, tmp_dir, True);
    
    # print(files_to_compile)
    # The stage is set! Let the compiling-fest begin!
    builder.ui.AddToLog("> Compiling ACS for {name}".format(name=partname));
    current = 0;
    
    root = sourceDir
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    for file in files_to_compile:
        outs = 0
        while True:
            
            os.chdir(src_dir);
            
            # Wait until the ACS Error dialog gives us an answer
            if outs == 1:
                if builder.ui.response == 0: # Sthap
                    builder.ui.AddToLog("> Aborting ACS Compilation.")
                    builder.abort = True
                    outs = -1
                elif builder.ui.response == 1: # Keep going
                    builder.ui.AddToLog("> Retrying ACS Compilation on the current file ({0}).".format(file))
                    outs = 0
                    acs_update_compilable_files(builder, partname, tmp_dir);
                continue
            
            if builder.abort: 
                rmtree(tmp_dir)
                return -1
            else:
                # If you have acs files, compile them like libnraries.
                
                f_target = os.path.join(src_dir, file)
                f_name = os.path.basename(f_target).split('.')[0]
                f_names = os.path.basename(f_target).split('.')[0] + '.' + os.path.basename(f_target).split('.')[1]
                
                compcmd     = [comp_path] + includes + [f_target] + [os.path.join(acs_dir, f_name + '.o')]
                subprocess.call(compcmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, startupinfo=startupinfo)
                # acs_err = os.path.join(rootDir, 'acs.err')
                acs_err = f_target.replace(f_names, 'acs.err')
                # We got an error in the acs script? Stop it, and show the error ASAP.
                if os.path.isfile(acs_err):
                    acs_err_dir = utils.get_file_dir(acs_err)
                    os.chdir(acs_err_dir);
                    # os.system('cls')
                    with open('acs.err', 'rt') as errorlog:
                        error = errorlog.read()
                        builder.ui.AddToLog(error)
                        # builder.ui.ACSErrorOutput(error)
                        wx.CallAfter(builder.ui.ACSErrorOutput, error + "\n\nDo you wish to RETRY or ABORT the ACS Compilation?")
                        errorlog.close()
                    os.remove(os.path.join(acs_err_dir, 'acs.err'))
                    builder.ui.AddToLog("> The file contains some errors, compilation failed.")
                    outs = 1
                    continue

                    # Actually instead of just bouncing you out, I prefer to just repeat the compilation of that file.
                
                # Also stop if the expected file was'nt created.
                if not os.path.isfile(os.path.join(acs_dir, f_name + '.o')):
                    os.chdir(rootDir);
                    # os.system('cls')
                    if(os.path.isfile(acs_err)): os.remove(acs_err)
                    wx.CallAfter(builder.ui.ACSErrorOutput, "Something blew up :/")
                    builder.ui.AddToLog("> The expected file was'nt created, compilation failed.")
                    outs = 1
                    continue
                
                break
        if(outs == -1):
            rmtree(tmp_dir)
            return -1
        current+=1;
        utils.printProgress(builder.ui, current, len(files_to_compile), '> Compiled', 'acs files. (' + f_names + ')')
                
    
    # Job's done here, get back to the root directory and continue with the rest.
    rmtree(tmp_dir)
    os.chdir(rootDir)
    builder.ui.AddToLog("> {name} ACS Compiled Sucessfully.".format(name=partname));
    return 0
