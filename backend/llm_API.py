from langchain_openai import ChatOpenAI
import json
from flask import Flask, request, jsonify, Response
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
    print(f"user query: {user_input}\n")
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    # call llm
    def generate():
        for stream_mode, chunk in welcome_agent.stream(
                {"messages": [{"role": "user", "content": f'{user_input}'}]},
                context=CustomContext(user_id="1"),
                config={"configurable": {"thread_id": "1"}},
                stream_mode=["messages", "custom","updates"],
        ):
            if stream_mode in ["updates","custom"]:
                print(f"stream_mode: {stream_mode}")
                print(f"content: {chunk}")
                print("\n")

            elif stream_mode == "messages":
                chunk_message, metadata = chunk
                text = chunk_message.content
                if text.strip() != '':
                    print(f'AI is typing: {text}\n')
                    yield f"data: {json.dumps({'reply': text})}\n\n"
        yield "data: [DONE]\n\n"

    #[11/Nov/2025 16:53:17] "POST /chat HTTP/1.1" 200 - only means the header of response is sent, later on the output
    #will send streamly

    return Response(generate(), content_type="text/event-stream")

    # response = welcome_agent.invoke(
    #     {"messages": [{"role": "user", "content": f'{user_input}'}]},
    #     context = CustomContext(user_id="1"),
    #     config={"configurable": {"thread_id": "1"}}
    # )
    # print(response)
    # reply = response['messages'][-1].content.strip()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)