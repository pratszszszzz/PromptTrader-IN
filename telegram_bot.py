import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from parse_prompt import parse_trade_prompt
from broker import place_order
from smartapi.smartConnect import SmartConnect

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USERS = [int(uid) for uid in os.getenv("TELEGRAM_ALLOWED_IDS", "").split(",") if uid.strip().isdigit()]

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP = os.getenv("ANGEL_TOTP")

bot = telegram.Bot(token=TELEGRAM_TOKEN)
obj = SmartConnect(api_key=API_KEY)
session = obj.generateSession(CLIENT_CODE, PASSWORD, TOTP)

def start(update, context):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("❌ Unauthorized")
        return
    update.message.reply_text("👋 Welcome! Send a smart trading prompt like 'Buy 1 lot NIFTY 22500 CE expiry 27 JUN'")

def help_cmd(update, context):
    update.message.reply_text("📘 Format: 'Buy 1 lot NIFTY 22500 CE expiry 27 JUN'. Also supports closing % of positions.")

def positions(update, context):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("❌ Unauthorized")
        return
    try:
        positions = obj.position()
        if not positions or not positions.get("data"):
            update.message.reply_text("📭 No open positions.")
            return

        lines = []
        for p in positions["data"]:
            qty = p.get("netqty", 0)
            if int(qty) == 0:
                continue
            lines.append(f"📈 {p['tradingsymbol']}: {qty} qty @ {p['averageprice']} avg")

        if lines:
            update.message.reply_text("\n".join(lines))
        else:
            update.message.reply_text("📭 No open positions.")
    except Exception as e:
        update.message.reply_text(f"❌ Error fetching positions: {str(e)}")

def exit_all(update, context):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("❌ Unauthorized")
        return
    try:
        positions = obj.position()
        if not positions or not positions.get("data"):
            update.message.reply_text("📭 No open positions to exit.")
            return

        exited = []
        for p in positions["data"]:
            qty = int(p.get("netqty", 0))
            if qty == 0:
                continue
            try:
                order = obj.placeOrder({
                    "variety": "NORMAL",
                    "tradingsymbol": p["tradingsymbol"],
                    "symboltoken": p["symboltoken"],
                    "transactiontype": "SELL" if qty > 0 else "BUY",
                    "exchange": p["exchange"],
                    "ordertype": "MARKET",
                    "producttype": p["producttype"],
                    "duration": "DAY",
                    "price": "0",
                    "squareoff": "0",
                    "stoploss": "0",
                    "quantity": abs(qty)
                })
                exited.append(f"✅ {p['tradingsymbol']}: {qty} closed")
            except Exception as oe:
                exited.append(f"❌ {p['tradingsymbol']}: {str(oe)}")

        if exited:
            update.message.reply_text("\n".join(exited))
        else:
            update.message.reply_text("📭 No positions to exit.")
    except Exception as e:
        update.message.reply_text(f"❌ Error exiting positions: {str(e)}")

def cancel_all(update, context):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("❌ Unauthorized")
        return
    try:
        orders = obj.orderBook()
        if not orders or not orders.get("data"):
            update.message.reply_text("📭 No orders found.")
            return

        cancelled = []
        for o in orders["data"]:
            if o.get("status") == "open":
                try:
                    obj.cancelOrder(
                        variety=o["variety"],
                        orderid=o["orderid"]
                    )
                    cancelled.append(f"✅ Cancelled {o['tradingsymbol']} ({o['orderid']})")
                except Exception as ce:
                    cancelled.append(f"❌ Failed {o['tradingsymbol']}: {str(ce)}")

        if cancelled:
            update.message.reply_text("\n".join(cancelled))
        else:
            update.message.reply_text("📭 No open orders to cancel.")
    except Exception as e:
        update.message.reply_text(f"❌ Error cancelling orders: {str(e)}")

def handle_message(update, context):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        update.message.reply_text("❌ Unauthorized")
        return
    prompt = update.message.text
    parsed = parse_trade_prompt(prompt)
    response = place_order(parsed)
    update.message.reply_text(response)

    if "✅" in response:
        update.message.reply_text("🔔 Trade successfully executed!")
    elif "❌" in response:
        update.message.reply_text("⚠️ Trade failed. Please review your prompt.")

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("positions", positions))
    dp.add_handler(CommandHandler("exitall", exit_all))
    dp.add_handler(CommandHandler("cancelall", cancel_all))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Telegram bot running...")
    updater.start_polling()
    updater.idle()
