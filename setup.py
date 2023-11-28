from setuptools import setup, find_packages
from pack_o_daemon.src.constants import VERSION

VERSION_SETUP = (str)(VERSION[0]) + "." + (str)(VERSION[1]) + "." + (str)(VERSION[2])
DESCRIPTION = 'A small asistant for your directory based doom projects.'
LONG_DESCRIPTION = "It's a small tool that helps you to pack your directory based doom project in a single zip.\nIt makes your life easier with the structure of your files, and best of all, \nin a nice looking GUI. \nLiterally just clicks away before playing your project."
# Setting up
setup(
    name="pack_o_daemon",
    version=VERSION_SETUP,
    author="Samuel Marquez (Samuzero15)",
    author_email="<samueloml@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="executable",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={"":["**/*.png","*.ico", "**/*.gif", "*.md", "LICENSE", "./changelog.md"]},
    include_package_data=True,
    install_requires=['altgraph', 'future', 'numpy', 'pefile', 'Pillow', 'six', 'wxPython', 'importlib.resources'],
    keywords=['python', 'doom', 'gui', 'modding'],
    classifiers=[
        "Development Status :: 3 - Mantaining",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
		'console_scripts': ['pack_o_daemon=pack_o_daemon.run:main'],
    }
)

