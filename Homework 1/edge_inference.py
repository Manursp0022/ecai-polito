from subprocess import Popen
from time import sleep, time
from tqdm.auto import trange
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
models = [  #'openai/whisper-tiny.en', 
            #'openai/whisper-base.en', 
            #'openai/whisper-small.en', 
            'openai/whisper-medium.en', 
            'openai/whisper-large.en', 
            'openai/whisper-largev2.en']
#model_name = 'openai/whisper-base.en'

# Load test WAV file
#filename = '../lab2/examples-2/stop_0b40aa8e_nohash_0.wav'
filename = 'lab2/examples-2/stop_0b40aa8e_nohash_0.wav'
x, sampling_rate = torchaudio.load(filename)
x = x.squeeze(0)
results = {}



for model_name in models:
    times = []
    processor = WhisperProcessor.from_pretrained(model_name)
    print("Initializing model:", model_name)
    model = WhisperForConditionalGeneration.from_pretrained(model_name)
    print("Model initialized. Starting inference...\n|", end=' ', flush=True)
    #for i in range(20):
    for i in trange(20, desc=f"Inference {model_name}", unit="it"):
        start = time()
        input_features = processor(
            x, sampling_rate=16000, return_tensors="pt"
        ).input_features
        predicted_ids = model.generate(input_features)
        transcription = processor.batch_decode(
            predicted_ids, skip_special_tokens=False
        )
        end = time()
        #print(f'*', end=' ', flush=True)
        times.append(end - start)
        sleep(0.1)
    #print(f'|')
    median_time = np.median(times)
    std_time = np.std(times)
    result = f'Done {model_name} : Latency: {median_time:.2f}+/-{std_time:.2f}s'
    print(result)
    results[model_name] = result

print('\n'.join([f'{k}: {v}' for k, v in results.items()]))
# save results to a text file
with open('lab2/edge_inference_results.txt', 'w') as f:
    f.write('\n'.join([f'{k}: {v}' for k, v in results.items()]))