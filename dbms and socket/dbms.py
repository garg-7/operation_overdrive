#pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread


# def manageConnections ():
#     while True:  
#         clientsocket, address = s.accept()
#         clients.append((clientsocket, address))
#         start_new_thread(handleConnection, (clientsocket , address))
#         print(f"Connected with {address}")


# def handleConnection(currentClient,address) :
#     passwordCheck =  currentClient.recv(100).decode()
#     if(passwordCheck == "letmepass"):
#         print(f"Password authentication successful with {address}")
#         currentClient.send(str("Correct").encode())
#     else : 
#         #server to be closed 
#         print(f"Password authentication unsuccessful with {address}")
#         currentClient.send(str("Wrong").encode())
        
#     purposeCheck =  currentClient.recv(100).decode()
    
#     if(purposeCheck == 'Y'):
#         print(f"File Transfer Requested by address : {address}")
#     else :
#         #do something
#         print()        
    

currentUserName = getpass.getuser()
print(currentUserName)
userData=[]

files=os.listdir('backup')
# print(files)

for file in (files):
    userData.append(currentUserName)
    
files = tuple(zip(files, userData)) 
# print(files)



# s = socket.socket()
# port=9077
# s.bind(('127.0.0.1',port))
# s.listen() 

# clients = []
# manageConnections()


mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
mycursor = mydb.cursor()


#get credentials ::

# import socket    
# hostname = socket.gethostname()    
# IPAddr = socket.gethostbyname(hostname)    
# print("Your Computer Name is:" + hostname)    
# print("Your Computer IP Address is:" + IPAddr)    

# Your Computer Name is:LAPTOP-RBAGRA85
# Your Computer IP Address is:192.168.56.1

#new database creation ::

# mycursor.execute("Create database fileInfo")

#print all databases that exist ::

# mycursor.execute("Show databases")
# for db in mycursor:
#     print (db)

#Create a new table  ::

# mycursor.execute("Create table backupData(file varchar(200), owner varchar(200))")

#print all tables that exist ::

# mycursor.execute("Show tables")
# for tb in mycursor :
    # print(tb)

#create entry in table ::

dataPush = "Insert into backupdata(file, owner) values (%s, %s)"

mycursor.executemany(dataPush,files)
mydb.commit()


    
#delete table contencts  ::

# deleteOperation = "DELETE FROM backupdata"

# mycursor.execute(deleteOperation)
# mydb.commit()
 

#print table contents ::

mycursor.execute("Select * from backupdata")
myFiles = mycursor.fetchall()

for row in myFiles:
    print (row)
    
    
# print(mydb)

