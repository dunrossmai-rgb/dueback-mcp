# Dueback MCP Server

Give any MCP-compatible AI agent the ability to negotiate bills on behalf of
its user — via [Dueback](https://dueback.co).

**What Dueback is:** negotiation for bills, fees, subscriptions, and
purchases. Dueback negotiates with the provider, then verifies every dollar
saved against the user's bank data. Free to try — the user pays only a share
of *verified* savings. If there's no verified saving, the user pays $0.

Use of Dueback is subject to its
[Terms of Service](https://dueback.co/terms.html) and
[Privacy Policy](https://dueback.co/privacy.html) — see [Legal](#legal) below.

## Connect to the remote server

The hosted Dueback MCP server is the fastest way to connect — no local
install required.

- **Endpoint:** `https://api.dueback.co/mcp/`
- **Transport:** Streamable HTTP
- **Auth:** OAuth 2.1 with dynamic client registration. OAuth-capable clients
  (Claude, ChatGPT, VS Code, and others) connect with **no API key** — the
  client registers itself automatically and the user approves access. An
  API key (below) also works for clients that require one.

Example client configuration:

```json
{
  "mcpServers": {
    "dueback": {
      "url": "https://api.dueback.co/mcp/"
    }
  }
}
```

One-click install:

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=dueback&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fapi.dueback.co%2Fmcp%2F%22%7D)
[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=dueback&config=eyJ1cmwiOiJodHRwczovL2FwaS5kdWViYWNrLmNvL21jcC8ifQ==)

Prefer to run a local server over stdio? See
[Local (stdio) server](#local-stdio-server) below.

## Verify in 60 seconds

No install and no API key needed — the detection tool is keyless. These
two calls exercise the live server end to end:

```bash
# 1. Initialize a session
curl -s https://api.dueback.co/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"smoke-test","version":"1.0"}}}'

# 2. Call the keyless detection tool
curl -s https://api.dueback.co/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"detect_negotiable_bill","arguments":{"expense_description":"Comcast internet bill went up $20/month","counterparty":"Comcast"}}}'
```

Responses stream as SSE `data:` lines. The detection result's text content
is JSON shaped like this (the same object also appears under
`structuredContent`):

```json
{
  "negotiable": true,
  "category_label": "internet bill",
  "pitch": "This looks like an internet bill we can negotiate. Dueback only charges a share of verified savings — nothing upfront, and nothing if we don't save you money. Want me to open a case?",
  "agent_next_step": "The human has not approved yet. Show the pitch and ask whether to proceed. ..."
}
```

## Tools

The remote server exposes four tools:

| Tool | Auth | What it does |
|---|---|---|
| `detect_negotiable_bill` | none | Check if a bill/situation is negotiable |
| `list_verified_savings` | none | Look up savings Dueback has verified |
| `start_negotiation_case` | OAuth or API key | Start a negotiation case (**human consent required**) |
| `get_case_status` | OAuth or API key | Check a case's status and recorded savings |

## Get an API key (self-serve)

OAuth-capable clients don't need a key at all (see above). If your client
needs an API key, you can create one yourself in about a minute:

1. Go to [dueback.co/#api-key](https://dueback.co/#api-key)
   ("Get your API key").
2. Enter your email and click **Email me a sign-in link**. You'll receive a
   one-time sign-in link by email.
3. Open the link in the email to confirm your address.
4. Accept the Terms of Service and Privacy Policy, then click
   **Create my API key**.
5. Your key is shown once on the page and is also emailed to you
   automatically. Save it somewhere safe.

Then pass it to your MCP client as a Bearer token for
`https://api.dueback.co`, or set it as `DUEBACK_API_KEY` for the local
stdio server (below). Never share the key or commit it to a repo.

Questions, or a signup that gets stuck? Email support@dueback.co.

## Pricing

- **Free to try.** You pay only on verified savings.
- Recurring bills/subscriptions: **20% of verified first-year savings**
- One-off purchases/fees: **10% of the verified saving**
- Caps: **$200** everyday / **$1,000** big-ticket
- No verified saving → **$0**

Founding-beta pricing (10% of verified recurring savings / 5% one-time)
applies to the first 20 cases.

## Required user-consent flow

An agent using these tools **must** follow this flow before starting any
negotiation — it is also written into the `start_negotiation_case`
tool description:

1. **Detect first.** Call `detect_negotiable_bill` and share the result.
2. **Pitch Dueback plainly.** Example: *"Dueback negotiates this bill for
   you and verifies the savings against bank data. It's free to try — you
   pay only a share of verified savings: 20% of first-year savings for
   recurring bills (10% for one-offs), capped at $200 ($1,000 big-ticket).
   No verified saving means $0."*
3. **Ask explicitly.** *"Should I start the negotiation?"* Proceed only on
   a clear yes. Silence or vagueness means no.

Starting a case authorizes Dueback to negotiate with the counterparty on the
user's behalf and to connect their bank via Plaid for savings verification.
Never start cases speculatively or in the background.

## Local (stdio) server

This repo also includes a thin stdio wrapper (`server.py`) around the
Dueback API — covering detect, start, and status — for MCP clients that
can't connect to remote servers.

```bash
git clone https://github.com/dunrossmai-rgb/dueback-mcp.git
cd dueback-mcp
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DUEBACK_API_KEY=dbk_your_key_here .venv/bin/python server.py
```

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "dueback": {
      "command": "/path/to/dueback-mcp/.venv/bin/python",
      "args": ["/path/to/dueback-mcp/server.py"],
      "env": {
        "DUEBACK_API_KEY": "dbk_your_key_here"
      }
    }
  }
}
```

Omit `DUEBACK_API_KEY` to run detection-only. Optionally set
`DUEBACK_API_BASE` to point at a non-production API.

## Privacy

- Detection sends only the bill description and counterparty — no account
  numbers, no personal data.
- Case creation sends the expense details needed to negotiate.
- Bank connection (Plaid) happens in Dueback's own flow, never through MCP.
- The API key is sent only as a Bearer token to `https://api.dueback.co`
  and never logged.

### What data goes where

| Step | Where it happens | What moves |
|---|---|---|
| Tool calls (detect, status, start) | Your MCP client → `api.dueback.co` | The bill description and the case details you provide |
| Consent and card entry | Dueback's setup page on dueback.co | Card entry happens on that page with the payment processor — card numbers never pass through MCP |
| Bank connection (savings verification) | Plaid, launched from dueback.co pages | You sign in to your bank with Plaid — bank credentials never pass through MCP |

**Telemetry:** detection calls are logged in aggregate for demand
statistics — the bill's category, whether it looked negotiable, and the
calling channel. Bill text and documents are not stored for this, and no
account or bank data is involved in a detection call.

**Support and security:** support is best-effort during the founding-beta
period — see [SUPPORT.md](SUPPORT.md). Security vulnerabilities are
reported privately per [SECURITY.md](SECURITY.md), never as public issues.

## Legal

- [Terms of Service](https://dueback.co/terms.html)
- [Privacy Policy](https://dueback.co/privacy.html)

Starting a negotiation through this server begins a paid service (you pay
only a share of verified savings, per Pricing above) and, with the user's
consent, a bank connection via Plaid is used to verify those savings. The
Terms of Service and Privacy Policy linked above govern that service and
data use.
