#!/usr/bin/env python3
##########################
# Core functions for PTF
##########################

import os
import subprocess
import readline
import glob
import platform
import sys

# tab completion
def complete(text, state):
	a = (glob.glob(text + '*') + [None])[state].replace("__init__.py", "").replace(".py", "").replace("LICENSE", "").replace("README.md", "").replace("config", "").replace("ptf", "").replace("readme", "").replace("src", "").replace("msfdb.sh", "").replace("         ", "") + "/"
	a = a.replace("//", "/")
	if os.path.isfile(a[:-1] + ".py"):
		return a[:-1]
	else:
		return a

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

# color scheme for core
class bcolors:
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	ENDC = '\033[0m'

# get the main SET path
def definepath():
	if os.path.isfile("ptf"):
		return os.getcwd()

	else:
		if os.path.isdir("/usr/share/ptf/"):
			return "/usr/share/ptf/"
		else:
			return os.getcwd()

# main status calls for print functions
def print_status(message):
	print((bcolors.GREEN) + (bcolors.BOLD) + ("[*] ") + (bcolors.ENDC) + (str(message)))

def print_info(message):
	print((bcolors.BLUE) + (bcolors.BOLD) + ("[-] ") + (bcolors.ENDC) + (str(message)))

def print_warning(message):
	print((bcolors.YELLOW) + (bcolors.BOLD) + ("[!] ") + (bcolors.ENDC) + (str(message)))

def print_error(message):
	print((bcolors.RED) + (bcolors.BOLD) + ("[!] ") + (bcolors.ENDC) + (bcolors.RED) + (str(message)) + (bcolors.ENDC))

def set_title(title):
	sys.stdout.write("\x1b]2;%s\x07" % title)

# version information
version = "1.20.2 beta"

# banner
banner = """\n\n                          
                        
			 Pentest Tool Framework v%s
 \n\n""" % version

# check the config file and return value
def check_config(param):
	fileopen = open("%s/config/ptf.config" % (definepath()), "r")
	for line in fileopen:
		if line.startswith(param):
			line = line.rstrip()
			# remove any quotes or single quotes
			line = line.replace('"', "")
			line = line.replace("'", "")
			line = line.split("=")
			return line[1]

# parser module for module and term
def module_parser(filename, term):
	# if the file exists
	if os.path.isfile(filename) and not "install_update_all" in filename and ".py" in filename and not ".pyc" in filename:

		# set a base counter
		counter = 0

		# open the file
		fileopen = open(filename, "r")
		# iterate through the file
		for line in fileopen:
			# strip any bogus stuff
			line = line.rstrip()
			# if the line starts with the term
			if line.startswith(term):
				line = line.replace(term + '="', "")
				line = line.replace(term + "='", "")
				line = line.replace(term + "=", "")
				if str(line).endswith('"'): line = line[:-1]
				if str(line).endswith("'"): line = line[:-1]
				# reflect we hit this and our search term was found
				counter = 1
				return line

	# if the file isn't there
	if not os.path.isfile(filename):
		return None

# help menu for PTF
def show_help_menu():
	print(("Available from main prompt: " + bcolors.BOLD + "show modules" + bcolors.ENDC + "," + bcolors.BOLD + " show <module>" + bcolors.ENDC + "," + bcolors.BOLD + " search <name>" + bcolors.ENDC + "," + bcolors.BOLD + " use <module>" + bcolors.ENDC))
	print(("Inside modules:" + bcolors.BOLD + " info" + bcolors.ENDC + "," + bcolors.BOLD + " back" + bcolors.ENDC + "," + bcolors.BOLD + " show options" + bcolors.ENDC + "," + bcolors.BOLD + " set <option>" + bcolors.ENDC + "," + bcolors.BOLD + " run" + bcolors.ENDC))
	print(("Additional commands: " + bcolors.BOLD + " help" + bcolors.ENDC + "," + bcolors.BOLD + " ?" + bcolors.ENDC + "," + bcolors.BOLD + " clear" + bcolors.ENDC + "," + bcolors.BOLD + " cls" + bcolors.ENDC + "," + bcolors.BOLD + " version" + bcolors.ENDC + "," + bcolors.BOLD + " ver" + bcolors.ENDC + "," + bcolors.BOLD + " exit" + bcolors.ENDC + "," + bcolors.BOLD + " quit" + bcolors.ENDC))
	print(("Update or Install: " + bcolors.BOLD + "update" + bcolors.ENDC + "," + bcolors.BOLD + " upgrade" + bcolors.ENDC + "," + bcolors.BOLD + " install" + bcolors.ENDC + "," + bcolors.BOLD + " run" + bcolors.ENDC))

# exit message for PTF
def exit_ptf():
	print_status("Exiting..")

# this is the main handler to check what distribution we are using
# if it can't find it, will default to manual install base
def profile_os():
	# Check if we are running a Debian variant
	if os.path.isfile("/usr/bin/apt-get") or os.path.isfile("/usr/bin/aptitude"):
		return "DEBIAN"
	else:
		print_error("PTF currently only supports Debian-based systems.")
		print_error("Exiting...")
		sys.exit(1)

# this will run commands after install or update on a module
def after_commands(filename, install_location):
	from src.commands import after_commands
	commands = module_parser(filename, "AFTER_COMMANDS")
	if commands != "":
		commands = commands.replace("{VENV_py3}","python3 -m venv {INSTALL_LOCATION}/venv && source {INSTALL_LOCATION}/venv/bin/activate && pip3 install wheel") # Corrected comma to &&
		commands = commands.replace("{PATH_VENV3}","find . -maxdepth 1 -name '*.py' -exec sed -i '1i#!{INSTALL_LOCATION}/venv/bin/python3' {} \\; -exec chmod +x {} \\;") # More robust sed and chmod
		commands = commands.replace("{INSTALL_LOCATION}", install_location) # INSTALL_LOCATION replacement
		# PTF_LOCATION replacement
		if "{PTF_LOCATION}" in commands:
			commands = commands.replace("{PTF_LOCATION}", os.getcwd())
		print_status("Running post download commands for installation requirements..")
		after_commands(commands, install_location)
		print_status("Completed running after commands routine..")

# launcher - create launcher under /usr/local/bin
def launcher(filename, install_location):
	launcher_names_str = module_parser(filename, "LAUNCHER")

	if not launcher_names_str:  # Covers None or empty string
		return

	if "," in launcher_names_str:
		launcher_list = launcher_names_str.split(",")
	else:
		launcher_list = [launcher_names_str]

	for launcher_name in launcher_list:
		launcher_name = launcher_name.strip()
		if not launcher_name:  # Skip empty names if "a,,b" or "a, "
			continue

		if os.path.isfile("/usr/local/bin/" + launcher_name):
			os.remove("/usr/local/bin/" + launcher_name)
		if not os.path.isfile("/usr/local/bin/" + launcher_name):

			point = ""
			file_point = ""

			# Check for known filetypes to determine the command and target file
			if os.path.isfile(os.path.join(install_location, launcher_name)):
				point = "./" + launcher_name
				file_point = launcher_name
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".py")):
				point = "./" + launcher_name + ".py"
				file_point = launcher_name + ".py"
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".rb")):
				point = "./" + launcher_name + ".rb"
				file_point = launcher_name + ".rb"
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".pl")):
				point = "./" + launcher_name + ".pl"
				file_point = launcher_name + ".pl"
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".sh")):
				point = "./" + launcher_name + ".sh"
				file_point = launcher_name + ".sh"
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".exe")):
				point = "wine " + launcher_name + ".exe"
				file_point = launcher_name + ".exe"
			elif os.path.isfile(os.path.join(install_location, launcher_name + ".jar")):
				point = "java -jar " + launcher_name + ".jar"
				file_point = launcher_name + ".jar"

			if point and file_point:  # Ensure a command and target file were determined
				launcher_path = "/usr/local/bin/" + launcher_name
				with open(launcher_path, "w") as filewrite:
					filewrite.write('#!/bin/bash\ncd %s\n%s "$@"\n' % (install_location, point))
				
				target_file_full_path = os.path.join(install_location, file_point)
				subprocess.Popen("chmod +x %s %s" % (launcher_path, target_file_full_path), shell=True, executable='/bin/bash').wait()
				print_status("Created automatic launcher, you can run the tool from anywhere by typing: " + launcher_name)

# search functionality here
def search(term):
	term = term.replace("search ", "")
	module_files = []
	if "update" in term or "install" in term:
		module_files.append("modules/install_update_all")

	else:
		for dirpath, subdirs, files in os.walk("modules/"):
			for x in files:
				if x.endswith(".py"):
					if not "__init__.py" in x:
						path = os.path.join(dirpath, x)
						if term in path:
							x = x.replace(".py", "")
							module_files.append(os.path.join(dirpath, x))

						if not term in path:
							data = open(path, "r").readlines()
							# normally just searched entire file, but we don't
							# want to search # lines
							for line in data:
								line = line.rstrip()
								if term in line:
									if not line.startswith("#"):
										x = x.replace(".py", "")
										module_files.append(
											os.path.join(dirpath, x))
										break
	if module_files != []:
		print_status("Search results below:")
		for modules in module_files:
			print(modules)

	else:
		print_warning("Search found no results.")


# auto update packages
def auto_update():
	# if we want to do auto update
	check = check_config("AUTO_UPDATE=").lower()
	if check == "on":
		print_status("Auto updating is turned to on, installing normal package updates..")
		print_status("If you want to turn this off, go to the PTF config directory and set AUTO_UPDATE to OFF")
		if profile_os() == "DEBIAN":
			subprocess.Popen("sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get dist-upgrade -y && sudo apt-get autoremove -y && apt-get autoclean -y && updatedb >/dev/null 2>&1", shell=True, executable='/bin/bash').wait()
		print_status("Finished with normal package updates, moving on to the tools section..")
	else:
		print_status("Auto updating for packages is turned off, to enable go to the PTF config directory and set AUTO_UPDATE to ON.")

# check if a blank directory exists
def check_blank_dir(path):

	if os.path.isdir(path):
		if os.listdir(path) == []:
			print_status("Detected an empty folder, purging and re-checking out..")
			subprocess.Popen("rm -rf %s" % (path), shell=True, executable='/bin/bash').wait()

		# we put a second one in there in case the path was removed from above
		if os.path.isdir(path):
			if os.listdir(path) == ['.git', '.gitignore']:
				print_status("Detected an empty folder, purging and re-checking out..")
				subprocess.Popen("rm -rf %s" % (path), shell=True, executable='/bin/bash').wait()

# do platform detection on 32 or 64 bit
def arch():
	return str(platform.architecture()[0])

# check to see if we are running kali linux
def check_kali():
	if os.path.isfile("/etc/apt/sources.list"):
		kali = open("/etc/apt/sources.list", "r")
		kalidata = kali.read()
		if "kali" in kalidata:
			return "Kali"
		# if we aren't running kali
		else:
			return "Non-Kali"
	else:
		print("[!] Not running a Debian variant..")
		return "Non-Kali"
