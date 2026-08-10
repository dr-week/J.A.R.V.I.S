# Security & Authentication

This document outlines the security architecture and authentication mechanisms for the Jarvis assistant.

## Device Pairing

To ensure that only authorized devices can communicate with the brain, we use a pairing mechanism based on a shared secret.

### Flow

1. **Setup**: The brain is configured with a `JARVIS_PAIRING_SECRET` environment variable (default: `change-me`, though a warning will be emitted if the default is used in production).
2. **Pairing**: A client (Windows, Android, etc.) prompts the user to enter the pairing code/secret.
3. **Exchange**: The client sends a `POST /pair` request to the brain with the `pairing_secret` and a unique `device_id`.
4. **Token Issuance**: The brain validates the secret. If valid, it generates an opaque 32-byte URL-safe `device_token`, stores it in the `devices` SQLite table (persisted across restarts), and returns it to the client.
5. **Authentication**: All subsequent requests from the client must include the token:
   - For REST endpoints: In the `Authorization: Bearer <token>` header.
   - For WebSockets: As a query parameter `?token=<token>` or as the first message payload, depending on the client library.

### Storage & Revocation

- Tokens are stored locally in the brain's `brain.db` SQLite database in the `devices` table.
- Using a database-backed token allows instant revocation (by deleting the row) compared to stateless JWTs.
- Tokens expire by default after a long period (e.g., 365 days) but can be revoked earlier if a device is lost.

## Secrets Management

- **NEVER commit secrets to the repository**. All secrets must reside in the local `.env` file.
- The `JARVIS_PAIRING_SECRET` is used *only* for the initial exchange and should never be cached long-term by the client. Only the `device_token` should be stored securely on the client.
- LLM provider API keys (e.g., `GEMINI_API_KEY`) are kept exclusively on the brain and are never sent to clients.
- Connector credentials (for example `JARVIS_GITHUB_TOKEN`) also remain exclusively in the brain host's `.env`. Tools must never accept, log, return, or sync these credentials to clients.

## Auditing

- High-risk tool calls (e.g., deleting files, sending messages) require explicit confirmation and are logged to the `action_log` table along with the `device_id` that initiated or confirmed them.

## Wake word privacy notes

Hands-free summon is **opt-in only** and disabled by default. Enabling it has
privacy implications you should know about:

- **Mic is active while the wake loop runs.** Once a wake-word session starts
  (e.g. `python clients/windows/client.py --wake-word jarvis`), the client
  continuously captures from the microphone so it can hear the wake phrase.
  This is never on unless the user explicitly starts that mode.
- **No always-on room mics without consent.** Refer to `docs/SCOPE.md` — the
  same opt-in rule applies here as it does to audio capture generally.
- **Transient transcription, no retention.** Detected phrases are only used to
  check for the wake word / feed the spoken turn to the brain; audio is not
  recorded or stored on the client beyond the passing transcription.
- **Cloud vs local STT.** The default recognizer for a spoken turn is
  Google's free network recognizer (which sends audio to Google for
  transcription). If you prefer to keep audio fully local, configure the
  recognizer to use offline Sphinx (`pocketsphinx`) instead. Set
  `JARVIS_WAKE_ENABLED`, `JARVIS_WAKE_WORD`, or pass `--wake-word` to control
  when this mode activates.
