echo off
cls
echo.
echo =============================================
echo      CACO PACKER BUILDER batch script
echo =============================================
echo.
echo Make sure you have python 3.8.5 or adobe.
echo. 
pause
call "%~dp0\env\scripts\activate"
"pyinstaller" run.py -w --onefile --name pack-o-daemon -i "icon.ico" --add-data "src/*.*;src" --add-data "src/imgs/*.*;src/imgs" --add-data "changelog.md;."
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