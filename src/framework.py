#!/usr/bin/env python3
###########################
# PTF main framework code
###########################

from src.core import *
import sys
import readline
import os
import time

# print the main welcome banner
print(banner)

# blank variables used later
deb_modules = ""
arch_modules = ""
fedora_modules = ""
openbsd_modules = ""

# grab current user
if 'SUDO_USER' in os.environ:
	tool_owner = os.environ['SUDO_USER']
else:
	tool_owner = os.environ['USER']

userpath = check_config("USERNAME_PATH=")
filewrite = open(userpath, "w")
filewrite.write(tool_owner)
filewrite.close()

# determine operating system
if check_kali() == "Kali":
	os_profile = "Kali"
else:
	os_profile = profile_os()

print_status("Operating system detected as: " + bcolors.BOLD + os_profile + bcolors.ENDC)

# main intro here
if profile_os() == "DEBIAN":
	subprocess.Popen("sudo dpkg --add-architecture i386", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()

print_status("Welcome to PTF")

base_install = check_config("BASE_INSTALL_PATH=")
if not os.path.exists(base_install):
	print_warning("First launch detected, consider rebooting to process apt updates and upgrades!")

print("""
For a list of available commands type ? or help
""")

ignore_update_these = []
if check_config("IGNORE_UPDATE_ALL_MODULES") is not None:
	ignore_update_these = check_config("IGNORE_UPDATE_ALL_MODULES").split(",")

def ignore_update_all_module(module):
	result = False
	for check in ignore_update_these:
		if "/*" in check:
			if check[:-1] in module:
				result = True
		else:
			if (os.getcwd() + "/" + check + ".py") == module:
				result = True
	return result

ignore_these = []
if check_config("IGNORE_THESE_MODULES") is not None:
	ignore_these = check_config("IGNORE_THESE_MODULES").split(",")
	if ignore_these[0] != "":
		if ignore_these[0] != '"':
			print_info("Ignoring the following modules: " + (", ").join(ignore_these))

# ignore modules if they are specified in the ptf.config
def ignore_module(module):
	result = False
	for check in ignore_these:
		if "/*" in check:
			if check[:-1] in module:
				result = True
		else:
			if (os.getcwd() + "/" + check + ".py") == module:
				result = True
	if result:
		print_warning("Ignoring module: " + module)

	return result

include_these = []
if check_config("INCLUDE_ONLY_THESE_MODULES") is not None:
	include_these = check_config("INCLUDE_ONLY_THESE_MODULES").split(",")
	if include_these[0] != "":
		if include_these[0] != '"':
			print_info("Including only the following modules: " + (", ").join(include_these))
		else:
			include_these = []
	else:
		include_these = []

# include only particular modules if they are specified in the ptf.config
def include_module(module):
	if not include_these:
		return True

	result = False
	for check in include_these:
		if "/*" in check:
			if check[:-1] in module:
				result = True
		else:
			if (os.getcwd() + "/" + check + ".py") == module:
				result = True
	if result:
		print_status("Including module: " + module)

	return result

# check the folder structure
def show_module():
	modules_path = os.getcwd() + "/modules/"
	print("\n")
	print((bcolors.BOLD + "Modules" + bcolors.ENDC))
	print(("""=======

   """) + (bcolors.BOLD) + ("""Name                                                 Description """) + (bcolors.ENDC) + ("""
   ----                                                 -----------
	"""))

	print("   modules/install_update_all                           This will install or update all tools with modules within PTF")
	print("   modules/update_installed                             This will update all installed tools within PTF")

	for path, subdirs, files in os.walk(modules_path):
		for name in files:
			# join the structure
			filename = os.path.join(path, name)
			# strip un-needed files
			if not name in ('__init__.py', 'install_update_all.py', 'update_installed.py'):
				# shorten it up a little bit
				filename_short = filename.replace(os.getcwd() + "/", "")
				filename_short = filename_short.replace(".py", "")
				filename_short = str(filename_short)
				description = module_parser(filename, "DESCRIPTION")
				# print the module name
				if description != None:
					temp_number = 53 - len(filename_short)
					print("   " + filename_short + " " * temp_number + description)
	print("\n")

def show_new_modules():
	modules_path = os.getcwd() + "/modules/"
	for path, subdirs, files in os.walk(modules_path):
		for name in files:
			filename = os.path.join(path, name)
			if not name in ('__init__.py', 'install_update_all.py', 'update_installed.py'):
				filename_short = filename.replace(os.getcwd() +"/","")
				filename_short = filename_short.replace(".py","")
				filename_short = str(filename_short)
				description = module_parser(filename, "DESCRIPTION")
				location = module_parser(filename,"INSTALL_LOCATION")
				if not ((location is None) or (os.path.exists(os.path.join(path.replace("ptf/modules/",""), location)))):
					if description != None:
						temp_number = 53 - len(filename_short)
						print("   " + filename_short + " " * temp_number + description)
	print("\n")

def discover_module_filename(module):
	SPECIAL_MODULE_NAMES = ("install_update_all", "update_installed", "custom_list", "__init__",)
	module_suffix = ".txt" if "custom_list" in module else ".py"

	# is module already a path?
	if '/' in module or any(map(module.__contains__, SPECIAL_MODULE_NAMES)):
		return definepath() + "/" + module + module_suffix

	# find module
	modules_path = os.getcwd() + "/modules/"
	for path, subdirs, files in os.walk(modules_path):
		for name in sorted(files):
			if name in ('__init__.py', 'install_update_all.py', 'update_installed.py'):
				continue
			name_short = name.replace(".py","")
			if name_short == module:
			   return os.path.join(path, name)

	raise Exception("module not found")

def filename_to_module(filename):
	module = filename.replace(os.getcwd() +"/","").replace(".py","")
	return str(module)

# this is when a use <module> command is initiated
def use_module(module, all_trigger):

	# if we aren't using all
	if not "install_update_all" in module and not "update_installed" in module and not "__init__" in module and not "custom_list" in module:

		# set terminal title
		set_title("ptf - %s" % module)

		# if we are using a normal module
		if int(all_trigger) == 0 or int(all_trigger) == 1 or int(all_trigger) == 2:
			filename = discover_module_filename(module)
			module = filename_to_module(filename)

			# grab the author
			try:
				author = module_parser(filename, "AUTHOR")

			except TypeError:
				author = "Invalid"

			# grab the description
			description = module_parser(filename, "DESCRIPTION")

			# grab install type
			install_type = module_parser(filename, "INSTALL_TYPE")

			# if were are tool depends for other modules prior to install
			tool_depend = module_parser(filename, "TOOL_DEPEND")

			# grab repository location
			repository_location = module_parser(filename, "REPOSITORY_LOCATION")

			# grab release extension
			release_extension = module_parser(filename, "RELEASE_EXTENSION")

			# grab release filename using filter
			release_filter = module_parser(filename, "RELEASE_FILTER")

			# here we check if we need to do x86 or x64
			if module_parser(filename, "X64_LOCATION") != "":
				# grab architecture
				arch_detect = arch()
				if "64bit" in arch_detect:
					repository_location = module_parser(filename, "X64_LOCATION")

			# grab install path
			base_install = check_config("BASE_INSTALL_PATH=")
			install_base_location = module_parser(filename, "INSTALL_LOCATION")
			module_split = module.split("/")
			module_split = module_split[1]
			install_location = os.path.expanduser(base_install + "/" + module_split + "/" + install_base_location)
			#tool_owner = check_config("TOOL_OWNER=")
			#tool_group = check_config("TOOL_GROUP=")

		while 1:

			# if we aren't doing update/install all
			if int(all_trigger) == 0:
				try:
					prompt = input(bcolors.BOLD + "ptf:" + bcolors.ENDC + "(" + bcolors.RED + "%s" % module + bcolors.ENDC + ")>")
				except EOFError:
					prompt = "back"
					print("")

				# exit if we need to
				if prompt == "back":
					return "None"

				# if we want to exit out
				if prompt == "quit" or prompt == "exit":
					exit_ptf()
					sys.exit()

				# show the help menu
				if prompt == "?" or prompt == "help":
					show_help_menu()

				# clear the screen
				if prompt == "cls" or prompt == "clear":
					os.system("clear")

				# show modules
				if prompt == "show modules":
					print_warning("In order to show modules, you must type 'back' first")

				# if we are using a module within a module we return our prompt 
				if "use " in prompt:
					return prompt

				# if we are searching for something
				if "search " in prompt:
					search(prompt)

				if prompt == "ver" or prompt == "version":
					print(version)

				# show info of a module
				if prompt.lower() == "info":
					if module != "modules/install_update_all":
						print("\n")
						print(bcolors.BOLD + "Module Author:         " + bcolors.ENDC + author)
						print(bcolors.BOLD + "Module Description:    " + bcolors.ENDC + description)
						print("-------------------------------------------------------------------------------------")
						print(bcolors.BOLD + "INSTALL_TYPE           " + bcolors.ENDC + install_type)
						print(bcolors.BOLD + "REPOSITORY_LOCATION    " + bcolors.ENDC + repository_location)
						print(bcolors.BOLD + "INSTALL_LOCATION       " + bcolors.ENDC + install_location)
						print("-------------------------------------------------------------------------------------")

				# options menu - was a choice here to load upon initial load of dynamically pull each time
				# if changes are made, it makes sense to keep it loading each
				# time
				if prompt.lower() == "show options":
					if module != "modules/install_update_all":
						print("Module options (%s):" % module)
						print("\n")
						print(bcolors.BOLD + "INSTALL_TYPE          " + bcolors.ENDC + install_type)
						print(bcolors.BOLD + "REPOSITORY_LOCATION   " + bcolors.ENDC + repository_location)
						print(bcolors.BOLD + "INSTALL_LOCATION      " + bcolors.ENDC + install_location)

				# if we are setting the command now
				if prompt.lower().startswith("set"):
					# need to grab the options
					set_breakout = prompt.split(" ")
					# here we rewrite the options for the menu
					if set_breakout[1].upper() == "INSTALL_TYPE":
						install_type = set_breakout[2]
					if set_breakout[1].upper() == "REPOSITORY_LOCATION":
						repository_location = set_breakout[2]
					if set_breakout[1].upper() == "INSTALL_LOCATION":
						install_location = set_breakout[2]

			if int(all_trigger) == 1:
				prompt = "run"
			
			if int(all_trigger) == 2:
				prompt = "update"

			# if we are using run, check first to see if its there, if so, do
			# an upgrade
			if prompt.lower() == "run":

				# check if empty directory - if so purge it before anything
				# else
				check_blank_dir(install_location)

				if os.path.isdir(install_location):
					print_status("Detected installation already. Going to upgrade for you.")
					prompt = "update"
				else:
					print_status("Tool not installed yet, will run through install routine")
					prompt = "install"

			# check to see if we need to bypass after commands for certain
			# files - this is needed when using FILE and others where after
			# commands need to be run
			if module_parser(filename, "BYPASS_UPDATE") == "YES":
				if prompt.lower() == "update":
					prompt = "install"

			# if we are updating the tools
			if prompt.lower() == "update" or prompt.lower() == "upgrade":
				# if we are using ignore modules then don't process
				if not "__init__.py" in filename and not ignore_module(filename):

					if len(tool_depend) > 1:
						print_status("Tool depends on other modules, installing dependencies...")
						try:
							if " " in tool_depend: 
								tool_depend = tool_depend.split(" ")
								for tool in tool_depend: use_module(tool, "1")

							elif "," in tool_depend: 
								tool_depend = tool_depend.split(",")
								for tool in tool_depend: use_module(tool, "1")

							else: use_module(tool_depend, "1")
						except: pass

					# move to the location
					if os.path.isdir(install_location):
						if install_type.lower() == "git":
							print_status("Updating the tool, be patient while git pull is initiated.")
							#subprocess.Popen("cd %s;git pull" % (install_location), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							proc = subprocess.Popen("cd %s;git fetch origin master;git reset --hard FETCH_HEAD;git clean -df" % (install_location), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()

							# check launcher
							launcher(filename, install_location)

							# here we check to see if we need anything we need to
							# run after things are updated
							update_counter = 0
							#if not "Already up-to-date." in proc: #.communicate()[0]:
								#after_commands(filename, install_location)
							#	update_counter = 1
							#else: 
							#	print_status("Tool already up-to-date!")
							
							print_status("Finished installing at location: " + (install_location))
							# run after commands
							#if prompt != "update":
							if update_counter == 0:
									#after_commands(filename, install_location)
									print_status("Finished installing!")

						if install_type.lower() == "gitrelease":
							print_status("Updating the tool, be patient while pull is initiated.")
							repository_file = repository_location.split("/")[-1]
							repository_developer = repository_location.split("/")[-2]
							repository_toolname = repository_location.split("/")[-1].rsplit(".git", 1)[0]

							release_extension = release_extension.replace(".", "")

							if release_filter == "":
								subprocess.Popen("curl $(curl --silent https://api.github.com/repos/%s/%s/releases/latest | grep browser_download_url | grep .%s | head -n 1 | cut -d : -f 2,3 | cut -d '\"' -f 2) -o %s/%s.%s -L" % (repository_developer, repository_toolname, release_extension, install_location, install_base_location, release_extension), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							else:
								subprocess.Popen("curl $(curl --silent https://api.github.com/repos/%s/%s/releases/latest | grep browser_download_url | grep .%s | grep %s | head -n 1 | cut -d : -f 2,3 | cut -d '\"' -f 2) -o %s/%s.%s -L" % (repository_developer, repository_toolname, release_extension, release_filter, install_location, install_base_location, release_extension), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()

							print_status("Finished installing at location: " + (install_location))
							after_commands(filename, install_location) 
							launcher(filename, install_location)

						if install_type.lower() == "svn":
							print_status("Updating the tool, be patient while svn pull is initiated.")
							# here we do some funky stuff to store old
							# revisions
							proc = subprocess.Popen("cd %s;svn update" % (install_location), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							try:
								if not os.path.isfile(install_location + "/.goatsvn_storage"):
									filewrite = open(install_location + "/.goatsvn_storage", "w")
									filewrite.write(proc.communicate()[0])
									filewrite.close()

								if os.path.isfile(install_location + "/.goatsvn_storage"):
									cmp = open(install_location + "/.goatsvn_storage", "r").read()
									# if we are at a new revision
									if cmp != proc.communicate()[0]:
										# change prompt to something other than
										# update
										prompt = "goat"
							except:
								pass
							finally:
								proc.wait()
							print_status("Finished installing at location: " + (install_location))

							# run after commands
							if prompt != "update":
								after_commands(filename, install_location)

							# check launcher
							launcher(filename, install_location)

						print_status("Setting correct privileges on tools...")
						subprocess.Popen("chown -f -R %s:%s %s" % (tool_owner, tool_owner, install_location), shell=True, executable='/bin/bash').wait()

						# Additional methods
						#subprocess.Popen("chown -f -R ${TOOLUSER:=$(grep \":1000:\" /etc/passwd | cut -d : -f 1)}:$TOOLUSER %s" % (install_location), shell=True, executable='/bin/bash').wait()
						#subprocess.Popen("chown -f -R %s:%s %s" % (tool_owner, tool_group, install_location), shell=True, executable='/bin/bash').wait()

						print_status("Running updatedb to tidy everything up.")
						subprocess.Popen("updatedb >/dev/null 2>&1", shell=True, executable='/bin/bash').wait()

					if not os.path.isdir(install_location):
						print_error("The tool was not found in the install location. Try running install first!")

			# if we want to install it
			if prompt.lower() == "install":
				# if we are using ignore modules then don't process
				if not "__init__.py" in filename and not ignore_module(filename):

					# grab the OS type, DEBIAN, FEDORA, CUSTOM, BSD!!!! WOW!!,
					ostype = profile_os()

					# if OSTYPE is DEBIAN
					if ostype == "DEBIAN":
						print_status("Preparing dependencies for module: " + module)

						from src.platforms.debian import base_install_modules
						# grab all the modules we need
						deb_modules = module_parser(filename, "DEBIAN")
						base_install_modules(deb_modules)
						print_status("Pre-reqs for %s have been installed." % (module))

					# if OSTYPE is ARCHLINUX
					if ostype == "ARCHLINUX":
						print_status("Preparing dependencies for module: " + module)
						from src.platforms.archlinux import base_install_modules
						# grab all the modules we need
						arch_modules = module_parser(filename, "ARCHLINUX")
						base_install_modules(arch_modules)
						print_status("Pre-reqs for %s have been installed." % (module))

					# if OSTYPE is FEDORA
					if ostype == "FEDORA":
						print_status("Preparing dependencies for module: " + module)
						from src.platforms.fedora import base_install_modules
						# grab all the modules we need
						fedora_modules = module_parser(filename, "FEDORA")
						base_install_modules(fedora_modules)
						print_status("Pre-reqs for %s have been installed." % (module))

					# if OSTYPE is OPENBSD
					if ostype == "OPENBSD":
						print_status("Preparing dependencies for module: " + module)
						from src.platforms.openbsd import base_install_modules
						# grab all the modules we need
						openbsd_modules = module_parser(filename, "OPENBSD")
						base_install_modules(openbsd_modules)
						print_status("Pre-reqs for %s have been installed." % (module))

					if len(tool_depend) > 1:
						print_status("Tool depends on other modules, installing dependencies...")
						try:
							if " " in tool_depend: 
								tool_depend = tool_depend.split(" ")
								for tool in tool_depend: use_module(tool, "1")

							elif "," in tool_depend: 
								tool_depend = tool_depend.split(",")
								for tool in tool_depend: use_module(tool, "1")

							else: use_module(tool_depend, "1")
						except: pass

					print_status("Making the appropriate directory structure first")
					subprocess.Popen("mkdir -p %s" % install_location, shell=True, executable='/bin/bash').wait()

					# if we are using git
					if install_type.lower() == "git":
						# if there are files in the install_location, we'll update.
						if os.listdir(install_location):
							print_status("Installation already exists, going to git pull then run after commands..")
							#subprocess.Popen("cd %s;git pull" % (install_location), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							subprocess.Popen("cd %s;git fetch origin master;git reset --hard FETCH_HEAD;git clean -df" % (install_location), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							print_status("Finished updating the tool located in: " + install_location)
						else:
							print_status("GIT was the selected method for installation.. Using GIT to install.")
							print_status("Installing now..")
							subprocess.Popen("git clone %s %s" % (repository_location, install_location), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							print_status("Finished installing! Enjoy the tool located under: " + install_location)
						after_commands(filename, install_location)
						launcher(filename, install_location)

					# if we are using git release
					if install_type.lower() == "gitrelease":
						# if there are files in the install_location, we'll update.
						print_status("GITRELEASE was the selected method for installation... Using curl to install.")
						repository_file = repository_location.split("/")[-1]
						repository_developer = repository_location.split("/")[-2]
						repository_toolname = repository_location.split("/")[-1].rsplit(".git", 1)[0]

						release_extension = release_extension.replace(".", "")
		
						print_status("Installing now.. be patient...")

						if release_filter == "":
							subprocess.Popen("curl $(curl --silent https://api.github.com/repos/%s/%s/releases/latest | grep browser_download_url | grep .%s | head -n 1 | cut -d : -f 2,3 | cut -d '\"' -f 2) -o %s/%s.%s -L" % (repository_developer, repository_toolname, release_extension, install_location, install_base_location, release_extension), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
						else:
							subprocess.Popen("curl $(curl --silent https://api.github.com/repos/%s/%s/releases/latest | grep browser_download_url | grep .%s | grep %s | head -n 1 | cut -d : -f 2,3 | cut -d '\"' -f 2) -o %s/%s.%s -L" % (repository_developer, repository_toolname, release_extension, release_filter, install_location, install_base_location, release_extension), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()

						print_status("Finished installing! Enjoy the tool located under: " + install_location)
						after_commands(filename, install_location)  
						launcher(filename, install_location)

					# if we are using svn
					if install_type.lower() == "svn":
						print_status("SVN was the selected method for installation.. Using SVN to install.")
						subprocess.Popen("svn co %s %s" % (repository_location, install_location), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
						print_status("Finished installing! Enjoy the tool located under: " + install_location)
						after_commands(filename, install_location)
						launcher(filename, install_location)

					# if we are using file
					if install_type.lower() == "file":
						print_status("FILE was the selected method for installation.. Using curl -o to install.")
						repository_file = repository_location.split("/")[-1]
						subprocess.Popen('curl -k -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.112 Safari/534.30" -o %s/%s %s' % (install_location, repository_file, repository_location), stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
						print_status("Finished installing! Enjoy the tool located under: " + install_location)
						after_commands(filename, install_location)
						launcher(filename, install_location)

					# if we are using wget
					if install_type.lower() == "wget":
						print_status("WGET was the selected method for installation because it plays better than curl -l with recursive URLs.")
						subprocess.Popen("cd %s && wget -q %s" % (install_location, repository_location), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
						print_status("Finished installing! Enjoy the tool located under: " + install_location)
						after_commands(filename, install_location)
						launcher(filename, install_location)

					print_status("Setting correct privileges on tools..")
					subprocess.Popen("chown -f -R %s:%s %s" % (tool_owner, tool_owner, install_location), shell=True, executable='/bin/bash').wait()

					# Additional methods
					#subprocess.Popen("chown -f -R ${TOOLUSER:=$(grep \":1000:\" /etc/passwd | cut -d : -f 1)}:$TOOLUSER %s" % (install_location), shell=True, executable='/bin/bash').wait()
					#subprocess.Popen("chown -f -R %s:%s %s" % (tool_owner, tool_group, install_location), shell=True, executable='/bin/bash').wait()

					print_status("Running updatedb to tidy everything up.")
					subprocess.Popen("updatedb >/dev/null 2>&1", shell=True, executable='/bin/bash').wait()

			# if we update all we need to break out until finished
			if int(all_trigger) == 1 or int(all_trigger) == 2:
				break

# searches in the directory to find a file that references the location
def find_containing_file(directory, location):
	try:
		print("Finding %s in %s"%(location, directory))
		for file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
			with open(os.path.join(directory,file)) as handle:
				for line in handle:
					if ('INSTALL_LOCATION="%s"' % location) in line:
						return os.path.splitext(file)[0]
	except OSError:
		print_warning("%s is not managed by PTF" % location)
		# Didn't find anything, returning None
		return None
		
					
def handle_prompt(prompt, force=False):
	# specify no commands, if counter increments then a command was found
	base_counter = 0
	
	# main help menu
	if prompt == "?" or prompt == "help":
		show_help_menu()
		base_counter = 1

	# if we want to clear the screen
	if prompt == "cls" or prompt == "clear":
		base_counter = 1
		os.system("clear")

	# if we want to exit out
	if prompt == "quit" or prompt == "exit":
		base_counter = 1
		exit_ptf()
		sys.exit()

	# if we want to see the modules
	if prompt == "show modules":
		base_counter = 1
		show_module()

	# list new modules
	if prompt == "show new modules":
		base_counter = 1
		show_new_modules()

	# search functionality here
	if prompt.startswith("search"):
		base_counter = 1
		search(prompt)

	if prompt == "ver" or prompt == "version":
		base_counter = 1
		print(version)

	# if we want to use a module
	if prompt.startswith("use"):
		base_counter = 1
		counter = 0
		prompt = prompt.split(" ")

		# do a quick sanity check to see if the module is there first
		if "install_update_all" in prompt[1]:
			counter = 3
			try:
				install_query = input("[*] You are about to install/update everything. Proceed? [yes/no]:")
			except EOFError:
				install_query = "no"
				print("")
			if install_query.lower() == "yes" or install_query.lower() == "y":

				# do auto update check first
				auto_update()
				
				if not "custom_list" in prompt[1]:
					modules_path = definepath() + "/" + (prompt[1])[:-18]
				else:
					modules_path = definepath() + "/modules/"

				# base holder for all debian packages
				deb_modules = ""
				# base holder for all arch packages
				arch_modules = ""
				# base holder for all fedora packages
				fedora_modules = ""
				# base holder for all openbsd packages
				openbsd_modules = ""

				# first we install all depends for all applications
				print_status("We are going to first install all prereqs using apt before installing..")
				print_status("Cycling through modules and grabbing requirements..")
				
				for path, subdirs, files in os.walk(modules_path):
					for name in files:
						if "custom_list" in prompt[1] and name[:-4] not in open(definepath() + "/" + prompt[1] + ".txt").read():
							break
						# join the structure
						filename = os.path.join(path, name)
						# strip un-needed files
						if not "__init__.py" in filename and not ignore_module(filename) and include_module(filename) and ".py" in filename and not ".pyc" in filename and not ignore_update_all_module(filename):
							# shorten it up a little bit
							filename_short = filename.replace(os.getcwd() + "/", "")
							# update depend modules
							filename_short = str(filename_short)
							ostype = profile_os()
							if ostype == "DEBIAN":
								if not "install_update_all" in filename_short:
									from src.platforms.debian import base_install_modules
									# grab all the modules we need
									deb_modules = deb_modules + "," + module_parser(filename_short, "DEBIAN")

							# archlinux
							if ostype == "ARCHLINUX":
								if not "install_update_all" in filename_short:
									from src.platforms.archlinux import base_install_modules
									# grab all the modules we need
									arch_modules = ""
									arch_modules = arch_modules + "," + module_parser(filename_short, "ARCHLINUX")
							# fedora
							if ostype == "FEDORA":
								if not "install_update_all" in filename_short:
									from src.platforms.fedora import base_install_modules
									# grab all the modules we need
									fedora_modules = fedora_modules + "," + module_parser(filename_short, "FEDORA")
							# openbsd
							if ostype == "OPENSBD":
								if not "install_update_all" in filename_short:
									from src.platforms.openbsd import base_install_modules
									# grab all the modules we need
									openbsd_modules = openbsd_modules + "," + module_parser(filename_short, "OPENBSD")

				# install all of the packages at once
				ostype = profile_os()
				if ostype == "DEBIAN":
					deb_modules = deb_modules.replace(",", " ")
					if deb_modules != "":
						base_install_modules(deb_modules)
					print_status("Finished updating depends for modules.")

				if ostype == "ARCHLINUX":
					arch_modules = arch_modules.replace(",", " ")
					if arch_modules != "":
						base_install_modules(arch_modules)
					print_status("Finished updating depends for modules.")

				if ostype == "FEDORA":
					fedora_modules = fedora_modules.replace(",", " ")
					if fedora_modules != "":
						base_install_modules(fedora_modules)
					print_status("Finished updating depends for modules.")

				if ostype == "OPENBSD":
					openbsd_modules = openbsd_modules.replace(",", " ")
					if openbsd_modules != "":
						base_install_modules(openbsd_modules)
					print_status("Finished updating depends for modules.")

				for path, subdirs, files in os.walk(modules_path):
					for name in files:
						if "custom_list" in prompt[1] and name[:-4] not in open(definepath() + "/" + prompt[1] + ".txt").read():
							break
						# join the structure
						filename = os.path.join(path, name)
						if not "__init__.py" in filename and not ignore_module(filename) and include_module(filename) and ".py" in filename and not ".pyc" in filename and not "install_update_all" in filename and not "__init__" in filename and not "custom_list" in filename:
							# strip un-needed files
							# if not "__init__.py" in filename and not ignore_module(filename):
							# shorten it up a little bit
							filename_short = filename.replace(os.getcwd() + "/", "")
							filename_short = filename_short.replace(".py", "")
							# check if empty directory - if so purge it before
							# anything else
							check_blank_dir(path)
							print_status("Installing and/or updating: " + filename_short)
							# run the module for install
							use_module(filename_short, "1")
							# sleep a sec
							time.sleep(0.2)

				# clear the screen
				print_status("All finished installing and/or updating.\n")

			else:
				print_status("Cancelled installing and/or updating.")

		if "update_installed" in prompt[1]:
			counter = 3
			base_install = check_config("BASE_INSTALL_PATH=")

			if os.path.exists(base_install) and os.listdir(base_install) != []:
				for dir in os.listdir(base_install): # ptf dir
				# ignore PTF directory
					if not 'ptf' == dir  and not os.path.isfile(dir):
						for subdir in os.listdir(os.path.join(base_install, dir)): # module
							# Ignore normal files
							if not os.path.isfile(subdir):                             
								module = "modules/%s/%s"%(dir, subdir)
								# If the install file and install directory differ, search the correct file
								if(not os.path.isfile(module + '.py')):
									install_file = find_containing_file("modules/%s"%dir, subdir)
									module = "modules/%s/%s"%(dir, install_file)
								# Only update if we have an install file
								if not 'None' in module:
									print("Updating %s") % module
									use_module(module, 2)
			else:
				print("No modules currently installed at %s") % base_install

		if os.path.isfile(discover_module_filename(prompt[1])):
			counter = 1

		if counter == 1:
			while 1:
				try:
					module = use_module(prompt[1], "0")
					if "use " in module: 
						prompt = module.split(" ")
					else: break
				except Exception: break

		if counter == 0:
			print_error("Module name was not found, try retyping it again.")

	# if blanks are used
	if prompt == "":
		base_counter = 1

	if base_counter == 0:
		# else try to run as normal command
		#subprocess.Popen("%s" % (prompt), shell=True, executable='/bin/bash').wait()
		print_warning("Command was not found, try help or ? for more information.")

# start the main loop
def mainloop():

	while 1:
		# set title
		set_title("Pentest Tool Framework (PTF) v%s" % version)

		try:
			prompt = input(bcolors.BOLD + "ptf" + bcolors.ENDC + "> ")
		except EOFError:
			prompt = "quit"
			print("")
		handle_prompt(prompt)
