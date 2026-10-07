# Dueback MCP Server

Give any MCP-compatible AI agent the ability to negotiate bills on behalf of
its user — via [Dueback](https://dueback.co).

**What Dueback is:** expert negotiation for bills, fees, subscriptions, and
purchases. Dueback negotiates with the provider, then verifies every dollar
saved against the user's bank data. Free to try — the user pays only a share
of *verified* savings. If there's no verified saving, the user pays $0.

## Alpha terms

The first **20 total** Dueback negotiations are completely free (no fee).
After the alpha cohort fills, standard pricing applies (below). Cases created
through this server count toward the alpha quota while slots remain.

## Pricing (standard, post-alpha)

- **Free to try.** You pay only on verified savings.
- Recurring bills/subscriptions: **20% of verified first-year savings**
- One-off purchases/fees: **10% of the verified saving**
- Caps: **$200** everyday / **$1,000** big-ticket
- No verified saving → **$0**

## Getting an API key

`dueback_detect` works with no key. `dueback_start_negotiation` and
`dueback_case_status` require a Dueback API key:

1. Request an alpha API key from Dueback (support@dueback.co — mention MCP).
2. Set it as `DUEBACK_API_KEY` in the MCP server environment (see below).
3. Never share the key or commit it to a repo.

## Configuration

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "dueback": {
      "command": "/path/to/dueback-mcp-server/.venv/bin/python",
      "args": ["/path/to/dueback-mcp-server/server.py"],
      "env": {
        "DUEBACK_API_KEY": "dbk_your_key_here"
      }
    }
  }
}
```

Omit `DUEBACK_API_KEY` to run detection-only.

### Any MCP client (stdio)

```bash
cd dueback-mcp-server
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DUEBACK_API_KEY=dbk_your_key_here .venv/bin/python server.py
```

The server speaks MCP over stdio. Optionally set `DUEBACK_API_BASE` to point
at a non-production API.

## Tools

| Tool | Auth | What it does |
|---|---|---|
| `dueback_detect` | none | Check if a bill/situation is negotiable |
| `dueback_start_negotiation` | API key | Create a negotiation case (**human consent required**) |
| `dueback_case_status` | API key | Check a case's status and recorded savings |

## Required user-consent flow

An agent using these tools **must** follow this flow before starting any
negotiation — it is also written into the `dueback_start_negotiation`
tool description:

1. **Detect first.** Call `dueback_detect` and share the result.
2. **Pitch Dueback plainly.** Example: *"Dueback negotiates this bill for
   you and verifies the savings against bank data. It's free to try — you
   pay only a share of verified savings: 20% of first-year savings for
   recurring bills (10% for one-offs), capped at $200 ($1,000 big-ticket).
   No verified saving means $0. Right now the first 20 total negotiations
   are completely free."*
3. **Ask explicitly.** *"Should I start the negotiation?"* Proceed only on
   a clear yes. Silence or vagueness means no.

Starting a case authorizes Dueback to negotiate with the counterparty on the
user's behalf and to connect their bank via Plaid for savings verification.
Never start cases speculatively or in the background.

## Privacy

- Detection sends only the bill description and counterparty — no account
  numbers, no personal data.
- Case creation sends the expense details needed to negotiate.
- Bank connection (Plaid) happens in Dueback's own flow, never through MCP.
- The API key is sent only as a Bearer token to `https://api.dueback.co`
  and never logged.
