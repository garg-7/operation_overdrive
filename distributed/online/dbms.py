# pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import pyrebase
import os
import getpass
import socket
from _thread import start_new_thread

def initiateSocketConnection(db):
    host = socket.gethostname()
    print(f"Enter the following address on the clients' ends for the socket connection :: {host}")
    s = socket.socket()
    port=9000
    s.bind((host,port))
    s.listen()
    manageConnections(s,db)

def manageConnections (s,db):
    currentPortNumber = 9001
    while True:  
        clientsocket, address = s.accept()
        clients.append((clientsocket, address))
        start_new_thread(handleConnection, (clientsocket , address,currentPortNumber,db))
        currentPortNumber = currentPortNumber + 1  
        print(f"Connected with {address}")


def handleConnection(currentClient,address,currentPortNumber,db) :
    passwordCheck =  currentClient.recv(100).decode()
    if(passwordCheck == "letmepass"):
        print(f"Password authentication successful with {address}")
        currentClient.send(str("Correct").encode())
        intermediateStep =   currentClient.recv(100).decode()
        currentClient.send(str(currentPortNumber).encode())
        intermediateStep =   currentClient.recv(100).decode()
        
        print("Updating database")
        deteleTableData(db)
        files=getFileInfo(str("9000"))
        createTableEntry(db,files)
        for client in clients :
            try :
                client[0].send(str("Update Database").encode())
                intermediateStep =   client[0].recv(100).decode()
                # print("yo")
            except :
                continue
        print("Database updated successfully")
            
        purposeCheck =  currentClient.recv(100).decode()
        
        if(purposeCheck == 'Y'):
            print(f"File Transfer Requested by address : {address}")
        else :
            #do something
            print(f"{address} will participate in file transfer")
            
        # while True : 
        #     fileRequested = currentClient.recv(100).decode()
        #     if os.path.isfile(os.path.join('backup', fileRequested)) :
        #         fileAvailibility = "Y"
        #         currentClient.send(str(fileAvailibility).encode())
        #         filename = os.path.join('backup', fileRequested)
        #         f = open(os.path.join('backup', fileRequested) , 'rb')
        #         file_data = f.read(110241024)
        #         currentClient.send(file_data)
        #         print('File transfer completed')
        #     else :
        #         fileAvailibility = "N"
        #         currentClient.send(str(fileAvailibility).encode())
        #         print("This file is not present at this endpoint, kindly try again")
        #         #file not present
            
    
    else : 
        #server to be closed 
        print(f"Password authentication unsuccessful with {address}")
        currentClient.send(str("Wrong").encode())
        
    
def main():
    # currentUserName = getpass.getuser()
    # print(currentUserName)

    currentHostName = socket.gethostname()
    
    firebaseConfig = {"apiKey": "AIzaSyCEjFB1a4S_B8immDooU32nXWyUioOC3Ww",
    "authDomain": "protocolsinarms.firebaseapp.com",
    "databaseURL": "https://protocolsinarms-default-rtdb.firebaseio.com",
    "projectId": "protocolsinarms",
    "storageBucket": "protocolsinarms.appspot.com",
    "messagingSenderId": "159255006191",
    "appId": "1:159255006191:web:df5d6ca506df02def1041a",
    "measurementId": "G-0FKTBHCNWQ"}

    firebase = pyrebase.initialize_app(firebaseConfig)

    db = firebase.database()
    
    initiateSocketConnection(db)


#get credentials ::
def getCredentials():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is:" + hostname)    
    print("Your Computer IP Address is:" + IPAddr)    

    # Your Computer Name is:LAPTOP-RBAGRA85
    # Your Computer IP Address is:192.168.56.1

def getFileInfo(portNum):
    userData=[]
    portData =[]
    files=os.listdir('backup')
    currentHostName = socket.gethostname()

    for file in (files):
        userData.append(currentHostName)
        portData.append(portNum)
        
    files = tuple(zip(files, userData,portData))
    return files 


#create entry in table ::
def createTableEntry(db,files):
    for file in files :
        db.push(file)


#delete table contents  ::
def deteleTableData(db) : 
    db.remove()
 

#print table contents ::
def printTableData(db):
    tasks = db.get()

    for task in tasks.each() :
        print(task.val())
    
clients = []

if __name__ == '__main__' :
    main()