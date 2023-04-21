# Packodaemon Changelog

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