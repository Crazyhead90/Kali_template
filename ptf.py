#!/usr/bin/env python3
################################################
# Pentest Tool Framework (PTF)
# Originally written by: David Kennedy (ReL1K)
# 
# Fork with huge number of framework fixes
################################################

import sys
import subprocess
import os
import socket

# create launcher
def create_launcher():
	cwd = os.getcwd()
	filewrite = open("/usr/local/bin/ptf", "w")
	filewrite.write("#!/bin/bash\ncd %s \nchmod +x ptf\n./ptf $*" % (cwd))
	filewrite.close()
	subprocess.Popen("chmod +x /usr/local/bin/ptf", shell=True, executable='/bin/bash').wait()

# check for an Internet connection
def check_internet():
	try:
		rhost = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rhost.connect(('google.com', 0))
		rhost.settimeout(2)
		return 1

	except Exception:
		return 0


# some OS doesn't have /usr/local/bin create them if not
if not os.path.isdir("/usr/local/bin/"):
	os.makedirs("/usr/local/bin/")

if os.geteuid() != 0:
	print("\nPentest Tool Framework (PTF)")
	print("\nThis needs to be run as root. Exiting..")
	exit()

try:
	os.system("clear")
	# Bypass network check with argument
	if not "--no-network-connection" in sys.argv[1:]:
		# check internet connection
		if check_internet() == 0:
			print("[!] Unable to detect mandatory internet connection")
			print("[!] We will now exit PTF. Launch again when you got a connection.")
			print("[!] You can also run ptf with the --no-network-connection argument to bypass the network check.")
			sys.exit()

	if not os.path.isdir(os.getenv("HOME") + "/.ptf"):
		# run initial setup
		import src.core
		src.core.prep_install()
	else:
		os.system("sudo apt-get update -y")
	os.system("clear")
	if not os.path.isfile("/usr/local/bin/ptf"):
		# create automatic launcher
		create_launcher()

	# pull in the core library
	from src.core import *

	# pull in the framework
	import src.framework

	# if we want to skip going into module
	if  "--update-all" in sys.argv[1:]:
		src.framework.handle_prompt("use modules/install_update_all")
	elif "--update-installed" in sys.argv[1:]:
		src.framework.handle_prompt("use modules/update_installed")
	else:
		# or just ask what you want
		src.framework.mainloop()

except KeyboardInterrupt:
	print("\n")
	print("[*] Exiting PTF..")
	exit()

except Exception as e:
	print(("[!] Error: " + str(e)))
