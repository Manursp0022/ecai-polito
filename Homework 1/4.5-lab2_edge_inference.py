from subprocess import Popen
from time import sleep, time

import numpy as np
import torchaudio
from transformers import WhisperForConditionalGeneration, WhisperProcessor

# Fix the CPU frequency to its maximum value (1.5 GHz)
Popen(
    'sudo sh -c "echo performance >'
    '/sys/devices/system/cpu/cpufreq/policy0/scaling_governor"',
    shell=True,
).wait()

# Load model and processor
model_name = 'openai/whisper-medium.en'
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

# Load test WAV file
filename = 'lab2/examples-2/stop_0b40aa8e_nohash_0.wav'
x, sampling_rate = torchaudio.load(filename)
x = x.squeeze(0)

times = []

for i in range(20):
    start = time()
    input_features = processor(
        x, sampling_rate=16000, return_tensors="pt"
    ).input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(
        predicted_ids, skip_special_tokens=False
    )
    end = time()
    times.append(end - start)
    sleep(0.1)

median_time = np.median(times)
std_time = np.std(times)

print(f'Latency: {median_time:.2f}+/-{std_time:.2f}s')
