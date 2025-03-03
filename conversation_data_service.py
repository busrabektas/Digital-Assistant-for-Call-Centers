# conversation_data_service.py

import mysql.connector
from mysql.connector import Error
from typing import Dict, List
import os

class ConversationDataService:
    """
    MySQL veritabanından konuşma verilerini yükleyen servis.
    """

    # Bağlantı parametrelerini buraya girin
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "your_password",
        "database":"database_name",
    }

    @staticmethod
    def _get_connection():
        try:
            connection = mysql.connector.connect(**ConversationDataService.DB_CONFIG)
            return connection
        except Error as e:
            raise Exception(f"MySQL bağlantısı kurulamadı: {e}")

    @staticmethod
    def load_conversation(conversation_id: str) -> Dict:
        """
        MySQL veritabanından konuşma verilerini yükler.
        Eğer conversation_id "all" ise, bu metod doğrudan tüm verileri döndürmez.
        "all" durumunda ayrı olarak get_all_conversation_ids() kullanılmalıdır.

        Args:
            conversation_id (str): Yüklenecek konuşmanın benzersiz ID'si.

        Returns:
            Dict: Konuşma verileri, örneğin:
                {
                    "conversation_id": "<conversation_id>",
                    "turns": [
                        {"speaker": "SPEAKER_00", "text": "...", "start": 0.5, "end": 5.0},
                        ...
                    ]
                }
        """
        connection = ConversationDataService._get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            query = (
                "SELECT speaker, text, start, end FROM turns "
                "WHERE conversation_id = %s ORDER BY start"
            )
            cursor.execute(query, (conversation_id,))
            rows = cursor.fetchall()
            if not rows:
                raise ValueError(f"Veritabanında '{conversation_id}' ID'li konuşma bulunamadı.")
            turns = []
            for row in rows:
                turns.append({
                    "speaker": row["speaker"],
                    "text": row["text"],
                    "start": row["start"],
                    "end": row["end"]
                })
            return {"conversation_id": conversation_id, "turns": turns}
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all_conversation_ids() -> List[str]:
        """
        Veritabanındaki tüm konuşma ID'lerini döndürür.
        
        Returns:
            List[str]: Tüm conversation_id'lerin listesi.
        """
        connection = ConversationDataService._get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            query = "SELECT DISTINCT conversation_id FROM conversations"
            cursor.execute(query)
            rows = cursor.fetchall()
            ids = [row["conversation_id"] for row in rows]
            return ids
        finally:
            cursor.close()
            connection.close()
