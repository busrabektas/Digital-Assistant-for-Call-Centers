from langchain_core.tools import tool
from transformers import pipeline
from pydantic import BaseModel
from typing import List
from conversation_data_service import ConversationDataService

class SentimentAnalysisInput(BaseModel):
    conversation_id: str

class SentimentAnalysisOutput(BaseModel):
    speaker: str
    text: str
    start: float
    end: float
    sentiment: str
    score: float

@tool("analyze_sentiment")
def sentiment_analysis_tool(conversation_id: str) -> List[dict]:
    """
    Belirtilen konuşmanın duygu analizini gerçekleştirir.
    
    Bu fonksiyon, ConversationDataService aracılığıyla MySQL veritabanından çekilen konuşma verilerini kullanarak,
    her bir turn için duygu analizi yapar. Her bir turn için duygu etiketi, skor, başlangıç ve bitiş zamanı ile konuşmacı bilgisi
    döndürür.
    
    Args:
        conversation_id (str): Duygu analizi yapılacak konuşmanın benzersiz ID'si.
    
    Returns:
        List[dict]: Konuşmadaki her bir turn için duygu analizi sonuçlarını içeren liste.
            Her sözlük aşağıdaki anahtarları içerir:
                - text: Turn metni.
                - sentiment: Duygu etiketi.
                - score: Duygu skorunun güvenilirlik değeri.
                - start: Turn başlangıç zamanı.
                - end: Turn bitiş zamanı.
                - speaker: Konuşmacı bilgisi.
    
    Raises:
        FileNotFoundError: Konuşma verisi bulunamazsa.
        ValueError: Konuşma verisi geçersiz formatta ise.
    """
    dataset = ConversationDataService.load_conversation(conversation_id)

    sentiment_analyzer = pipeline("text-classification", model="savasy/bert-base-turkish-sentiment-cased")

    results = []
    for turn in dataset["turns"]:
        text = turn.get("text", "")
        if text:
            sentiment_result = sentiment_analyzer(text)[0]
            result = {
                "text": text,
                "sentiment": sentiment_result.get("label", ""),
                "score": sentiment_result.get("score", 0),
                "start": turn.get("start", 0),
                "end": turn.get("end", 0),
                "speaker": turn.get("speaker", "unknown")
            }
            results.append(result)

    return results
