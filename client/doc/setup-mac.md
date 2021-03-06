
# MacOS X toolchain setup instructions

The following are instructions for setting up the MiFlux development environment and toolchain under MacOS X.

This has only been tested under MacOS 10.9 (Mavericks) so far.

## XCode

Install XCode from the Apple App Store, then install the command line tools:

```bash
xcode-select --install
```

## MiFlux code

Get the MiFlux code from GitHub:

```bash
cd /opt
sudo mkdir miflux
sudo chown $USER miflux
git clone https://github.com/umich-flux/miflux.git
```


## Environment

The environment needs to be set up in each new shell you start, before doing any development on the MiFlux application.  You may want to put the following commands in your `~/.bashrc` or some other file.

Set up the environment to be make sure that no Homebrew or XQuartz stuff gets built in to what we're doing, as these things won't be on the systems the app gets installed on.

If you are compiling the toolchain yourself (see below), you can set `${TOOLCHAIN}` to be whatever directory you want.  This is where all of the tools needed to develop MiFlux will be installed.

```bash
unset DYLD_LIBRARY_PATH
unset LD_LIBRARY_PATH
export TOOLCHAIN=/opt/miflux/client/toolchain
export PATH=${TOOLCHAIN}/Frameworks/Python.framework/Versions/2.7/bin:${TOOLCHAIN}/bin:/usr/bin:/bin:/usr/sbin:/sbin
```


## Pre-built toolchain

Since it can take several hours to build the toolchain from source (installing Qt, in particular, can take a very long time), you may want to download and install a pre-built toolchain.

If you do this, you will still need to set the environment (see above) each time before doing any development using the toolchain.

```bash
cd /opt/miflux/client
curl -O -L https://miflux.lsa.umich.edu/mac/toolchain/toolchain-latest.tar.bz2
tar jxpf toolchain-latest.tar.bz2
rm toolchain-latest.tar.bz2
```

If you install the pre-built toolchain, skip to the section [Building the MiFlux application](#building-the-miflux-application) below.


## Install Python

Most (but not all) articles on using py2app say that building our own version of Python is necessary, and that using the Apple-supplied Python won't work.  To be safe, and also to have full control over the toolchain used by MiFlux, we will build and install our own version of Python.

We'd like to use the latest version of Python 3, just to have the latest features and be up to date, but Twisted 14.0 has not been fully ported to Python 3, so we need to install Python 2.7.  Pretty much everything else that MiFlux depends upon seems to work fine with Python 3, however.

See:

* http://binarybuilder.wordpress.com/2012/10/09/building-python-2-7-on-mac-os-x-mountain-lion/
* step 5 at http://www.trondkristiansen.com/?page_id=79

We're currently using the 10.8 SDK because this is the oldest that XCode 5.1.1 supports.  If we need the 10.7 SDK later, try https://github.com/devernay/xcodelegacy

```bash
cd ${TOOLCHAIN}/src

curl -O -L https://www.python.org/ftp/python/2.7.7/Python-2.7.7.tgz
tar zxf Python-2.7.7.tgz
cd Python-2.7.7
# Make sure homebrew stuff is not used:
export PATH=${TOOLCHAIN}/bin:/usr/bin:/bin:/usr/sbin:/sbin

# TODO: Mac: install our own Tcl/Tk to avoid dependence on Apple ones which may differ between versions of MacOS X?

./configure MACOSX_DEPLOYMENT_TARGET=10.8 \
  --prefix=${TOOLCHAIN} \
  --enable-framework=${TOOLCHAIN}/Frameworks \
  --enable-toolbox-glue \
  --enable-universalsdk="/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk" \
  --with-universal-archs=intel \
  2>&1 | tee log.configure

make 2>&1 | tee log.make
make test 2>&1 | tee log.test
  # 365 tests OK, 33 test skipped, 1 unexpected skip on Darwin
make install 2>&1 | tee log.install
```


## Install pip

* https://pip.pypa.io/en/latest/installing.html

```bash
cd ${TOOLCHAIN}/src
curl -O -L https://bootstrap.pypa.io/get-pip.py
python ./get-pip.py 2>&1 | tee log.pip
```


## Install Qt5

* http://qt-project.org/
* http://qt-project.org/resources/getting_started

```bash
cd ${TOOLCHAIN}/src

curl -O -L http://download.qt-project.org/official_releases/qt/5.3/5.3.0/single/qt-everywhere-opensource-src-5.3.0.tar.gz
tar zxf qt-everywhere-opensource-src-5.3.0.tar.gz
cd qt-everywhere-opensource-src-5.3.0
# Make sure homebrew stuff is not used:
export PATH=${TOOLCHAIN}/bin:/usr/bin:/bin:/usr/sbin:/sbin

./configure -prefix ${TOOLCHAIN} \
  -opensource -confirm-license \
  -framework -sdk macosx10.8 -release 2>&1 | tee log.configure

make 2>&1 | tee log.make
make install 2>&1 | tee log.install
make docs html_docs 2>&1 | tee log.docs
make install_docs install_html_docs 2>&1 | tee log.docs-install

# Test:
open ${TOOLCHAIN}/bin/Designer.app
```


## Install SIP

* http://www.riverbankcomputing.com/software/sip/download
* http://pyqt.sourceforge.net/Docs/sip4/

```bash
cd ${TOOLCHAIN}/src

curl -O -L \
  http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.1/sip-4.16.1.tar.gz
tar zxf sip-4.16.1.tar.gz
cd sip-4.16.1
python configure.py 2>&1 | tee log.configure
make 2>&1 | tee log.make
make install 2>&1 | tee log.install
```


## Install PyQt5

* http://pyqt.sourceforge.net/Docs/PyQt5/installation.html

```bash
cd ${TOOLCHAIN}/src

curl -O -L http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.3/PyQt-gpl-5.3.tar.gz
tar zxf PyQt-gpl-5.3.tar.gz
cd PyQt-gpl-5.3
python configure.py --confirm-license \
  --pyuic5-interpreter=${TOOLCHAIN}/bin/python2.7 \
  --sip=${TOOLCHAIN}/Frameworks/Python.framework/Versions/2.7/bin/sip \
  2>&1 | tee log.configure
make 2>&1 | tee log.make
make install 2>&1 | tee log.install

# Test it:
python ./examples/qtdemo/qtdemo.py
```


## Install dependencies for Twisted and Conch

```bash
cd ${TOOLCHAIN}/src
pip install zope.interface 2>&1 | tee log.zope.interface
pip install PyCrypto 2>&1 | tee log.PyCrypto
pip install PyASN1 2>&1 | tee log.PyASN1
pip install pyOpenSSL 2>&1 | tee log.pyOpenSSL
```


## Install Twisted

* https://twistedmatrix.com/trac/wiki/Downloads

```bash
cd ${TOOLCHAIN}/src
curl -O -L http://twistedmatrix.com/Releases/Twisted/14.0/Twisted-14.0.0.tar.bz2
tar zxf Twisted-14.0.0.tar.bz2
cd Twisted-14.0.0
python setup.py build 2>&1 | tee log.build
python setup.py install 2>&1 | tee log.install
```


## Install py2app

* http://pythonhosted.org//py2app/

We are installing this from source rather than via pip because we need to patch it to work with PyQt5.  The patch has been submitted for inclusion upstream:

https://bitbucket.org/ronaldoussoren/py2app/pull-request/7/add-support-for-pyqt5-to-sip-recipe/diff

```bash
cd ${TOOLCHAIN}/src
# Take care of py2app dependencies separately to simplify the py2app install:
pip install macholib 2>&1 | tee log.macholib
pip install modulegraph 2>&1 | tee log.modulegraph
pip install altgraph 2>&1 | tee log.altgraph

curl -O -L https://pypi.python.org/packages/source/p/py2app/py2app-0.8.1.tar.gz
tar zxf py2app-0.8.1.tar.gz
cd py2app-0.8.1
patch -p 1 < ../py2app.patch
python setup.py build 2>&1 | tee log.build
python setup.py install 2>&1 | tee log.install
```

## Install Esky

We're not using pip to install Esky because there have been a number of changes since the most recent release (0.9.8), we want to be able to read the tutorials and source code, and because we're patching Esky locally.

We're patching esky to add support for symlinks in .zip files; this substantially reduces the size (by 30% for small/simple apps).  The percentage will be lower for larger apps, although the absolute savings will still be 10 - 15 MB or more.  The patch has been submitted for inclusion upstream:

https://github.com/cloudmatrix/esky/pull/65

```bash
cd ${TOOLCHAIN}/src
git clone https://github.com/cloudmatrix/esky.git
cd esky
patch -p 1 < ../esky.patch
python setup.py build 2>&1 | tee log.build
python setup.py install 2>&1 | tee log.install
```

## Package up the toolchain

Do the following if you want to package up the toolchain you just built for other developers to download and use:

```bash
cd /opt/miflux/client
tar -c -f - --exclude toolchain/src --exclude toolchain/.gitignore \
  toolchain | bzip2 --best -c > toolchain-`date +%Y%m%d`.tar.bz2
scp toolchain-`date +%Y%m%d`.tar.bz2 \
  schrodingers.lsa.umich.edu:/var/www/miflux.lsa.umich.edu/html-ssl/mac/toolchain/
ssh schrodingers.lsa.umich.edu
  cd /var/www/miflux.lsa.umich.edu/html-ssl/mac/toolchain/
  rm toolchain-latest.tar.bz2
  ln -s toolchain-`date +%Y%m%d`.tar.bz2 toolchain-latest.tar.bz2
  exit
```

# Building the MiFlux application

This is currently a very rough, manual process.  It will be improved and automated in the near future.

## Build Miflux

```bash
cd /opt/miflux/client/miflux
pyuic5 -o ui_MainWindow.py MainWindow.ui
find . -name "*.pyc" | xargs rm
```

## Create an application bundle

```
cd /opt/miflux/client
rm -rf build dist
python setup.py bdist_esky 2>&1 | tee log.bundle  # creates an esky .zip file
mkdir dist/dmg
( cd dist/dmg ; unzip ../MiFlux-*.zip )  # extract app so we can create a dmg
```

If you run MiFlux normally (that is, without a tty), debugging messages will be written to `~/Library/Application Support/miflux/miflux.log`:

```bash
open dist/dmg/MiFlux.app
```

Alternatively, you can run MiFlux with a tty and debugging messages will be displayed on stderr:

```bash
./dist/MiFlux.app/Contents/MacOS/MiFlux
```

If you get the error "The application cannot be opened because its executable is missing", you can either `rm -rf build dist` then rebuild the app (using the procedure above) or you can rebuild the Launch Services database:

```bash
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f dist/dmg/MiFlux.app
```

## Create a disk image

```bash
cd /opt/miflux/client
rm -f MiFlux.dmg rw.MiFlux.dmg dist/MiFlux.dmg
./util/create-dmg/create-dmg \
  --volname MiFlux \
  --volicon ./assets/dmg-icon/dmg-icon.icns \
  --window-pos 200 120 \
  --window-size 800 400 \
  --background ./assets/dmg-background/dmg-background.tiff \
  --icon-size 128 \
  --icon MiFlux.app 200 190 \
  --hide-extension MiFlux.app \
  --app-drop-link 600 185 \
  ./dist/MiFlux.dmg \
  dist/dmg 2>&1 | tee log.create-dmg
```

If the placement of the app icons is not correct, try removing the .dmg and running the script again.  If, after 2-3 runs, the above script doesn't set the properties of the .dmg window correctly, or if you get AppleScript errors, make sure that the program under which you are running the `create-dmg` script (e.g., Terminal, XQuartz, iTerm2, etc.) is allowed to control the computer (In System Preferences, go to Secureity and Privacy, go to the Privacy tab, select Accessiblity, and make sure that the program is listed and its checkbox is checked).  If that does not resolve the problem, try running the following:

```bash
echo '
   tell application "System Events"
       activate
       if not (UI elements enabled) then set (UI elements enabled) to true
   end tell
' | osascript
```


## Debugging crashes

If the application dies and the crash reporter runs, there will be a text file containing the details and a stack trace in the directory `Library/Logs/DiagnosticReports` -- you will want the file whose name begins with `MiFlux_` *not* the crash report whose filename begins with `python.exe_`.

When `qFatal()` gets called in the Qt libraries, this will result in the following:

```text
Crashed Thread:  0  Dispatch queue: com.apple.main-thread

Exception Type:  EXC_CRASH (SIGABRT)
Exception Codes: 0x0000000000000000, 0x0000000000000000

Application Specific Information:
abort() called

Thread 0 Crashed:: Dispatch queue: com.apple.main-thread
0   libsystem_kernel.dylib              0x00007fff85259866 __pthread_kill + 10
1   libsystem_pthread.dylib             0x00007fff88dfc35c pthread_kill + 92
2   libsystem_c.dylib                   0x00007fff8548eb1a abort + 125
3   QtCore                              0x0000000108462eb9 0x108442000 + 134841
4   QtCore                              0x0000000108464361 QMessageLogger::fatal(char const*, ...) const + 161
```

Unfortunately, we do not currently have debugging information for the Qt libraries, even if py2app is run with `--no-strip`.  Someone should look into this and see what needs to be done to have/keep debugging information or to use the debugging versions of the Qt libraries.  But this blog post is helpful in determining which registers contain which function arguments in the absence of debugging information:

http://www.clarkcox.com/blog/2009/02/04/inspecting-obj-c-parameters-in-gdb/

Here are the commands to run to see what error message is being passed to `qFatal()` during Qt initialization.  Note that we're launching the actual app which is inside the Esky wrapper app.

```
lldb ./dist/dmg/MiFlux.app/MiFlux-2014060506.macosx-10_8-intel/MiFlux.app
breakpoint set --name QMessageLogger::fatal
run
bt
frame info
register read
p (char *)$rsi    # arg 0, the format string; usually "%s"
p (char *)$rdx    # arg 1, the first format string parameter / error message
```

