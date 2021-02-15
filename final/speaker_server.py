import socket
from threading import Thread
import time
import multi
import sys


def share_audio(conn_socket, m):
    while m.keep_going:
        try:
            data_to_be_sent = m.frames[0]
            # print(max(data_to_be_sent))
            conn_socket.send(data_to_be_sent)
            m.frames.pop(0)
        except IndexError:
            pass

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

    # for speaker loopback
    m = multi.manager()
    m_to_store = multi.manager()

    # start recording
    t = Thread(target=multi.main, args=(m,m_to_store))
    t.start()
    i=0
    soc, client = s.accept()
    print(f'Connected with {client}.')
        # # give 3 seconds for the buffer to fill up
        # time.sleep(4)
    t1 = Thread(target=share_audio, args=(soc, m))
    t1.start()
    i+=1
    t1.join()

if __name__ == '__main__':
    main()


