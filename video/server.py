import pickle
import socket
import struct

import cv2

HOST = '127.0.0.1'
PORT = 8089

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

s.bind((socket.gethostname(), PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

result = cv2.VideoWriter('server_webcam.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         30, (640, 480))


while True:
    conn, addr = s.accept()
    data = b''  # CHANGED
    payload_size = struct.calcsize("L")  # CHANGED
    while True:

        # Retrieve message size
        while len(data) < payload_size:
            data += conn.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]  # CHANGED

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Extract frame
        frame = pickle.loads(frame_data)

        result.write(frame)

        # Display
        cv2.imshow('frame', frame)
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    result.release()
