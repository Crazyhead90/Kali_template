#!/usr/bin/env python3
#####################################
# Installation module for Bloodhound
#####################################

# AUTHOR OF MODULE NAME
AUTHOR="Dirkjanm"

# DESCRIPTION OF THE MODULE
DESCRIPTION="BloodHound.py is a Python based ingestor for BloodHound, based on Impacket."

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/dirkjanm/BloodHound.py.git"

# EXTENSION OF THE RELEASE FILE (WITHOUT ".")
RELEASE_EXTENSION=""

# FILTER TO GRAB THE CORRECT RELEASE FILE
RELEASE_FILTER=""

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="bloodhound-ce-python"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN=""

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="cd {INSTALL_LOCATION},{VENV_py3} && pip install .,mv bloodhound.py bloodhound-ce-python.py,{PATH_VENV3}"

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER="bloodhound-ce-python"

# RUN AFTER_COMMAND AFTER UPDATING
BYPASS_UPDATE="YES"