#!bin/sh
echo =============================================
echo      CACO PACKER BUILDER shell script
echo =============================================
echo Make sure you have python 3.8.5 or adobe.
read -n 1 -r -s -p $'Press enter to continue...\n'
"create-version-file" metadata.yml --outfile file_version_info.txt
"pyinstaller" run.py -w --onefile --name pack-o-daemon_linux -i "icon.ico:" --add-data "src/*.*:src" --add-data "src/imgs/*.*:src/imgs" --add-data "changelog.md:." --version-file="file_version_info.txt"
