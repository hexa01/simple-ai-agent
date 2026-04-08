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

## Future Enhancements

The agent currently skips questions that include file attachments. The following tools are planned to close that gap:

### 🎵 Audio File Handling
- **Tool:** `transcribe_audio`
- Accepts audio files (`.mp3`, `.wav`, `.m4a`, etc.) attached to benchmark questions
- Transcribes speech to text using the [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text) or a local Whisper model (`openai-whisper`)
- The transcript is passed back into the agent's context so it can answer questions about the audio content

### 🖼️ Image Understanding
- **Tool:** `analyze_image`
- Accepts image files (`.png`, `.jpg`, `.jpeg`, `.gif`, etc.) attached to benchmark questions
- Sends the image to a vision-capable model (e.g. GPT-4o with image input) and returns a detailed description or a direct answer to the question about the image
- Handles charts, diagrams, screenshots, and photos

### 🎬 YouTube Video Transcription
- **Tool:** `get_youtube_transcript`
- Accepts a YouTube URL or video ID
- Retrieves the video transcript using the [`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api) library (no API key required for videos with captions)
- Falls back to downloading the audio and running Whisper transcription for videos without auto-generated captions
- Enables the agent to answer questions about video content, interviews, lectures, and tutorials

### Integration plan
Once the tools above are implemented:
1. Add them to `tools.py` following the same `@tool` decorator pattern
2. Register them in the `tools` list in both `agents.py` and `build_graph.py`
3. Update the file-attachment branch in `app.py` to route questions with a `file_name` through the appropriate tool based on file extension or MIME type

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
