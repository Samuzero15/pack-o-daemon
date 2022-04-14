
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

ACS_CHAR_BREAK = [' ', '\t', '\n', '+', '-', '*', '/', '>', '<', '|', '&', '\\']

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
        if((char in ACS_CHAR_BREAK) and len(word) != 0):
            
            for cb in ACS_CHAR_BREAK:
                word = word.replace(cb, "")
                
            word = word.lower()
            if(len(word) != 0): word_list.append(word)
            word = ""
        else:
            word += char 
    
    if(len(word) != 0): 
        word_list.append(word)
        word = ""
    
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
    utils.process_msg(builder, "Reading dependencies, this might take a while...");
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: return -1
            
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
    utils.process_msg(builder, "Checking extra dependencies...");
    all_dependencies = acs_check_extra_dependencies(builder, dependencies)
    if (all_dependencies == -1): return -1
    #  print ("All needed are: {0}".format(all_dependencies))
    utils.process_msg(builder, "All needed are: {0}".format(acs_set_to_string(all_dependencies)))
    utils.process_msg(builder, "ACS Compilation Dependencies detected.")
    return (all_dependencies, libraries)

def acs_check_extra_dependencies(builder, dependencies=[], scanned_deps=[]):
    if(len(scanned_deps) > 0):
        dependencies = scanned_deps.symmetric_difference(dependencies)
        # print(dependencies)
        
    total_dependencies = dependencies.copy()
    
    for d in dependencies:
        total_dependencies = total_dependencies.union(acs_file_dependency_check(builder, d, dependencies.union(scanned_deps)))
        if (total_dependencies == -1): return -1
    return total_dependencies

def acs_file_dependency_check(builder, target_file, dependencies=[]):
    new_dependencies = set([])
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: return -1
            
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
    '''
    new_dependencies = new_dependencies.union(dependencies)
    new_dependencies = new_dependencies.difference(dependencies)
    '''
    # print ("Dependencies in {0} are: {1}".format(target_file, new_dependencies))
    
    if len(new_dependencies) > 0:
        # print ("Detecting inner dependencies for {0}".format(target_file))
        extra_dependencies = acs_check_extra_dependencies(builder, dependencies.union(new_dependencies) , dependencies)
        if (extra_dependencies == -1): return -1
        # print ("Found inner dependencies for file {0}: {1}".format(target_file, extra_dependencies))
        dependencies = dependencies.union(new_dependencies)
        dependencies = dependencies.union(extra_dependencies)
        # print(extra_dependencies)
        
    
    return dependencies

def acs_set_to_string(this_set):
    string = ""
    counter = 0
    this_list = list(this_set)
    len_list = len(this_set)
    for i in range(len_list):
        counter += 1 
        if(i < len_list - 2):
            string += this_list[i] + ", "
        elif(i < len_list - 1):
            string += this_list[i] + " and "
        else:
            string += this_list[i]
    
    return string
    

def acs_filename_in(file, this_list):
    for f in this_list:
        if file.lower() == f.lower(): return True
    else: return False


def acs_update_compilable_files(builder, partname, src_dir, tmp_dir, get_files_to_compile=False):
    utils.process_msg(builder, "Checking for ACS script dependencies for {name} ".format(name=partname));
    utils.printProgress(builder, -1)
    acs_comp_dependencies =  acs_check_library_and_dependencies(builder)
    if (acs_comp_dependencies == -1): return -1
    # print(acs_comp_dependencies)
    
    utils.process_msg(builder, "Coping required files to workspace...")
    files_copied = []
    files_to_compile = []
    
    os.chdir(src_dir)
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: 
                rmtree(tmp_dir)
                return -1
            
                # Copy the dependencies and libraries to the temporary file
            if (acs_filename_in(file, acs_comp_dependencies[1].union(acs_comp_dependencies[0]))):
                acsfile = os.path.join(root, file)
                copy_dest = os.path.join(tmp_dir,file)
                if (acs_filename_in(file, acs_comp_dependencies[1])):
                    files_to_compile.append(file)
                    # utils.process_msg(builder, "File {0} targeted to be compiled.".format(file));
               
                files_copied.append(copy_dest)
                copyfile(acsfile, copy_dest)
                
                # utils.process_msg(builder, "{0} Copied to acscomp_tmp path".format(file));
    utils.process_msg(builder, "ACS Compilable files are Updated.")
    if get_files_to_compile: return files_to_compile

ACSCOMP_RUNNING = 0
ACSCOMP_PROMPT = 1
ACSCOMP_FALLBACK = -1
ACSCOMP_COMPLETED = 2

# A powerful function that compiles every single acs library file in the specified directory.
def acs_compile(builder, part):
    rootDir     = part.rootdir
    sourceDir   = part.sourcedir
    partname    = part.name
    
    pathdir = os.path.join(rootDir, sourceDir);
    
    os.chdir(builder.ui.rootdir)
    tools_dir = os.path.join(utils.relativePath(const.ini_prop("acscomp_path", "..\\")));
    src_dir = os.path.join(rootDir, sourceDir);
    acs_dir = os.path.join(pathdir, "acs");
    comp_path = os.path.join(tools_dir, const.COMPILER_EXE)
    
    if not os.path.isfile(comp_path):
        utils.process_msg(builder, "ACS compiler can't find " + const.COMPILER_EXE + "." + 
        "Please configure the directory on the project.ini file." +
        "ACS Compilation skipped.")
        return 0
    
    if not os.path.isdir(acs_dir):
        utils.process_msg(builder, "No ACS folder on {0} exists, creating it now.".format(partname))
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
    utils.process_msg(builder, "Clearing old compiled ACS for {name}".format(name=partname));
    current = 1;
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if builder.abort: return -1
            if file.endswith(".o"):
               os.remove(os.path.join(root, file));
               utils.printProgress(builder, current, len(files), 'Cleared', '.o files. (' + file + ')')
               current += 1;
    utils.process_msg(builder, "{name} Old Compiled ACS cleared.".format(name=partname));
    
    # Work-arround to hide the acc console.
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    os.chdir(src_dir);
    outs = 0
    while True:
        # Wait until the ACS Error dialog gives us an answer
        if outs == 1:
            if builder.ui.response == 0: # Sthap
                utils.process_msg(builder, "Aborting ACS Compilation.")
                builder.abort = True
                outs = ACSCOMP_FALLBACK
            elif builder.ui.response == 1: # Again
                # rmtree(tmp_dir) # Refresh the acs again!
                utils.process_msg(builder, "Retrying ACS Compilation.".format(file))
                outs = ACSCOMP_RUNNING
            continue
            
        if(outs == ACSCOMP_FALLBACK):
            os.chdir(rootDir)
            rmtree(tmp_dir)
            return -1
        
        if(outs == ACSCOMP_COMPLETED): 
            utils.process_msg(builder, "{name} ACS Compiled Sucessfully.".format(name=partname));
            break
        
        files_to_compile = []
        try:
            files_to_compile = acs_update_compilable_files(builder, partname, src_dir, tmp_dir, True);
        except Exception as e:
            utils.process_msg(builder, "Something went really wrong. Skipping ACS Comp for {0}. ".format(partname));
            utils.process_msg(builder, "Error msg: {0} ".format(str(e)));
            os.chdir(rootDir)
            return 0
        
        # If user called to abort.
        if (files_to_compile == -1): return -1
    
        # print(files_to_compile)
        # The stage is set! Let the compiling-fest begin!
        utils.process_msg(builder, "Compiling ACS for {name}".format(name=partname));
        current = 0;
        for file in files_to_compile:
            if builder.abort: 
                rmtree(tmp_dir)
                return -1
            else:
                # If you have acs files, compile them like libnraries.
                
                f_target = os.path.join(tmp_dir, file)
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
                    utils.process_msg(builder, "The file contains some errors, compilation failed.")
                    outs = ACSCOMP_PROMPT
                    break

                    # Actually instead of just bouncing you out, I prefer to just repeat the compilation of that file.
                
                # Also stop if the expected file was'nt created.
                if not os.path.isfile(os.path.join(acs_dir, f_name + '.o')):
                    os.chdir(rootDir);
                    # os.system('cls')
                    if(os.path.isfile(acs_err)): os.remove(acs_err)
                    wx.CallAfter(builder.ui.ACSErrorOutput, "Something blew up :/")
                    utils.process_msg(builder, "The expected file was'nt created, compilation failed.")
                    outs = ACSCOMP_PROMPT
                    break
                
                current+=1;
                utils.printProgress(builder, current, len(files_to_compile), 'Compiled', 'acs files. (' + f_names + ')')
        
        if outs == ACSCOMP_RUNNING: 
            outs = ACSCOMP_COMPLETED
    # Job's done here, get back to the root directory and continue with the rest.
    
    os.chdir(rootDir)
    rmtree(tmp_dir)
    return 0
