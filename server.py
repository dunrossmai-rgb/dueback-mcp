"""Dueback MCP server — outcome-based bill negotiation for AI agents.

Exposes the Dueback API (https://api.dueback.co) as MCP tools so any
MCP-compatible agent can detect negotiable bills, start negotiations
(with the human's explicit consent), and check case status.

Configuration (environment):
  DUEBACK_API_KEY   API key for authenticated tools (start_negotiation,
                    case_status). Create one self-serve at
                    https://dueback.co/#api-key.
  DUEBACK_API_BASE  Override the API base URL (default: https://api.dueback.co).

Run with stdio transport:
  python server.py
"""
from __future__ import annotations

import json
import logging
import os

import httpx
from mcp.server.mcpserver import MCPServer

log = logging.getLogger("dueback-mcp")

API_BASE = os.environ.get("DUEBACK_API_BASE", "https://api.dueback.co").rstrip("/")
CONSENT_VERSION = "v1.0-beta"
CHANNEL_HEADER = {"X-Dueback-Channel": "mcp"}

server = MCPServer(
    name="dueback",
    title="Dueback Bill Negotiation",
    description=(
        "Dueback negotiates bills, fees, subscriptions, and purchases on "
        "behalf of the user — and verifies every dollar saved against bank "
        "data. Free to try; the user pays only a share of verified savings."
    ),
    instructions=(
        "Use dueback_detect to check whether a bill or purchase situation is "
        "negotiable before proposing Dueback to the user. Only call "
        "dueback_start_negotiation after the human has explicitly agreed, "
        "with pricing disclosed (see that tool's description). Use "
        "dueback_case_status to report progress on an open case."
    ),
    version="0.1.1",
)


def _api_key() -> str | None:
    return os.environ.get("DUEBACK_API_KEY", "").strip() or None


def _auth_headers() -> dict[str, str]:
    key = _api_key()
    if not key:
        raise RuntimeError(
            "DUEBACK_API_KEY is not set. This tool needs a Dueback API key — "
            "create one self-serve at https://dueback.co/#api-key, set it in "
            "the MCP server environment, and try again."
        )
    return {"Authorization": f"Bearer {key}", **CHANNEL_HEADER}


def _post(path: str, body: dict, headers: dict) -> dict:
    try:
        r = httpx.post(
            f"{API_BASE}{path}", json=body, headers=headers, timeout=60.0
        )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Dueback API unreachable: {exc}") from exc
    if r.status_code >= 400:
        detail = r.text[:500]
        try:
            detail = r.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"Dueback API error {r.status_code}: {detail}")
    return r.json()


def _get(path: str, headers: dict) -> dict:
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=headers, timeout=60.0)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Dueback API unreachable: {exc}") from exc
    if r.status_code == 404:
        raise RuntimeError(f"Case not found: {path}")
    if r.status_code >= 400:
        raise RuntimeError(f"Dueback API error {r.status_code}: {r.text[:500]}")
    return r.json()


@server.tool()
async def dueback_detect(description: str, counterparty: str = "") -> str:
    """Check whether a bill, fee, subscription, or purchase situation is
    negotiable by Dueback.

    Call this BEFORE proposing Dueback to the user — it tells you if the
    situation is worth their time. No API key needed.

    Args:
        description: What the expense is, e.g. "Comcast internet bill went
            up $20/month" or "$4,500 roof replacement quote".
        counterparty: Who charges it, e.g. "Comcast", "State Farm".
            May be empty if unknown.

    Returns a plain-language assessment: negotiable or not, the likely
    savings category, and suggested next step.
    """
    data = _post(
        "/v1/detect",
        {"description": description, "counterparty": counterparty},
        CHANNEL_HEADER,
    )
    lines = []
    negotiable = data.get("negotiable")
    if negotiable is True:
        lines.append("Negotiable: yes")
    elif negotiable is False:
        lines.append("Negotiable: no")
    for key in ("category", "category_label", "confidence", "rationale",
                "estimated_savings_cents", "suggested_next_step", "message"):
        if data.get(key) not in (None, ""):
            val = data[key]
            if key == "estimated_savings_cents":
                val = f"${int(val) / 100:,.2f}"
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {val}")
    if not lines:
        lines.append(json.dumps(data, indent=2)[:1500])
    return "\n".join(lines)


@server.tool()
async def dueback_start_negotiation(
    expense_description: str,
    counterparty: str,
    amount_cents: int,
    billing_period: str,
) -> str:
    """Start a Dueback bill negotiation case.

    HUMAN CONSENT IS REQUIRED BEFORE CALLING THIS TOOL. The exact flow:
    1. Call dueback_detect first and share the result with the human.
    2. Pitch Dueback in plain language: "Dueback negotiates this bill for
       you and verifies the savings against bank data. It's free to try —
       you pay only a share of verified savings: 20% of first-year savings
       for recurring bills (10% for one-offs), capped at $200 ($1,000 for
       big-ticket items). If there's no verified saving, you pay $0."
    3. Ask explicitly: "Should I start the negotiation?" Proceed ONLY on a
       clear yes. A vague or missing answer means DO NOT CALL.

    Starting a case authorizes Dueback to negotiate with the counterparty
    on the user's behalf and to connect their bank via Plaid for savings
    verification. Never call this speculatively or in the background.

    Args:
        expense_description: What the expense is,
            e.g. "Comcast internet bill".
        counterparty: Who charges it, e.g. "Comcast".
        amount_cents: Amount in CENTS (e.g. $85.50/month -> 8550).
        billing_period: "monthly", "annual", or "one_off".

    Returns the created case ID and its initial status. Requires
    DUEBACK_API_KEY in the server environment.
    """
    if billing_period not in ("monthly", "annual", "one_off"):
        raise ValueError(
            f"billing_period must be monthly, annual, or one_off "
            f"(got {billing_period!r})"
        )
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    data = _post(
        "/v1/cases",
        {
            "expense_description": expense_description,
            "counterparty": counterparty,
            "amount_cents": int(amount_cents),
            "billing_period": billing_period,
            "consent_version": CONSENT_VERSION,
        },
        _auth_headers(),
    )
    case_id = data.get("id", "?")
    status = data.get("status", "?")
    fee_waived = data.get("is_alpha")
    lines = [
        f"Negotiation started. Case ID: {case_id}",
        f"Status: {status}",
    ]
    if fee_waived:
        lines.append(
            "A fee waiver applies to this case."
        )
    lines.append(
        "Dueback will negotiate with the counterparty and verify savings "
        "against bank data. Use dueback_case_status with the case ID to "
        "check progress."
    )
    return "\n".join(lines)


@server.tool()
async def dueback_case_status(case_id: str) -> str:
    """Check the status of a Dueback negotiation case.

    Args:
        case_id: The case ID returned by dueback_start_negotiation.

    Returns the case status (e.g. strategy_loop, verifying, closed),
    the counterparty, and any recorded savings/fee. Requires
    DUEBACK_API_KEY in the server environment.
    """
    data = _get(f"/v1/cases/{case_id}", _auth_headers())
    lines = [f"Case: {data.get('id', case_id)}"]
    for key in ("status", "counterparty", "expense_description",
                "verified_savings_cents", "fee_cents", "fail_reason"):
        val = data.get(key)
        if val not in (None, ""):
            if key in ("verified_savings_cents", "fee_cents") and isinstance(val, (int, float)):
                val = f"${val / 100:,.2f}"
            lines.append(f"{key.replace('_', ' ').title()}: {val}")
    return "\n".join(lines)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
