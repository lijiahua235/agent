from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
# from tools.daily import Tools

app = Flask(__name__)

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# 创建自己的模型实例
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    base_url="https://api.siliconflow.cn/v1",  # 改成你的API地址
    api_key="sk-glivxumizpjdkbgxbdnwaeuecmkzugydhpwnefbkfcvdqwge"
)
# resp = llm.invoke("hello,你会说中文吗")
# print(resp)

# agent = create_agent(
#     model=llm,
#     tools=[get_weather],
#     system_prompt="You are a helpful assistant",
# )
#
# # Run the agent
# agent.invoke(
#     {"messages": [{"role": "user", "content": "hello, tell me your name"}]}
# )

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    # 调用模型

    response = llm.invoke(user_input)
    reply = response.content if hasattr(response, "content") else str(response)

    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)