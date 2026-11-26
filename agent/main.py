import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from prompts import SYSTEM_PROMPT

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Point directly to the server script and use the same Python environment (.venv)
SERVER_SCRIPT = str(Path(__file__).parent.parent / "server" / "oda_mock_server.py")

llm = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

async def run_chat():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Fetch tools from the MCP server
            mcp_tools = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.input_schema,
                    },
                }
                for t in mcp_tools.tools
            ]

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
            ]

            print("Oda Agent is ready! Type 'exit' to quit.\n")

            # Outer loop: Interactive chat in the terminal
            while True:
                user_message = input("You: ")
                if user_message.strip().lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                if not user_message.strip():
                    continue

                messages.append({"role": "user", "content": user_message})

                # Inner loop: Let the agent call MCP tools (max 8 steps to prevent infinite loops)
                steps = 0
                while steps < 8:
                    steps += 1
                    response = llm.chat.completions.create(
                        model=OLLAMA_MODEL,
                        messages=messages,
                        tools=tools,
                    )
                    msg = response.choices[0].message

                    # Ignore empty responses from Ollama and keep looping
                    if not msg.tool_calls and not msg.content:
                        continue

                    messages.append(msg)

                    if not msg.tool_calls:
                        print(f"\nAgent:\n{msg.content}\n")
                        break

                    for tool_call in msg.tool_calls:
                        name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        print(f"  [MCP Tool]     {name}({args})")

                        # Human-in-the-Loop guardrail for critical actions
                        if name == "checkout":
                            confirm = input("  ⚠️  Approve checkout and payment? [y/n]: ")
                            if confirm.strip().lower() != "y":
                                response_text = "Checkout was cancelled by the user. Do not retry checkout unless asked again."
                                print(f"  [MCP Blocked]  {response_text}")