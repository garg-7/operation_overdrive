import pyaudio
import wave
import subprocess
import threading
import time

def recordData():
    while keep_going:
        data = stream.read(CHUNK)
        frames.append(data)

# set default input device to loopbacked speaker
set_input_device_cmd = 'pactl set-default-source alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'
process = subprocess.Popen(set_input_device_cmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
# print(output, error)


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

frames = []
t = threading.Thread(target=recordData)
keep_going = True

# start capturing speaker output into 'frames'
t.start()
while True:
    if input()=='stop':
        keep_going = False
        time.sleep(0.1)
        break

# stop capturing, close the stream and terminate pyaudio
stream.stop_stream()
stream.close()
p.terminate()

# save the captured audio into a wav file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# revert input device default to microphone
revert_input_device_cmd = 'pactl set-default-source alsa_input.pci-0000_00_1f.3.analog-stereo'
process = subprocess.Popen(revert_input_device_cmd.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
# print(output, error)