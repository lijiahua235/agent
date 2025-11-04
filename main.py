import streamlit as st
from backend.app import llm
import requests

st.set_page_config(page_title="ChatGPT Demo", page_icon="🤖")
st.title("🤖 Agent")

if "history" not in st.session_state:
    st.session_state.history = []

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
    with st.spinner("AI is typing..."):
        response = requests.post(
            "http://localhost:10000/chat",
            json={"message": user_input}
        )
        if response.status_code == 200:

            result = response.json()["reply"]
            st.chat_message("assistant").write(f"{result}")
        else:
            st.error(f"后端错误：{response.status_code}")
        # reply = llm.invoke(user_input)
    st.session_state.history.append({"role": "assistant", "content": result})
