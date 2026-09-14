# Neppy

Nep's Personal Assistant - just-in-time creation, execution, and monitoring of custom agentic workflows.

I use this to automatically respond to emails, track to-dos, etc.

Inspired by [Handmade Cities](https://handmadecities.com/)

# Requirements

1. install uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

# Quickstart

1. Create and Download Google Client Credentials with Full Gmail Access
2. Run `uv sync`

## Secrets

- `GOOGLE_SECRET_PATH` - path to `./google-secret.json`
- `GOOGLE_TOKEN_PATH` - local