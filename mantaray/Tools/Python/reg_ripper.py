#!/usr/bin/env python3
#This program runs regripper (written by Harlan Carvey) for each registry hive found in a Disk Image

#########################COPYRIGHT INFORMATION############################
#Copyright (C) 2011 dougkoster@hotmail.com				                 #
#This program is free software: you can redistribute it and/or modify    #
#it under the terms of the GNU General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or       #
#(at your option) any later version.                                     #
                                                                         #
#This program is distributed in the hope that it will be useful,         #
#but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#GNU General Public License for more details.                            #
                                                                         #
#You should have received a copy of the GNU General Public License       #
#along with this program.  If not, see http://www.gnu.org/licenses/.     #
#########################COPYRIGHT INFORMATION############################

#import modules
from easygui import *
from get_case_number import *
from get_output_location import *
from select_file_to_process import *
from select_folder_to_process import *
from parted import *
from mmls import *
from mount import *
from mount_ewf import *
from get_ntuser_paths import *
from get_usrclass_paths import *
from get_system_paths import *
from done import *
from unix2dos import *

import os
from os.path import join
import re
import io
import sys
import string
import subprocess
import pickle
import datetime

### GET ACCOUNT PROFILE NAMES #####################################

def get_account_profile_names(account):

	#This function takes the absolute path of the NTUSER.DAT file within a user's profile and returns the profile name
	#Example: If you pass the function this string: -> /mnt/windows_mount/Documents and Settings/Mr. Evil/NTUSER.DAT
	#it returns -> Mr. Evil

	#get substring to strip out /NTUSER.DAT from the string
	account_sub = account[:-11]

	#get length of account_sub
	account_sub_string_length = len(account_sub)

	#now that we have the length of the root string we need to find the offset of the last "/" in the string, then do a substring from that location
	#to the end of the string to get the user profile name
	rightmost_slash_location = account_sub.rindex('/')

	#calculate substring to just pull out the user name
	username = account_sub[(rightmost_slash_location+1):account_sub_string_length]
	return username	
	
	
### GET ACCOUNT PROFILE NAMES #####################################

### GET ACCOUNT PROFILE NAMES USRCLASS.DAT #####################################

def get_account_profile_names_usrclass(account):
  #This function takes the absolute path of the location of the USRCLASS.DAT file and returns the profile name where it was found
  
  print("The account is: " + account)

  #determine if system is running XP or above
  if(re.search("Documents and Settings", account)):
    print("We found Documents and Settings - this is an XP machine")
    #get substring that strips out the last 45 characters of the account absolute path
    usrclass_sub_string = account[:-63]
  else:
    #get substring that strips out the last 45 characters of the account absolute path (Windows Vista and 7)
    usrclass_sub_string = account[:-45]

  print("The shortened path is: " + usrclass_sub_string)

  #get length of usrclass_sub_string
  usrclass_sub_string_length = len(usrclass_sub_string)

  #get rightmost slash location 
  rightmost_slash_location = usrclass_sub_string.rindex('/')

  #get length of username
  username_length = ((usrclass_sub_string_length - rightmost_slash_location)-1)

  #calculate substring to just pull out the username
  username1 = usrclass_sub_string[(rightmost_slash_location+1):usrclass_sub_string_length]
  print("The username for this USRCLASS.DAT file is: " + username1)
  return username1


### GET ACCOUNT PROFILE NAMES USRCLASS.DAT #####################################
### CREATE SPLASH SCREEN ##

intro_splashscreen = buttonbox(msg='RUN REGISTRY RIPPER', image='/home/sansforensics/Tools/Python/images/cropped-regripper1.GIF',title='REG-RIPPER', choices=('Continue', 'Exit'))
if intro_splashscreen == "Exit":
	sys.exit(0)

#set up plugins for USRCLASS.DAT
usrclass_plugins = ("bagtest2", "muicache")

#set up plugins for NTUSER.DAT##
ntuser_plugins = ("ares", "vmplayer", "printers", "mspaper", "streammru", "acmru", "logonusername", "winzip", "appcompatflags", "controlpanel", "startmenuinternetapps_lm", "recentdocs", "wordwheelquery", "odysseus", "adoberdr", "shellfolders", "userassist2", "putty", "rootkit_revealer", "startmenuinternetapps_cu", "proxysettings", "privoxy", "autorun", "muicache", "bitbucket_user", "listsoft", "policies_u", "user_win", "haven_and_hearth", "applets", "typedpaths", "printermru", "mmc", "tsclient", "vmware_vsphere", "iexplore", "gthist", "yahoo_lm", "logon_xp_run", "autoendtasks", "ie_main", "environment", "domains", "gtwhitelist", "userlocsvc", "dependency_walker", "typedurls", "nero", "comlg32", "load", "warcraft3", "comdlg32a", "startpage", "skype", "vista_bitbucket", "aports", "yahoo_cu", "aim", "compdesc", "fileexts", "mp2", "publishingwizard", "realplayer6", "clampitm", "realvnc", "mndmru", "user_run", "userassist", "ie_settings", "wallpaper", "win7_ua", "unreadmail", "vncviewer", "clampi", "outlook", "bagtest", "cain", "cpldontload", "arpcache", "sevenzip", "bagtest2", "winvnc", "winlogon_u", "oisc", "mpmru", "brisv", "officedocs", "winrar", "runmru", "vista_comdlg32", "ccleaner.pl", "vnchooksapplicationprefs", "compatassist", "javafx", "run", "sysinternals")

##set up plugins for SYSTEM
system_plugins = ("usbstor3", "usb", "mountdev2", "xpedition", "usbstor2", "eventlog", "eventlogs", "crashdump", "timezone", "crashcontrol", "svcdll", "dllsearch", "devclass", "shutdown", "rdpport", "hibernate", "pagefile", "network", "mountdev", "mountdev2", "nic2", "usbstor", "nolmhash", "shares", "services", "ide", "ddm", "stillimage", "imagedev", "disablelastaccess", "compname", "fw_config", "routes", "svc2", "shutdowncount", "auditfail", "safeboot", "usbdevices", "svc", "nic", "producttype", "kbdcrash", "legacy", "termserv", "nic_mst2", "timezone2", "spp_clients.pl", "filesnottosnapshot.pl", "appcompatcache", "diag_sr", "securityproviders", "termcert", "wpdbusenum")

## set up plugins for SAM
#sam_plugins = ()
#sam_plugins = ("samparse")

#set up plugins to run against software hive
software_plugins = ("appinitdlls", "winver", "secctr", "urlzone", "cmd_shell", "notify", "schedagent", "ie_version", "kb950582", "port_dev", "sql_lastconnect", "bitbucket", "regback", "bho", "sfc", "banner", "macaddr", "apppaths", "msis", "svchost", "taskman", "networkuid", "vista_wireless", "installedcomp", "drwatson", "shelloverlay", "winlogon", "ctrlpnl", "virut", "winnt_cv", "ssid", "shellexec", "win_cv", "renocide", "uninstall", "networkcards", "product", "profilelist", "shellext", "landesk", "assoc", "specaccts", "userinit", "imagefile", "removdev", "networklist", "clsid", "init_dlls", "codeid", "snapshot", "defbrowser", "soft_run", "EMDMgmt.pl", "winlivemail.pl", "dfrg", "direct", "run", "tracing", "trappoll", "wbem")

#set up array for security plugins
security_plugins = ("lsasecrets", "auditpol", "polacdms")


#get datetime
now = datetime.datetime.now()

#set Mount Point
mount_point = "/mnt/" + now.strftime("%Y-%m-%d_%H_%M_%S")

#get case number
case_number = get_case_number()

#get output location
folder_path = get_output_location(case_number)

#open a log file for output
log_file = folder_path + "/" + case_number + "_logfile.txt"
outfile = open(log_file, 'wt+')

#select dd image to process	
Image_Path = select_file_to_process(outfile)

#check if Image file is in Encase format
if re.search(".E01", Image_Path):

	#strip out single quotes from the quoted path
	#no_quotes_path = Image_Path.replace("'","")
	#print("THe no quotes path is: " +  no_quotes_path)
	#call mount_ewf function
	Image_Path = mount_ewf(Image_Path, outfile,mount_point)


#call mmls function
partition_info_dict = mmls(outfile, Image_Path)
partition_info_dict_temp = partition_info_dict

#get filesize of mmls_output.txt
file_size = os.path.getsize("/tmp/mmls_output.txt") 


#if filesize of mmls output is 0 then run parted
if(file_size == 0):
	print("mmls output was empty, running parted")
	outfile.write("mmls output was empty, running parted")
	#call parted function
	partition_info_dict = parted(outfile, Image_Path)	

else:

	#read through the mmls output and look for GUID Partition Tables (used on MACS)
	mmls_output_file = open("/tmp/mmls_output.txt", 'r')
	for line in mmls_output_file:
		if re.search("GUID Partition Table", line):
			print("We found a GUID partition table, need to use parted")
			outfile.write("We found a GUID partition table, need to use parted\n")
			#call parted function
			partition_info_dict = parted(outfile, Image_Path)
			

#loop through the dictionary containing the partition info (filesystem is VALUE, offset is KEY)
for key,value in sorted(partition_info_dict.items()):

	#call mount sub-routine
	success_code = mount(value,str(key),Image_Path, outfile, mount_point)

	if(success_code):
		print("Could not mount partition with filesystem: " + value + " at offset:" + str(key))
		outfile.write("Could not mount partition with filesystem: " + value + " at offset:" + str(key))
	else:
		
		print("We just mounted filesystem: " + value + " at offset:" + str(key) + "\n")
		outfile.write("We just mounted filesystem: " + value + " at offset:" + str(key) + "\n")

	if(value == "fat32") or (value == "ntfs"):
		#get path to registry hives	
		paths = get_system_paths(value, "YES", outfile, mount_point)

		#set up path variables from paths list
		system_hive_path = paths[0]
		system_hive_regback_path = paths[1]
		sam_hive_path = paths[2]
		sam_hive_regback_path = paths[3]
		software_hive_path = paths[4]
		software_hive_regback_path = paths[5]
		security_hive_path = paths[6]
		security_hive_regback_path = paths[7] 


		#calculate MD5 values for registry hives
		if(system_hive_path != "NONE"):
			system_hive_md5 = subprocess.check_output(['md5sum ' + system_hive_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(system_hive_regback_path != "NONE"):		
			system_hive_regback_md5 = subprocess.check_output(['md5sum ' + system_hive_regback_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(sam_hive_path != "NONE"):		
			sam_hive_md5 = subprocess.check_output(['md5sum ' + sam_hive_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(sam_hive_regback_path != "NONE"):
			sam_hive_regback_md5 = subprocess.check_output(['md5sum ' + sam_hive_regback_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(software_hive_path != "NONE"):		
			software_hive_md5 = subprocess.check_output(['md5sum ' + software_hive_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(software_hive_regback_path != "NONE"):		
			software_hive_regback_md5 = subprocess.check_output(['md5sum ' + software_hive_regback_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(security_hive_path != "NONE"):		
			security_hive_md5 = subprocess.check_output(['md5sum ' + security_hive_path+ "| awk '{print $1}'"], shell=True, universal_newlines=True)
		if(security_hive_regback_path != "NONE"):			
			security_hive_regback_md5 = subprocess.check_output(['md5sum ' + security_hive_regback_path + "| awk '{print $1}'"], shell=True, universal_newlines=True)

		

	##### PROCESS NTUSER.DAT FILES ######################################################################################################################
		#get path to NTUSER.DAT files, pass the mount point
		nt_user_dat = get_ntuser_paths(mount_point)
		
		#print out nt_user_dat info to logfile
		if(outfile != "NONE"):
			outfile.write("The NTUSER.DAT files are: *********************************************\n")
			for line in nt_user_dat:
				line.strip()
				user_account_md5 = subprocess.check_output(['md5sum ' + "'" + line + "'" + "| awk '{print $1}'"], shell=True, universal_newlines=True)
				outfile.write(line + "\t" + " MD5: " + str(user_account_md5) + "\n")

			outfile.write("********************************************************************\n")

		#create output folder 
		if(len(nt_user_dat) > 0):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/NTUSER_INFO/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/NTUSER_INFO/")		

		#create folder for each ntuser.dat file
		for user_account in nt_user_dat:
			account_name = get_account_profile_names(user_account)
			#add quotes to image path in case of spaces
			quoted_user_account = "'" +user_account +"'"

			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/NTUSER_INFO/" + account_name):
				os.mkdir(folder_path + "/Regripper_Partition_" + str(key) + "/NTUSER_INFO/" + account_name)

			#run ntuser plugins against each user_account
			for plugin in ntuser_plugins:
				print ("Currently running plugin: " + plugin + " against " + account_name + "\n")
				outfile.write("Currently running plugin: " + plugin + " against " + account_name + "\n")
				rip_ntuser_command = "perl /usr/share/regripper/rip.pl -r " + quoted_user_account + " -p " +  plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) + "/NTUSER_INFO/" + account_name + "/" + plugin + ".txt" + "'"
				print("The rip_ntuser command is: " + rip_ntuser_command + "\n")			
				subprocess.call([rip_ntuser_command], shell=True)
	##### PROCESS NTUSER.DAT FILES ######################################################################################################################

	##### PROCESS USRCLASS.DAT FILES ######################################################################################################################
		#get path to USRCLASS.DAT files, pass the mount point
		usrclass_dat = get_usrclass_paths(mount_point)

		#print out usrclass_dat info to logfile
		if(outfile != "NONE"):
			outfile.write("The USRCLASS.DAT files are: *********************************************\n")
			for line in usrclass_dat:
				line.strip()
				user_account_md5 = subprocess.check_output(['md5sum ' + "'" + line + "'" + "| awk '{print $1}'"], shell=True, universal_newlines=True)
				outfile.write(line + "\t" + " MD5: " + str(user_account_md5) + "\n")

			outfile.write("********************************************************************\n")

		#create output folder 
		if(len(usrclass_dat) > 0):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/USRCLASS_INFO/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/USRCLASS_INFO/")

		#create folder for each ntuser.dat file
		for user_account in usrclass_dat:
			account_name = get_account_profile_names_usrclass(user_account)
			#add quotes to image path in case of spaces
			quoted_user_account = "'" +user_account +"'"

			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/USRCLASS_INFO/" + account_name):
				os.mkdir(folder_path + "/Regripper_Partition_" + str(key) + "/USRCLASS_INFO/" + account_name)
	  
			#run ntuser plugins against each user_account
			for plugin in usrclass_plugins:
				print ("Currently running plugin: " + plugin + " against " + account_name + "\n")
				outfile.write("Currently running plugin: " + plugin + " against " + account_name + "\n")
				rip_usrclass_command = "perl /usr/share/regripper/rip.pl -r " + quoted_user_account + " -p " +  plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) + "/USRCLASS_INFO/" + account_name + "/" + plugin + ".txt" + "'"
				print("The rip_usrclass command is: " + rip_usrclass_command + "\n")			
				subprocess.call([rip_usrclass_command], shell=True)

		

	##### PROCESS USRCLASS.DAT FILES ######################################################################################################################

	##### PROCESS SYTEM HIVE ######################################################################################################################
		#create output folder 
		if(system_hive_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/SYSTEM/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/SYSTEM/")	
			#run plugins against each user_account
			for plugin in system_plugins:
				print ("Currently running plugin: " + plugin + " against SYSTEM HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SYSTEM HIVE with MD5: " + str(system_hive_md5) + "\n")

				rip_system_command = "perl /usr/share/regripper/rip.pl -r "+ system_hive_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/SYSTEM/" + plugin + ".txt" + "'"
				print("The rip system_command is: " + rip_system_command + "\n")
				subprocess.call([rip_system_command], shell=True)
		if(system_hive_regback_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SYSTEM/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SYSTEM/")
			for plugin in system_plugins:
				print ("Currently running plugin: " + plugin + " against SYSTEM REGBACK HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SYSTEM REGBACK HIVE with MD5: " + str(system_hive_regback_md5) + "\n")	
				
				rip_system_regback_command = "perl /usr/share/regripper/rip.pl -r "+ system_hive_regback_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/REGBACK_SYSTEM/" + plugin + ".txt" + "'"
				print("The rip system_command is: " + rip_system_regback_command + "\n")
				subprocess.call([rip_system_regback_command], shell=True)
		
	##### PROCESS SYTEM HIVE ######################################################################################################################

	##### PROCESS SAM HIVE ########################################################################################################################
		#create output folder 
		if(sam_hive_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/SAM/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/SAM/")	

			#run samparse
			print ("Currently running plugin: samparse against SAM HIVE\n")
			outfile.write("Currently running plugin: samparse against SAM HIVE with MD5: " + str(sam_hive_md5) + "\n")

			rip_sam_command = "perl /usr/share/regripper/rip.pl -r "+ sam_hive_path + " -p samparse > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/SAM/samparse.txt" + "'"
			print("The rip sam_command is: " + rip_sam_command + "\n")
			subprocess.call([rip_sam_command], shell=True)

		if(sam_hive_regback_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SAM/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SAM/")
			#run samparse
			print ("Currently running plugin: samparse against SAM REGBACK HIVE\n")
			outfile.write("Currently running plugin: samparse against SAM REGBACK HIVE with MD5: " + str(sam_hive_regback_md5) + "\n")

			rip_sam_regback_command = "perl /usr/share/regripper/rip.pl -r "+ sam_hive_regback_path + " -p samparse > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/REGBACK_SAM/samparse.txt" + "'"
			print("The rip sam_regback_command is: " + rip_sam_command + "\n")
			subprocess.call([rip_sam_regback_command], shell=True)

	##### PROCESS SAM HIVE ###########################unmount and remove mount points

	##### PROCESS SECURITY HIVE ########################################################################################################################

		#create output folder 
		if(security_hive_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/SECURITY/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/SECURITY/")	

			#run plugins against each user_account
			for plugin in security_plugins:
				print ("Currently running plugin: " + plugin + " against SECURITY HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SECURITY HIVE with MD5: " + str(security_hive_md5) + "\n")

				rip_security_command = "perl /usr/share/regripper/rip.pl -r "+ security_hive_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/SECURITY/" + plugin + ".txt" + "'"
				print("The rip security_command is: " + rip_security_command + "\n")
				subprocess.call([rip_security_command], shell=True)

		if(security_hive_regback_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SECURITY/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SECURITY/")
			for plugin in security_plugins:
				print ("Currently running plugin: " + plugin + " against SECURITY REGBACK HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SECURITY REGBACK HIVE with MD5: " + str(security_hive_regback_md5) + "\n")	
				
				rip_security_regback_command = "perl /usr/share/regripper/rip.pl -r "+ security_hive_regback_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/REGBACK_SECURITY/" + plugin + ".txt" + "'"
				print("The rip security_regback_command is: " + rip_security_regback_command + "\n")
				subprocess.call([rip_security_regback_command], shell=True)


	##### PROCESS SECURITY HIVE ########################################################################################################################

	##### PROCESS SOFTWARE HIVE ########################################################################################################################

		#create output folder 
		if(software_hive_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/SOFTWARE/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/SOFTWARE/")	

			#run plugins against each user_account
			for plugin in software_plugins:
				print ("Currently running plugin: " + plugin + " against SOFTWARE HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SOFTWARE HIVE with MD5: " + str(software_hive_md5)  + "\n")

				rip_software_command = "perl /usr/share/regripper/rip.pl -r "+ software_hive_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/SOFTWARE/" + plugin + ".txt" + "'"
				print("The rip software_command is: " + rip_software_command + "\n")
				subprocess.call([rip_software_command], shell=True)

		#create output folder 
		if(software_hive_regback_path != "NONE"):
			if not os.path.exists(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SOFTWARE/"):
				os.makedirs(folder_path + "/Regripper_Partition_" + str(key) + "/REGBACK_SOFTWARE/")	

			#run plugins against each user_account
			for plugin in software_plugins:
				print ("Currently running plugin: " + plugin + " against SOFTWARE REGBACK HIVE\n")
				outfile.write("Currently running plugin: " + plugin + " against SOFTWARE REGBACK HIVE with MD5: " + str(software_hive_regback_md5) + "\n")

				rip_software_regback_command = "perl /usr/share/regripper/rip.pl -r "+ software_hive_regback_path + " -p " + plugin + " > " + "'" + folder_path + "/Regripper_Partition_" + str(key) +"/REGBACK_SOFTWARE/" + plugin + ".txt" + "'"
				print("The rip software_regback_command is: " + rip_software_regback_command + "\n")
				subprocess.call([rip_software_regback_command], shell=True)


	##### PROCESS SOFTWARE HIVE ########################################################################################################################

#run text files through unix2dos
for root, dirs, files in os.walk(folder_path):
		for filenames in files:
			#get file extension
			fileName, fileExtension = os.path.splitext(filenames)
			if(fileExtension.lower() == ".txt"):
				full_path = os.path.join(root,filenames)
				quoted_full_path = "'" +full_path+"'"
				print("Running Unix2dos against file: " + filenames)
				unix2dos_command = "sudo unix2dos " + quoted_full_path
				subprocess.call([unix2dos_command], shell=True)

#close outfile
outfile.close()

#unmount and remove mount points
if(os.path.exists(mount_point)):
	subprocess.call(['sudo umount -f ' + mount_point], shell=True)
	os.rmdir(mount_point)
if(os.path.exists(mount_point+"_ewf")):
	subprocess.call(['sudo umount -f ' + mount_point + "_ewf"], shell=True)
	os.rmdir(mount_point+"_ewf")

#call done sub to tell user program is done and alert them where the output files are located
done(folder_path)

