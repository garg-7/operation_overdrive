import socket
from threading import Thread
import time
import multi
import sys
import mss
import zlib
import pickle
import socket
import struct
import numpy as np
import cv2


def send_screen(conn, m):
    SCREEN_SIZE = (1920, 1080)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("server_screen.avi", fourcc, 20.0, (SCREEN_SIZE))

    with mss.mss() as mss_instance:
        rect = {'top': 0, 'left': 0,
                'width': 1920, 'height': 1080}

        while m.keep_going:

            img = mss_instance.grab(rect)
            frame = np.array(img)
            # convert colors from BGR to RGB
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            out.write(frame)
            pixels = zlib.compress(img.rgb, 6)

            size = len(pixels)

            size_len = (size.bit_length() + 7) // 8

            size_bytes = size.to_bytes(size_len, 'big')

            try:
                conn.send(bytes([size_len]))
                conn.send(size_bytes)
                conn.sendall(pixels)
            except:
                print(f'Client Disconnected [{conn}]')
                m.keep_going = False


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
    port = 11111

    # welcoming socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print('Listening for connections...')

    # for speaker loopback
    m = multi.manager()
    m_to_store = multi.manager()

    # for mic stream
    m1 = multi.manager()
    m1_to_store = multi.manager()


    

    result = cv2.VideoWriter('server_webcam.avi',
                            cv2.VideoWriter_fourcc(*'MJPG'),
                            30, (640, 480))

    # start recording
    t = Thread(target=multi.main, args=(m,m_to_store, m1, m1_to_store))
    t.start()
    i=0
    managers = [m, m1]

    while i<2:
        soc, client = s.accept()
        print(f'Connected with {client}.')
        # # give 3 seconds for the buffer to fill up
        # time.sleep(4)
        t1 = Thread(target=share_audio, args=(soc, managers[i]))
        t1.start()
        i+=1

    cam_soc, client = s.accept()
    screen_soc, _ = s.accept()
    print("connected video stream")
    vid = 'sshare'
    if vid=='webcam':
        cap = cv2.VideoCapture(0)
        while m.keep_going:
            ret, frame = cap.read()
            result.write(frame)
            # Serialize frame
            data = pickle.dumps(frame)

            # Send message length first
            message_size = struct.pack("L", len(data))  # CHANGED

            # Then data
            cam_soc.sendall(message_size + data)
        cap.release()
    else:
        vid_sending_thread = Thread(target=send_screen, args=(screen_soc, m))
        vid_sending_thread.start()
    t1.join()

if __name__ == '__main__':
    main()



