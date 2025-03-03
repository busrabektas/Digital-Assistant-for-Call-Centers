import whisperx
import gc
import torch
import os
import json
import logging

HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

logging.getLogger("speechbrain.utils.quirks").setLevel(logging.ERROR)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

batch_size = 16 
compute_type = "float16" if device == "cuda" else "float32" 

asr_options = {
"multilingual":False,
"hotwords":None
}

dataset_path = "your_dataset_path" 
output_dir = "output_direction" 

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Loading ASR model...")
model = whisperx.load_model("large-v2", device, compute_type=compute_type, asr_options=asr_options)


for filename in os.listdir(dataset_path):
    if filename.endswith((".mp3", ".wav", ".ogg", ".flac")): 
        audio_file = os.path.join(dataset_path, filename)
        output_json_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".json") # 
        print(f"Processing {filename}...")
        print("Loading audio...")
        try:
            audio = whisperx.load_audio(audio_file)
        except Exception as e:
            print(f"Error loading audio file {filename}: {e}")
            continue 

        print("Transcribing...")
        try:
            result = model.transcribe(audio, batch_size=batch_size)
            print("Detected language:", result["language"]) 
           
        except Exception as e:
            print(f"Transcription error for {filename}: {e}")
            continue

        gc.collect()
        torch.cuda.empty_cache()

        print("Loading alignment model...")
        try:
            model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        except Exception as e:
            print(f"Alignment model yükleme hatası for {filename}: {e}")
            continue


        # Alignment
        print("Aligning transcription...")
        try:
            result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

        except Exception as e:
            print(f"Alignment hatası for {filename}: {e}")
            continue


        gc.collect()
        torch.cuda.empty_cache()

        print("Loading diarization model...")
        try:
            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=HF_TOKEN, device=device
            )
        except Exception as e:
            print(f"Diarization model yükleme hatası for {filename}: {e}")
            continue


        print("Performing diarization...")
        try:
            diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2) # 
            result = whisperx.assign_word_speakers(diarize_segments, result)
        except Exception as e:
            print(f"Diarization hatası for {filename}: {e}")
            continue

        print(f"Saving results to {output_json_path}")
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4) 
            print(f"Processed {filename} and saved results to {output_json_path}")
        except Exception as e:
            print(f"Sonuçları kaydetme hatası for {filename}: {e}")

        gc.collect()
        torch.cuda.empty_cache()

print("All files processed.")