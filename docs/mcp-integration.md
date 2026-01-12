# MCP Integration

Aetheris v3.0 supports the Model Context Protocol (MCP) for extending capabilities through external servers.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that allows AI applications to connect to external tools and resources through standardized servers. Aetheris can connect to MCP servers to gain access to additional tools.

## Configuration

Configure MCP servers in your `config.json`:

```json
{
  "mcp": {
    "enabled": true,
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"],
        "env": {}
      },
      {
        "name": "github",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        }
      }
    ],
    "connection_timeout": 2.0,
    "override_builtins": false
  }
}
```

## Server Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Unique identifier for the server |
| `command` | string | Command to start the server |
| `args` | array | Command line arguments |
| `env` | object | Environment variables |

## Environment Variable Expansion

Use `${VAR_NAME}` to reference environment variables:

```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}"
  }
}
```

The variable is read from your shell environment or `.env` file.

## Tool Discovery

When Aetheris connects to an MCP server, it automatically discovers available tools:

```
aetheris[gemini]> /mcp status
MCP Servers:
  ✅ filesystem (3 tools, 0 resources)
  ✅ github (5 tools, 0 resources)
```

## Using MCP Tools

MCP tools are automatically available to the AI. They appear with a `mcp:` prefix:

```
Available tools:
  - read_file (built-in)
  - mcp:filesystem:read_directory
  - mcp:github:create_issue
```

The AI can invoke them like any other skill:

```
aetheris[gemini]> Create a GitHub issue for the bug we found
```

## Conflict Resolution

When an MCP tool has the same name as a built-in skill:

- **Default**: Built-in skills take priority
- **Override**: Set `"override_builtins": true` to prefer MCP tools

```json
{
  "mcp": {
    "override_builtins": true
  }
}
```

## Connection Handling

### Automatic Reconnection

If connection to an MCP server is lost, Aetheris will:
1. Log a warning
2. Continue operating without that server
3. Attempt to reconnect on next request

### Connection Timeout

Default connection timeout is 2 seconds. Increase for slow servers:

```json
{
  "mcp": {
    "connection_timeout": 5.0
  }
}
```

## Popular MCP Servers

### Filesystem Server

Access files outside the sandbox:

```json
{
  "name": "filesystem",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
}
```

### GitHub Server

Interact with GitHub repositories:

```json
{
  "name": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

### Slack Server

Post to Slack channels:

```json
{
  "name": "slack",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_TOKEN": "${SLACK_TOKEN}"
  }
}
```

### PostgreSQL Server

Query databases:

```json
{
  "name": "postgres",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres"],
  "env": {
    "DATABASE_URL": "${DATABASE_URL}"
  }
}
```

## Resources

MCP servers can also expose resources (read-only data):

```
aetheris[gemini]> /mcp resources
Resources:
  - file:///project/README.md (text/markdown)
  - github://repo/owner/name (application/json)
```

Resources can be read by the AI for context.

## Troubleshooting

### Server Won't Start

1. Check the command is installed:
   ```bash
   npx -y @modelcontextprotocol/server-filesystem --help
   ```

2. Check environment variables are set:
   ```bash
   echo $GITHUB_TOKEN
   ```

3. Check logs for errors:
   ```
   aetheris[gemini]> /mcp logs filesystem
   ```

### Tools Not Discovered

1. Verify server is connected:
   ```
   aetheris[gemini]> /mcp status
   ```

2. Check server capabilities:
   ```
   aetheris[gemini]> /mcp info filesystem
   ```

### Connection Timeout

Increase timeout in config:

```json
{
  "mcp": {
    "connection_timeout": 10.0
  }
}
```

### Permission Errors

MCP servers may require specific permissions. Check the server's documentation.

## Security Considerations

### Trust MCP Servers

Only use MCP servers you trust. They can execute arbitrary code.

### Limit Server Access

Configure servers with minimal permissions:

```json
{
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/specific/dir"]
}
```

### Audit Tool Calls

Enable audit logging to track MCP tool invocations:

```json
{
  "safety": {
    "audit_log_path": "aetheris-audit.jsonl"
  }
}
```

## Disabling MCP

To run without MCP:

```json
{
  "mcp": {
    "enabled": false
  }
}
```

Or start Aetheris with:

```bash
aetheris --cli --no-mcp
```
