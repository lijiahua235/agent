import streamlit as st
import requests
import time
import json

st.set_page_config(page_title="ChatGPT Demo", page_icon="🤖")
st.title("🤖 Agent")

###################Globalize#################
if "history" not in st.session_state:
    st.session_state.history = []

if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

FINAL_OUTPUT_FOR_EACH_QUERY = []

###################Function Definition#################
def stream_output(res,delay=0.02):
    """streaming"""
    for line in res.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                data_json = json.loads(data_str)
                text = data_json.get("reply", "")
                FINAL_OUTPUT_FOR_EACH_QUERY.append(text)
                yield text
                time.sleep(delay)

###################Main  Page Rendering#################
# Using "with" notation
with st.sidebar:
    if st.button("start new conversation"):
        st.session_state.history.clear()
    st.write("chat")
    # if st.session_state.history:


#render history chat before querying
if len(st.session_state.history) != 0:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


#user input
if user_input := st.chat_input("Say something"):
    print(f'start querying')
    st.session_state.history.append({"role": "user", "content": user_input})
    FINAL_OUTPUT_FOR_EACH_QUERY.clear()
    st.chat_message("user").write(user_input)
    #streaming
    with st.spinner("AI is typing..."):
        with requests.post(
            "http://localhost:10000/chat",
            json={"message": user_input},
            stream=True
        ) as response:
            if response.status_code == 200:
                st.chat_message("assistant").write_stream(stream_output(response))
                result = "".join(FINAL_OUTPUT_FOR_EACH_QUERY)
            else:
                st.error(f"backend error：{response.status_code}")
    print(f'end')
    st.session_state.history.append({"role": "assistant", "content": result})
