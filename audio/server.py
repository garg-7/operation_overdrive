import socket
import read_music
from threading import Thread
import time


def main():
    host = '127.0.0.1'
    port = 11112

    # welcoming socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print('Listening for connections...')

    while True:
        conn_socket, client = s.accept()
        print(f'Connected with {client}')
        print(f'Sending stream...')
        m = read_music.manager()
        m_to_store = read_music.manager()
        speaker = read_music.get_speaker()
        read_music.set_speaker_loopback(speaker)
        
        # start recording 
        t = Thread(target=read_music.main, args=(m,m_to_store))
        t.start()
        
        # # give 3 seconds for the buffer to fill up
        # time.sleep(0.1)

        print('Starting sending audio stream...')
        sent = 0
        failed = 0
        while m.keep_going:
            try:
                data_to_be_sent = m.frames[0]
                conn_socket.send(data_to_be_sent)
                m.frames.pop(0)
                sent+=1
                # if sent%2==0:
                #     print(sent)
            except IndexError:
                failed+=1
                pass
        
        # print('I exited')
        t.join()
        read_music.reset_default_mic()
if __name__ == '__main__':
    main()


