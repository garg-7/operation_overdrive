import pickle
import socket
from threading import Thread
import time
import multi

def main():
    host = socket.gethostbyname(socket.gethostname())
    print(host)
    port = 11112

    # welcoming socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print('Listening for connections...')

    conn_socket, client = s.accept()
    print(f'Connected with {client}')
    print(f'Sending stream...')

    # for mic stream
    m = multi.manager()
    m_to_store = multi.manager()

    # for speaker loopback
    m1 = multi.manager()
    m1_to_store = multi.manager()

    # start recording
    t = Thread(target=multi.main, args=(m,m_to_store, m1, m1_to_store))
    t.start()

    # # give 3 seconds for the buffer to fill up
    # time.sleep(0.1)

    print('Starting to sending audio stream...')
    while m.keep_going:
        try:
            data_to_be_sent = {
                    'speaker':  m.frames[0], 
                    'mic':      m1.frames[0]
                    }
            conn_socket.send(pickle.dumps(data_to_be_sent))
            m.frames.pop(0)
            m1.frames.pop(0)
        except IndexError:
            pass

if __name__ == '__main__':
    main()


