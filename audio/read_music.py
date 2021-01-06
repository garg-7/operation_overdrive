import pyaudio
import wave
import subprocess
import threading
import time
from copy import deepcopy
class manager:
    def __init__(self):
        self.frames = []
        self.keep_going = True

def recordData(m, CHUNK, stream):
    while m.keep_going:
        data = stream.read(CHUNK)
        m.frames.append(data)


def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    # for i in range(p.get_device_count()):
    #     print(p.get_device_info_by_index(i))

    # open pyaudio input stream to start recording
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print('Recording...')

    m = manager()
    # frames = []
    t = threading.Thread(target=recordData, args=(m, CHUNK, stream, ))
    # keep_going = True

    # start capturing speaker output into 'frames'
    t.start()
    while True:
        if input()=='stop':
            m.keep_going = False
            time.sleep(0.1)
            break

    # stop capturing, close the stream and terminate pyaudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    print('Stopped recording.')

    # save the captured audio into a wav file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(m.frames))
    wf.close()
    print('Saved wav recording.')

def set_speaker_loopback(speaker):
    # set default input device to loopbacked speaker
    set_input_device_cmd = 'pactl set-default-source ' + speaker
    process = subprocess.Popen(set_input_device_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    assert error==None
    # print(output, error)

def reset_default_mic():
    # revert input device default to microphone
    revert_input_device_cmd = 'pactl set-default-source alsa_input.pci-0000_00_1f.3.analog-stereo'
    process = subprocess.Popen(revert_input_device_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    assert error==None
    # print(output, error)

def get_speaker():
    listing_cmd = 'pactl list sources'
    process = subprocess.Popen(listing_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    assert error==None
    output = output.decode()
    # print(output.decode())
    lines = output.split('\n')
    devices = {}
    temp = []
    for line in lines:
        # print(line)
        if line.startswith('Source'):
            if len(temp)!=0:
                devices[temp[0].strip()] = temp[1:]
            temp = []
        temp.append(line.strip())
    devices[temp[0].strip()] = temp[1:]
    final = {}
    for k in devices.keys():
        for attr in devices[k]:
            if attr.startswith('Description: '):
                if 'Monitor of' in attr:
                    final[k] = deepcopy(devices[k])
    
    required = {}
    for k in final.keys():
        # print(k)
        required[k] = []
        for attr in devices[k]:
            if attr.startswith('Description'):
                required[k].append(attr.split(':')[1].strip())
            elif attr.startswith('Name'):
                required[k].append(attr.split(':')[1].strip())
    
    for k in required.keys():
        print(k)
        print('\tDescription:', required[k][1])
        print('\tName:', required[k][0])

    while True:
        speaker_stream = input('Enter the stream number #:')
        for k in required.keys():
            if speaker_stream.strip() == k[8:]:
                return required[k][0]
        print('Incorrect stream number !')

if __name__ == '__main__':
    speaker = get_speaker()
    set_speaker_loopback(speaker)
    main()
    reset_default_mic()