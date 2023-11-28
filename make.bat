echo off
cls
echo.
echo ========================================================
echo      PACK-O-DAEMON EXECUTEABLE BUILDER batch script
echo ========================================================
echo.
echo Make sure you have python 3.8.5 or adobe, and make sure there are 2 enviroments with you. 
echo The env32 and the env (for 64 bits) for recent python builds.
echo Also an envw7, done with python 3.8.7, for windows 7 compatible versions.
echo. 
pause
call "create-version-file" metadata.yml --outfile file_version_info.txt
call "%~dp0\envw7\scripts\activate"
"pyinstaller" pack_o_daemon\run.py -w --onefile --name pack-o-daemon_win7-32 -i "icon.ico" --add-data "pack_o_daemon/src/*.*;pack_o_daemon/src" --add-data "pack_o_daemon/src/imgs/*.*;pack_o_daemon/src/imgs" --add-data "changelog.md;pack_o_daemon/" --version-file="file_version_info.txt"
call "%~dp0\env32\scripts\activate"
"pyinstaller" pack_o_daemon\run.py -w --onefile --name pack-o-daemon_win32 -i "icon.ico" --add-data "pack_o_daemon/src/*.*;pack_o_daemon/src" --add-data "pack_o_daemon/src/imgs/*.*;pack_o_daemon/src/imgs" --add-data "changelog.md;pack_o_daemon/" --version-file="file_version_info.txt"
call "%~dp0\env\scripts\activate"
"pyinstaller" pack_o_daemon\run.py -w --onefile --name pack-o-daemon_win64 -i "icon.ico" --add-data "pack_o_daemon/src/*.*;pack_o_daemon/src" --add-data "pack_o_daemon/src/imgs/*.*;pack_o_daemon/src/imgs" --add-data "changelog.md;pack_o_daemon/" --version-file="file_version_info.txt"
echo. 
echo ========================================================
echo      PACK-O-DAEMON EXECUTEABLE BUILDER Completed!
echo ========================================================
echo. 
echo By Samuzero15tlh. 
echo Thanks to..
echo sirjuddington: For the slade's acs compiler source code
echo Xaser: For the base code of his package builder for the eriguns doom mods.
echo AdmiralKosnov: For changing the name. The last one sounded more of a fudge packer. 
echo TDRR: For guiding me on how tf I set a linux enviroment for testing. Without him, this tool would be in Windows only :)
echo FusedQyou: For the report button's idea.
echo. 
echo ========================================================
echo. 
echo You can go now. Happy dooming!
echo. 
pause