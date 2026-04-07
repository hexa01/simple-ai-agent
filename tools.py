# tools.py
import logging
from langchain_core.tools import tool
from ddgs import DDGS
from simpleeval import simple_eval, InvalidExpression
import requests
import wikipediaapi
import trafilatura 

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

@tool
def fetch_page(url: str) -> str:
    """Fetch and return the main text content of any webpage by URL.
    Use this when you have a specific URL from search results and need
    the full content, not just the snippet.
    Use for: news articles, government pages, research papers, any non-Wikipedia URL.
    Do NOT use for Wikipedia URLs — use wikipedia_search instead.
    Requires: a full URL starting with https://
    Example: fetch_page("https://www.bbc.com/news/science-12345")
    """
    MAX_PAGE_CHARS = 8000
    REQUEST_TIMEOUT = 10

    try:
        response = requests.get(url, timeout = REQUEST_TIMEOUT)

        if response.status_code == 404:
            return f"Page not found(404): {url}"
        
        if response.status_code == 403:
            return f"Access Denied(403): {url}"

        if response.status_code != 200:
            return f"HTTP error {response.status_code} fetching {url}"

        content = trafilatura.extract(response.text, include_tables=True,no_fallback= False )

        if not content or len(content.strip())<50:
            return f"Couldn't extract meaningful content from url: {url}. Page may require javascript or has no readable content."
        
        if len(content) > MAX_PAGE_CHARS:
            content = content[:MAX_PAGE_CHARS]
            content += f"Content truncated at {MAX_PAGE_CHARS} characters. If the answer is not found, try a more specific search query."

        return f"Source: {url}\n\nContent: {content}"

    except requests.exceptions.Timeout:
        return f"Timeout: {url} didn't respond within {REQUEST_TIMEOUT} seconds"
    
    except requests.exceptions.ConnectionError:
        return f"ConnectionError: {url} couldn't be reached. Check if the url is correct."
    except Exception as e:
        logger.exception(f"fetch_page failed for url:{url}")
        return f"Unexpected error fetching {url} {type(e).__name__}: {e}"
    

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual information about people, places,
    events, concepts, history, or science.
    Use this when:
    - The question references Wikipedia explicitly
    - You need reliable encyclopedic facts
    - The topic is a named entity, event, or concept
    Prefer this over fetch_page for any Wikipedia content.
    Pass the topic name, not a URL.
    Example: wikipedia_search("2020 Summer Olympics")
    Example: wikipedia_search("Marie Curie")
    """
    MAX_WIKI_CHARS= 8000
    REQUEST_TIMEOUT = 10
    try:
        wiki = wikipediaapi.Wikipedia(
            language = "en",
            user_agent = "MyPersonalResearchBot/1.0 (sushanpoudel80@gmail.com)",
            extract_format = wikipediaapi.ExtractFormat.WIKI
        )

        page = wiki.page(query)

        if not page.exists():
            search_results = wiki.search(query)

            if not search_results:
                return f"No wikipedia article found for {query}. Try different search term."
            
            page = wiki.page(search_results[0]) #most relevant search term

            if not page.exists():
                return (
                    f"No Wikipedia article found for '{query}'. "
                    f"Similar articles exist: {', '.join(search_results)}. "
                    f"Try wikipedia_search with one of these exact titles."
                )
        
        section_titles = [s.title for s in page.sections]

        content = f"Article: {page.title}\n"
        content += f"URL: {page.canonicalurl}\n\n"
        content += f"Summary: {page.summary}\n\n"

        if section_titles:
            content += f"Available sections: {', '.join(section_titles)}\n\n"
            
        content += f"Full content: \n{page.text}"

        if len(content) >  MAX_WIKI_CHARS:
            content = content[:MAX_WIKI_CHARS]
            content += (
            f"\n\n[Article truncated at {MAX_WIKI_CHARS} characters. "
            f"Sections available: {', '.join(section_titles)}. "
            f"If you need a specific section, call get_wikipedia_section('{page.title}', 'section name')."
            )
            
        return content           

    except Exception as e:
        logger.exception(f"wikipedia_search failed for query: {query}")
        return f"Unexpected error searching wikipedia {type(e).__name__}: {e}"    

   
@tool
def get_wikipedia_section(article_title: str, section_name: str) -> str:
    """Get a specific section from a Wikipedia article.
    Use this when wikipedia_search returned truncated content and you
    need a specific section from that article.
    Example: get_wikipedia_section("2020 Summer Olympics", "Medal table")
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            language = "en",
            user_agent = "MyPersonalResearchBot/1.0 (sushanpoudel80@gmail.com)",
            extract_format = wikipediaapi.ExtractFormat.WIKI
        )
        page = wiki.page(article_title)

        if not page.exists():
            return f"Article not found: {article_title}"   

        section = page.section_by_title(section_name)

        if not section:
            all_sections = [s.title for s in page.sections]
            return (
                f"Section: '{section_name}' not found in article: '{article_title}'."
                f"Available sections: '{', '.join(all_sections)}'"
            )
        if not section.text:
            return (
                f"There is no meaningful context in this section: '{section_name}' for article: '{article_title}'"
                f"Choose another section if you need further information."
            )

        return f"{section.title}\n\n{section.text}"

    except Exception as e:
        logger.exception(f"get_wikipedia_section failed for article_title: {article_title}, section: {section_name}")
        return f"Unexpected error fetching wikipedia section {type(e).__name__}: {e}" 

