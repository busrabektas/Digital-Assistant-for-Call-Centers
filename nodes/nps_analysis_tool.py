from langchain_core.tools import tool
from transformers import pipeline
from conversation_data_service import ConversationDataService

@tool("analyze_nps")
def nps_analysis_tool(conversation_id: str) -> dict:
    """
    Verilen konuşmadan NPS (Net Promoter Score) analizi gerçekleştirir.
    
    Eğer conversation_id "all" olarak verilirse, veritabanındaki tüm konuşma ID'leri üzerinden 
    ayrı ayrı analiz yapılarak en düşük NPS skoruna sahip konuşmanın analizi döndürülür.
    
    Args:
        conversation_id (str): Konuşma ID'si. "all" girilirse, tüm konuşmalar için analiz yapılır.
    
    Returns:
        dict: Eğer conversation_id "all" ise, en düşük NPS skoruna sahip konuşmanın analizi; 
              aksi halde belirtilen conversation_id için analiz sonucu.
              Sonuç şu anahtarları içerir:
                - conversation_id: Analiz edilen konuşmanın id'si.
                - nps: Promoter yüzdesi - detractor yüzdesi.
                - promoters_percentage: Promoter oranı.
                - passives_percentage: Passive oranı.
                - detractors_percentage: Detractor oranı.
                - classified_turns: Her müşteri ifadesi için sınıflandırma sonucu.
    """
    classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli", disable_tqdm=True)
    candidate_labels = ["promoter", "passive", "detractor"]

    def analyze_single_conversation(conv_id: str) -> dict:
        dataset = ConversationDataService.load_conversation(conv_id)
        customer_turns = [turn for turn in dataset["turns"] if turn.get("speaker", "").upper() == "SPEAKER_01"]
        if not customer_turns:
            return {"nps": None}
        
        classified_turns = []
        promoter_count = 0
        passive_count = 0
        detractor_count = 0

        for turn in customer_turns:
            text = turn.get("text", "")
            if not text:
                continue
            result = classifier(text, candidate_labels)
            top_label = result["labels"][0].lower()
            classified_turns.append({
                "text": text,
                "predicted_label": top_label,
                "scores": dict(zip(result["labels"], result["scores"]))
            })
            if top_label == "promoter":
                promoter_count += 1
            elif top_label == "passive":
                passive_count += 1
            elif top_label == "detractor":
                detractor_count += 1

        total = promoter_count + passive_count + detractor_count
        promoters_percentage = (promoter_count / total) * 100 if total > 0 else 0
        passives_percentage = (passive_count / total) * 100 if total > 0 else 0
        detractors_percentage = (detractor_count / total) * 100 if total > 0 else 0
        nps_score = promoters_percentage - detractors_percentage

        return {
            "conversation_id": conv_id,
            "nps": nps_score,
            "promoters_percentage": promoters_percentage,
            "passives_percentage": passives_percentage,
            "detractors_percentage": detractors_percentage,
            "classified_turns": classified_turns
        }

    if conversation_id.lower() == "all":
        all_ids = ConversationDataService.get_all_conversation_ids()
        lowest_nps = None
        lowest_result = None
        for conv_id in all_ids:
            try:
                result = analyze_single_conversation(conv_id)
                if result.get("nps") is not None:
                    if lowest_nps is None or result["nps"] < lowest_nps:
                        lowest_nps = result["nps"]
                        lowest_result = result
            except Exception as e:
                continue
        if lowest_result is None:
            raise ValueError("Hiçbir geçerli konuşma bulunamadı veya analiz yapılamadı.")
        return lowest_result
    else:
        return analyze_single_conversation(conversation_id)
