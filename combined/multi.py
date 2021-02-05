from copy import deepcopy
import subprocess
import sys
import threading
import time
import wave

import pyaudio


class manager:
    def __init__(self):
        self.frames = []
        self.keep_going = True

def recordData(m, m_to_store, CHUNK, stream):
    while m.keep_going:
        data = stream.read(CHUNK)
        m.frames.append(data)
        m_to_store.frames.append(data)

def save_wav(filename, channels, rate, sample_size, frames):
    # save the captured audio into a wav file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_size)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f'Saved {filename}.')

def main(m=manager(), m_to_store=manager(),
            m1=manager(), m1_to_store=manager()):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    MIC_OUTPUT_FILENAME = "server_mic.wav"
    SPEAKER_OUTPUT_FILENAME = "server_speaker.wav"

    p = pyaudio.PyAudio()

    loopback_speaker = None

    print("\n********Input Devices***********")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels']>0:
            print(dev['index'], dev['name'])
        if 'Stereo Mix' in dev['name']:
            loopback_speaker = int(dev['index'])
    print("********************************\n")
    mic = int(input("Mic Stream #"))

    # sys.exit()

    # open mic input stream
    stream_mic = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=mic,
                    frames_per_buffer=CHUNK)

    # open speaker loopback stream
    stream_loopback_speaker = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=loopback_speaker,
                        frames_per_buffer=CHUNK)

    # sys.exit()
    print('Recording...')

    t = threading.Thread(target=recordData, args=(m, m_to_store, CHUNK, stream_loopback_speaker, ))
    t1 = threading.Thread(target=recordData, args=(m1, m1_to_store, CHUNK, stream_mic, ))
    t1.start()
    t.start()

    # start capturing speaker output into 'frames'
    while True:
        if input()=='stop':
            #stop speaker loopback recording
            m.keep_going = False
            #stop mic recording
            m1.keep_going = False
            time.sleep(0.1)
            break

    # stop capturing, close the stream and terminate pyaudio
    stream_loopback_speaker.stop_stream()
    stream_loopback_speaker.close()
    stream_mic.stop_stream()
    stream_mic.close()
    p.terminate()
    print('Stopped recording.')
    save_wav(SPEAKER_OUTPUT_FILENAME, CHANNELS, RATE, p.get_sample_size(FORMAT), m_to_store.frames)
    save_wav(MIC_OUTPUT_FILENAME, CHANNELS, RATE, p.get_sample_size(FORMAT), m1_to_store.frames)

if __name__ == '__main__':
    main()
