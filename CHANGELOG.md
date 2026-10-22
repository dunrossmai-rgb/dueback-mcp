# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-10-21

### Added

- "Connect to the remote server" guide with one-click install options for
  VS Code and Cursor, plus a "Verify in 60 seconds" smoke test that uses
  the keyless detection tool.
- Self-serve API key instructions — keys are created at dueback.co and
  delivered automatically; they no longer need to be requested by email.
- A "What data goes where" overview covering the setup page, the Plaid
  bank connection, and detection telemetry.
- `SECURITY.md` (with private vulnerability reporting), `SUPPORT.md`,
  `CONTRIBUTING.md`, issue and pull-request templates, Dependabot, and CI.
- Apache License 2.0.
- Server icon in the MCP Registry listing.

### Changed

- Repository and documentation renamed consistently to `dueback-mcp`.
- Terms of Service and Privacy Policy are linked from the README,
  including a Legal section covering the paid negotiation and the bank
  connection used to verify savings.
- The stdio wrapper's copy now matches the documentation: self-serve key
  instructions and no promotional language in tool text.

### Removed

- The LAUNCH20 promo code and alpha-quota messaging from the
  documentation. Founding-beta pricing is stated once, factually, in the
  Pricing section.

## [0.1.0] - 2026-10-20

### Added

- Initial public release: stdio wrapper for the Dueback API and the
  official MCP Registry listing for the hosted remote server
  (`https://api.dueback.co/mcp/`).
