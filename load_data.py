import os
import json
import mysql.connector
from mysql.connector import Error

# MySQL bağlantı ayarları (DB_CONFIG)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "database_name",
}

def load_json_data(json_file_path: str) -> dict:
    """Belirtilen JSON dosyasını okuyup veri döndürür."""
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def insert_conversation(data: dict) -> None:
    """
    Verilen JSON verisini MySQL veritabanına yükler.
    Önce conversations tablosuna, ardından ilgili turnları turns tablosuna ekler.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        conversation_id = data["conversation_id"]
        
        # Konuşmayı conversations tablosuna ekleyin (varsa güncelleme yapmadan)
        insert_conversation_query = """
            INSERT INTO conversations (conversation_id)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE conversation_id = conversation_id
        """
        cursor.execute(insert_conversation_query, (conversation_id,))

        # Her bir turn'ı turns tablosuna ekleyin
        insert_turn_query = """
            INSERT INTO turns (conversation_id, speaker, text, start, end)
            VALUES (%s, %s, %s, %s, %s)
        """
        for turn in data.get("turns", []):
            speaker = turn.get("speaker")
            text = turn.get("text")
            start = turn.get("start")
            end = turn.get("end")
            cursor.execute(insert_turn_query, (conversation_id, speaker, text, start, end))
        
        connection.commit()
        print(f"Conversation {conversation_id} successfully inserted.")
    except Error as e:
        print(f"Error inserting conversation {conversation_id}: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    # JSON dosyalarının bulunduğu klasörü belirtin (örneğin "conversations")
    json_folder = "conversations"
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            json_file_path = os.path.join(json_folder, filename)
            data = load_json_data(json_file_path)
            insert_conversation(data)

if __name__ == "__main__":
    main()
