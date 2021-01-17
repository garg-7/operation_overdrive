import socket
import pyaudio
import multi
from threading import Thread
import time

class frame_keeper:
    def __init__(self):
        self.frames = []

def play_audio(f, channels, format, rate):
    p = pyaudio.PyAudio()

    sinks = []
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if device['maxOutputChannels'] > 0 and ('HDMI' not in device['name']):
            sinks.append(device)
    for i in sinks:
        print(i['index'], i['name'])
    speaker_id = int(input('Enter index of speaker to use: #'))
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    output=True,
                    output_device_index=speaker_id)
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
    shost = '127.0.0.1'
    sport = 11112
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((shost, sport))
    f = frame_keeper()
    t = Thread(target=play_audio, args=(f, CHANNELS, FORMAT, RATE,))
    t.start()
    while True:
        recv_data = s.recv(1024)
        f.frames.append(recv_data)
        if len(recv_data)==0:
            break
    print('Finished receiving audio stream.')
    # print('Saving recording as wav file.')
    # multi.save_wav(WAVE_OUTPUT_FILENAME, CHANNELS, RATE, 2, f.frames)

if __name__ == '__main__':
    main()