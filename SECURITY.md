# Security Policy

## Supported Versions

We actively maintain and provide security updates for the current major branch of J.A.R.V.I.S.:

| Version | Supported          |
| ------- | ------------------ |
| `master` (v1.x) | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

The security of your personal AI operator and local hardware is a top priority. If you believe you have discovered a security vulnerability in J.A.R.V.I.S., please report it responsibly:

1. **Do NOT open a public GitHub issue** for undisclosed security vulnerabilities.
2. Email your findings directly to **security@dr-week.dev** or submit a private vulnerability report via GitHub Security Advisories.
3. Please include:
   - Type of vulnerability (e.g. prompt injection, unauthorized tool execution, privilege escalation, token leak).
   - Step-by-step reproduction instructions or proof-of-concept.
   - Potential impact and suggested mitigation if known.

### Response Timeline
- We will acknowledge receipt of your vulnerability report within **48 hours**.
- We will provide status updates at least every **7 days** until the issue is patched.
- Once fixed, a security advisory and release credit will be published.

---

## Local Security Best Practices

When running J.A.R.V.I.S. locally:
- Never expose the Brain server (`port 8787`) to the public internet without a reverse proxy, SSL/TLS, and strong pairing secret.
- Keep `JARVIS_PAIRING_SECRET` set to a strong random passphrase in `.env`.
- Store third-party credentials (GitHub, Slack, Notion, Linear tokens) solely in `.env` with strict file permissions (`chmod 600 .env`).
