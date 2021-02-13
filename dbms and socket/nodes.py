import pickle
import socket
import sys
from threading import Thread

class OtherNodes:
    def __init__(self):
        self.hosts = set()

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters

def get_other_nodes(soc, nodes):
    soc.send('give'.encode())
    received_node_info = pickle.loads(soc.recv(99999999))
    for i in received_node_info.keys():
        nodes.hosts.add(i)

def contact_masters(masters, nodes):
    # masters are listening on 65121 for new nodes
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65121))
            print(f'Connected with master: {m}')
            info_obtaining_thread = Thread(target=get_other_nodes, args=(s, nodes))
            info_obtaining_thread.start()
        except:
            continue

def main():
    masters = get_master_nodes()

    nodes = OtherNodes()
    contact_masters(masters, nodes)

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
