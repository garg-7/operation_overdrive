import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread

def serverConnection(portNum):
    host = socket.gethostname()
    print(f"Enter the following address on the clients' ends for the socket connection :: {host}")
    s = socket.socket()
    port=portNum
    s.bind((host,port))
    s.listen()
    #something

def initiateSocketConnection():
    s = socket.socket()
    host = input("Please enter the hostname of the server : ")
    port = 9000
    s.connect((host, port))
    handleConnection(s)


def handleConnection(s):
    print("Enter the password to authenticate the connection ! ")
    passwordCheck = input()

    s.send(passwordCheck.encode())
    passwordVerified = s.recv(100).decode()

    if(passwordVerified == "Correct") : 
        print("Password authentication successful")
        serverPortNumber = s.recv(100).decode()
        serverPortNumber = int(serverPortNumber)
        
        start_new_thread(serverConnection, (serverPortNumber))
        
    else : 
        print("Password authentication unsuccessful")
        print("The connection will be aborted")
        exit()
        
    print("Enter Y if you want to receive a file or N if you want to participate in the file transfer")
    purpose = input()
    s.send(purpose.encode())


def main():
    # currentUserName = getpass.getuser()
    # print(currentUserName)
    
    currentHostName = socket.gethostname()
    
    # mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
    # mycursor = mydb.cursor()
    
    initiateSocketConnection()
    
    # files = getFileInfo(currentHostName,portNumber)
    
    # databaseCreation(mycursor)
    
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