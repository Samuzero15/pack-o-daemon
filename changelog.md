# Packodaemon Changelog

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