"""
NEX Telegram Bot — routes Telegram messages to NEX Agent Co. x402 services.

Built by NEX Agent Co. · 2026-09-02
Free tier: NEX absorbs the cost via /v1/free/ endpoints
Paid tier: user pays x402 USDC directly

Setup:
  1. Talk to @BotFather on Telegram, get a bot token
  2. export NEX_BOT_TOKEN=<token from BotFather>
  3. export NEX_X402_BASE=https://charm-preparing-avon-ips.trycloudflare.com
  4. python3 bot.py

Usage in Telegram:
  /start        — show help
  /chat <msg>   — chat with NEX (nemotron-3.5 30B)
  /code <task>  — code generation (qwen3-coder 30B)
  /check <url>  — phishing URL check
  /audit <addr> — full wallet security audit
  /contract <addr> — smart contract risk grade
  /ens <name>   — ENS resolution
  /hacks [chain] — recent crypto exploits
  <plain text>  — defaults to chat with NEX
"""
import os
import json
import logging
import urllib.request
import urllib.parse
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Config
NEX_BOT_TOKEN = os.environ.get("NEX_BOT_TOKEN")
if not NEX_BOT_TOKEN:
    raise SystemExit("Set NEX_BOT_TOKEN env var (get one from @BotFather)")

NEX_X402_BASE = os.environ.get("NEX_X402_BASE", "https://charm-preparing-avon-ips.trycloudflare.com")
NEX_WALLET = "0x28F3D3fb24D4926BF5C35296c822d2a43D181177"
NEX_COMPANY = "NEX Agent Co."

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
log = logging.getLogger("nex-bot")

# ---------- NEX x402 call helper ----------
async def call_nex(path, params):
    url = f"{NEX_X402_BASE}{path}"
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    full_url = f"{url}?{qs}" if qs else url
    req = urllib.request.Request(full_url, method="POST")
    req.add_header("User-Agent", "NEX-Telegram-Bot/1.0")
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
        return json.loads(response.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

# ---------- Command handlers ----------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"👋 *{NEX_COMPANY} Telegram Bot*\n\n"
        "I route your messages to NEX's 25 x402 paid services — for free, "
        "powered by local Ollama models (30B-class) on Apple M5 Max 128GB.\n\n"
        "*Commands:*\n"
        "• `/chat <msg>` — chat with NEX (nemotron-3.5 30B, 1M context)\n"
        "• `/code <task>` — code generation (qwen3-coder 30B, 70% SWE-bench)\n"
        "• `/check <url>` — phishing URL check (14 rules)\n"
        "• `/audit <addr>` — full wallet security audit\n"
        "• `/contract <addr>` — smart contract risk grade\n"
        "• `/ens <name>` — ENS name → address\n"
        "• `/hacks [chain]` — recent crypto exploits (default 10)\n"
        "• `/pay` — how to use NEX x402 paid endpoints\n"
        "• Just send a message — defaults to chat\n\n"
        f"_All endpoints also at: {NEX_X402_BASE}_\n"
        f"_Bazaar (28K x402 services): https://nexaitechau.github.io/x402bazaar.com/_\n"
        f"_Playground: https://nexaitechau.github.io/nex-playground/_"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /chat <message>")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text("Thinking... (nemotron-3.5 30B, 2-5s)")
    r = await call_nex("/v1/free/chat", {"prompt": prompt})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    reply = r.get("message", {}).get("content") or r.get("reply") or json.dumps(r, indent=2)
    # Telegram has 4096 char limit; truncate if needed
    if len(reply) > 4000:
        reply = reply[:4000] + "\n\n[truncated — see full response at NEX Playground]"
    await update.message.reply_text(reply)

async def cmd_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /code <task description>")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text("Generating code... (qwen3-coder 30B)")
    r = await call_nex("/v1/free/code", {"prompt": prompt})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    reply = r.get("message", {}).get("content") or r.get("reply") or json.dumps(r, indent=2)
    if len(reply) > 4000:
        reply = reply[:4000] + "\n\n[truncated]"
    await update.message.reply_text(f"```\n{reply}\n```", parse_mode="Markdown")

async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /check <url>")
        return
    url = " ".join(context.args)
    r = await call_nex("/v1/free/phishing-check", {"url": url})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    score = r.get("risk_score", "?")
    flags = r.get("flag_count", "?")
    rec = r.get("recommendation", "")
    msg = (
        f"🔒 *Phishing Check*\n"
        f"URL: `{url}`\n"
        f"Risk score: *{score}/100* · {flags} flag(s)\n"
        f"Recommendation: {rec}\n\n"
    )
    flag_list = r.get("flags", [])
    if flag_list:
        msg += "*Flags:*\n"
        for f in flag_list[:5]:
            msg += f"• [{f.get('severity', '?')}] {f.get('code', '?')}: {f.get('detail', '')}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /audit <0x...>\nOr: /audit <0x...> <chain>")
        return
    address = context.args[0]
    chain = context.args[1] if len(context.args) > 1 else "base"
    await update.message.reply_text(f"Auditing {address[:10]}...{address[-6:]} on {chain}...")
    r = await call_nex("/v1/free/wallet-audit", {"address": address, "chain": chain})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    grade = r.get("grade", "?")
    score = r.get("audit_score", "?")
    summary = r.get("summary", "")
    notes = r.get("notes", [])
    msg = (
        f"👛 *Wallet Security Audit*\n"
        f"Address: `{address[:10]}...{address[-6:]}`\n"
        f"Chain: {chain}\n"
        f"Grade: *{grade}* ({score}/100)\n"
        f"{summary}\n\n"
    )
    if notes:
        msg += "*Notes:*\n"
        for n in notes[:5]:
            msg += f"• {n}\n"
    comp = r.get("components", {})
    if comp.get("address_label", {}).get("label"):
        msg += f"\n*Label:* {comp['address_label']['label']} (risk: {comp['address_label'].get('risk', '?')})"
    if comp.get("ens_reverse", {}).get("name"):
        msg += f"\n*ENS:* {comp['ens_reverse']['name']}"
    if comp.get("approvals", {}).get("total_approvals") is not None:
        a = comp["approvals"]
        msg += f"\n*Approvals:* {a['total_approvals']} total, {a.get('unlimited_approvals', 0)} unlimited"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_contract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /contract <0x...> [chain]")
        return
    address = context.args[0]
    chain = context.args[1] if len(context.args) > 1 else "base"
    r = await call_nex("/v1/free/contract-risk", {"address": address, "chain": chain})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    grade = r.get("grade", "?")
    score = r.get("risk_score", "?")
    factors = r.get("factors", [])
    msg = (
        f"📜 *Contract Risk*\n"
        f"Address: `{address[:10]}...{address[-6:]}`\n"
        f"Chain: {chain}\n"
        f"Grade: *{grade}* ({score}/100)\n\n"
    )
    if factors:
        msg += "*Factors:*\n"
        for f in factors[:6]:
            msg += f"• [{f.get('severity', '?')}] {f.get('code', '?')}: {f.get('detail', '')[:100]}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_ens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ens <name>")
        return
    name = " ".join(context.args)
    r = await call_nex("/v1/free/ens-lookup", {"name": name})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    if r.get("address"):
        msg = (
            f"🌐 *ENS Resolution*\n"
            f"Name: `{name}`\n"
            f"Address: `{r['address']}`\n"
        )
        if r.get("avatar"):
            msg += f"Avatar: {r['avatar']}\n"
    else:
        msg = f"🌐 ENS name `{name}` not found or has no primary address"
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def cmd_hacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = context.args[0] if context.args else ""
    params = {"max": "5"}
    if chain:
        params["chain"] = chain
    r = await call_nex("/v1/free/hack-feed", params)
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    hacks = r.get("hacks", [])
    msg = f"💥 *Recent Crypto Hacks* ({r.get('result_count', 0)} shown, {r.get('total_in_db', '?')} total)\n"
    if chain:
        msg += f"Filter: chain={chain}\n"
    msg += "\n"
    for h in hacks[:5]:
        chains = ", ".join(h.get("chain", []) if isinstance(h.get("chain"), list) else [h.get("chain", "?")])
        msg += f"• *${h.get('amount_millions', '?')}M* — {h.get('name', '?')[:30]} ({chains[:15]})\n  _{h.get('technique', '?')[:60]}_\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"💰 *Use NEX x402 Paid Endpoints*\n\n"
        f"This bot uses free mirrors. For paid access (better rate limits, no queueing):\n\n"
        f"1. Get USDC on Base (https://bridge.base.org)\n"
        f"2. Use any x402 client (npm install x402-fetch)\n"
        f"3. Send signed EIP-3009 payment to wallet `{NEX_WALLET[:10]}...{NEX_WALLET[-4:]}`\n"
        f"4. Call any endpoint with X-PAYMENT header\n\n"
        f"See full API manifest: {NEX_X402_BASE}/.well-known/x402.json\n"
        f"Try the free Playground: https://nexaitechau.github.io/nex-playground/"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default: route to chat."""
    text = update.message.text.strip()
    await update.message.reply_text(f"Thinking... (nemotron-3.5 30B, 2-5s)")
    r = await call_nex("/v1/free/chat", {"prompt": text})
    if r.get("ok") is False:
        await update.message.reply_text(f"Error: {r.get('error', 'unknown')}")
        return
    reply = r.get("message", {}).get("content") or r.get("reply") or json.dumps(r, indent=2)
    if len(reply) > 4000:
        reply = reply[:4000] + "\n\n[truncated — use /chat for longer responses]"
    await update.message.reply_text(reply)

def main():
    log.info(f"Starting NEX Telegram Bot (token: {NEX_BOT_TOKEN[:10]}...)")
    log.info(f"NEX x402 base: {NEX_X402_BASE}")
    app = Application.builder().token(NEX_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("chat", cmd_chat))
    app.add_handler(CommandHandler("code", cmd_code))
    app.add_handler(CommandHandler("check", cmd_check))
    app.add_handler(CommandHandler("audit", cmd_audit))
    app.add_handler(CommandHandler("contract", cmd_contract))
    app.add_handler(CommandHandler("ens", cmd_ens))
    app.add_handler(CommandHandler("hacks", cmd_hacks))
    app.add_handler(CommandHandler("pay", cmd_pay))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("Bot is polling. Send /start to test.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
