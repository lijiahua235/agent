import streamlit as st
import requests
import time
import json

st.set_page_config(page_title="ChatGPT Demo", page_icon="🤖")
st.title("🤖 Agent")

if "history" not in st.session_state:
    st.session_state.history = []

if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

###################定义函数#################
def stream_output(res,delay=0.02):
    """逐字符输出文本，可中途停止"""
    for line in res.iter_lines(decode_unicode=True):
        print(f"{line}")
        if line:
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                data_json = json.loads(data_str)
                text = data_json.get("reply", "")
                yield text
                time.sleep(delay)

###################主页面#################
# Using "with" notation
with st.sidebar:
    if st.button("开始新的对话"):
        st.session_state.history.clear()
    st.write("chat")
    # if st.session_state.history:


#在输入框出现之前，先渲染所有历史对话
if len(st.session_state.history) != 0:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# 用户输入
if user_input := st.chat_input("Say something"):
    st.session_state.history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    #流式输出

    with st.spinner("AI is typing..."):
        with requests.post(
            "http://localhost:10000/chat",
            json={"message": user_input},
            stream=True
        ) as response:
            if response.status_code == 200:

                # result = response.json()["reply"]
                st.chat_message("assistant").write_stream(stream_output(response))
            else:
                st.error(f"后端错误：{response.status_code}")
            # response_box.write_stream(stream_output(buffer))
        # reply = llm.invoke(user_input)
    # st.session_state.history.append({"role": "assistant", "content": result})
