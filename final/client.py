import socket
import zlib
import pygame
import cv2
import numpy as np
from threading import Thread
from speaker_client import main as audio_main

WIDTH = 1366  # default
HEIGHT = 768  # default
HOST = "0.0.0.0"  # default
PORT = 9999  # default


def setup():
    global WIDTH
    global HEIGHT
    global HOST

    HOST = input("Enter the IP address of the video server (IPv4): \n")
    # print("Enter the dimension [should be same as server]")
    # WIDTH = int(input("WIDTH: "))
    # HEIGHT = int(input("HEIGHT: "))


def getAll(conn, length):
    buffer = b''
    while len(buffer) < length:
        data = conn.recv(length - len(buffer))
        if not data:
            return data
        buffer += data
    return buffer


def connect_to_server():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(HOST)
    fake_screen = screen.copy()

    clock = pygame.time.Clock()
    # display screen resolution, get it from your OS settings
    SCREEN_SIZE = (1366, 768)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("client_sceen.avi", fourcc, 12.0, (1366, 768))

    ADDR = (HOST, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect(ADDR)

        lHEIGHT = HEIGHT
        lWIDTH = WIDTH

        watching = True
        while watching:
            size_len = int.from_bytes(server.recv(1), byteorder='big')

            size = int.from_bytes(server.recv(size_len), byteorder='big')

            pixels = zlib.decompress(getAll(server, size))

            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')
            try:
                pygame.image.save_extended(img, "temp.png")
            except pygame.error:
                continue
                
            variable = cv2.imread('temp.png')

            # cv2.imshow('temp', variable)

            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(variable)
            # convert colors from BGR to RGB
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            out.write(frame)

            fake_screen.blit(img, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    out.release()
                    break
                elif event.type == pygame.VIDEORESIZE:
                    lWIDTH, lHEIGHT = event.dict['size']

            screen.blit(pygame.transform.scale(
                fake_screen, (lWIDTH, lHEIGHT)), (0, 0))

            pygame.display.flip()

            clock.tick(60)
    finally:
        server.close()


if __name__ == '__main__':
    setup() # for video
    t1 = Thread(target=connect_to_server, args=()) # connect to video server
    t1.start()

    audio_main()