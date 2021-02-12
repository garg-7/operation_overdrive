import mss
import os
import pickle
import socket
import struct
import sys
from threading import Thread
import time
import zlib

from cv2 import cv2
import numpy as np
import pygame

import util


def send_screen(screen_soc, screen_manager):
    # compress the frame, send its size and then the frame
    while screen_manager.keep_going:
        try:
            img_bytes = screen_manager.frames[0]
            screen_manager.frames.pop(0)
            pixels = zlib.compress(img_bytes.rgb, 6)
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            size_bytes = size.to_bytes(size_len, 'big')
            try:
                screen_soc.send(bytes([size_len]))
                screen_soc.send(size_bytes)
                screen_soc.sendall(pixels)
            except:
                print(f'Client Disconnected [{screen_soc}]')
                screen_manager.keep_going = False
        except IndexError:
            pass


def send_webcam_feed(webcam_soc, webcam_manager):
    while webcam_manager.keep_going:
        try:
            frame_to_send = webcam_manager.frames[0]
            # print(max(data_to_be_sent))

            # Serialize frame
            data = pickle.dumps(frame_to_send)
            # Send message length first then data
            message_size = struct.pack("L", len(data))
            try:
                webcam_soc.sendall(message_size + data)
            except:
                print('Client not connected anymore...')
            webcam_manager.frames.pop(0)
        except IndexError:
            pass


def local_webcam_writer(webcam_manager):
    video_writer = cv2.VideoWriter('server_webcam.avi',
                            cv2.VideoWriter_fourcc(*'MJPG'),
                            1.5, (640, 480))
    while webcam_manager.keep_going:
        try:
            frame = webcam_manager.kept_frames[0]
            video_writer.write(frame)
            webcam_manager.kept_frames.pop(0)
        except IndexError:
            pass

def local_screen_writer(screen_manager):
    SCREEN_SIZE = (1920, 1080)
    WIDTH, HEIGHT = SCREEN_SIZE
    # define the codec
    # four character code used to specify the video codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    # create the video writer object
    out = cv2.VideoWriter("server_screen.avi", fourcc, 8, SCREEN_SIZE)

    while screen_manager.keep_going:
        try:
            img_bytes = screen_manager.kept_frames[0]
            screen_manager.kept_frames.pop(0)

            img = pygame.image.fromstring(img_bytes.rgb, (WIDTH, HEIGHT), 'RGB')
            os.makedirs("temp", exist_ok=True)
            pygame.image.save_extended(img, "temp/temp_screen.png")
            frame = cv2.imread("temp/temp_screen.png")

            # write the frame to the video file
            out.write(np.asarray(frame))
        except IndexError:
            pass
    os.remove("temp/temp_screen.png")
    os.rmdir("temp")


def record_webcam(webcam_manager):
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    count = 0
    while webcam_manager.keep_going:
        _, frame = cap.read()
        webcam_manager.frames.append(frame)
        webcam_manager.kept_frames.append(frame)
        count+=1
    duration = time.time() - start_time
    fps = count/duration
    print("webcam: %.2f fps" % fps, "over %.2f seconds" % duration)
    cap.release()
    print('webcam was released')


def record_screen(screen_manager):
    with mss.mss() as mss_instance:
        rect = {'top': 0, 'left': 0,
                'width': 1920, 'height': 1080}
        count = 0
        start_time = time.time()
        while screen_manager.keep_going:
            img_bytes = mss_instance.grab(rect)
            screen_manager.frames.append(img_bytes)
            screen_manager.kept_frames.append(img_bytes)
            count+=1
        duration = time.time() - start_time
        fps = count/duration
        print("screen share: %.2f fps" % fps, "over %.2f seconds" % duration)


def share_audio(conn_socket, speaker_manager):
    while speaker_manager.keep_going:
        try:
            data_to_be_sent = speaker_manager.frames[0]
            # print(max(data_to_be_sent))
            conn_socket.send(data_to_be_sent)
            speaker_manager.frames.pop(0)
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

    # for speaker stream
    speaker_manager = util.manager()

    # for mic stream
    mic_manager = util.manager()

    # for screen stream
    screen_manager = util.manager()
    
    # for webcam stream
    webcam_manager = util.manager()

    # setup recording audio from speaker and mic
    audio_recording_thread = Thread(target=util.main, args=(speaker_manager, mic_manager, webcam_manager, screen_manager))
    audio_recording_thread.start()

    # setup recording the screen and webcam
    webcam_recording_thread = Thread(target=record_webcam, args=(webcam_manager, ))
    screen_recording_thread = Thread(target=record_screen, args=(screen_manager, ))

    # connect with the client to share 4 streams
    speaker_soc, _ = s.accept()
    mic_soc, _ = s.accept()
    webcam_soc, _ = s.accept()
    screen_soc, client = s.accept()

    # connections established
    print(f"Connected with {client}.")

    # start recording streams
    # webcam_recording_thread.start()
    screen_recording_thread.start()

    # setup speaker stream & mic stream sharing threads
    speaker_sending_thread = Thread(target=share_audio,
                                        args=(speaker_soc, speaker_manager))
    mic_sending_thread = Thread(target=share_audio,
                                        args=(mic_soc, mic_manager))

    # setup screen and webcam feed sharing threads
    webcam_sending_thread = Thread(target=send_webcam_feed, args=(webcam_soc, webcam_manager))
    screen_sending_thread = Thread(target=send_screen, args=(screen_soc, screen_manager))

    # start local writing threads
    local_webcam_write_thread = Thread(target=local_webcam_writer, args=(webcam_manager,))
    local_screen_write_thread = Thread(target=local_screen_writer, args=(screen_manager,))
    # local_webcam_write_thread.start()
    local_screen_write_thread.start()

    # start sending all the streams
    speaker_sending_thread.start()
    mic_sending_thread.start()
    # webcam_sending_thread.start()
    screen_sending_thread.start()


if __name__ == '__main__':
    main()
