# Packodaemon Changelog
## v1.7.2 [Resume button, other fixes]
	* Now, after clicking a button on the ACS Error dialog, the Pack-o-daemon will pop back up to the front.
	* Now the build flag values can be saved to the file after saving the settings (and it gets reflected by the build flags from the main tab)
	* Cleaned up some print stuff.
	* Added a "Resume" button, which it lets you continue the ACS compilation on the last file to be compiled after an ACS error.
	* The ACS error dialog now it does'nt need to be generated from zero, now it only hides and shows as one dialog, and updates it's message accordingly.

## v1.7.1 [Warning bypass and few fixes]
	* Now compilers can ignore warnings messages and continue the compilation process.
	* Added a new option for GDCC-C Compilation, target engine (Zandronum and Zdoom)
	* Now the skip flags will be preserved after saving the settings from the config dialog.
	* The acs compilation script will not be executed twice after retrying.
	* Little fix with the notification message.

## v1.7.0 [UI Revamp, GDCC Support, extra stuff]
	* The UI has been edited and compacted down in tabs for easier access to the different functions from the pack-o-daemon!
	* The build flags can be saved in the project.json file for the next uses, using the Save Flag button!
	* GDCC-ACC and GDCC-C is now supported! For the GDCC-C users, there are someextra settings under "acs_compilation" attribute of your project.json files in order to execute the respective compilers.
	* Restart the program? Screw that, now the Config Dialog will update the settings acordingly!
	* Log files are now added, view past logs any time!
	* Now the "project_parts" attributes can be modified through the settings button!
	* For the first time users, they will no longer need to restart the program. They will just be greet by the message and that's all, you're ready to go.
	* Few fixes and error catching for some file reading functions.

## v1.6.3 [Some new build flags + Reorganization]
	* Fixed the make.bat file for the windows builds.
	* Updated Readme.md
	* Deharcoded the build flags.
	* Added the "Cache ACS Files" build flag, searchs for libraries once, and update these files always.
	* Added also the "Hide ACS Sources" build flag, now you can make your code a closed source.

## v1.6.2 [Smoll reorganization]
	* Reorganized the whole directory, for the linux users.
	* Changelog fix on Patch notes link

## v1.6.1 [Linux Fixes]
	* Some linux fixes

## v1.6.0 [Reports, Command executer, and few fixes.]
	* Now you can call extra commands with the Execute button!
	* Now you can see some informative stuff with the Reports button!
	(Such as the actors in your project, the doomednums, and the file directory, aside of other useful information)
	* Some extra fixes

## v1.5.3 [Adding some meta-data and a 32bit build yay!]
	* Some builds later.
	* Added some yml and updated requirements for faster builds.

## v1.5.2 [Linux thread fix-up]
	* Modified the thread casting, now should be linux friendly. I think.
	* Now the notifications only appear in windows, there will be a work-arround for linux soon-ish

## v1.5.1 [Smol bugfix]
	* Changed the default project file generated for the first time use
	* Added the oneline format for the string replacers!
	* Fixed up some buggy bugs
	* Now you dont really need to take resets for each edits on the config dialog, the changes are now instant-ish.
	* If you need a version for your os, you gotta build it yourself. i guess. oof.

## v1.5.0 [JSon conversion, and some extra stuff]
	* Now from ini files, to json files. For an easier access.
	* Now you must specify the sourceport executeable path and also the pwad to be used in the play dialog.
	* Added some little icons.
	* New string replacer! Replace strings when building your project!
	* Now you can copy to clipboard the log output!
	* Now, the cacodemon is now trasparent1!1, PEAK CHANGE OMG
	* The cacodemon now speeens, and cries and laughs when the build fails or succeds.
	* Now, BCC is now supported! (or at least this version: https://github.com/zeta-group/zt-bcc)
	* Now, the cacodemon can be hidden and shown in the new Taskbar! Control the pack-o-daemon in a minimalistic way :D
	* Extra flags! for skipping Logs after a build or after a play operations, and a quick-play flag!
	* Now, add some extra files after zipping your mod!
	* A new settings dialog! Edit your json easy!
	* Some bug fixes too

## v1.4.3 [Reordering repository]
	* Reordering the files, separating the soruce from the python env files. (In order to make the repository setup easier and constant)
	* Updating Readme.md

## v1.4.2 [Minor Fixes + Snapshot tagging]
	* If you want to make temporaly relases (snapshots), the new build-flag will help you out!
	* Snapshot versions will be loaded up in the play menu but only if you build it first! They're supposed to be temporal.
	* If build-n-play is checked, the game will run ONLY if the build process was sucessful.
	* Little touch on the ACS Compiling script.

## v1.4.1 [Fooling arround with logs]
	* Now the changelog will be shown in this little tabbed window :3 (It's synched with the changelog.md file :3)
	* Random accept messages can appear in the log result.
	
## v1.4.0 [UI Trinkets + Some Fixes]
	* Now the output text in the result dialog will obey the word-wrapping rule depending on the new checkbox state.
	* Now for some tasks that requires some indeterminate time, the gauge will pulse, waiting for a response.
	* Each message from the output will print out the time now.
	* Some cleanup made on the main frame.
	* Some hyperlinks are added at the bottom of the program, just cause screw it.
	* Fixin' some bugs about the file routing in the ACS compiler
	* Ah yeah, now you can see the current patch notes about this thingy. Yay I guess?
	* The ACS Compilation can update the dependencies on each Retry button click.

## v1.3.2 [Some small but important fixes]
	* Fixes on the ACS Parser. ACS is case insensitive, but ZDoom not. oof
	* Word-wrap disabled for the result dialogs, because im tired of moving the horizontal bar
	* A bit of cleanup in the log messages
	* The dependency detection can be skipped if asked to.

## v1.3.1 [Bugfix]
	* Version bumped to 1.3.1

## v1.3.0 [ACS Comp library parse + a pair of new flags]
	* #Include and #Import files can be updated now, letting you to modify and press retry after the ACS error.
	* Now the packing script can put the proper tag to the zip.
	* A new project config variable has been added, build_dir, where you can specify the directory to work on.
	* A new flag has been added, build-n-play, which it lets you build the project and play it on the last settings.
	* Some other misc. Fixes.
	
## v1.2.0 [ACS Error prompt and bugfixes]
	* Fixed the packing script.
	* The play settings can be saved temporaily in case of any quick changes.
	* Now the zipping files can skip the extensions, splitting the space.
	* On the ACS compilation, if an error occurs, a prompt will be shown, displaying the type of error found, with 2 buttons in it. You can Retry the compilation on that file, or just Abort the build.

## v1.1.1 [ACS Compile patch]
	* The console spam for the acs compilation has been removed.

## v1.1.0 [Critical fixes]
	* Now the acs compilation and the running script for soruce ports should work correctly this time.
	* Small fix on the ini reader part.
	* Some other renaming stuff.
	* Other fixes in the batch file

## v1.0.1 [Re-naming the bat]
	* Small fix on the batch file for the building. Renaming to pack-o-daemon.exe

## v1.0.0 [Yeeting to Repo]
	* Added the readme and changelog files for documentation.
	* Added the whole project the to the repository.
