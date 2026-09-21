# MCP servers for DeepAgent (draft)

Model Context Protocol servers extend the agent with external context
(docs, filesystem, web). Configure them in `mcp_config.json`.

## Config format

Standard MCP-client format:

```json
{
  "mcpServers": {
    "docs-langchain": {"url": "https://docs.langchain.com/mcp"},
    "tavily-search": {"command": "npx", "args": ["-y", "tavily-mcp@latest"], "env": {"TAVILY_API_KEY": "..."}}
  }
}
```

## Local docs server

`servers/docs_server.py` is a minimal stub showing where a custom
DeepSeek/docs MCP server would live. Swap it for a real server
(`langchain-mcp-adapters` compatible) as the project matures.
