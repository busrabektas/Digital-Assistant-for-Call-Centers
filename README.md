# 🤖 DIGITAL ASSISTANT FOR CALL CENTERS


## Overview
This project is an AI-powered digital assistant designed to analyze customer service calls. The assistant processes structured text data and applies three key analytical tools using LangGraph and GPT-4o:

- NPS Analysis: Evaluates customer loyalty and satisfaction.

- Sentiment Analysis: Assesses the emotional tone of conversations.

- Summarization: Generates concise summaries of customer interactions.

## Technologies Used

- Speech-to-Text & Diarization: WhisperX (Pre-Processing Step)

- Database: MySQL

- AI & NLP Models: GPT-4o, RoBERTa-based Zero-Shot Classification, BERT for Sentiment Analysis, mT5 for Summarization

- Frameworks & Libraries: LangGraph, Transformers, Streamlit

## Architecture

![output](images/architecture.png)

### 1. Dataset Preperation 
- Customer service calls are recorded in audio format.

- WhisperX performs diarization and converts speech to text.

- The processed text is stored in JSON format.

### 2. Data Storage
- Conversations in JSON format are stored in a database.

- MySQL is used to store structured conversation data with unique IDs.

### 3. Data Processing & Analysis
LangGraph creates a workflow that processes structured text data using GPT-4o.

**Three AI-based tools analyze the conversations:** 

- 📊 **NPS Analysis**: Predicts and evaluates customer loyalty and satisfaction.

    - **Model used** : joeddav/xlm-roberta-large-xnli​

        - Uses zero-shot classification to categorize customer feedback into promoter, passive, and detractor.​

        - Based on RoBERTa, a multilingual Natural Language Inference (NLI) model that analyzes meaning and intent.

    - **Process**
        - Customer sentences are analyzed using the model.​

        - NPS score is calculated as (Promoter % - Detractor %).​

        - Conversations with the lowest NPS scores are identified and reported 

- 😊 **Sentiment Analysis**: Analyzes the emotional tone of the conversation.​

    - **Model used** : savasy/bert-base-turkish-sentiment-cased​
        - A Turkish-specific fine-tuned BERT model.​
        -Classifies sentences into positive, negative, or neutral emotions.​

    - **Process**
        - Data is retrieved from MySQL, separating customer and agent dialogues.​

        - Each customer statement is analyzed and assigned a sentiment label.​

        - Sentiment scores are calculated, providing confidence percentages.​



- 📝 **Summarization**: Extracts key points from the conversation to generate a summary.

    - **Model used** : ozcangundes/mt5-small-turkish-summarization​
        - A Turkish-specific summarization model based on mT5.​

    - **Process**
        - Conversation data is retrieved from the database.​

        - All turns are merged into a structured "Speaker: Text" format.​

        - The model generates a summary with a max length of 300 tokens and a min length of 100 tokens.​

### 4. Dashboard

- Chat UI created with Streamlit 

![output](images/1.jpeg)

![output](images/2.jpeg)

![output](images/3.png)

![output](images/4.jpeg)

![output](images/5.jpeg)




## References

1. **Sentiment Analysis Model:** [BERT-base Turkish Sentiment](https://huggingface.co/savasy/bert-base-turkish-sentiment-cased)

    - Yildirim, Savas. Fine-tuning Transformer-based Encoder for Turkish Language Understanding Tasks. arXiv preprint (2024). arXiv:2401.17396

    - Yildirim, Savas & Asgari-Chenaghlu, Meysam. Mastering Transformers: Build state-of-the-art models from scratch with advanced natural language processing techniques. Packt Publishing Ltd, 2021.

2. **NPS Analysis Model**: [XLM-RoBERTa Large XNLI ](https://huggingface.co/joeddav/xlm-roberta-large-xnli) 

3. **Summarization Model**: [mT5 Small Turkish Summarization ](https://huggingface.co/ozcangundes/mt5-small-turkish-summarization)

