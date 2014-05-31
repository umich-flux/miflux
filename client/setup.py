"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = [ 'src/MiFlux.py' ]
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    #'iconfile': 'bell.icns',
    'includes': [ 'sip', 'PyQt5', 'twisted' ] }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)