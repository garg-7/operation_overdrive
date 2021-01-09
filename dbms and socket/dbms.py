#pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import mysql.connector
import os
import getpass

currentUserName = getpass.getuser()
print(currentUserName)
userData=[]

files=os.listdir('backup')
# print(files)

for file in (files):
    userData.append(currentUserName)
    
files = tuple(zip(files, userData)) 
# print(files)

mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
mycursor = mydb.cursor()

# Your Computer Name is:LAPTOP-RBAGRA85
# Your Computer IP Address is:192.168.56.1

# mycursor.execute("Create database fileInfo")

# mycursor.execute("Show databases")
# for db in mycursor:
#     print (db)

# mycursor.execute("Create table backupData(file varchar(200), owner varchar(200))")

mycursor.execute("Show tables")

for tb in mycursor :
    print(tb)


# print(mydb)

# import socket    
# hostname = socket.gethostname()    
# IPAddr = socket.gethostbyname(hostname)    
# print("Your Computer Name is:" + hostname)    
# print("Your Computer IP Address is:" + IPAddr)    