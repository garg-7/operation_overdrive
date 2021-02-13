import socket
import sys

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters

def contact_master(masters):
    # masters are listening on 65121 for new nodes
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65121))
            # if connected to another master, return the corresponding socket
            return s
        except socket.timeout:
            continue

def main():
    masters = get_master_nodes()

    master_soc = contact_master(masters)

    if master_soc:
        master_soc.send('give'.encode())
        received_node_info = master_soc.recv(99999999)
        for i in received_node_info:
            print(i)
    else:
        print("We hoped this day would never come...")
        print("Unfortunately it has...")
        print("[FATAL ERROR] No master nodes online.")
        sys.exit()
    
    # do the database thing now...
    # to add - query all the nodes on 65123 for the latest database
    # after getting the database... consider whatever needs to be done
    # for the redundancy of data... do that in the background...
    # do whatever requesting you need need to do in foreground...
    pass

if __name__ == '__main__':
    main()
