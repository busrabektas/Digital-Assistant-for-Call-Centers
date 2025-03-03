import json
import os
import uuid  

def load_diarization_results(file_path):
    """JSON dosyasını yükler."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def process_diarization_data(data):
    """Diarization JSON çıktısını düzenler ve turn formatına çevirir."""
    turns = []
    for segment in data["segments"]:
        turn = {
            "speaker": segment["speaker"],
            "text": segment["text"].strip(),
            "start": segment["start"],
            "end": segment["end"]
        }
        turns.append(turn)
    return turns

def save_processed_data(turns, output_folder):
    """İşlenmiş veriyi belirtilen dosyaya JSON olarak benzersiz conversation_id ile kaydeder."""
    conversation_id = str(uuid.uuid4())  # Benzersiz ID üretimi
    output_path = os.path.join(output_folder, f"{conversation_id}.json")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump({"conversation_id": conversation_id, "turns": turns}, file, indent=4, ensure_ascii=False)
    return output_path  

def process_all_files(input_folder, output_folder):
    """Bir klasördeki tüm JSON dosyalarını işleyerek başka bir klasöre kaydeder."""
    files = [f for f in os.listdir(input_folder) if f.endswith(".json")]
    
    for file_name in files:
        input_path = os.path.join(input_folder, file_name)
        
        print(f"Processing {file_name}...")
        
        data = load_diarization_results(input_path)
        
       
        turns = process_diarization_data(data)
        
        output_path = save_processed_data(turns, output_folder)
        print(f"Processed data saved to {output_path}")


input_folder = "dataset/diarization_results"
output_folder = "conversations"
os.makedirs(output_folder, exist_ok=True)  
process_all_files(input_folder, output_folder)
