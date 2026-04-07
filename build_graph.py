# build_graph.py

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from agents import agent_node, AgentState
from tools import calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section

tools = [calculator, web_search, fetch_page, wikipedia_search, get_wikipedia_section]

# nodes
builder = StateGraph(AgentState)
builder.add_node("assistant",agent_node)
builder.add_node("tools",ToolNode(tools))

#edges
builder.add_edge(START,"assistant")
builder.add_conditional_edges("assistant",tools_condition)
builder.add_edge("tools","assistant")

react_agent = builder.compile()

