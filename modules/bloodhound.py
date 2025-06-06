#!/usr/bin/env python3
#####################################
# Installation module for Bloodhound
#####################################

# AUTHOR OF MODULE NAME
AUTHOR="David Kennedy (ReL1K)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update Bloodhound - Reveal hidden relationships and attack paths in an Active Directory environment"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="FILE"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://raw.githubusercontent.com/Crazyhead90/pythontools/main/docker_installer.sh"

# EXTENSION OF THE RELEASE FILE (WITHOUT ".")
RELEASE_EXTENSION=""

# FILTER TO GRAB THE CORRECT RELEASE FILE
RELEASE_FILTER=""

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="bloodhound"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN=""

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="cd {INSTALL_LOCATION},chmod +x docker_installer.sh,./docker_installer.sh,chmod a+rx bloodhound_start.sh bloodhound_stop.sh bloodhound_delete_data.sh"

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER="bloodhound_start,bloodhound_stop,bloodhound_delete_data"

# RUN AFTER_COMMAND AFTER UPDATING
BYPASS_UPDATE="YES"