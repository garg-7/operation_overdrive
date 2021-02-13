import pyrebase
import os
import getpass
import socket
from _thread import start_new_thread

class globalVariables():
    def __init__ (self, portNum) :
        self.currentPortNumber = portNum

def serverConnection(portNum):
    host = socket.gethostname()
    print(f"Enter the following address on the clients' ends for the socket connection :: {host} and the following port number :: {portNum}")
    s = socket.socket()
    port=portNum
    s.bind((host,port))
    s.listen()
    #something
    
    while True:  
        clientsocket, address = s.accept()
        start_new_thread(handleServerConnection, (clientsocket , address))
        print(f"Connected with {address}") 
        
def handleServerConnection(clientsocket, address):
    while True:
        fileRequested = clientsocket.recv(100).decode()
        if os.path.isfile(os.path.join('backup', fileRequested)) :
            fileAvailability = "Y"
            clientsocket.send(str(fileAvailability).encode())
            filename = os.path.join('backup', fileRequested)
            f = open(os.path.join('backup', fileRequested) , 'rb')
            file_data = f.read(9999999999)
            clientsocket.send(file_data)
            print('File transfer completed')
        else :
            fileAvailability = "N"
            clientsocket.send(str(fileAvailability).encode())
            print("This file is not present at this endpoint, kindly try again")
            #file not present


def receiveFilesFromServer(s,fileName):
    s.send(fileName.encode())
    fileAvaibility = s.recv(100).decode()
    if fileAvaibility == "Y" :
        print("The requested file is getting transferred !! ")
        filename = os.path.join('backup', fileName)
        f = open(filename, 'wb')
        file_data = s.recv(9999999999)
        f.write(file_data)
        f.close()
        print("File  transferred and saved in the backup folder with the same file name !")
    print("The file is not available at the requested endpoint")
    

def receiveFiles(s,db):
    print("Enter Y if you want to receive a file or N if you want to participate in the file transfer")
    purpose = input()
    s.send(purpose.encode())
    
    if purpose == "Y" :
        
        while True :
            print("Following is the file info of all the data available with associated host and port number")
            printTableData(db)
            
            fileName = input("Enter the filename that you want alongwith the extension ::  ")
            hostName = input("Enter the hostname where the desired file is located ::  ")
            portName = input("Enter the port number where socket connection is to be established ::  ")
            portName = int(portName)
            
            # if portName == 9000 :
            #     start_new_thread(receiveFilesFromServer, (s,fileName))
            
            sGetFiles = socket.socket()
            sGetFiles.connect((hostName, portName))

            sGetFiles.send(fileName.encode())
            fileAvaibility = sGetFiles.recv(100).decode()
            
            if fileAvaibility == "Y" :
                print("The requested file is getting transferred !! ")
                filename = os.path.join('backup', fileName)
                f = open(filename, 'wb')
                file_data = sGetFiles.recv(9999999999)
                f.write(file_data)
                f.close()
                print("File  transferred and saved in the backup folder with the same file name !")
            else :
                print("The file is not available at the requested endpoint")
        
    else :
        print("Kindly wait now ...")
        print("If you want to request for a file, connect again.")
    
def handleConnection(s,db,portObject):
    print("Enter the password to authenticate the connection ! ")
    passwordCheck = input()

    s.send(passwordCheck.encode())
    
    while True :
        passwordVerified = ""
        passwordVerified = s.recv(100).decode()
        s.send(passwordCheck.encode())
        
        print (f"Received input ::             {passwordVerified} ")
        if(passwordVerified == "Correct") : 
            print("Password authentication successful")
            start_new_thread(receiveFiles, (s,db))
            
        elif (passwordVerified == "Wrong") : 
            print("Password authentication unsuccessful")
            print("The connection will be aborted")
            exit()
        
        elif (passwordVerified == "Update Database") : 
            # print("second last")
            files=getFileInfo(portObject.currentPortNumber)
            createTableEntry(db,files)
            print("Database successfully updated")
            
        else :
            serverPortNumber = int(passwordVerified)
            portObject.currentPortNumber = serverPortNumber
            start_new_thread(serverConnection, (serverPortNumber,))    

def initiateSocketConnection(db):
    s = socket.socket()
    host = input("Please enter the hostname of the server : ")
    port = 9000
    s.connect((host, port))
    
    portObject = globalVariables(0)
    
    handleConnection(s,db,portObject)

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

def getFileInfo(portNum):
    currentHostName = socket.gethostname()
    userData=[]
    portData =[]
    files=os.listdir('backup')
    # print(files)

    for file in (files):
        userData.append(currentHostName)
        portData.append(str(portNum))
        
    files = tuple(zip(files, userData,portData))
    # print(files)
    return files 


#create entry in table ::
def createTableEntry(db,files):
    for file in files :
        db.push(file)

 

#print table contents ::
def printTableData(db):
    tasks = db.get()

    for task in tasks.each() :
        print(task.val())


if __name__ == '__main__' :
    main()