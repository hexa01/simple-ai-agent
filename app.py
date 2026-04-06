# app.py
import logging
from build_graph import react_agent
from langchain_core.messages import HumanMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

if __name__ == "__main__":
    while True:
        q = input("Question: ")
        if q.lower() in ["exit", "quit"]:
            break

        answer = react_agent.invoke({
            "messages" : [HumanMessage(content = q)]
        })
        print("Answer:", answer["messages"][-1].content)