"""
This code connects to a Model Context Protocol (MCP) server, retrieves available tools, and interacts with them.

1. **Logging Setup:**
    - **Purpose**: Records detailed logs for all operations.
    - **How**: Uses `logging.basicConfig` to configure the log file (`client.log`) with `INFO` level logging, making it easier to track execution steps and debug any issues.

2. **MCP Client Setup:**
    - **Purpose**: Connects to a Model Context Protocol (MCP) server at `localhost:8000/mcp` for tool interactions.
    - **How**: Creates an asynchronous connection (`streamablehttp_client`) to interact with the server. The session (`ClientSession`) is used to send and receive data from the server.

3. **Tools Listing:**
    - **Purpose**: Retrieves available tools on the server.
    - **How**: Calls `session.list_tools()` to get all the available tools, and extracts the tool names for display. Logs and prints the available tools for the user.

4. **Tool Interaction:**
    - **Purpose**: Sends a request to call a tool, in this case, a simple `hello` tool with a name as an argument.
    - **How**: Uses `session.call_tool("hello", arguments={"name": "Hajar"})` to invoke the tool, then logs and prints the response received from the tool.

5. **Prompt (for tool selection):**
    - **Purpose**: Provides a pre-defined instruction to the assistant on how to select and explain tools.
    - **How**: The prompt is structured to guide the AI assistant in reading user requests, selecting the right tools from the list, and explaining why these tools are appropriate for solving the task.

6. **Asynchronous Execution:**
    - **Purpose**: Runs the asynchronous functions that handle MCP interactions.
    - **How**: The code uses `asyncio.run(main())` to initiate the asynchronous process, ensuring that all I/O operations (e.g., calling tools, fetching messages) run in an efficient, non-blocking manner.
"""



from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import asyncio
import logging

logging.basicConfig(
    filename='client.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (reader, writer, session_id):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            logging.info("Connected to MCP server")

            # List tools (empty)
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print("Available tool names:", tool_names)
            logging.info(f"Available tool names: {tool_names}")
            tools_list = await session.list_tools()
            print("Available tools:", tools_list)
            logging.info(f"Available tools list: {tools_list}")
            # Call the 'hello' tool
            response = await session.call_tool("hello", arguments={"name": "Hajar"})
            print("Response:", response.content[0].text)
            logging.info(f"Response: {response.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
