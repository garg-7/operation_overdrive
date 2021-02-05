import cv2
import numpy as np
import socket
import sys
import pickle
import struct

cap = cv2.VideoCapture(0)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

size = (frame_width, frame_height)

result = cv2.VideoWriter('client_webcam.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         30, size)

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((socket.gethostname(), 8089))

while True:
    ret, frame = cap.read()
    result.write(frame)
    # Serialize frame
    data = pickle.dumps(frame)

    # Send message length first
    message_size = struct.pack("L", len(data))  # CHANGED

    # Then data
    clientsocket.sendall(message_size + data)
cap.release()
cv2.destroyAllWindows()
