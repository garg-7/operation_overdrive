#pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread

def initiateSocketConnection():
    s = socket.socket()
    port=9077
    s.bind(('127.0.0.1',port))
    s.listen() 
    manageConnections(s)

def manageConnections (s):
    clients = []
    while True:  
        clientsocket, address = s.accept()
        clients.append((clientsocket, address))
        start_new_thread(handleConnection, (clientsocket , address))
        print(f"Connected with {address}")


def handleConnection(currentClient,address) :
    passwordCheck =  currentClient.recv(100).decode()
    if(passwordCheck == "letmepass"):
        print(f"Password authentication successful with {address}")
        currentClient.send(str("Correct").encode())
    else : 
        #server to be closed 
        print(f"Password authentication unsuccessful with {address}")
        currentClient.send(str("Wrong").encode())
        
    purposeCheck =  currentClient.recv(100).decode()
    
    if(purposeCheck == 'Y'):
        print(f"File Transfer Requested by address : {address}")
    else :
        #do something
        print()        
    
def main():
    currentUserName = getpass.getuser()
    # print(currentUserName)
    
    mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()
    
    initiateSocketConnection()
    
    # files = getFileInfo(currentUserName)
    
    # databaseCreation(mycursor)
    
    # printDatabases(mycursor)
    
    # printDatabaseName(mydb)
    
    # createTable(mycursor)
    
    # printTables(mycursor)
    
    # createTableEntry(mycursor,mydb,files)
    
    # deteleTableData(mycursor,mydb)
    
    # printTableData(mycursor)



#get credentials ::
def getCredentials():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is:" + hostname)    
    print("Your Computer IP Address is:" + IPAddr)    

    # Your Computer Name is:LAPTOP-RBAGRA85
    # Your Computer IP Address is:192.168.56.1

def getFileInfo(currentUserName):
    userData=[]
    files=os.listdir('backup')
    # print(files)

    for file in (files):
        userData.append(currentUserName)
        
    files = tuple(zip(files, userData))
    return files 

#new database creation ::
def databaseCreation(mycursor):
    mycursor.execute("Create database fileInfo")

# print all databases that exist ::
def printDatabases(mycursor):
    mycursor.execute("Show databases")
    for db in mycursor:
        print (db)

#Create a new table  ::
def createTable(mycursor):
    mycursor.execute("Create table backupData(file varchar(200), owner varchar(200))")


#print all tables that exist ::
def printTables(mycursor):
    mycursor.execute("Show tables")
    for tb in mycursor :
        print(tb)

#create entry in table ::
def createTableEntry(mycursor,mydb,files):
    dataPush = "Insert into backupdata(file, owner) values (%s, %s)"
    mycursor.executemany(dataPush,files)
    mydb.commit()


#delete table contents  ::
def deteleTableData(mycursor,mydb) : 
    deleteOperation = "DELETE FROM backupdata"
    mycursor.execute(deleteOperation)
    mydb.commit()
 

#print table contents ::
def printTableData(mycursor):
    mycursor.execute("Select * from backupdata")
    myFiles = mycursor.fetchall()

    for row in myFiles:
        print (row)
    
def printDatabaseName(mydb) :
    print(mydb)

if __name__ == '__main__' :
    main()