import os
import sounddevice as sd
from time import time
from scipy.io.wavfile import write
import argparse

parser = argparse.ArgumentParser(description='Record audio with configurable parameters')

parser.add_argument('--bit-depth', type=str, choices=['int16', 'int32'], 
                    required=True, help='Bit depth: int16 or int32')

parser.add_argument('--sampling-rate', type=int, required=True, 
                    help='Sampling rate in Hz (e.g., 44100 or 48000)')

parser.add_argument('--duration', type=int, required=True, 
                    help='Recording duration in seconds')

args = parser.parse_args()

bit_depth = args.bit_depth          
sampling_rate = args.sampling_rate  
duration = args.duration

blocksize = sampling_rate * duration

print(f"=== Recording Configuration ===")
print(f"Bit Depth: {bit_depth}")
print(f"Sampling Rate: {sampling_rate} Hz")
print(f"Duration: {duration} second(s)")
print(f"Blocksize: {blocksize} samples")
print("===============================\n")


def callback(indata, frames, callback_time, status):
    """This is called (from a separate thread) for each audio block."""
    global store_audio

    if store_audio is True:
        timestamp = time()
        write(f'{timestamp}.wav', 48000, indata)
        filesize_in_bytes = os.path.getsize(f'{timestamp}.wav')
        filesize_in_kb = filesize_in_bytes / 1024
        print(f'Size: {filesize_in_kb:.2f}KB')
    
    # Se store_audio è True, salva il file audio
    if store_audio is True:
        # Ottiene il timestamp corrente (numero float di secondi da epoch)
        timestamp = time()
        filename = f'{timestamp}.wav'
        write(filename, sampling_rate, indata)
        #dimensione file in bytes
        filesize_in_bytes = os.path.getsize(filename)
        #bytes a kilobytes
        filesize_in_kb = filesize_in_bytes / 1024
        print(f'Saved: {filename} - Size: {filesize_in_kb:.2f} KB')

# Flag per abilitare/disabilitare il salvataggio audio

store_audio = True

with sd.InputStream(device=1, channels=1, dtype='int32', samplerate=48000, blocksize=48000, callback=callback):
    while True:
        key = input()
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
        if key in ('p', 'P'):
            store_audio = not store_audio
        

with sd.InputStream(
    device=1,              # Dispositivo audio (1 = USB microphone)
    channels=1,            # Mono (1 canale)
    dtype=bit_depth,       # Tipo di dato: 'int16' o 'int32' (da argparse)
    samplerate=sampling_rate,  # Frequenza di campionamento (da argparse)
    blocksize=blocksize,   # Numero di sample per blocco (da argparse)
    callback=callback      # Funzione da chiamare per ogni blocco
):
    print("Recording started. Press 'P' to toggle storage, 'Q' to quit.\n")
    
    while True:
        # Aspetta l'input dell'utente (blocca fino a quando non premi Enter)
        key = input()
        
        #esce dal loop e termina
        if key in ('q', 'Q'):
            print('Stop recording.')
            break
        
        # Se premi P o p, inverte lo stato di store_audio
        if key in ('p', 'P'):
            store_audio = not store_audio
            status = "ENABLED" if store_audio else "DISABLED"
            print(f'Audio storage {status}')