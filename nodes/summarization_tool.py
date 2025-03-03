import warnings
from langchain_core.tools import tool
from transformers import pipeline, logging
from conversation_data_service import ConversationDataService

warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["TRANSFORMERS_NO_TQDM"] = "1"
logging.set_verbosity_error()

@tool("summarize_conversation")
def summarization_tool(conversation_id: str) -> str:
    """
    MySQL veritabanından çekilen konuşma verilerini kullanarak, Hugging Face özetleme modeli ile 
    verilen konuşmayı özetler.
    
    Bu fonksiyon, ConversationDataService aracılığıyla belirtilen conversation_id'ye ait verileri 
    (turns listesini) veritabanından çeker, tüm turn'ları "SPEAKER: metin" formatında birleştirir ve 
    özetleme modeli ile işleyerek özet metni üretir.
    
    Args:
        conversation_id (str): Özetlenecek konuşmanın benzersiz ID'si veya "all" (tüm konuşmalar için).
    
    Returns:
        str: Konuşmanın özetini içeren metin.
    
    Raises:
        FileNotFoundError: Veritabanından veri çekilemezse.
        ValueError: Konuşma verileri beklenen formatta değilse.
    """
    dataset = ConversationDataService.load_conversation(conversation_id)

    if "turns" not in dataset:
        raise ValueError("Invalid dataset format: 'turns' key not found.")

    conversation_text = " ".join(
        [f"{turn['speaker']}: {turn['text']}" for turn in dataset["turns"]]
    )

    summarizer = pipeline("summarization", model="ozcangundes/mt5-small-turkish-summarization")

    summary = summarizer(
        conversation_text,
        max_length=300,
        min_length=100,
        do_sample=False,
        num_beams=4
    )

    summary_text = summary[0].get("summary_text", "")

    if "Konuşmanın özeti:" in summary_text:
        summary_text = summary_text.split("Konuşmanın özeti:")[-1].strip()

    return summary_text
