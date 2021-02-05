import multi
import pickle
import socket
from threading import Thread
import time
import sys
import pyaudio
import pickle
import socket
import struct
import pygame
import zlib
import numpy as np
import cv2
import os
class frame_keeper:
    def __init__(self):
        self.frames = []
        self.frames_save = []
        self.keep_getting = True

def play_audio(f, f1, speaker_stream, mic_stream):
    last_time = time.time()
    while time.time() - last_time < 5:
        try:
            data_to_be_played = f.frames[0]
            # speaker_stream.write(data_to_be_played)
            data_to_be_played = f1.frames[0]
            if max(data_to_be_played)>100:
                # mic_stream.write(data_to_be_played)
                pass
            f.frames.pop(0)
            f1.frames.pop(0)
            last_time = time.time()
        except IndexError:
            pass

def receiving_data(s, f):
    while True:
        recv_data = s.recv(4129)
        f.frames.append(recv_data)
        f.frames_save.append(recv_data)
        if len(recv_data)==0:
            f.keep_getting = False
            break

def receiving_vid_stream(conn, result, f):
    data = b''  # CHANGED
    payload_size = struct.calcsize("L")  # CHANGED
    while f.keep_getting:
        # Retrieve message size
        while len(data) < payload_size:
            recv_data = conn.recv(4096)
            data += recv_data

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

        # if len(frame)==0:
        #     print('i was here')
        #     cv2.destroyAllWindows()
        #     cv2.waitKey(1)
        #     sys.exit()

        result.write(frame)

        # Display
        cv2.imshow('frame', frame)
        cv2.waitKey(1)


def getAll(conn, length):
    buffer = b''
    while len(buffer) < length:
        data = conn.recv(length - len(buffer))
        if not data:
            return data
        buffer += data
    return buffer

def receiving_screen_stream(server, f):
    WIDTH=1920
    HEIGHT=1080
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("server screen")
    fake_screen = screen.copy()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("client_screen.avi", fourcc, 20.0, (1920, 1080))

    while f.keep_getting:
        size_len = int.from_bytes(server.recv(1), byteorder='big')

        size = int.from_bytes(server.recv(size_len), byteorder='big')

        pixels = zlib.decompress(getAll(server, size))

        img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

        pygame.image.save_extended(img, "loser.png")

        variable = cv2.imread('loser.png')
        
        # cv2.imshow('loser', variable)

        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(variable)

        # write the frame
        out.write(frame)

        fake_screen.blit(img, (0, 0))

        screen.blit(pygame.transform.scale(
            fake_screen, (WIDTH, HEIGHT)), (0, 0))

        pygame.display.flip()

        clock.tick(60)
    os.remove('loser.png')

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "gotten/output.wav"
    shost = input("Enter server IP")
    sport = 11111
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sshare_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    f = frame_keeper()
    f1 = frame_keeper()
    p = pyaudio.PyAudio()
    
    sinks = []
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device['maxOutputChannels'] > 0 and ('HDMI' not in device['name']):
            sinks.append(device)
    for i in sinks:
        print(i['index'], i['name'])
    speaker_id = int(input('Enter index of speaker to use: #'))
    # print(type(speaker_id))
    speaker_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    output_device_index=speaker_id)

    mic_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    output_device_index=speaker_id)

    webcam_result = cv2.VideoWriter('client_webcam.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         30, (640, 480))

   

    t = Thread(target=play_audio, args=(f, f1, speaker_stream, mic_stream))
    t.start()
    s.connect((shost, sport))
    speaker_data_thread = Thread(target=receiving_data, args=(s, f))
    speaker_data_thread.start()

    s1.connect((shost, sport))
    mic_data_thread = Thread(target=receiving_data, args=(s1, f1))
    mic_data_thread.start()

    s_vid.connect((shost, sport))
    # video_stream_thread = Thread(target=receiving_vid_stream, args=(s_vid, webcam_result, f))
    # video_stream_thread.start()

    sshare_vid.connect((shost, sport))
    sshare_stream_thread = Thread(target=receiving_screen_stream, args=(sshare_vid, f))
    sshare_stream_thread.start()
    
    speaker_data_thread.join()
    mic_data_thread.join()
    
    print('Finished receiving audio stream.')
    # print('Saving recording as wav file.')
    multi.save_wav('client_speaker.wav', CHANNELS, RATE, 2, f.frames_save)
    multi.save_wav('client_mic.wav', CHANNELS, RATE, 2, f1.frames_save)
    # video_stream_thread.join()
if __name__ == '__main__':
    main()
