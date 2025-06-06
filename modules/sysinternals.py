#!/usr/bin/env python3
#############################################
# Installation module for Sysinternals Suite
#############################################

# AUTHOR OF MODULE NAME
AUTHOR="David Kennedy (HackingDave)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update sysinternals - Bundle of Sysinternals Utilities"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="FILE"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://download.sysinternals.com/files/SysinternalsSuite.zip"

# EXTENSION OF THE RELEASE FILE (WITHOUT ".")
RELEASE_EXTENSION=""

# FILTER TO GRAB THE CORRECT RELEASE FILE
RELEASE_FILTER=""

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="sysinternals"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="curl unzip"

# DEPENDS FOR FEDORA INSTALLS
FEDORA=""

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="cd {INSTALL_LOCATION},unzip -j -o *.zip, mkdir -p $HOME/httpserver/sysinternals, mv ./* $HOME/httpserver/sysinternals"

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER=""

# RUN AFTER_COMMAND AFTER UPDATING
BYPASS_UPDATE="YES"