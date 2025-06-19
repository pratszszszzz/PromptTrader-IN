# 🤖 PromptTrader-IN

This bot allows you to execute trading commands on the Indian stock market using smart prompts over Telegram. Powered by the AngelOne SmartAPI, it supports equity and options trading, exit commands, and real-time notifications.

---

## 📁 Project Structure

```
.
├── telegram_bot.py        # Telegram bot logic and command handlers
├── parse_prompt.py        # Natural language prompt parser
├── broker.py              # Core trading logic and order execution
├── symbol_utils.py        # Fetches correct symbol token from exchange
├── lot_size.py            # Lot size lookup for F&O
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not included in repo)
```

---

## 🔧 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/telegram-trading-bot.git
cd telegram-trading-bot
```

### 2. Create `.env` file
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ALLOWED_IDS=123456789

ANGEL_API_KEY=your_angel_api_key
ANGEL_CLIENT_CODE=your_client_code
ANGEL_PASSWORD=your_password
ANGEL_TOTP=your_totp_secret
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the bot
```bash
python telegram_bot.py
```

You should see: `🤖 Telegram bot running...`

---

## 💬 Supported Commands

### 📈 Smart Prompts (via chat)
- `buy 1 lot NIFTY 22500 CE expiry 27 JUN`
- `sell 100 INFY`
- `close 50% INFY`
- `short straddle at strike 22400 expiry 20 JUN`
- `long straddle at strike 22400 expiry 20 JUN`

### ⌨️ Slash Commands
- `/start` — Greeting message
- `/help` — Prompt usage help
- `/positions` — Show current positions
- `/exitall` — Exit all open positions
- `/cancelall` — Cancel all open orders

---

## ✅ Features

| Feature | Description |
|--------|-------------|
| 🔒 Authenticated Access | Only authorized Telegram IDs can use it |
| 🧠 Prompt Parsing | Flexible natural language for trading |
| 💹 Market Orders | Trades NSE Equity & F&O using market orders |
| 📊 Position Management | View and close positions directly |
| 🚫 Order Cancelation | Cancel all open pending orders |
| 🔔 Notifications | Success/failure messages in real-time |
| ⚙️ Straddle Orders | Execute straddles (1 lot CE + 1 lot PE) as short (sell) or long (buy) based on prompt |

---

## 🚀 Deployment (Optional)

For 24/7 uptime:
- Use a cloud service like [Railway](https://railway.app/), [Render](https://render.com/) or a VPS
- Use `pm2` or `nohup` for background processes

```bash
nohup python telegram_bot.py &
```

---

## ⚠️ Disclaimer
This is for educational purposes only. Live trading involves financial risk. You are responsible for any loss incurred while using this bot.

---

## 📬 Contact
Need help? Email me at prathmeshaglawe7@gmail.com

