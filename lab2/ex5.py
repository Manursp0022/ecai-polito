from subprocess import Popen
from time import sleep, time
import base64
import numpy as np
import requests
import torchaudio
import string
import torch
from transformers import WhisperProcessor

# Fix the CPU frequency to its maximum value (1.5 GHz)
Popen(
    'sudo sh -c "echo performance >'
    '/sys/devices/system/cpu/cpufreq/policy0/scaling_governor"',
    shell=True,
).wait()

API_URL = (
    'https://fb23886e-32ac-4d94-9ced-d9b579c3274d.deepnoteproject.com/predict'
)

filename = 'examples-2/stop_0b40aa8e_nohash_0.wav'
x, sampling_rate = torchaudio.load(filename)

times = []

model_name = 'openai/whisper-tiny.en'
processor = WhisperProcessor.from_pretrained(model_name)

for i in range(20):
    start = time()
    try:
        input_features = processor(
            x.numpy(),
            sampling_rate = sampling_rate,
            return_tensors='pt',
        ).input_features

        print(input_features)
        encoded = base64.b64encode(input_features.flatten().numpy().tobytes()).decode('utf-8')
        response = requests.post(
            API_URL, json={'input': encoded, 'sampling_rate': sampling_rate}
        )
        prediction = response.json()['output']
        print(f'Prediction: {prediction}')
        end = time()
        times.append(end - start)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    sleep(2)

median_time = np.median(times)
std_time = np.std(times)

print(f'Latency: {median_time:.2f}+/-{std_time:.2f}s')
