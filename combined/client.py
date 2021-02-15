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
import pyaudio
import pygame

import util

def play_audio(speaker_manager, mic_manager, speaker_stream, mic_stream):
    last_time = time.time()
    while time.time() - last_time < 5:
        try:
            data_to_be_played = speaker_manager.frames[0]
            # speaker_stream.write(data_to_be_played)
            data_to_be_played = mic_manager.frames[0]
            try:
                if max(data_to_be_played)>100:
                    # mic_stream.write(data_to_be_played)
                    pass
            except ValueError:
                pass
            speaker_manager.frames.pop(0)
            mic_manager.frames.pop(0)
            last_time = time.time()
        except IndexError:
            pass

def receiving_audio(speaker_soc, speaker_manager):
    while True:
        recv_data = speaker_soc.recv(4129)
        speaker_manager.frames.append(recv_data)
        speaker_manager.kept_frames.append(recv_data)
        if len(recv_data)==0:
            speaker_manager.keep_going = False
            break

def receiving_webcam_stream(conn, result, speaker_manager):
    data = b''  # CHANGED
    payload_size = struct.calcsize("L")  # CHANGED
    while speaker_manager.keep_going:
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

        # if len(frame)==0:
        #     print('i was here')
        #     cv2.destroyAllWindows()
        #     cv2.waitKey(1)
        #     sys.exit()

        result.write(frame)

        # Display
        cv2.imshow('frame', frame)
        cv2.waitKey(500)
    cv2.destroyAllWindows()

def getAll(conn, length):
    buffer = b''
    while len(buffer) < length:
        data = conn.recv(length - len(buffer))
        if not data:
            return data
        buffer += data
    return buffer

def receiving_screen_stream(server, speaker_manager):
    WIDTH=1920
    HEIGHT=1080
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("server screen")
    fake_screen = screen.copy()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # create the video write object
    out = cv2.VideoWriter("client_screen.avi", fourcc, 8, (1920, 1080))

    while speaker_manager.keep_going:
        size_len = int.from_bytes(server.recv(1), byteorder='big')

        size = int.from_bytes(server.recv(size_len), byteorder='big')

        pixels = zlib.decompress(getAll(server, size))

        img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

        pygame.image.save_extended(img, "temp.png")

        variable = cv2.imread('temp.png')

        # cv2.imshow('temp', variable)

        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(variable)

        # write the frame
        out.write(frame)

        fake_screen.blit(img, (0, 0))

        screen.blit(pygame.transform.scale(
            fake_screen, (WIDTH, HEIGHT)), (0, 0))

        pygame.display.flip()

        clock.tick(60)
    os.remove('temp.png')


def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "gotten/output.wav"
    shost = input("Enter server IP")
    sport = 11111

    speaker_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mic_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    webcam_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screen_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    speaker_manager = util.manager()
    mic_manager = util.manager()

    p = pyaudio.PyAudio()

    sinks = []
    print("\n********Output Devices***********")
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device['maxOutputChannels'] > 0 and ('HDMI' not in device['name']):
            sinks.append(device)
    for i in sinks:
        print(i['index'], i['name'])
    print("********************************\n")
    speaker_id = int(input("Speaker Index: #"))
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
                         1.5, (640, 480))

    audio_playback_thread = Thread(target=play_audio, args=(speaker_manager, mic_manager, speaker_stream, mic_stream))
    audio_playback_thread.start()

    speaker_soc.connect((shost, sport))
    mic_soc.connect((shost, sport))
    webcam_soc.connect((shost, sport))
    screen_soc.connect((shost, sport))

    speaker_receiving_thread = Thread(target=receiving_audio, args=(speaker_soc, speaker_manager))
    mic_receiving_thread = Thread(target=receiving_audio, args=(mic_soc, mic_manager))
    webcam_receiving_thread = Thread(target=receiving_webcam_stream, args=(webcam_soc, webcam_result, speaker_manager))
    screen_receiving_thread = Thread(target=receiving_screen_stream, args=(screen_soc, speaker_manager))

    # wait for 4 seconds then start receiving
    # time.sleep(5)
    speaker_receiving_thread.start()
    mic_receiving_thread.start()
    # webcam_receiving_thread.start()
    screen_receiving_thread.start()

    speaker_receiving_thread.join()
    mic_receiving_thread.join()
    # webcam_receiving_thread.join()
    screen_receiving_thread.join()
    print("Finished receiving audio stream.")
    util.save_wav('client_speaker.wav', CHANNELS, RATE, 2, speaker_manager.kept_frames)
    util.save_wav('client_mic.wav', CHANNELS, RATE, 2, mic_manager.kept_frames)

    # file_name = input("Enter filename: ")
    os.system(f'ffmpeg -i client_screen.avi -i client_mic.wav -i client_speaker.wav -filter_complex "[1][2]amix=inputs=2[a]" -map 0:v -map "[a]" -c:v copy screen_comb.mp4')
    os.system(f'ffmpeg -i client_webcam.avi -i client_mic.wav -i client_speaker.wav -filter_complex "[1][2]amix=inputs=2[a]" -map 0:v -map "[a]" -c:v copy webcam_comb.mp4')
    # os.remove('client_speaker.wav')
    # os.remove('client_mic.wav')
    # os.remove('client_webcam.avi')
if __name__ == '__main__':
    main()
