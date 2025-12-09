## MCP Template

Minimal Model Context Protocol sample with a tiny server exposing a single `hello` tool and a client that lists tools and calls `hello`.

### Files
- `server.py` — FastMCP server on `localhost:8000` with a `hello(name)` tool and basic logging to `server.log`.
- `client.py` — Async client that connects via streamable HTTP, lists tools, and invokes `hello` (logs to `client.log`).

### Quick start
1) Install deps:
```bash
pip install mcp
```
2) Run the server:
```bash
python server.py
```
3) In another shell, run the client:
```bash
python client.py
```

### Notes
- Server listens on `http://localhost:8000/mcp` using streamable HTTP transport.
- Extend by adding more `@mcp.tool()` functions in `server.py`; the client will list them automatically.

