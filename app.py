import streamlit as st
import uuid
from graph import part_1_graph  

st.set_page_config(page_title="Çağrı Merkezi Asistanınız", page_icon="📞")
st.title("📞 Çağrı Merkezi Asistanınız")
st.write("Merhaba! Sorularınızı yazın, size yardımcı olacağım.")

if "messages" not in st.session_state:
    st.session_state.messages = []  

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı yazın:"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)


    messages = [(msg["role"], msg["content"]) for msg in st.session_state.messages]
    state = {"messages": messages}
    
    config = {
        "configurable": {
            "conversation_id": "all",  
            "thread_id": str(uuid.uuid4()),
            "folder_path": "conversations"
        }
    }
    
    responses = list(part_1_graph.stream(state, config, stream_mode="values"))
    assistant_response = ""
    for event in responses:
        msgs = event.get("messages")
        if msgs:
            assistant_response = msgs[-1].content  
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
