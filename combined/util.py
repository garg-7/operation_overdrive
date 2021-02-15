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
        self.kept_frames = []
        self.keep_going = True
        self.play_along = False


def recordData(m, stream, CHUNK=1024):
    while m.keep_going:
        data = stream.read(CHUNK)
        m.frames.append(data)
        m.kept_frames.append(data)


def save_wav(filename, channels, rate, sample_size, frames):
    # save the captured audio into a wav file
    print("Length of frames array:", len(frames))
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sample_size)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f'Saved {filename}.')


def main(speaker_manager=manager(), mic_manager=manager(), webcam_manager=manager(), screen_manager=manager()):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    OUT_RATE = 32000
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
    mic = int(input("Mic Index #"))

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

    speaker_recording_thread = threading.Thread(target=recordData, args=(speaker_manager, stream_loopback_speaker, ))
    mic_recording_thread = threading.Thread(target=recordData, args=(mic_manager, stream_mic, ))

    mic_recording_thread.start()
    speaker_recording_thread.start()

    # start capturing speaker output into 'frames'
    while True:
        if input()=='stop':
            #stop recording from all streams
            speaker_manager.keep_going = False
            mic_manager.keep_going = False
            screen_manager.keep_going = False
            webcam_manager.keep_going = False
            # add a little delay to prevent dependent threads from crashing
            time.sleep(0.1)
            break

    # stop capturing, close the stream and terminate pyaudio
    stream_loopback_speaker.stop_stream()
    stream_loopback_speaker.close()
    stream_mic.stop_stream()
    stream_mic.close()
    p.terminate()
    print('Stopped recording.')
    save_wav(SPEAKER_OUTPUT_FILENAME, CHANNELS, RATE, p.get_sample_size(FORMAT), speaker_manager.kept_frames)
    save_wav(MIC_OUTPUT_FILENAME, CHANNELS, RATE, p.get_sample_size(FORMAT), mic_manager.kept_frames)


if __name__ == '__main__':
    main()
