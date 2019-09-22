
import threading
from datetime import datetime
from netmiko import ConnectHandler
from netmiko import ssh_exception
from netmiko.ssh_exception import (
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
	SSHException
)
import re
# import time
import os
import os.path
import json
from multiprocessing.dummy import Pool as ThreadPool
from time import time


# from logging import log
# import scp
# from paramiko import SSHClient

# import subprocess

''' After SetConfig it exit config mode but after SendConfig Still in config mode ALSO u can send sho ip int br after SendConfig'''

num =[
"192.168.1.1","192.168.1.2"
]


Device_Type=[ 'cisco_ios','cisco_ios_telnet']
Username_Device=['Cisco','BMB-Supp','cisco','mahmeda']
Passowrd_Device=['Cisco','L@F@rgeBmB2030','cisco','Simon_guevara@7999']
Global_Output=[]

FailedIps=[]
count=0
ConfigurationTest_Boolen =0

#############  Check ping ##################
def ping_is_successful(ping_result):
	return True if '!' in ping_result else False

#############  Check Date of Cetifaction ##################
def CheckDateOfCertifcation(date_output , CheckOn):
	return True if str(CheckOn) in date_output else False




##############################################################################
##################### The SCP Function of configuration ##################### 
##############################################################################

def loginandcopy(hostname='',uname='',pwd='',sfile='',tfile=''):
	try:
		client = SSHClient()
		client.load_system_host_keys()
		client.connect('',port=22,username='',password='')
	except paramiko.AuthenticationException:
		print("Authentication failed, please verify your credentials: %s")
	except paramiko.SSHException as sshException:
		print("Unable to establish SSH connection: %s" % sshException)
	except paramiko.BadHostKeyException as badHostKeyException:
		print("Unable to verify server's host key: %s" % badHostKeyException)
	except Exception as e:
		print(e.args)
	try:
		GetTransport=client.get_transport()
		scpclient = scp.SCPClient(GetTransport)
		scpclient.put(sfile,tfile)
	except scp.SCPException as e:
		print("Operation error: %s", e) 


##############################################################################
##################### The main Function of configuration ##################### 
##############################################################################

def ConfigurationTest(ip,Device_Type_Num= 0,User_Pass_Num= 0):

	if ConfigurationTest_Boolen==1 :
		return ConfigurationTest_Boolen==1

# If increment of Num is out of range for User_Pass_Num and Device_Type_Num return 1
	elif User_Pass_Num >= len(Username_Device)  or Device_Type_Num >= len (Device_Type)  :
		print ("Out Of Range For IP\t" + ip+"\n")
		return ConfigurationTest_Boolen==1

# If increment of Num is in range for User_Pass_Num and Device_Type_Num contune
	else :

	 	iosv_l2={
			'device_type': str(Device_Type[Device_Type_Num]),  ##### Type of connection SSH/Telnet
			'ip':str(ip),
			'username': Username_Device[User_Pass_Num],
			'password': Passowrd_Device[User_Pass_Num],
			'global_delay_factor': 3
			}

		try:
			# time.sleep(3)
			Conf_Variables=[]  # To check if any faliure on the configuration after sending it
			net_connect = ConnectHandler(**iosv_l2)
			# print("this is TRY   "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
			# print(net_connect.find_prompt())

	############ function to check output to send any confirmation message as pass or confirmation of yes or no
			def SpecialConfirmation (command , message , reply):
				net_connect.config_mode()    #To enter config mode
				net_connect.remote_conn.sendall(str(command)+'\n' )
				time.sleep(3)
				output = net_connect.remote_conn.recv(65535).decode('utf-8')
				ReplyAppend=''
				if str(message) in output:
					for i in range(0,(len(reply))):
						ReplyAppend+=str(reply[i])+'\n'
					net_connect.remote_conn.sendall(ReplyAppend)
					output = net_connect.remote_conn.recv(65535).decode('utf-8') 
				print (output)
				return output

			print ("Entered Device Successfully \t"+ip +"\n")
			# output=net_connect.send_command("sho ip int br"+'\n\n')
			# output=net_connect.send_command_timing("show run | i hostname "+'\n\n')
			# print (output)

			SetCommands=['no int loo0','exit']


	######################################################################
	################ Here Is The Cisco Configuration  ####################
	######################################################################
		# Check if in config mode or not to exit config mode
			if net_connect.check_config_mode() :
				net_connect.exit_config_mode()

			# Hostname_Output=net_connect.send_command_timing("show run | i hostname "+'\n\n', strip_prompt=False , strip_command=False)
			Hostname_Output=net_connect.send_command_timing("show run | i hostname "+'\n')
			net_connect.config_mode()
			# Community_Command=net_connect.send_command("userna f496341025ac nopass "+'\n\n')
			Community_Command=net_connect.send_command("userna 7c763571e9f9 nopass "+'\n' , strip_command=False)
			# Community_Command=net_connect.send_command("userna f894c2620b24 nopass "+'\n\n')
			# Community_Command=net_connect.send_command("userna f48c50857834 nopass "+'\n\n')
			# Community_Command=net_connect.send_command("userna f8a2d6ec8e0b nopass "+'\n\n')
			net_connect.exit_config_mode()
			Configuration_Output=net_connect.send_command_timing(" copy running-config startup-config  "+'\n' , strip_command=False)
			# Configuration_Output=net_connect.send_command_timing("termin len 0"+'\n\n')
			# Configuration_Output=net_connect.send_command_timing("show run "+'\n\n')
			# Hostname_Output=net_connect.send_config_set(SetCommands)
			# print (Hostname_Output)
			
				# Configuration_Output=net_connect.send_command_timing("termin len 0"+'\n\n')
				# Configuration_Output=net_connect.send_command_timing("show run  "+'\n\n')
				# Hostname_Output=net_connect.send_config_set(SetCommands)
				# print (Hostname_Output)
			# print (Hostname_Output)
			Spilt_Hostname_Ouput=Hostname_Output.split()
			Hostname_Output=Spilt_Hostname_Ouput[1]
			# print (str(Hostname_Output)+ " " + ip)
			print (Hostname_Output +'\n')
			# print (Configuration_Output+"\n" )
			# print(Community_Command+'\n')

	############### Append Configuration Variables to Global Variable ##########
			Conf_Variables.append(Community_Command)
			Conf_Variables.append(Hostname_Output)
			Conf_Variables.append(Configuration_Output)
	############### Search in Configuration if any command error and return its IP ################
			for y in Conf_Variables:
				if "% Invalid input detected at '^' marker." in y :
					FailedIps.append(ip+"	Invalid input")
	###############	SAVE Output IN FILES  #######################		
			# with open(Hostname_Output,'w') as f:
			# 	f.write(Configuration_Output)

		# This is Summary of all Ip's output
			# Global_Output.append(Hostname_Output+"\t"+(ip))
			Global_Output.append(Hostname_Output)

			# CheckConfigMode=net_connect.check_config_mode()
			# print (str(CheckConfigMode)+" 1")
			net_connect.disconnect()

		except ( NetMikoAuthenticationException) :
			# print ('Authentication Failure\t' + ip)
			print (str (User_Pass_Num)+"\tAuthentication\t"+ip)
			User_Pass_Num+=1
		# If it tried all users and pass and failed add it to failedIps
			if User_Pass_Num >= len(Username_Device) :
				FailedIps.append(ip+"	Authentication Error ")
			# if User_Pass_Num < len(Username_Device) :
			# 	print("this is Authentication  "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
		# Recursive function
			return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num )
		except (NetMikoTimeoutException):	
			# print ('Timeout  Failure\t' + ip)
			print (str (Device_Type_Num)+"\tTimeoutException\t"+ip)
			Device_Type_Num+=1
			if  Device_Type_Num >= len(Device_Type) :
				FailedIps.append(ip+"	Timeout Error")
			# if  Device_Type_Num < len(Device_Type) :
			# 	print("this is Timeout "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
			return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num )
		except (SSHException):	
			# print ('SSH  Failure\t' + ip)
			print (str (Device_Type_Num)+"\tSSHException\t"+ip)
			Device_Type_Num+=1
			if  Device_Type_Num >= len(Device_Type) :
				FailedIps.append(ip+"	SSHException Error ")
			# if  Device_Type_Num < len(Device_Type) :
			# 	print("this is SSHException "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
			return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num )
		except (EOFError):	
			# print ('End of File wihle attempting device\t' +ip)
			FailedIps.append(ip+"	EOFError")
			# print("this is EOFError "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
			return ConfigurationTest_Boolen==1
		except Exception as unknown_error :
			FailedIps.append(ip+"	Unknown Error")
			# print("this is Uknown "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))	
			return ConfigurationTest_Boolen==1
		# print ("\nLast return ")
	
	return ConfigurationTest_Boolen==1
start_time = datetime.now()

# ===============================================================================
#=============  Calling Main Function and Run Threads  ==========================
# ===============================================================================

#####################################################################
################## Controling nuber of processing  ##################
#####################################################################

FailedExceptionIps=[]
for x in num:
	ConfigurationTest_Boolen==0
	try:
		my_thread = threading.Thread(target=ConfigurationTest, args=(x,0,0))
		my_thread.start()
	except Exception:
		FailedExceptionIps.append(num[x])

main_thread = threading.currentThread()
for some_thread in threading.enumerate():
	if some_thread != main_thread:
		print(some_thread)
		some_thread.join()





#####################################################
############### Thread For SCP ######################
#####################################################
# for x in Global_Output:
# 	try:
# 		my_thread2 = threading.Thread(target=loginandcopy, args=('10.231.0.84','khyat','P@ssw0rd',x,(x+'.txt')))
# 		my_thread2.start()
# 	except Exception:
# 		print (" Thread Of Copying\t"+ x+"\n")
# main_thread = threading.currentThread()
# for some_thread in threading.enumerate():
# 	if some_thread != main_thread:
# 		print(some_thread)
# 		some_thread.join()

# subprocess.call(["rm", Global_Output[0]])
# loginandcopy('10.231.0.84','khyat','P@ssw0rd',Global_Output[0],Global_Output[0])

print ("Output Summary ")
for i in Global_Output :
	print ("\t\t"+i)
print("\nElapsed time: " + str(datetime.now() - start_time))
print("FailedIps")
for i in FailedIps :
	print('\t  '+i)
print("FailedExceptionIps")
print(FailedExceptionIps)
# print (FailedIps)
