# tools.py
import logging
from langchain_core.tools import tool
from ddgs import DDGS
from simpleeval import simple_eval, InvalidExpression


logger = logging.getLogger(__name__)


@tool
def calculator(expr: str) -> str:
    """Evaluate a mathematical expression safely. Examples: '5+10', '14000/2000', '(3**2)*4'.
    Never compute math yourself — always use this tool.
    """
    try:
        result = simple_eval(expr)
        return str(result)
    except InvalidExpression as e:
        logger.warning("Invalid expression passed to calculator: %s | error: %s", expr, e)
        return f"Invalid expression: {e}. Please provide a valid math expression."
    except Exception as e:
        logger.exception("Calculator error for expr=%s", expr)
        return f"Calculation error: {e}"


@tool
def web_search(query: str) -> str:
    """Search the web for current, factual information using DuckDuckGo.
    Use for recent events, facts, or anything requiring up-to-date information.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found."
        # Return top 3 snippets formatted

        formatted = []
        for i, r in enumerate(results):
            formatted.append(
                f"[{i+1}] {r['title']}\n"
                f"URL: {r['href']}\n"
                f"Summary: {r['body']}\n"
            )
        return "\n".join(formatted)

    except Exception as e:
        logger.exception("Web search failed for query=%s", query)
        return f"Search error: {e}"

