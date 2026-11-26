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

async def run_agent(user_message: str):
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
                {"role": "user", "content": user_message},
            ]

            print(f"User: {user_message}\n")

            while True:
                response = llm.chat.completions.create(
                    model=OLLAMA_MODEL,
                    messages=messages,
                    tools=tools,
                )
                msg = response.choices[0].message
                messages.append(msg)

                if not msg.tool_calls:
                    print(f"\nAgent:\n{msg.content}")
                    break

                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"  [MCP Tool]     {name}({args})")

                    result = await session.call_tool(name, arguments=args)
                    response_text = result.content[0].text if result.content else "No results found."
                    print(f"  [MCP Response] {response_text}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": response_text,
                    })

if __name__ == "__main__":
    task = "I am making pancakes today. Find the ingredients I need in the store and add them to the cart."
    asyncio.run(run_agent(task))