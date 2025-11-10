from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
import redis
from agent_list import welcome_agent
from tools.daily import CustomContext

app = Flask(__name__)
pool = redis.ConnectionPool(host='localhost', port=8080, decode_responses=True)
redis_db = redis.Redis(connection_pool=pool)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    print(f"{user_input}")
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    # 调用模型
    response = welcome_agent.invoke(
        {"messages": [{"role": "user", "content": f'{user_input}'}]},
        context = CustomContext(user_id="1"),
        config={"configurable": {"thread_id": "1"}}
    )
    print(response)
    reply = response['messages'][-1].content.strip()
    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)