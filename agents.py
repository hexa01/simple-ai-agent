# agents.py
import logging
from typing import Annotated
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from dotenv import load_dotenv
from tools import calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section
from prompts import SYSTEM_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)



class AgentState(BaseModel):
    messages : Annotated[list[BaseMessage], add_messages]
    model_config = {"arbitrary_types_allowed": True}

MAX_RETRIES = 3

model = ChatOpenRouter(
    model="qwen/qwen3.6-plus:free",
    temperature=0.3,
    max_tokens=1024,
    max_retries=MAX_RETRIES,
)

tools = [calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section]

model_with_tools = model.bind_tools(tools)


def agent_node(state: AgentState):
    """Assistant node: invokes LLM, injects system prompt if missing."""
    messages = state.messages
    if not any(isinstance(m, SystemMessage) for m in state.messages):
        messages = [SystemMessage(content = SYSTEM_PROMPT)] + messages

    try:
        response = model_with_tools.invoke(messages)
        logger.debug("LLM response: %s", response)
        return {"messages": [response]} 
    except Exception:
        logger.exception("LLM invocation failed")
        raise
    
        