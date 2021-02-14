import pickle
import socket
import sys
from threading import Thread
import os

class OtherNodes:
    def __init__(self):
        self.hosts = set()

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters

def send_file_info(soc, files):
    get_request = soc.recv(100).decode()
    if get_request == "give":
        soc.sendall(pickle.dumps(files))

def contact_masters(masters, nodes, files):
    # masters are listening on 65121 for new nodes
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65121))
            print(f'Connected with master: {m}')
            info_obtaining_thread = Thread(target=send_file_info, args=(s, files))
            info_obtaining_thread.start()
        except:
            continue

def main():
    masters = get_master_nodes()

    currentIPAddress = socket.gethostbyname(socket.gethostname())
    # portNum = 65530 
    userData=[]
    portData =[]
    files=os.listdir('backup')

    for file in (files):
        userData.append(currentIPAddress)
        
    files = tuple(zip(files, userData))

    nodes = OtherNodes()
    contact_masters(masters, nodes, files)

    if nodes.hosts:
        print("Active nodes: ")
        for i in sorted(list(nodes.hosts)):
            print(i)
    else:
        print("We hoped this day would never come...")
        print("Unfortunately it has...")
        print("[FATAL ERROR] No nodes online.")
        sys.exit()
    
    # do the database thing now...
    # to add - query all the nodes on 65123 for the latest database
    # after getting the database... consider whatever needs to be done
    # for the redundancy of data... do that in the background...
    # do whatever requesting you need need to do in foreground...
    pass

if __name__ == '__main__':
    main()
