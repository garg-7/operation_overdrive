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
    print(f"Enter the following address on the clients' ends for the socket connection :: {host}")
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
    fileRequested = clientsocket.recv(100).decode()
    if os.path.isfile(os.path.join('backup', fileRequested)) :
        filename = os.path.join('backup', fileRequested)
        f = open(filename, 'wb')
        file_data = clientsocket.recv(110241024)
        f.write(file_data)
        f.close()
        print('File transfer completed')
    else :
        print()
        #file not present

def initiateSocketConnection(mycursor,mydb):
    s = socket.socket()
    host = input("Please enter the hostname of the server : ")
    port = 9000
    s.connect((host, port))
    
    portObject = globalVariables(0)
    
    handleConnection(mycursor,mydb,s,portObject)

def receiveFiles(s,mycursor):
    print("Enter Y if you want to receive a file or N if you want to participate in the file transfer")
    purpose = input()
    # s.send(purpose.encode())
    
    if purpose == "Y" :
        print("Following is the file info of all the data available with associated host and port number")
        printTableData(mycursor)
        
        
    else :
        print("Kindly wait now ...")
        print("If you want to request for a file, connect again.")
    
def handleConnection(mycursor,mydb,s,portObject):
    print("Enter the password to authenticate the connection ! ")
    passwordCheck = input()

    s.send(passwordCheck.encode())
    
    while True :
        passwordVerified = s.recv(100).decode()
        print (f"Received Input ::        {passwordVerified}")
        if(passwordVerified == "Correct") : 
            print("Password authentication successful")
            start_new_thread(receiveFiles, (s,mycursor))
            
            
        elif (passwordVerified == "Wrong") : 
            print("Password authentication unsuccessful")
            print("The connection will be aborted")
            exit()
        
        elif (passwordVerified == "Update Database") : 
            # print()
            files=getFileInfo(portObject.currentPortNumber)
            createTableEntry(mycursor,mydb,files)
            
        else : 
            print()
            serverPortNumber = s.recv(100).decode()
            serverPortNumber = int(serverPortNumber)
            portObject.currentPortNumber = serverPortNumber
            s.send(passwordCheck.encode())
            
            start_new_thread(serverConnection, (serverPortNumber))
    
    


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

def getFileInfo(currentHostName,portNum):
    userData=[]
    portData =[]
    files=os.listdir('backup')
    # print(files)

    for file in (files):
        userData.append(currentHostName)
        portData.append(str(portNum))
        
    files = tuple(zip(files, userData,portData))
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
            mycursor.executemany(dataPush,files)
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