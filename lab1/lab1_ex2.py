import sounddevice as sd 
from time import time
from scipy.io.wavfile import write
import os
#Samplerate: how much sample we collect each second

"""
Modify the script to store the audio data every second. Use the stream callback function to store
data in parallel while recording. Use the scipy.io.wavfile.write function to store the audio data.
Use the timestamp of the recording as the filename
"""
#indata will be populated by soundevice with the recorded data
def callback(indata,frames,callback_time,status):
    timestamp = time()
    write(f'{timestamp}.wav',48000,indata)
    filesize_in_bytes = os.path.getsize(f'{timestamp}.wav')
    filesize_in_Kbytes = filesize_in_bytes / 1024
    print(f'Size:{filesize_in_Kbytes:.2f}KB')

with sd InputStream(device=1,channels=1,dtype='int32',samplerate=48000,
callback=callback,blockSize=48000):  #samplerate = 48000 because we want to execute each second
    while True: 
        key = input()
        if key in ('q','Q'):
            print('Stop recording.')
        #in this version we don't store the audio data
