# Contributing

Thanks for helping improve the Dueback MCP integration.

## Scope of this repository

This repository contains the **local stdio wrapper** (`server.py`) and the
documentation for connecting to Dueback. The production MCP server is
hosted by Dueback and is not open source, so contributions here are
limited to:

- The stdio wrapper code
- Documentation, examples, and install instructions
- Repository metadata (`server.json`) and community files

Behavioral issues in the hosted tools themselves are still welcome as bug
reports — they just get fixed on the server side.

## Development setup

```bash
git clone https://github.com/dunrossmai-rgb/dueback-mcp.git
cd dueback-mcp
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Run the wrapper locally (detection works without a key):

```bash
.venv/bin/python server.py
```

## Before opening a pull request

- Run the import smoke check: `python -c "import server"` (in the venv).
- If you touched `server.json`, validate it with
  [mcp-publisher](https://github.com/modelcontextprotocol/registry):
  `mcp-publisher validate ./server.json`.
- If you touched the README, try the
  [60-second smoke test](README.md#verify-in-60-seconds) against the live
  server.
- Update the docs and `CHANGELOG.md` when behavior or instructions change.

## Ground rules

- **No secrets, ever** — no API keys, tokens, real bills, or bank details
  in code, issues, or pull requests. Use placeholders like
  `dbk_your_key_here`.
- Keep user-facing copy factual: describe what the tools do and what they
  cost, without promotional claims.
- Security vulnerabilities are reported privately per
  [SECURITY.md](SECURITY.md), never as public issues or PRs.
