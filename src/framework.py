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

			# grab release extension
			release_extension = module_parser(filename, "RELEASE_EXTENSION")

			# grab release filename using filter
			release_filter = module_parser(filename, "RELEASE_FILTER")

			# grab install path
			# grab repository location
			repository_location = module_parser(filename, "REPOSITORY_LOCATION")

			base_install = check_config("BASE_INSTALL_PATH=")
			install_base_location = module_parser(filename, "INSTALL_LOCATION")

			module_parts = module.split('/') # e.g., ['modules', 'category', 'tool'] or ['modules', 'tool']
			path_components = [base_install]

			if len(module_parts) > 2: # Module has a category, e.g., modules/category/tool
				category_name = module_parts[1]
				path_components.append(category_name)
				path_components.append(install_base_location) # install_base_location is the tool's specific directory
			elif len(module_parts) == 2: # Module has no category, e.g., modules/tool
				# tool_name_from_path is the 'tool' part from 'modules/tool'
				tool_name_from_path = module_parts[1] 
				if tool_name_from_path == install_base_location:
					# Avoids /pentest/tool/tool if INSTALL_LOCATION is 'tool', path becomes /pentest/tool
					path_components.append(install_base_location) 
				else:
					# Path will be /pentest/tool_name_from_path/install_base_location
					# e.g., if module is modules/mytool and INSTALL_LOCATION is 'actual_install_dir'
					path_components.append(tool_name_from_path)
					path_components.append(install_base_location)
			install_location = os.path.expanduser(os.path.join(*path_components))
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


			# if we are updating the tools
			if prompt.lower() == "update" or prompt.lower() == "upgrade":
				# if we are using ignore modules then don't process
				if not "__init__.py" in filename and not ignore_module(filename):

					# move to the location
					if os.path.isdir(install_location):
						updated_something = False
						if install_type.lower() == "git":
							print_status("Updating the tool, be patient while git pull is initiated.")
							subprocess.Popen("cd %s;git fetch origin master;git reset --hard FETCH_HEAD;git clean -df" % (install_location), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							launcher(filename, install_location)
							after_commands(filename, install_location)
							print_status("Finished updating tool at location: " + (install_location))
							updated_something = True

						if install_type.lower() == "gitrelease":
							print_status("GITRELEASE: Fetching latest release asset for update.")
							if not repository_location:
								print_error("Repository location not set for gitrelease.")
							else:
								repo_parts = repository_location.split("/")
								if len(repo_parts) >= 2:
									repository_toolname = repo_parts[-1].rsplit(".git", 1)[0]
									repository_developer = repo_parts[-2]

									asset_url_command = (
										f"curl --silent \"https://api.github.com/repos/{repository_developer}/{repository_toolname}/releases/latest\" "
										f"| grep 'browser_download_url' "
										f"| head -n 1 "
										f"| cut -d '\"' -f 4"
									)
									proc = subprocess.Popen(asset_url_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
									asset_url_bytes, asset_err_bytes = proc.communicate()
									asset_url = asset_url_bytes.decode('utf-8').strip()

									if proc.returncode == 0 and asset_url:
										downloaded_filename = asset_url.split("/")[-1]
										if not os.path.isdir(install_location): # Should exist for update
											print_warning(f"Install location {install_location} not found for update, attempting to create.")
											subprocess.Popen(f"mkdir -p \"{install_location}\"", shell=True, executable='/bin/bash').wait()
										
										output_path = os.path.join(install_location, downloaded_filename)
										print_status(f"Updating by downloading {asset_url} to {output_path}")
										curl_download_cmd = f"curl -fL \"{asset_url}\" -o \"{output_path}\""
										download_proc = subprocess.Popen(curl_download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
										_, download_err_bytes = download_proc.communicate()

										if download_proc.returncode == 0:
											print_status(f"Finished updating to: {output_path}")
											updated_something = True
										else:
											print_error(f"Failed to download update from {asset_url}.")
											if download_err_bytes: print_error(f"Error: {download_err_bytes.decode('utf-8').strip()}")
									else:
										print_error(f"Could not determine download URL for gitrelease update: {repository_developer}/{repository_toolname}.")
										if asset_err_bytes: print_error(f"Error: {asset_err_bytes.decode('utf-8').strip()}")
								else:
									print_error(f"Invalid repository_location for gitrelease: {repository_location}")
							
							if updated_something:
								after_commands(filename, install_location) 
								launcher(filename, install_location)

						if install_type.lower() == "svn":
							print_status("Updating the tool, be patient while svn pull is initiated.")
							subprocess.Popen("cd %s;svn update" % (install_location), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash').wait()
							print_status("Finished updating tool at location: " + (install_location))
							after_commands(filename, install_location)
							launcher(filename, install_location)
							updated_something = True

						if updated_something or install_type.lower() not in ["git", "gitrelease", "svn"]:
							if install_type.lower() in ["file", "wget"]:
								print_status(f"'{install_type.upper()}' type module. 'Update' implies re-installing.")
								prompt = "install" 
							elif updated_something:
								print_status("Setting correct privileges on tools...")
								subprocess.Popen("chown -f -R %s:%s %s" % (tool_owner, tool_owner, install_location), shell=True, executable='/bin/bash').wait()
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
					# Non-Debian OS types (ARCHLINUX, FEDORA, OPENBSD) were removed
					# as per the request to only support DEBIAN.
					# The profile_os() function in core.py will now exit if not Debian.
					else:
						# This case should not be reached if profile_os() exits on non-Debian.
						print_error(f"Unsupported OS type: {ostype} encountered in install. PTF should have exited.")
						return "None" # or sys.exit()

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
						print_status("GITRELEASE was the selected method for installation... Using curl to install.")
						if not repository_location:
							print_error("Repository location not set for gitrelease.")
						else:
							repo_parts = repository_location.split("/")
							if len(repo_parts) >= 2:
								repository_toolname = repo_parts[-1].rsplit(".git", 1)[0]
								repository_developer = repo_parts[-2]

								asset_url_command = (
									f"curl --silent \"https://api.github.com/repos/{repository_developer}/{repository_toolname}/releases/latest\" "
									f"| grep 'browser_download_url' "
									f"| head -n 1 "
									f"| cut -d '\"' -f 4"
								)
								proc = subprocess.Popen(asset_url_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
								asset_url_bytes, asset_err_bytes = proc.communicate()
								asset_url = asset_url_bytes.decode('utf-8').strip()

								if proc.returncode == 0 and asset_url:
									downloaded_filename = asset_url.split("/")[-1]
									output_path = os.path.join(install_location, downloaded_filename)
									
									print_status(f"Installing now.. be patient by downloading {asset_url} to {output_path}")
									curl_download_cmd = f"curl -fL \"{asset_url}\" -o \"{output_path}\""
									download_proc = subprocess.Popen(curl_download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
									_, download_err_bytes = download_proc.communicate()

									if download_proc.returncode == 0:
										print_status(f"Finished installing! Enjoy the tool located under: {output_path}")
										after_commands(filename, install_location)  
										launcher(filename, install_location)
									else:
										print_error(f"Failed to download from {asset_url} for installation.")
										if download_err_bytes: print_error(f"Error: {download_err_bytes.decode('utf-8').strip()}")
								else:
									print_error(f"Could not determine download URL for gitrelease install for {repository_developer}/{repository_toolname}.")
									if asset_err_bytes: print_error(f"Error: {asset_err_bytes.decode('utf-8').strip()}")
							else:
								print_error(f"Invalid repository_location for gitrelease: {repository_location}")

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
		
					
def handle_prompt(prompt):
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

				all_debian_deps = []
				SPECIAL_MODULE_SCRIPTS = ('install_update_all.py', 'update_installed.py', '__init__.py')

				# first we install all depends for all applications
				print_status("We are going to first install all prereqs using apt before installing..")
				print_status("Cycling through modules and grabbing requirements..")
				
				for path, subdirs, files in os.walk(modules_path):
					for name in files:
						filename = os.path.join(path, name)

						if not name.endswith(".py") or name.endswith(".pyc") or name in SPECIAL_MODULE_SCRIPTS:
							continue

						# Handle custom_list if specified
						if "custom_list" in prompt[1]:
							try:
								with open(definepath() + "/" + prompt[1] + ".txt", "r") as custom_list_file:
									custom_list_content = custom_list_file.read()
								if name[:-3] not in custom_list_content: # name[:-3] to remove .py
									continue
							except FileNotFoundError:
								print_error(f"Custom list file {prompt[1]}.txt not found.")
								return # Exit if custom list is specified but not found

						if ignore_module(filename) or not include_module(filename) or ignore_update_all_module(filename):
							continue
						
						ostype = profile_os()
						if ostype == "DEBIAN":
							# module_parser expects full path for filename
							current_deps_str = module_parser(filename, "DEBIAN")
							if current_deps_str:
								all_debian_deps.extend(d.strip() for d in current_deps_str.split(',') if d.strip())
						elif ostype != "DEBIAN": # Should not be reached
							print_error(f"Unsupported OS type: {ostype} encountered in install_update_all. PTF should have exited.")
							return

				# install all of the packages at once
				ostype = profile_os()
				if ostype == "DEBIAN":
					if all_debian_deps:
						unique_deps = list(dict.fromkeys(all_debian_deps)) # Remove duplicates
						deb_modules_str = " ".join(unique_deps)
						if deb_modules_str:
							from src.platforms.debian import base_install_modules
							base_install_modules(deb_modules_str)
					print_status("Finished updating depends for modules.")

				for path, subdirs, files in os.walk(modules_path):
					for name in files:
						if "custom_list" in prompt[1] and name[:-4] not in open(definepath() + "/" + prompt[1] + ".txt").read():
							break
						# join the structure
						# The 'break' above should be 'continue' if it's to skip the current file and proceed with others in the same directory.
						# If it's 'break', it exits the inner loop (files in current path).
						# For consistency with the dependency loop, let's assume it means skip this file.
						if "custom_list" in prompt[1]:
							with open(definepath() + "/" + prompt[1] + ".txt", "r") as custom_list_file:
								if name[:-3] not in custom_list_file.read(): # name[:-3] to remove .py
									continue
						filename = os.path.join(path, name)
						if not name in SPECIAL_MODULE_SCRIPTS and not name.endswith(".pyc") and name.endswith(".py") and not ignore_module(filename) and include_module(filename) and not "custom_list" in filename : # custom_list.py is not a module
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
								if module and 'None' not in module: # Ensure module is not None
									print(f"Updating {module}")
									use_module(module, 2)
			else:
				print(f"No modules currently installed at {base_install}")

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
