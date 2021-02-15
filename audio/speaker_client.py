import multi
import pickle
import socket
from threading import Thread
import time

import pyaudio


class frame_keeper:
    def __init__(self):
        self.frames = []
        self.frames_save = []

def play_audio(f, speaker_stream):
    last_time = time.time()
    while time.time() - last_time < 5:
        try:
            data_to_be_played = f.frames[0]
            speaker_stream.write(data_to_be_played)
            f.frames.pop(0)
            last_time = time.time()
        except IndexError:
            pass

def receiving_data(s, f):
    while True:
        recv_data = s.recv(4129)
        f.frames.append(recv_data)
        f.frames_save.append(recv_data)
        if len(recv_data)==0:
            break

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "gotten/output.wav"
    shost = input("Enter server IP")
    sport = 11112
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    f = frame_keeper()
    p = pyaudio.PyAudio()
    sinks = []
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device['maxOutputChannels'] > 0 and ('HDMI' not in device['name']):
            sinks.append(device)
    for i in sinks:
        print(i['index'], i['name'])
    speaker_id = int(input('Enter index of speaker to use: #'))
    print(type(speaker_id))
    speaker_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    output_device_index=speaker_id)

    t = Thread(target=play_audio, args=(f, speaker_stream))
    t.start()
    s.connect((shost, sport))
    speaker_data_thread = Thread(target=receiving_data, args=(s, f))
    speaker_data_thread.start()
    speaker_data_thread.join()
    print('Finished receiving audio stream.')
    # print('Saving recording as wav file.')
    multi.save_wav('speaker.wav', CHANNELS, RATE, 2, f.frames_save)

if __name__ == '__main__':
    main()
