import socket
from zlib import decompress
from PIL import Image
import numpy as np
import cv2

import pygame

WIDTH = 1920
HEIGHT = 1080


def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf


def main(host='127.0.0.1', port=5000):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True 
    # display screen resolution, get it from your OS settings
    SCREEN_SIZE = (1920, 1080)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("output.avi", fourcc, 60.0, (SCREEN_SIZE))

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), port))
    try:
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break

            # Retreive the size of the pixels length, the pixels length and pixels
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))


            # Create the Surface from raw pixels
            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')
            frame = pygame.surfarray.array3d(img)
            #frame.swapaxes(0,1)
            cv2.imshow("screenshot", frame)
            out.write(frame)

            filename = 'test.jpg'
            # Using cv2.imwrite() method 
            # Saving the image 
            cv2.imwrite(filename, frame)

            #cv2.imshow('test',img)

            # Display the picture
            #screen.blit(img, (0, 0))
            #pygame.display.flip()
            clock.tick(60)
    finally:
        sock.close()


if __name__ == '__main__':
    main()