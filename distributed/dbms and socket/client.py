import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread
import pickle
import sys
from threading import Thread

class OtherNodes:
    def __init__(self):
        self.hosts = set()
        self.masterNodes = [] #list of active master IP addresses
        self.masterBiSockets = [] #client hosting and servers listening for database update
        self.activeMasterSockets = [] #clients connecting to dbms servers

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters


def serverConnection(nodes):
    host = socket.gethostbyname(socket.gethostname())
    # print(f"Enter the following address on the clients' ends for the socket connection :: {host} and the following port number :: 65123")
    s = socket.socket()
    port=65123
    s.bind((host,port))
    s.listen()

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
            file_data = f.read(9999999)
            clientsocket.send(file_data)
            f.close()
            print('File transfer completed')
        else :
            fileAvailability = "N"
            clientsocket.send(str(fileAvailability).encode())
            print("This file is not present at this endpoint, kindly try again")
            #file not present


def sendFileInfoAllMasters(files, nodes) :
    masters = get_master_nodes()
    nodes.masterNodes = []
    nodes.masterBiSockets = []
    
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65122))
            # if connected to another master, return the corresponding socket
            print(f'Sending DB update to master: {m}')
            nodes.masterNodes.append(m)
            nodes.masterBiSockets.append(s)
        except:
            continue

    for m in nodes.masterBiSockets :
        sendFileInfoSingleMaster(files, m)

def sendFileInfoSingleMaster(files,masterClientSocket) :
    get_request = masterClientSocket.recv(19000).decode()
    if get_request == 'give_update':
        masterClientSocket.sendall(pickle.dumps(files))
        masterClientSocket.recv(1000)

def receiveFiles(s, nodes, files):
    purpose = input("Do you want to receive a file? (Y/N)")
    s.send(purpose.encode())

    if purpose.lower() == "y"  :
        
        while True :
            print("Following is the file info of all the data available with associated host and port number")
            printTableData(nodes)
            
            fileName = input("Enter the filename that you want alongwith the extension ::  ")
            hostName = input("Enter the hostname where the desired file is located ::  ")
            
            try:
                sGetFiles = socket.socket()
                sGetFiles.settimeout(3)
                sGetFiles.connect((hostName, 65123))
                sGetFiles.settimeout(None)
            except:
                print('unable to connect to this node')
                continue

            sGetFiles.send(fileName.encode())
            fileAvaibility = sGetFiles.recv(100).decode()
            
            if fileAvaibility == "Y" :
                print("The requested file is getting transferred !! ")
                filename = os.path.join('backup', fileName)
                f = open(filename, 'wb')
                file_data = sGetFiles.recv(9999999)
                f.write(file_data)
                f.close()
                print("File  transferred and saved in the backup folder with the same file name !")
                
                files = getFileInfo()
                sendFileInfoAllMasters(files, nodes)
                print("Database Updated Successfully")
            else:
                print("The file is not available at the requested endpoint")
        
    else :
        print("Kindly wait now ...")
        print("If you want to request for a file, connect again.")
    
def handleConnection(nodes, files):
    passwordCheck = input("Enter the password to authenticate the connection:  ")

    for s in nodes.activeMasterSockets : 
        s.send(passwordCheck.encode())
        
        # while True :
        passwordVerified = s.recv(100).decode()
        
        print (f"Received input :: {passwordVerified} ")
        if(passwordVerified == "Correct") : 
            print("Password authentication successful")
            t3 = Thread(target=sendFileInfoAllMasters, args=(files, nodes))
            t3.start()
            t1 = Thread(target=receiveFiles, args=(s, nodes, files))
            t1.start()
        elif (passwordVerified == "Wrong") : 
            print("Password authentication unsuccessful")
            print("The connection will be aborted")
            exit()
    
    t2 = Thread(target=serverConnection, args=(nodes, ))
    t2.start()
def initiateSocketConnection(masters, nodes, files):
    for m in masters : 
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65121))
            print(f'Connected with master: {m}')
            nodes.masterNodes.append(m)
            nodes.activeMasterSockets.append(s)
        except:
            continue
    
    if len(nodes.masterNodes) != 0: 
        info_obtaining_thread = Thread(target=handleConnection, args=(nodes, files))
        info_obtaining_thread.start()
        
    else:
        print('No active master nodes.')
        # handleConnection(s)

def main():
    masters = get_master_nodes()
    files = getFileInfo()

    nodes = OtherNodes()

    initiateSocketConnection(masters,nodes,files)
    

#get credentials ::
def getCredentials():
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is:" + hostname)    
    print("Your Computer IP Address is:" + IPAddr)

def getFileInfo():
    currentIPAddress = socket.gethostbyname(socket.gethostname())
    userData=[]
    files=os.listdir('backup')

    for file in (files):
        userData.append(currentIPAddress)
        
    files = tuple(zip(files, userData))
    return files

#print all tables that exist ::
def printTables(mycursor):
    mycursor.execute("Show tables")
    for tb in mycursor :
        print(tb)


#print table contents ::
def printTableData(nodes):      
    for ip_address in nodes.masterNodes :
        try :
            mydb = mysql.connector.connect(host=ip_address, user="root",passwd="letmepass", database="fileInfo")
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM filebackupdata ORDER BY file ASC")
            myFiles = mycursor.fetchall()

            for row in myFiles:
                print (row)

            break
        except :
            continue
        
    
def printDatabaseName(mydb) :
    print(mydb)

if __name__ == '__main__' :
    main()