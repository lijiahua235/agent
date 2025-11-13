from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from tools.daily import CustomState, CustomContext, get_weather, update_user_info, greet
import inspect
import yaml
import json


API_Path = "config/API_Resource.yaml"
with open(API_Path, 'r', encoding='utf-8') as f:
    data = f.read()
    API_list = yaml.load(data, Loader=yaml.FullLoader)

with open('config/SystemPrompt.json', 'r') as prompt_file:
    system_prompt = json.load(prompt_file)

checkpointer = InMemorySaver()

#config error management
@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

# create an Object of LLM
qwen = ChatOpenAI(
    model=API_list['SILICONFLOW']['Qwen3-8B'],
    base_url=API_list['SILICONFLOW']['BASE_URL'],
    api_key=API_list['SILICONFLOW']['API_KEY'],
    temperature=0.5,
    timeout=30,
    max_tokens=1000,
)

welcome_agent = create_agent(
                                model=qwen,
                                checkpointer=checkpointer,
                                tools=[get_weather, update_user_info, greet],
                                system_prompt=system_prompt['Welcome_Agent'],
                                state_schema=CustomState,
                                context_schema=CustomContext,
                                middleware=[handle_tool_errors]
                             )