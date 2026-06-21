FROM python:3.11-slim

# tgcrypto needs a C compiler to build
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The bot is a long-running process (pyrogram idle()); Docker's restart policy
# replaces the old start.py tmux supervisor. All data goes to the
# medical_website API over HTTPS — no database runs in this container.
CMD ["python", "bot.py"]
