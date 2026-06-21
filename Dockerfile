FROM python:3.11-slim

# tgcrypto needs a C compiler to build
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# flush stdout/stderr so logs (incl. FloodWait wait messages) show up live
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pyrogram writes its login session here. Mount a PERSISTENT disk on this path
# so a restart/redeploy reuses the session instead of re-authorizing — repeated
# auth.ImportBotAuthorization calls are exactly what triggers Telegram FloodWait.
ENV SESSION_DIR=/app/session
RUN mkdir -p /app/session
VOLUME ["/app/session"]

# The bot is a long-running process (pyrogram idle()); Docker's restart policy
# replaces the old start.py tmux supervisor. All data goes to the
# medical_website API over HTTPS — no database runs in this container.
CMD ["python", "bot.py"]
