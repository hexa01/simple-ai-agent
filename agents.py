# agents.py
import logging
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from dotenv import load_dotenv
from tools import calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section
from prompts import SYSTEM_PROMPT
import os

load_dotenv()
logger = logging.getLogger(__name__)



class AgentState(BaseModel):
    messages : Annotated[list[BaseMessage], add_messages]
    steps : int = 0
    model_config = {"arbitrary_types_allowed": True}

MAX_RETRIES = 3

if not os.environ.get('OPENAI_API_KEY'):
    raise EnvironmentError('Setup valid OPENAI_API_KEY in .env')

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=1024,
    max_retries=MAX_RETRIES,
)

tools = [calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section]

model_with_tools = model.bind_tools(tools)


def agent_node(state: AgentState):
    """Assistant node: invokes LLM, injects system prompt if missing."""
    messages = state.messages
    steps = state.steps
    MAX_STEPS = 7

    if not any(isinstance(m, SystemMessage) for m in state.messages):
        messages = [SystemMessage(content = SYSTEM_PROMPT)] + messages


    if steps >= MAX_STEPS:
        return {
            "messages": [
                AIMessage(content="Provide your best possible final answer based on current information.")
            ],
            "steps": steps
        }
    

    try:
        response = model_with_tools.invoke(messages)
        logger.debug("LLM response: %s", response)
        return {"messages": [response],
                "steps": steps + 1} 
    except Exception:
        logger.exception("LLM invocation failed")
        raise
    
        