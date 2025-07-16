# Project Repository

This is the initial README file for the project.

## Email (SMTP) Integration Setup

To enable reminders via Email, set the following environment variables (in `.env` or your server environment):

- `SMTP_HOST`: SMTP server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (e.g., 587)
- `SMTP_USER`: SMTP login username (usually the sender's email)
- `SMTP_PASS`: SMTP login password or app password
- `SMTP_FROM`: (Optional) From address for sent emails (defaults to SMTP_USER)

If these are not defined or invalid, email reminder attempts will fail with a 500 error.

## WhatsApp Integration

WhatsApp reminder integration is currently a stub only. Extend `send_whatsapp_reminder` in `src/api/integrations.py` for production/3rd party integration.
