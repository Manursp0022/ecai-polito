import base64
from subprocess import Popen
from time import sleep, time

import numpy as np
import requests
import torchaudio

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

encoded = base64.b64encode(x.numpy().tobytes()).decode('utf-8')

times = []

for i in range(20):
    start = time()
    try:
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