# pip install mysql-connector-python
# https://dev.mysql.com/downloads/installer/

import mysql.connector
import os
import getpass
import socket
from _thread import start_new_thread
import pickle
import socket
import sys
from threading import Thread

class NodesInfo:
    def __init__(self):
        self.hosts = {}
        self.keep_going = True
        self.database = set()

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters

def contact_masters(masters):
    # other masters listening on 65120
    sockets_masters= []
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65120))
            # if connected to another master, return the corresponding socket
            print(f'Connected with master: {m}\n')
            # return s
            sockets_masters.append(s)
        except socket.timeout:
            print(f'Timed out with {m}\n')
            continue
    return sockets_masters

def get_nodes_list(master_soc, nodes):
    master_soc.send('give'.encode())
    recv_nodes = master_soc.recv(9999999)
    recv_data = pickle.loads(recv_nodes)

    for file in recv_data :
        nodes.database.add(file)
    return


def handle_master_node(soc, nodes):
    get_request = soc.recv(100).decode()
    if get_request == 'give':
        soc.sendall(pickle.dumps(nodes.database))
    return

def listen_for_masters(nodes):
    # listen on 65120
    inviting_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_master_ip = socket.gethostbyname(socket.gethostname())
    inviting_soc.bind((current_master_ip, 65120))
    inviting_soc.listen()
    while nodes.keep_going:
        client_soc, client = inviting_soc.accept()
        master_handling_thread = Thread(target=handle_master_node,
                                        args=(client_soc, nodes, ))
        master_handling_thread.start()
    pass


def initiateSocketConnection(nodes):
    host = socket.gethostname()
    print(f"Enter the following address on the clients' ends for the socket connection :: {host}")
    s = socket.socket()
    port=65521
    s.bind((host,port))
    s.listen()
    while True:
        clientsocket, address = s.accept()
        clients.append((clientsocket, address))
        start_new_thread(handleConnection, (clientsocket, address, nodes))
        print(f"Connected with {address}")


def handleConnection(currentClient,address,nodes) :
    passwordCheck =  currentClient.recv(100).decode()
    if(passwordCheck == "letmepass"):
        print(f"Password authentication successful with {address}")
        currentClient.send(str("Correct").encode())
        intermediateStep =   currentClient.recv(100).decode()

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


def handle_db_update(s, nodes):
    s.sendall('give_update'.encode())
    print("Updating database")
    get_file_info = pickle.loads(s.recv(99999999))

    mydb = mysql.connector.connect(host=socket.gethostbyname(socket.gethostname()), user="root", passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()

    # remove existing entries from db
    mycursor.execute(f"DELETE FROM filebackupdata WHERE owner={get_file_info[0][0]}")
    mydb.commit()
    # add received entries to db
    push_cmd = (f"Insert into filebackup(file, owner) ")
    
    for i in get_file_info:
        mycursor.execute(push_cmd, i)
        mydb.commit()

    # remove existing entries from main memory
    for i in nodes.database:
        if i[0]==get_file_info[0][0]:
            nodes.database.remove(i)

    # add received entries to main memory
    for item in get_file_info:
        nodes.database.add(item)

    print("Database updated successfully")
    
def listen_for_db_update(nodes):
    # listen on 65122
    inviting_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_master_ip = socket.gethostbyname(socket.gethostname())
    inviting_soc.bind((current_master_ip, 65122))
    inviting_soc.listen()
    while nodes.keep_going:
        client_soc, client = inviting_soc.accept()
        db_handling_thread = Thread(target=handle_db_update,
                                        args=(client_soc, client[0], nodes, ))
        db_handling_thread.start()

def main():
    # currentUserName = getpass.getuser()
    # print(currentUserName)

    masters = get_master_nodes()
    nodes = NodesInfo()
    # find any other active servers
    existing_masters = contact_masters(masters)

    # sys.exit()
    # if server found, obtain host list
    if existing_masters:
        for existing_master in existing_masters :
            print("Requesting this master for file info data...")
            get_nodes_list(existing_master, nodes)
            # print("Node data received:")
            # for i in nodes.hosts.keys():
            #     print(i, nodes.hosts[i])

    deteleTableData()
    createTableEntry(nodes.database)

    # listening for new masters joining in
    listening_for_masters_thread = Thread(target=listen_for_masters,
                                            args=(nodes, ))
    listening_for_masters_thread.start()
    print('Listening for requests from other masters...')

    listening_for_db_update_thread = Thread(target=listen_for_db_update,
                                            args=(nodes, ))
    listening_for_db_update_thread.start()

    currentHostName = socket.gethostname()

    mydb = mysql.connector.connect(host="LAPTOP-RBAGRA85", user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()

    initiateSocketConnection(nodes)


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
    mycursor.execute("Create table filebackupData(file varchar(200), owner varchar(200), port varchar(200))")


#print all tables that exist ::
def printTables(mycursor):
    mycursor.execute("Show tables")
    for tb in mycursor :
        print(tb)

#create entry in table ::
def createTableEntry(files):
    hostName = socket.gethostname()
    mydb = mysql.connector.connect(host=hostName, user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()

    mycursor.execute("Select * from filebackupdata")
    alreadyInputFiles = mycursor.fetchall()

    dataPush = "Insert into filebackupdata(file, owner) values (%s, %s)"
    for file in files :
        if file not in alreadyInputFiles :
            mycursor.execute(dataPush,file)
            mydb.commit()


#delete table contents  ::
def deteleTableData() :
    hostName = socket.gethostname()
    mydb = mysql.connector.connect(host=hostName, user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()

    deleteOperation = "DELETE FROM filebackupdata"
    mycursor.execute(deleteOperation)
    mydb.commit()


#print table contents ::
def printTableData():
    hostName = socket.gethostname()
    mydb = mysql.connector.connect(host=hostName, user="root",passwd="letmepass", database="fileInfo")
    mycursor = mydb.cursor()

    mycursor.execute("Select * from filebackupdata")
    myFiles = mycursor.fetchall()

    for row in myFiles:
        print (row)

def printDatabaseName(mydb) :
    print(mydb)

clients = []

if __name__ == '__main__' :
    main()


#65120 : master listening to other masters
#65121 : master listening to other nodes
#65122 : client listening to other masters
#65123 : cleint listening to othert clients
