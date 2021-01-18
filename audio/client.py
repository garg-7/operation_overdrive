import multi
import pickle
import socket
from threading import Thread
import time

import pyaudio


class frame_keeper:
    def __init__(self):
        self.frames = []

def play_audio(f, stream):
    last_time = time.time()
    while time.time() - last_time < 5:
        try:
            data_to_be_played = f.frames[0]
            stream.write(data_to_be_played)
            f.frames.pop(0)
            last_time = time.time()
        except IndexError:
            pass

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "gotten/output.wav"
    shost = input("Enter server IP")
    sport = 11112
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((shost, sport))
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
    print(type(speaker_id))
    stream = p.open(format=format,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    output_device_index=speaker_id)
    t = Thread(target=play_audio, args=(f, stream,))
    t1 = Thread(target=play_audio, args=(f1, stream,))
    t.start()
    t1.start()
    while True:
        recv_data = s.recv(3000)
        recv_data = pickle.loads(recv_data)
        speaker_data = recv_data['speaker']
        mic_data = recv_data['mic']
        f.frames.append(speaker_data)
        f1.frames.append(mic_data)
        if len(recv_data)==0:
            break
    print('Finished receiving audio stream.')
    # print('Saving recording as wav file.')
    # multi.save_wav(WAVE_OUTPUT_FILENAME, CHANNELS, RATE, 2, f.frames)

if __name__ == '__main__':
    main()