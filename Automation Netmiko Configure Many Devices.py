# ls | wc -l ## commad to see numbers of files on the directory
# ssh 192.168.1.2 -o Kexalgorithms=+diffie-hellman-group1-sha1  ## to solve problem while connecting from client that have mismatch on Diffe
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
import os
import os.path
import json
from multiprocessing.dummy import Pool as ThreadPool
import time 

# from logging import log
import scp
from paramiko import SSHClient
import codecs
import subprocess

''' After SetConfig it exit config mode but after SendConfig Still in config mode ALSO u can send sho ip int br after SendConfig'''
TruePing=[]
FalsePing=[]
# num =[
# # "192.168.233.11",
# # "192.168.233.12",
# # "192.168.233.13"
# ]

TestPingIPs=[
"192.168.233.11",
"192.168.233.12",
"192.168.233.13"
]

Device_Type=[ 'cisco_ios_telnet','cisco_ios']
Passowrd_Device_Enable=["Test","cisco"]
Username_Device=["test","cisco"]
Passowrd_Device=["barkotel","cisco"]

Device_Type=[ 'cisco_ios_telnet','cisco_ios']

# Username_Device=["cisco"]
# Passowrd_Device=["cisco"]
# Passowrd_Device_Enable=["cisco","cs"]

Global_Output=[]
Hostname_Output_list=[]
Configuration_Output_list=[]
Configuration_Output_ID2_list=[]
Configuration_Output_ID254_list=[]
FailedIps=[]
count=0
ConfigurationTest_Boolen =0
num_New=[]




##################################################################
						########## Get IPs from file ############
##################################################################
with open('s.txt', 'r') as file:
		num =file.read().splitlines()


#############  Check ping ##################
def ping_is_successful(ping_result):
		return True if '!' in ping_result else False

#############  Check Date of Cetifaction ##################
def CheckDateOfCertifcation(date_output , CheckOn):
		return True if str(CheckOn) in date_output else False




##############################################################################
##################### The SCP Function of configuration ##################### 
##############################################################################

def loginandcopy(hostname='10.231.0.84',uname='khyat',pwd='P@ssw0rd',sfile='a1.py',tfile='a1.py'):
		try:
				client = SSHClient()
				client.load_system_host_keys()
				client.connect(hostname,port=22,username=uname,password=pwd)
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
# loginandcopy('10.231.0.84','khyat','P@ssw0rd','a1.py','a1.py')


##############################################################################
##################### The main Function of configuration ##################### 
##############################################################################

def ConfigurationTest(ip,Device_Type_Num= 0,User_Pass_Num= 0,Passowrd_Enable_Num=0):
# def ConfigurationTest(ip,Device_Type_Num= 0,User_Pass_Num= 0):

		if ConfigurationTest_Boolen==1 :
				return ConfigurationTest_Boolen==1

# If increment of Num is out of range for User_Pass_Num and Device_Type_Num return 1
		elif User_Pass_Num >= len(Username_Device)  or Device_Type_Num >= len (Device_Type) or Passowrd_Enable_Num>=len(Passowrd_Device_Enable) :
				print ("Out Of Range For IP\t" + ip+"\n")
				return ConfigurationTest_Boolen==1

# If increment of Num is in range for User_Pass_Num and Device_Type_Num contune
		else :

				iosv_l2={
						'device_type': str(Device_Type[Device_Type_Num]),  ##### Type of connection SSH/Telnet
						'ip':str(ip),
						'username': Username_Device[User_Pass_Num],
						'password': Passowrd_Device[User_Pass_Num],
						'global_delay_factor': 15,
						# 'secret':'cs'
						'secret':Passowrd_Device_Enable[Passowrd_Enable_Num],
						'timeout':10
						 # 'session_timeout':5
								}

				try:
						# time.sleep(3)
						Conf_Variables=[]  # To check if any faliure on the configuration after sending it
						net_connect = ConnectHandler(**iosv_l2)
						# print(net_connect.find_prompt())

		############ function to check output to send any confirmation message as pass or confirmation of yes or no
						def SpecialConfirmation (command , message , reply):
								net_connect.config_mode()    #To enter config mode
								print ("SpecialConfirmation Config")
								try :
										if Device_Type[Device_Type_Num] == "cisco_ios_telnet" :
												print ("First Write Telnet")
												net_connect.remote_conn.write(str(command)+'\n' )
										else :
												net_connect.remote_conn.sendall(str(command)+'\n' )
								except : 
										print ("Exception For Sendall ")
								print ("SpecialConfirmation Before Sleep")
								time.sleep(3)
								print ("SpecialConfirmation after Sleep")
								if Device_Type[Device_Type_Num] == "cisco_ios_telnet" :
										print ("First READ Telnet")
										output = net_connect.remote_conn.read_very_eager().decode("utf-8", "ignore")
								else :
										output = net_connect.remote_conn.recv(65535).decode('utf-8')
								ReplyAppend=''
								print ("SpecialConfirmation output")
								print (output)
								try :
										if str(message) in output:
												for i in range(0,(len(reply))):
														ReplyAppend+=str(reply[i])+'\n'
												if Device_Type[Device_Type_Num] == "cisco_ios_telnet" :
														print ("SECOND Telnet")
														net_connect.remote_conn.write(ReplyAppend)
														output = net_connect.remote_conn.read_very_eager().decode("utf-8", "ignore") 
												else :
														net_connect.remote_conn.sendall(ReplyAppend)
														output = net_connect.remote_conn.recv(65535).decode('utf-8') 
										print (output)
								except :
										print ("Confirmation Exception Error")
								return output

						print ("Entered Device Successfully \t"+ip +"\n")



		######################################################################
		################ Here Is The Cisco Configuration  ####################
		######################################################################
						print ("check enable mode for "+str(ip))
						if not net_connect.check_enable_mode() :
								net_connect.enable()
								print ("entered enable mode for "+str(ip))

				##################################################################
				########### Check if in config mode or not to exit config mode
				##################################################################
						if net_connect.check_config_mode() :
								net_connect.exit_config_mode()
								print ("After exiting config "+str(ip))
						print ("After checking config "+str(ip))

		######################################################################


						print ("Terminal length \n")

						Configuration_Output=net_connect.send_command_timing("termin len 0"+'\n\n' )
						# Configuration_Output=net_connect.send_command_timing("show run "+'\n\n'  ,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show ip inte br "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Switch=net_connect.send_command_timing("show fex  "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show cdp neighbors detail "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Switch+=net_connect.send_command_timing("show interfaces status  "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show inter desc "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Router=net_connect.send_command_timing("show ip ospf neighbor "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show version "+'\n\n' ,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show cdp neighbors "+'\n\n' ,strip_prompt=False,strip_command=False)


						Configuration_Output_ID2=net_connect.send_command_timing("show ip arp vrf ID2 "+'\n\n'  ,strip_prompt=False,strip_command=False)
						Configuration_Output_ID254=net_connect.send_command_timing("show ip arp vrf ID254 "+'\n\n'  ,strip_prompt=False,strip_command=False)


						
						# Configuration_Output=net_connect.send_command_timing("termin len 0"+'\n\n',delay_factor=5)
						# Configuration_Output=net_connect.send_command_timing("show run "+'\n\n' ,delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show ip inte br "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Switch=net_connect.send_command_timing("show fex  "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show cdp neighbors detail "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Switch+=net_connect.send_command_timing("show interfaces status  "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show inter desc "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Router=net_connect.send_command_timing("show ip ospf neighbor "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show version "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)
						# Configuration_Output+=net_connect.send_command_timing("show cdp neighbors "+'\n\n',delay_factor=5,strip_prompt=False,strip_command=False)



						# Hostname_Output=net_connect.send_command("show run | i hostname"+'\n\n')

						# Configuration_Output+=net_connect.send_command_timing("show ip inte br "+'\n\n',strip_prompt=False,strip_command=False)
						
						Configuration_Router=""
						Configuration_Switch=""

						Hostname_Output=net_connect.send_command("show run | i hostname"+'\n\n',delay_factor=5)





				###########################################################################################################
				##################    	Add new IPs from CDP Command     ##################################################
				###########################################################################################################
						CDP_ALL=net_connect.send_command_timing("show cdp neighbors detail | i IP address: "+'\n\n')
						# print("CDP_ALL\n")
						# print(CDP_ALL)
						# print(type(CDP_ALL))
						# change output to list of lines
						CDP_Lines_List=CDP_ALL.splitlines()  # change output to list of lines
						CDP_IPs_List=[]
						# change list of line to list of IPs wihtout IP address sentence
						for i in CDP_Lines_List :
							j=i.lstrip("IP address: ")
							CDP_IPs_List.append(j)
						# print("CDP_IPs_List for "+str(ip))
						# print(CDP_IPs_List)

						# check on each ip if it's in the mangement range or not and append it to new list if it's not exsit in the IPs list
						for i in CDP_IPs_List :
							if "172" in i :
								# check on the IP to add it to the list
								if i not in num :
									num_New.append(i)
									# num.append(i)
								# CDP_IPs_List.remove(i)
						

				###########################################################################################################
				###########################################################################################################


						# if ip =="192.168.233.13":
						#       print (str (SpecialConfirmation("crypto key generate rsa general-keys" ,"modulus" ,"1024")))

						if net_connect.check_config_mode() :
								net_connect.exit_config_mode()
						print ("After second check config "+str(ip))


						# for k in TestPingIPs : 
						# 		ping_result=net_connect.send_command_timing("ping "+k)
						# 		print (str(k)+" is "+str(ping_is_successful(ping_result))+" from "+str(ip))

		################################################################################
		####################### Test Ping For Rang Of IP  ##############################
		################################################################################
						# for IpPing in TestPingIPs :
						#       PingPool="ping "+IpPing
						#       TestPingResult=net_connect.send_command_timing(PingPool+'\n\n')
						#       if ping_is_successful(TestPingResult) :
						#               TruePing.append(IpPing)
						#       else :
						#               FalsePing.append(IpPing)




						Spilt_Hostname_Ouput=Hostname_Output.split()
						Hostname_Output=ip+".__"+Spilt_Hostname_Ouput[-1]
						# print ("After Split")

		############### Append Configuration Variables to Global Variable ##########

						Conf_Variables.append(Hostname_Output)
						Conf_Variables.append(Configuration_Output)
		############### Search in Configuration if any command error and return its IP ################
						for y in Conf_Variables:
								if "% Invalid input detected at '^' marker." in y :
										FailedIps.append(ip+"   Invalid input")
#########################################################################################################
						# Configuration_Output+=Configuration_Switch
						# Configuration_Output+=Configuration_Router
						Hostname_Output_list.append(Hostname_Output)
						test=Configuration_Switch
						test+= Configuration_Output
						test+=Configuration_Router
						Configuration_Output_list.append(test)
						Configuration_Output_ID2_list.append(Configuration_Output_ID2)
						Configuration_Output_ID254_list.append(Configuration_Output_ID254)





		############### SAVE Output IN FILES  #######################
						Global_Output.append(Hostname_Output)
						net_connect.disconnect()


################### Exception ###################################
				except ( NetMikoAuthenticationException) :
						# print ('Authentication Failure\t' + ip)
						print (str (User_Pass_Num)+"\tAuthentication\t"+ip)
						User_Pass_Num+=1
				# If it tried all users and pass and failed add it to failedIps
						if User_Pass_Num >= len(Username_Device) :
								FailedIps.append(ip+"   Authentication Error ")
						# if User_Pass_Num < len(Username_Device) :
						#       print("this is Authentication  "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))
				# Recursive function
						return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num,Passowrd_Enable_Num )
				except (ValueError):
						print (str (Passowrd_Enable_Num)+"\tEnable Authentication\t"+ip)
						Passowrd_Enable_Num+=1
						if Passowrd_Enable_Num>=len(Passowrd_Device_Enable):
								FailedIps.append(ip+"\tEnable Authentication Error ")
						return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num ,Passowrd_Enable_Num) 
				except (NetMikoTimeoutException):
						# print ('Timeout  Failure\t' + ip)
						print (str (Device_Type_Num)+"\tTimeoutException\t"+ip)
						Device_Type_Num+=1
						if  Device_Type_Num >= len(Device_Type) :
								FailedIps.append(ip+"   Timeout Error")
						# if  Device_Type_Num < len(Device_Type) :
						#       print("this is Timeout "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))
						return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num ,Passowrd_Enable_Num)
				except (SSHException):
						# print ('SSH  Failure\t' + ip)
						print (str (Device_Type_Num)+"\tSSHException\t"+ip)
						Device_Type_Num+=1
						if  Device_Type_Num >= len(Device_Type) :
								FailedIps.append(ip+"   SSHException Error ")
						# if  Device_Type_Num < len(Device_Type) :
						#       print("this is SSHException "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))
						return ConfigurationTest (ip ,Device_Type_Num ,User_Pass_Num ,Passowrd_Enable_Num)
				except (EOFError):
						# print ('End of File wihle attempting device\t' +ip)
						FailedIps.append(ip+"   EOFError")
						# print("this is EOFError "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))
						return ConfigurationTest_Boolen==1
						
		####################################################################
		########## if you want to show error , comment next lines if you want to show which Ips have error remove comment  ##############
		####################################################################
				except Exception as e:
						# print ('End of File wihle attempting device\t' +ip)
						FailedIps.append(ip+"   Exception as e")
						# print("this is EOFError "+str(ip)+" Device_Type "+str(Device_Type[Device_Type_Num])+" Username_Device " +str(Username_Device[User_Pass_Num])+" Passowrd_Device " +str(Passowrd_Device[User_Pass_Num]))
						return ConfigurationTest_Boolen==1


		####################################################################

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


# loginandcopy('10.231.0.84','khyat','P@ssw0rd','a1.py','a1.py')

####################################################################################################
###################    Add new IPs and Remove Deplicated IPs   #####################################
####################################################################################################
num_New= list(dict.fromkeys(num_New))
with open('s.txt', 'a') as file:
	for i in num_New:
		file.write((str(i)+"\n"))
file.close()

#new file for only new IPs
with open('s_New.txt', 'a') as file1:
	for i in num_New:
		file1.write((str(i)+"\n"))
file1.close()

####################################################################################################
####################### To Save File in the same host you have run on it ###########################
####################################################################################################
for f in range (0, len(Hostname_Output_list)) :
		file1 = codecs.open(Hostname_Output_list[f]+".txt", encoding='utf-8',mode="w+")
		file1.write(Configuration_Output_list[f])
		file1.close()

####################################################################################################
###############     This for vrf ID2 arp #############################
for f in range (0, len(Hostname_Output_list)) :
		file1 = codecs.open(Hostname_Output_list[f]+"__ID2.txt", encoding='utf-8',mode="w+")
		file1.write(Configuration_Output_ID2_list[f])
		file1.close()


		
####################################################################################################
###############     This for vrf ID254 arp #############################
for f in range (0, len(Hostname_Output_list)) :
		file1 = codecs.open(Hostname_Output_list[f]+"__ID254.txt", encoding='utf-8',mode="w+")
		file1.write(Configuration_Output_ID254_list[f])
		file1.close()







#####################################################
############### Thread For SCP ######################
#####################################################
# for x in Hostname_Output_list:
#       try:
#               # X is text that  you want to save , x+'.txt' is filename 
#               z=x+".txt"
#               my_thread2 = threading.Thread(target=loginandcopy, args=('172.100.130.110','root','toor',z,(z)))
#               # my_thread2 = threading.Thread(target=loginandcopy, args=('172.100.130.171','root','toor',(x),(x+'.txt')))
#               my_thread2.start()
#       except Exception:
#               print (" Thread Of Copying\t"+ x+"\n")
# main_thread = threading.currentThread()
# for some_thread in threading.enumerate():
#       if some_thread != main_thread:
#               print(some_thread)
#               some_thread.join()


		# subprocess.call(["rm",z ])


# subprocess.call(["rm", Global_Output[0]])
# loginandcopy('10.231.0.84','khyat','P@ssw0rd',Global_Output[0],Global_Output[0])
# loginandcopy('172.100.130.171','root','toor',"Karate.txt","Karate.txt")
# FileNameRm ="Karate"+".txt"

# for n in Hostname_Output_list:
#       try:
#               # X is text that  you want to save , x+'.txt' is filename 
#               m=n+".txt"
#               my_thread2 = threading.Thread(target=subprocess.call, args=('rm',m,(m)))
#               my_thread2.start()
#       except Exception:
#               print (" Thread Of Deleting\t"+ n+"\n")
# main_thread = threading.currentThread()
# for some_thread in threading.enumerate():
#       if some_thread != main_thread:
#               print(some_thread)
#               some_thread.join()

# for n in Hostname_Output_list: 
#       m=n+".txt"
#       subprocess.call(["rm",m ])

# for y in Hostname_Output_list :
#       FileNameRm=y+".txt"
#       subprocess.call(["rm",FileNameRm ])
####################################################################################################


print ("Output Summary ")

for i in Hostname_Output_list :
		print ("\t\t"+i)

print("\nElapsed time: " + str(datetime.now() - start_time))
print("FailedIps")
for i in FailedIps :
		print('\t  '+i)
print(len(FailedIps))


	############# these are the failed IPs while running threads together 
print("FailedExceptionIps")
print(FailedExceptionIps)
