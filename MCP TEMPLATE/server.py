"""
### Description:

This Python script sets up an MCP (Model Context Protocol) server using the `FastMCP` library. The server is configured with no pre-registered tools, but a simple "hello" function is defined as a tool. This function takes a name as input and returns a greeting message.

### Components:

1. **FastMCP Server Setup**:
    - `FastMCP`: This is a class that handles the creation and running of an MCP server. It is initialized with a name (`"EmptyMCPServer"`) and runs on `localhost` at port `8000`.
    - The server is configured to use streamable HTTP transport (`"streamable-http"`), which allows for continuous communication over HTTP, potentially useful for real-time applications.

2. **Logging**:
    - The `logging` module is configured to record logs into a file (`server.log`) with a log level of `INFO`. It also defines a log format that includes the timestamp, log level, and message for easy tracking of server activity.

3. **Tool Definition**:
    - The `hello` function is defined as a tool using the `@mcp.tool()` decorator. This function takes a `name` argument and returns a string greeting the user (`"Hello, {name}!"`).
    - This is a simple example of a tool that the server can use to respond to requests.

4. **Server Execution**:
    - The `mcp.run()` method is called to start the MCP server. It specifies `"streamable-http"` as the transport method, allowing for persistent connections to the server. This is useful for systems that require continuous interaction, like chatbots or other real-time applications.

### Workflow:
1. The `FastMCP` server is initialized with no tools but with a basic "hello" tool that can respond with a greeting.
2. The logging system captures any actions performed by the server.
3. The `hello` function is registered as a tool that can be invoked via the server.
4. The MCP server is started using streamable HTTP, making it ready to receive requests.

### Use Case:
This setup can be used for:
- Running a server that can handle tools defined with `@mcp.tool()`.
- Easily adding additional tools and functionality to the server by simply defining new functions and decorating them with `@mcp.tool()`.
- A simple test setup for experimenting with MCP servers using a basic tool like "hello".

### How It Works:
1. The server listens for requests on `localhost:8000`.
2. A client can call the `hello` function via the server, passing a `name` as a parameter to receive a greeting message.
3. The server logs all activity to `server.log` for debugging and monitoring purposes.

### Potential Expansion:
- You can expand the server to include more complex tools, handling various tasks like natural language processing, data transformations, or interactions with other services.
- Integration with external APIs or databases can be added to handle more advanced use cases.
"""

from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP with no tools registered
mcp = FastMCP("EmptyMCPServer", host="localhost", port=8000)

logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@mcp.tool()
def hello(name: str):
    """ a function that says hello"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Run MCP server using streamable HTTP transport
    mcp.run(transport="streamable-http")
