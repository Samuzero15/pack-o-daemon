# Samuzero15's Pack-o-daemon 
Just an small asistant for your directory based doom projects.
#### What is this?
It's a small tool that helps you to pack your directory based doom project in a single zip.

It makes your life easier with the structure of your files, and best of all, 
in a nice looking GUI. 

Literally just clicks away before playing your project.

#### What it does?
* Zippes directories containing doom data into pk3 packages.
* Versionifies the packages inmediatly.
* Zippes all the created pk3 files for your project in one single zip file.
* It can skip the zipping process for some of the project parts, for faster builds.
* If the project part contains acs library files, this program will compile them all before zipping.
* Runs your project, with the given settings and outputs the game result once you close the game.
* Also logs the progress made on the build process if you need to check for errors. (Such as ACS Compilation errors.)
* New string replacer system!, now add dynamic data after each versioning!

#### Why this?
* For the people who likes to work in their local directory using the file explorer.
* Allows you to use third party programs directly. (Audacity, Photoshop, Notepad++, Sublime Text, you name it)
* Smack some git repository in there to save your progress in your project.
* You like Slade, but you're kind of alergic to the text editor, or, yo find tedious to re-compile every acs file, everytime you make a change.

#### How to use it?
1. Get the pack-o-daemon.exe, and place it on your root folder. (where the doom project resides)
	> The directory structure should be somethin' like this:
	> * /my-doom-project
	> * -- pack-o-daemon.exe
	> * -- /src
	> * ----- whatever-files-you-got.txt
	
2. Run it, that will create the project.ini file where you can change the settings for the pack-o-demon.
3. Open pack-o-daemon.exe again, and everything should be set for the typical use.

If you change something from the project.ini file, and you have the executable running, restart it.

#### Hm... I want to build the source code, how can I do that?
1. Pack-O-Daemon uses the power of **Python 3.8.5**, so get that version or better.
2. Clone the repository, and extract it.
3. Get the console and ```cd``` it to the extracted repository.
4. Make a new virtual enviroment with ```python -m venv env```,
5. Use the command ```.\env\scripts\activate```, and check if "(env)" is right next to the command prompt line.
6. Now get the requirements installed with ```pip install -r requirements.txt```
7. And you're ready to go, it depends on what you want to do.
	> * To run it, do step 5 if env is not activated, and then ```python run.py```

	> * To build it execute this line using pyinstaller.
		```"pyinstaller" run.py -w --onefile --name pack-o-daemon -i "icon.ico" --add-data "src/*.*;src" --add-data "src/imgs/*.*;src/imgs" --add-data "changelog.md;."``` 
		* Depending on your python build (on the virtual enviroment too), the output file will be 64 bits or 32 bits.
		* Depending on what OS you execute this, might output to Windows, Linux or Mac.


You can use any text editor if you wish.

#### Frequently Asked Questions
> No questions yet...

#### Thanks to
* **sirjuddington** For the slade's acs compiler source code
* **Xaser** For the base code of his package builder for the eriguns doom mods.
* **AdmiralKosnov** For changing the name. The last one sounded more of a fudge packer. 
* **TDRR** For guiding me on how tf I set a linux enviroment for testing. Without him, this tool would be in Windows only :)

### See the changelog in the changelog.md file

