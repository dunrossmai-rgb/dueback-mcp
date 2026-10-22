# Security Policy

## Supported versions

Security fixes are applied to the latest release of this repository and to
the hosted Dueback MCP server at `https://api.dueback.co/mcp/`.

| Version | Supported |
|---|---|
| 0.1.x (latest release) | Yes |
| Older versions | No — please upgrade |

## Reporting a vulnerability

Please report security issues **privately** — never in a public GitHub
issue, discussion, or pull request.

- Preferred: GitHub's private vulnerability reporting —
  [Report a vulnerability](https://github.com/dunrossmai-rgb/dueback-mcp/security/advisories/new)
- Or email: support@dueback.co with "Security" in the subject line

Please include the affected component (this wrapper, the hosted server, or
the Dueback website), what you found, and steps to reproduce if you have
them. Do not include real API keys, bank details, or other people's data in
a report.

Our goals — not an SLA: we aim to acknowledge reports within 2 business
days and to triage them within 5 business days. Verified vulnerabilities
are fixed as quickly as their severity warrants.

## Scope notes

- Card numbers and bank credentials **never pass through this MCP server**
  or the hosted MCP endpoint. Card entry and consent happen only on
  Dueback's own setup page, and the bank connection happens only through
  Plaid on Dueback's pages.
- API keys are bearer credentials: treat them like passwords, keep them in
  your MCP client's secret storage or environment, and never commit them
  to a repository. If a key may have leaked, email support@dueback.co so it
  can be revoked.
- Vulnerabilities in third-party MCP clients themselves are out of scope
  for this policy; please report those to the client's vendor.
