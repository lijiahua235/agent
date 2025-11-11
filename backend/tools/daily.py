from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command
from langgraph.config import get_stream_writer
from pydantic import BaseModel


class CustomState(AgentState):
    user_name: str

class CustomContext(BaseModel):
    user_id: str


@tool
def update_user_info(
    runtime: ToolRuntime[CustomContext, CustomState],
) -> Command:
    """Look up and update user info before greeting."""
    writer = get_stream_writer()
    user_id = runtime.context.user_id
    name = "Jiahua" if user_id == "1" else "Unknown user"
    writer(f"From now on I will call you as: {name}")
    return Command(update={
        "user_name": name,
        # update the message history
        "messages": [
            ToolMessage(
                "Successfully looked up user information",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

@tool
def greet(
    runtime: ToolRuntime[CustomContext, CustomState]
) -> str:
    """Use this to greet the user once the user says greeting"""
    writer = get_stream_writer()
    user_name = runtime.state.get("user_name", "dear")
    writer(f"Hello {user_name}")
    return f"🌈"

def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"