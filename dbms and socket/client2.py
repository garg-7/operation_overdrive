import mysql.connector
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
        if os.path.isfile(os.path.join('backup2', fileRequested)) :
            filename = os.path.join('backup2', fileRequested)
            f = open(os.path.join('backup2', fileRequested) , 'rb')
            file_data = f.read(110241024)
            clientsocket.send(file_data)
            print('File transfer completed')
        else :
            print("This file is not present at this endpoint, kindly try again")
            #file not present

def initiateSocketConnection(mycursor,mydb):
    s = socket.socket()
    host = input("Please enter the hostname of the server : ")
    port = 9000
    s.connect((host, port))
    
    portObject = globalVariables(0)
    
    handleConnection(mycursor,mydb,s,portObject)

def receiveFilesFromServer(s,fileName):
    s.send(fileName.encode())
            
    print("The requested file is getting transferred !! ")
    filename = os.path.join('backup2', fileName)
    f = open(filename, 'wb')
    file_data = s.recv(110241024)
    f.write(file_data)
    f.close()
    print("File  transferred and saved in the backup folder with the same file name !")
    

def receiveFiles(s,mycursor):
    print("Enter Y if you want to receive a file or N if you want to participate in the file transfer")
    purpose = input()
    s.send(purpose.encode())
    
    if purpose == "Y" :
        print("Following is the file info of all the data available with associated host and port number")
        printTableData(mycursor)
        
        while True :
            fileName = input("Enter the filename that you want alongwith the extension ::  ")
            hostName = input("Enter the hostname where the desired file is located ::  ")
            portName = input("Enter the port number where socket connection is to be established ::  ")
            portName = int(portName)
            
            if portName == 9000 :
                start_new_thread(receiveFilesFromServer, (s,fileName))
            
            sGetFiles = socket.socket()
            sGetFiles.connect((hostName, portName))

            sGetFiles.send(fileName.encode())
            
            print("The requested file is getting transferred !! ")
            filename = os.path.join('backup2', fileName)
            f = open(filename, 'wb')
            file_data = sGetFiles.recv(110241024)
            f.write(file_data)
            f.close()
            print("File  transferred and saved in the backup folder with the same file name !")
        
    else :
        print("Kindly wait now ...")
        print("If you want to request for a file, connect again.")
    
def handleConnection(mycursor,mydb,s,portObject):
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
            start_new_thread(receiveFiles, (s,mycursor))
            
        elif (passwordVerified == "Wrong") : 
            print("Password authentication unsuccessful")
            print("The connection will be aborted")
            exit()
        
        elif (passwordVerified == "Update Database") : 
            print("second last")
            files=getFileInfo(portObject.currentPortNumber)
            createTableEntry(mycursor,mydb,files)
            print("Database successfully updated")
            
        else :
            serverPortNumber = int(passwordVerified)
            portObject.currentPortNumber = serverPortNumber
            start_new_thread(serverConnection, (serverPortNumber,))    


def main():
    # currentUserName = getpass.getuser()
    # print(currentUserName)
    
    currentHostName = socket.gethostname()
    
    mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()
    
    
    initiateSocketConnection(mycursor,mydb)
    
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

def getFileInfo(portNum):
    currentHostName = socket.gethostname()
    userData=[]
    portData =[]
    files=os.listdir('backup2')
    # print(files)

    for file in (files):
        userData.append(currentHostName)
        portData.append(str(portNum))
        
    files = tuple(zip(files, userData,portData))
    # print(files)
    return files 

#print all tables that exist ::
def printTables(mycursor):
    mycursor.execute("Show tables")
    for tb in mycursor :
        print(tb)

#create entry in table ::
def createTableEntry(mycursor,mydb,files):
    mycursor.execute("Select * from filebackupdata")
    alreadyInputFiles = mycursor.fetchall()
    
    dataPush = "Insert into filebackupdata(file, owner, port) values (%s, %s, %s)"
    for file in files :
        if file not in alreadyInputFiles :
            mycursor.execute(dataPush,file)
            mydb.commit()


#delete table contents  ::
def deteleTableData(mycursor,mydb) : 
    deleteOperation = "DELETE FROM filebackupdata"
    mycursor.execute(deleteOperation)
    mydb.commit()
 

#print table contents ::
def printTableData(mycursor):
    mycursor.execute("Select * from filebackupdata")
    myFiles = mycursor.fetchall()

    for row in myFiles:
        print (row)
    
def printDatabaseName(mydb) :
    print(mydb)


if __name__ == '__main__' :
    main()