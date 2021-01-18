# pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread

def initiateSocketConnection():
    host = socket.gethostname()
    print(f"Enter the following address on the clients' ends for the socket connection :: {host}")
    s = socket.socket()
    port=9000
    s.bind((host,port))
    s.listen()
    manageConnections(s)

def manageConnections (s):
    currentPortNumber = 9001
    while True:  
        clientsocket, address = s.accept()
        clients.append((clientsocket, address))
        start_new_thread(handleConnection, (clientsocket , address,currentPortNumber))
        currentPortNumber = currentPortNumber + 1 
        print(f"Connected with {address}") 
        
        print("Updating database")
        for client in clients :
            clients[0].send(str("Update Database").encode())
        print("Database updated successfully")


def handleConnection(currentClient,address,currentPortNumber) :
    passwordCheck =  currentClient.recv(100).decode()
    if(passwordCheck == "letmepass"):
        print(f"Password authentication successful with {address}")
        currentClient.send(str("Correct").encode())
        # strPortNum = str(currentPortNumber)
        currentClient.send(str(currentPortNumber).encode())
            
        purposeCheck =  currentClient.recv(100).decode()
        
        if(purposeCheck == 'Y'):
            print(f"File Transfer Requested by address : {address}")
        else :
            #do something
            print(f"{address} will participate in file transfer")
    
    else : 
        #server to be closed 
        print(f"Password authentication unsuccessful with {address}")
        currentClient.send(str("Wrong").encode())
        
    
def main():
    # currentUserName = getpass.getuser()
    # print(currentUserName)

    currentHostName = socket.gethostname()
    
    # mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
    # mycursor = mydb.cursor()
    
    initiateSocketConnection()
    
    # files = getFileInfo(currentHostName,portNumber)
    
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

def getFileInfo(currentHostName,portNum):
    userData=[]
    portData =[]
    files=os.listdir('backup')
    # print(files)

    for file in (files):
        userData.append(currentHostName)
        portData.append(portNum)
        
    files = tuple(zip(files, userData,portData))
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
    
clients = []

if __name__ == '__main__' :
    main()