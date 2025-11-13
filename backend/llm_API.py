from langchain_openai import ChatOpenAI
import json
import uuid
from flask import Flask, request, jsonify, Response
import redis
from schema import RedisSaver
from agent_list import welcome_agent
from tools.daily import CustomContext

app = Flask(__name__)
saver = RedisSaver()


@app.route("/chat", methods=["POST"])
async def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    thread_id = data.get("thread_id", "default_thread")
    print(f"user query: {user_input}\n")
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    #save the chat
    await saver.add_message(thread_id, "user", user_input)

    # call llm
    async def generate():
        for stream_mode, chunk in welcome_agent.stream(
                {"messages": [{"role": "user", "content": f'{user_input}'}]},
                context=CustomContext(user_id="1"),
                config={"configurable": {"thread_id": thread_id}},
                stream_mode=["messages", "custom","updates"],
        ):
            if stream_mode in ["updates","custom"]:
                print(f"stream_mode: {stream_mode}")
                print(f"content: {chunk}")
                print("\n")
                if 'model' in chunk:
                    llm_reply = chunk['model']['messages'][-1].content
                    await saver.add_message(thread_id,"assistant",llm_reply)

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