import socket
import zlib
import pygame
import cv2
import numpy as np

WIDTH = 1920  # default
HEIGHT = 1080  # default
HOST = "0.0.0.0"  # default
PORT = 9999  # default


def setup():
    global WIDTH
    global HEIGHT
    global HOST
    print()
    print("To connect to server, complete the setup: ")
    print()
    HOST = input("Enter the IP address of server (IPv4): ")
    print()
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
    SCREEN_SIZE = (1920, 1080)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("client_sceen.avi", fourcc, 20.0, (1920, 1080))

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

            pygame.image.save_extended(img, "loser.png")

            variable = cv2.imread('loser.png')

            # cv2.imshow('loser', variable)

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
    setup()
    connect_to_server()
