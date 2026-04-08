# simple-ai-agent

A ReAct-style AI agent built with [LangChain](https://www.langchain.com/), [LangGraph](https://github.com/langchain-ai/langgraph), and OpenAI GPT-4o-mini. Built as a submission for the [Hugging Face Agents Course – Unit 4](https://huggingface.co/learn/agents-course) evaluation benchmark.

## What it does

The agent fetches a set of questions from the Hugging Face scoring API, answers each one by reasoning and calling tools, then submits the answers back to the API and prints the final score.

**Flow:**
```
Fetch questions → Run ReAct agent on each question → Submit answers → Get score
```

## Architecture

The agent uses a [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph` with two nodes:

- **`assistant`** – Calls the LLM (GPT-4o-mini) with the current message history. Injects a system prompt on the first step. Caps execution at 7 steps to prevent runaway loops.
- **`tools`** – Executes whichever tool the LLM chose to call.

Edges use `tools_condition` so the graph loops between assistant and tools until the LLM produces a final answer (no tool call).

```
START → assistant ⇄ tools → (final answer)
```

## Tools

| Tool | Description |
|---|---|
| `calculator` | Safely evaluates mathematical expressions using `simpleeval` |
| `web_search` | Searches the web via DuckDuckGo and returns the top 3 results |
| `fetch_page` | Fetches and extracts readable content from a given URL using `trafilatura` |
| `wikipedia_search` | Searches Wikipedia and returns a summary + full article content |
| `get_wikipedia_section` | Retrieves a specific section from a Wikipedia article (useful when content is truncated) |

## Project Structure

```
simple-ai-agent/
├── app.py            # Entry point: fetches questions, runs agent, submits answers
├── agents.py         # Agent node definition, LLM setup, AgentState
├── build_graph.py    # LangGraph StateGraph construction
├── tools.py          # Tool implementations
├── prompts.py        # System prompt
├── requirements.txt  # Python dependencies
└── .env.example      # Environment variable template
```

## Setup

**1. Clone the repo and install dependencies:**

```bash
git clone https://github.com/hexa01/simple-ai-agent.git
cd simple-ai-agent
pip install -r requirements.txt
```

**2. Configure environment variables:**

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
OPENAI_API_KEY="your-openai-api-key-here"
USERNAME="your-huggingface-username-here"
AGENT_CODE="your-agent-repo-link"
```

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key (required to call GPT-4o-mini) |
| `USERNAME` | Your Hugging Face username (used when submitting answers) |
| `AGENT_CODE` | Link to your Hugging Face Space or agent repo (included in submission) |

**3. Run the agent:**

```bash
python app.py
```

The agent will fetch the benchmark questions, solve them one by one, submit the answers, and print the result:

```
Submission Successful!
User: your-username
Overall Score: 42.0% (7/10 correct)
Message: ...
```

## Notes

- Questions that include file attachments (`file_name` field) currently return a default placeholder answer. Adding file-handling tools would improve coverage on those questions.
- The agent is capped at **7 reasoning steps** per question to keep costs and latency in check.
- The LLM is instructed to return **only the final answer** with no explanation, matching the benchmark's expected output format.

## Dependencies

- [langchain](https://github.com/langchain-ai/langchain) / [langchain-openai](https://github.com/langchain-ai/langchain) / [langgraph](https://github.com/langchain-ai/langgraph)
- [openai](https://platform.openai.com/) (via `langchain-openai`)
- [ddgs](https://github.com/deedy5/duckduckgo_search) – DuckDuckGo search
- [wikipedia-api](https://github.com/martin-majlis/Wikipedia-API) – Wikipedia access
- [trafilatura](https://github.com/adbar/trafilatura) – Web page content extraction
- [simpleeval](https://github.com/danthedeckie/simpleeval) – Safe math expression evaluation
- [pydantic](https://docs.pydantic.dev/) – Data validation
- [python-dotenv](https://github.com/theskumar/python-dotenv) – Environment variable loading
