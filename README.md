# NEX Telegram Bot

Routes Telegram messages to NEX Agent Co.'s 25 x402 paid services — for free, powered by local Ollama models.

## Setup (1 minute)

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Run `/newbot`, follow prompts, copy the token
3. Set the token:
   ```bash
   export NEX_BOT_TOKEN="<paste your token here>"
   ```
4. Install dependencies:
   ```bash
   pip install python-telegram-bot
   ```
5. Run:
   ```bash
   python3 bot.py
   ```

## Commands

| Command | Example | What it does |
|---------|---------|--------------|
| `/start` | — | Show help |
| `/chat <msg>` | `/chat What is x402?` | Chat with NEX (30B model) |
| `/code <task>` | `/code Python fibonacci` | Code generation |
| `/check <url>` | `/check http://g00gle.tk/login` | Phishing URL check |
| `/audit <addr>` | `/audit 0xd8dA6BF...` | Full wallet security audit |
| `/contract <addr>` | `/contract 0x833589fC...` | Smart contract risk grade |
| `/ens <name>` | `/ens vitalik.eth` | ENS → address |
| `/hacks [chain]` | `/hacks base` | Recent crypto exploits |
| `/pay` | — | How to use paid x402 endpoints |
| (plain text) | `What is x402?` | Defaults to chat |

## Architecture

- Single-process Python bot using `python-telegram-bot` library
- Polls Telegram API (no webhook needed)
- Routes commands to NEX x402 free mirror endpoints (no payment required)
- Free tier: NEX absorbs the cost (uses `/v1/free/*` mirrors)
- Paid tier path: users can use `/pay` to learn how to call paid endpoints directly

## Why this is valuable

1. **Discovery surface**: Anyone on Telegram can use NEX services. No wallet, no x402 client, no signup.
2. **Brand presence**: The bot username becomes a permanent touchpoint.
3. **Funnel to paid**: Once users see value in free mode, the `/pay` command teaches them how to integrate paid.
4. **Viral**: Telegram users share useful bots. Word of mouth scales.
5. **Zero ongoing cost**: NEX absorbs the inference cost (free mirrors = $0 per call).

## Environment variables

| Var | Required | Default | Description |
|-----|----------|---------|-------------|
| `NEX_BOT_TOKEN` | yes | — | Token from @BotFather |
| `NEX_X402_BASE` | no | `https://charm-preparing-avon-ips.trycloudflare.com` | NEX x402 server base URL |

## Files

- `bot.py` — main bot code (12K, all 9 command handlers + default text handler)
- `README.md` — this file
- `LICENSE` — MIT
- `requirements.txt` — single dep: python-telegram-bot

## Deployment

### Option 1: Local (current)
```bash
python3 bot.py
```

### Option 2: launchd (persistent on macOS)
Create `~/Library/LaunchAgents/com.nex.agents-co.telegram-bot.plist` and load with launchctl.

### Option 3: Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install python-telegram-bot
CMD ["python3", "bot.py"]
```

## License

MIT
