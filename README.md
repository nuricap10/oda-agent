# Oda Agent

A local AI shopping assistant built to explore the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) and tool-calling agents. It uses a locally hosted LLM through Ollama (`qwen2.5:7b` by default) and a mock grocery store instead of the live Oda API.

## How it works

1. The agent starts the local MCP server as a subprocess over stdio.
2. It retrieves the store tools: `search_products`, `add_to_cart`, and `get_cart`.
3. It sends the user request and available tools to the Ollama model.
4. The agent runs the model's tool calls and returns a summary of the cart.

## Project structure

```text
oda-agent/
├── agent/
│   ├── __init__.py
│   ├── main.py              # MCP client and agent loop
│   └── prompts.py           # System instructions for the LLM
├── data/
│   └── varer.json           # Mock grocery catalog
├── server/
│   └── oda_mock_server.py   # Local MCP server exposing store tools
├── .env.example             # Environment variable template
└── requirements.txt         # Python dependencies
```

## Requirements

- Python 3
- [Ollama](https://ollama.com/) with the `qwen2.5:7b` model available

Pull the model if needed:

```bash
ollama pull qwen2.5:7b
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file:

```bash
cp .env.example .env
```

## Configuration

The `.env` file supports these settings:

| Variable | Default | Description |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama's OpenAI-compatible API URL |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model used by the agent |

## Run

Start the agent from the project root:

```bash
python3 agent/main.py
```
