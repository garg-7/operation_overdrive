import pickle
import socket
import sys
from threading import Thread
import time

class NodesInfo:
    def __init__(self):
        self.hosts = []
        self.keep_going = True

def get_master_nodes():
    masters = []
    f = open('master_nodes.txt')
    for line in f.readlines():
        masters.append(line.strip())
    return masters

def contact_masters(masters):
    # other masters listening on 65120
    for m in masters:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((m, 65120))
            # if connected to another master, return the corresponding socket
            return s
        except socket.timeout:
            print(f'Timed out with {m}')
            continue

def get_nodes_list(master_soc, nodes):
    master_soc.send('give'.encode())
    recv_nodes = master_soc.recv(9999999)
    nodes.hosts = recv_nodes
    return

def handle_node_request(soc, client, nodes):
    get_request = soc.recv(100).decode()
    if get_request == 'give':
        soc.sendall(pickle.dumps(nodes.hosts))
    latest_time = time.time()
    nodes.hosts.append((client, latest_time))
    return

def listen_for_new_nodes(nodes):
    # listen on 65121
    # act as a tracker for new nodes
    inviting_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_master_ip = socket.gethostbyname(socket.gethostname())
    inviting_soc.bind((current_master_ip, 65121))
    inviting_soc.listen()
    while nodes.keep_going:
        client_soc, client = inviting_soc.accept()
        node_handling_thread = Thread(target=handle_node_request,
                                        args=(client_soc, client, nodes, ))
        node_handling_thread.start()
    pass

def handle_master_node(soc, nodes):
    get_request = soc.recv(100).decode()
    if get_request == 'give':
        soc.sendall(pickle.dumps(nodes.hosts))
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

def ping_active_nodes(nodes):
    # ping on 65122 or run some terminal command to
    # re-verify availability
    pass

def main():
    masters = get_master_nodes()

    nodes = NodesInfo()
    # find any other active servers
    existing_master = contact_masters(masters)

    # sys.exit()
    # if server found, obtain host list
    if existing_master:
        get_nodes_list(existing_master, nodes)

    # listening for new nodes trying to find other nodes
    listening_for_nodes_thread = Thread(target=listen_for_new_nodes,
                                            args=(nodes, ))
    listening_for_nodes_thread.start()
    print('Listening for requests from nodes...')

    # listening for new masters joining in
    listening_for_masters_thread = Thread(target=listen_for_masters,
                                            args=(nodes, ))
    listening_for_masters_thread.start()
    print('Listening for requests from other masters...')
    
    # pinging existing nodes to confirm availability
    pinging_thread = Thread(target=ping_active_nodes, args=(nodes, ))
    pinging_thread.start()

    while True:
        if input().lower()=='stop':
            nodes.keep_going = False
            break
    
    listening_for_masters_thread.join()
    listening_for_nodes_thread.join()
    pinging_thread.join()
    print('Stopped the server.')


if __name__ == '__main__':
    main()