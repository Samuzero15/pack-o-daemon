echo off
cls
echo.
echo =============================================
echo      CACO PACKER BUILDER batch script
echo =============================================
echo.
echo Make sure you have python 3.8.5 or adobe, and make sure there are 2 enviroments with you. The env32 and the env, also an envw7, done with python 3.8 for windows 7 compatible versions.
echo. 
pause
call "create-version-file" metadata.yml --outfile file_version_info.txt
call "%~dp0\envw7\scripts\activate"
"pyinstaller" run.py -w --onefile --name pack-o-daemon_win7-32 -i "icon.ico" --add-data "src/*.*;src" --add-data "src/imgs/*.*;src/imgs" --add-data "changelog.md;." --version-file="file_version_info.txt"
call "%~dp0\env32\scripts\activate"
"pyinstaller" run.py -w --onefile --name pack-o-daemon_win32 -i "icon.ico" --add-data "src/*.*;src" --add-data "src/imgs/*.*;src/imgs" --add-data "changelog.md;." --version-file="file_version_info.txt"
call "%~dp0\env\scripts\activate"
"pyinstaller" run.py -w --onefile --name pack-o-daemon_win64 -i "icon.ico" --add-data "src/*.*;src" --add-data "src/imgs/*.*;src/imgs" --add-data "changelog.md;." --version-file="file_version_info.txt"
echo. 
echo =============================================
echo        CACO PACKER BUILD Completed
echo =============================================
echo. 
echo  By Samuzero15tlh. Thanks to Xaxer's python  
echo  code, and sirjuddington for the slade's acs 
echo  compiler.
echo. 
echo =============================================
echo. 
echo You can go now. Happy dooming!
echo. 
"deactivate"
pause

REM  run.py --onefile -w --name CacoPacker -i \"icon.ico\" --add-data "imgs/*.*;imgs"