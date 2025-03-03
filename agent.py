from datetime import datetime
datetime.now()
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from nodes.sentiment_analysis_tool import sentiment_analysis_tool
from nodes.summarization_tool import summarization_tool
from nodes.nps_analysis_tool import nps_analysis_tool 

#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            conversation_id = configuration.get("conversation_id", None)
            state = {**state, "conversation_info": conversation_id }

            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}



OPENAI_API_KEY="your_open_ai_api_key"
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
#llm = ChatOllama(model="qwen2.5:7b-instruct-fp16", temperature=0)

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sen bir çağrı merkezi süpervizör asistanısın. Görevin, müşteri temsilcilerinin (agent) performansını analiz etmek ve konuşmaların detaylı analizlerini sunmaktır. "
            "Verilen araçları (duygu analizi, özetleme ve NPS analizi) kullanarak konuşmaları analiz et. "
            "Eğer spesifik bir conversation_id verilmişse, o konuşma üzerinden; verilmemişse, tüm konuşmalar üzerinden analiz yap. "
            "Performans değerlendirmesi, duygu durumları ve özet bilgilerini düzenli şekilde raporla. "
            "\n\nŞu anki kullanıcı bilgisi:\n<Conversation>\n{conversation_info}\n</Conversation>"
            "\nŞu anki zaman: {time}."

        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

part_1_tools = [
    sentiment_analysis_tool,
    summarization_tool,
    nps_analysis_tool,  

]

part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)


