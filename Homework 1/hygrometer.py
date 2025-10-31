import argparse
import redis
import time
from datetime import datetime
import adafruit_dht
import uuid
from board import D4
import numpy as np
import torchaudio
from transformers import WhisperForConditionalGeneration, WhisperProcessor
import sounddevice as sd
import torch


# 1. Parsing degli argomenti per Redis
parser = argparse.ArgumentParser(description='Smart Hygrometer with VUI & Redis')
parser.add_argument('--host', type=str, required=True, help='Redis Cloud host')
parser.add_argument('--port', type=int, required=True, help='Redis Cloud port')
parser.add_argument('--user', type=str, required=True, help='Redis Cloud username')
parser.add_argument('--password', type=str, required=True, help='Redis Cloud password')
args = parser.parse_args()
REDIS_HOST = args.host
REDIS_PORT = args.port
REDIS_USERNAME = args.user
REDIS_PASSWORD = args.password

REDIS_HOST = 'redis-14100.c293.eu-central-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = 14100
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'fMVnUawdIIZcSAHcDpJKaZykdIAynJFN'


# 2. Inizializza DHT-11
mac_address = hex(uuid.getnode())
dht_device = adafruit_dht.DHT11(D4)

# 3. Connessione a Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)
try:
    redis_client.ts().create('temp_timeseries')
    redis_client.ts().create('hum_timeseries')
except redis.ResponseError:
    pass

print('Redis Connected:', redis_client.ping())

# 4. Caricamento modello Whisper
model_name = 'openai/whisper-tiny.en'
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# 5. Parametri audio
AUDIO_DEVICE = 1              # USB microphone
CHANNELS = 1
BIT_DEPTH = 'int16'
SAMPLING_RATE = 48000         # 48kHz
WINDOW_SEC = 1                # analizza finestre da 1 secondo

# 6. Stato sistema (disabilitato di default)
data_collection_enabled = False
audio_buffer = np.zeros(SAMPLING_RATE * WINDOW_SEC, dtype=np.int16)

def audio_callback(indata, frames, callback_time, status):
    global audio_buffer
    # Aggiornamento buffer per trascrizione
    audio_buffer = indata.copy().flatten()

def recognize_command(buffer):
    # Conversione, normalizzazione, downsampling
    waveform = buffer.astype(np.float32) / 32768.0  # [-1,1]
    waveform = waveform[np.newaxis, :]
    waveform16k = torchaudio.functional.resample(torch.tensor(waveform), SAMPLING_RATE, 16000).squeeze()
    input_features = processor(waveform16k, sampling_rate=16000, return_tensors="pt").input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    # Pulizia
    cmd = "".join(c for c in transcription if c.isalnum())
    return cmd.lower()

def collect_and_send_data():
    global data_collection_enabled, mac_address, dht_device
    if data_collection_enabled:
        timestamp = time.time()
        formatted_datetime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            print(f'{formatted_datetime} - {mac_address}:temperature = {temperature}')
            print(f'{formatted_datetime} - {mac_address}:humidity = {humidity}')
            timestamp_ms = int(timestamp * 1000)
            redis_client.ts().add('temp_timeseries', timestamp_ms, temperature)
            redis_client.ts().add('hum_timeseries', timestamp_ms, humidity)
        except:
            print(f'{formatted_datetime} - sensor failure')
            dht_device.exit()
            dht_device = adafruit_dht.DHT11(D4)

def main():
    global data_collection_enabled
    print("Sistema Smart Hygrometer avviato. Pronuncia 'up' per abilitare, 'stop' per disabilitare.")
    last_data_time = 0
    with sd.InputStream(device=AUDIO_DEVICE, channels=CHANNELS, dtype=BIT_DEPTH, samplerate=SAMPLING_RATE,
                        blocksize=SAMPLING_RATE * WINDOW_SEC, callback=audio_callback):
        while True:
            # 1. Ascolta audio ogni secondo
            time.sleep(WINDOW_SEC)
            print("[VOICE] Begin audio recording...")            
            cmd = recognize_command(audio_buffer)
            if 'up' in cmd:
                data_collection_enabled = True
                print('[VOICE] Data collection ENABLED')
            elif 'stop' in cmd:
                data_collection_enabled = False
                print('[VOICE] Data collection DISABLED')
            else:
                print(f'[VOICE] Command not recognized: "{cmd}"')
            # 2. Se abilitato, raccogli dati ogni 5 secondi
            cur_time = time.time()
            if data_collection_enabled and cur_time - last_data_time >= 5:
                collect_and_send_data()
                last_data_time = cur_time

if __name__ == "__main__":
    main()
