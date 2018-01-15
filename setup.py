# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)

# my setup.py is based on one generated with gui2exe, so data_files is done a bit differently
data_files = []
includes = ["sip"]
excludes =[]
#excludes = [
#'_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
#            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
#            'Tkconstants', 'Tkinter', 'pydoc', 'doctest', 'test', 'sqlite3'
#            ]
packages = ['pytz']
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']
icon_resources = []
bitmap_resources = []
other_resources = []

# add the mpl mpl-data folder and rc file
import matplotlib as mpl
data_files += mpl.get_py2exe_datafiles()

import glob
data_files += [(r'mpl-data', glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\*.*')),
                    # Because matplotlibrc does not have an extension, glob does not find it (at least I think that's why)
                    # So add it manually here:
                  (r'mpl-data', [r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
                  (r'mpl-data\images',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
                  (r'mpl-data\fonts',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]

	

setup(name="Gas Turbine Developer",
    version="0.93",
    author="Sebastian Barthmes et al.",
    author_email="sebastian.barthmes@googlemail.com",
    url="www.sourceforge.com/projects/gtdev",
    license="GNU General Public License (GPL)",
	packages=['gtdev'],
	package_dir={'gtdev':'gtdev'},
	package_data={'gtdev':['gui/*']},
    #scripts=["gtdev"],
    windows=[{"script":"gtdev.py"}],
    options={"py2exe": {  "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          # using 2 to reduce number of files in dist folder
                          # using 1 is not recommended as it often does not work
                          "dist_dir": 'dist',
                          "skip_archive": True}},
	zipfile = r'lib\library.zip',
    data_files=data_files
	
	) 
