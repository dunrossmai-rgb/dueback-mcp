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

Prefer to run a local server over stdio? See
[Local (stdio) server](#local-stdio-server) below.

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

## Legal

- [Terms of Service](https://dueback.co/terms.html)
- [Privacy Policy](https://dueback.co/privacy.html)

Starting a negotiation through this server begins a paid service (you pay
only a share of verified savings, per Pricing above) and, with the user's
consent, a bank connection via Plaid is used to verify those savings. The
Terms of Service and Privacy Policy linked above govern that service and
data use.
