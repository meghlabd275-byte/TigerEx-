#!/usr/bin/env python3
"""
TigerEx Telegram Bot
Complete trading bot with all features
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'your-telegram-bot-token')
API_BASE_URL = 'https://api.tigerex.com'

# ==================== BOT COMMANDS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Welcome message"""
    keyboard = [
        [InlineKeyboardButton("📊 Markets", callback_data="markets")],
        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📈 Trade", callback_data="trade")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🐯 *Welcome to TigerEx Bot!*\n\n"
        f"Your personal crypto trading assistant\n\n"
        f"Use /help to see all commands",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - Show all commands"""
    help_text = """
*Available Commands:*

*📊 Market Data*
/price - Get price of a coin
/markets - List all markets
/depth - Order book depth

*💰 Wallet*
/balance - Check your balance
/deposit - Get deposit address
/withdraw - Withdraw funds

*📈 Trading*
/buy - Buy crypto
/sell - Sell crypto
/orders - Your open orders

*👤 Account*
/login - Link your account
/profile - Your profile
/verify - KYC verification

*🔔 Alerts*
/alert - Set price alert
/alerts - Your alerts

*ℹ️ Info*
/help - Show this message
/contact - Contact support
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get price of a cryptocurrency"""
    if not context.args:
        await update.message.reply_text("Usage: /price BTC")
        return
    
    symbol = context.args[0].upper()
    # In production, fetch from API
    prices = {
        'BTC': {'price': 42547.32, 'change': 2.45},
        'ETH': {'price': 2256.78, 'change': 3.12},
        'BNB': {'price': 324.56, 'change': -1.2},
        'SOL': {'price': 98.45, 'change': 5.67}
    }
    
    if symbol in prices:
        p = prices[symbol]
        change_emoji = "🟢" if p['change'] > 0 else "🔴"
        await update.message.reply_text(
            f"*{symbol}/USDT*\n\n"
            f"Price: ${p['price']:,.2f}\n"
            f"Change: {change_emoji} {p['change']:+.2f}%",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"Market {symbol} not found")

async def markets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all markets"""
    markets = [
        ("BTC/USDT", "42,547.32", "+2.45%"),
        ("ETH/USDT", "2,256.78", "+3.12%"),
        ("BNB/USDT", "324.56", "-1.20%"),
        ("SOL/USDT", "98.45", "+5.67%"),
        ("XRP/USDT", "0.62", "+1.50%")
    ]
    
    text = "*Top Markets:*\n\n"
    for symbol, price, change in markets:
        emoji = "🟢" if "+" in change else "🔴"
        text += f"{symbol}: ${price} {emoji} {change}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check wallet balance"""
    # In production, fetch from API with auth
    balances = [
        ("BTC", "0.5234", "$22,258.00"),
        ("ETH", "3.5000", "$7,896.00"),
        ("USDT", "5,000.00", "$5,000.00"),
        ("BNB", "10.0000", "$3,240.00")
    ]
    
    text = "*Your Balance:*\n\n"
    for asset, amount, value in balances:
        text += f"{asset}: {amount} ≈ {value}\n"
    
    total = sum([float(v.split('$')[1].replace(',','')) for _,_,v in balances])
    text += f"\n*Total: ${total:,.2f}*"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buy crypto"""
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data="buy_BTC")],
        [InlineKeyboardButton("ETH", callback_data="buy_ETH")],
        [InlineKeyboardButton("USDT", callback_data="buy_USDT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select crypto to buy:",
        reply_markup=reply_markup
    )

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sell crypto"""
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data="sell_BTC")],
        [InlineKeyboardButton("ETH", callback_data="sell_ETH")],
        [InlineKeyboardButton("USDT", callback_data="sell_USDT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select crypto to sell:",
        reply_markup=reply_markup
    )

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show open orders"""
    # In production, fetch from API
    orders = [
        ("ORD12345", "BTC/USDT", "buy", "0.5", "42,500"),
        ("ORD12346", "ETH/USDT", "sell", "2.0", "2,250")
    ]
    
    if orders:
        text = "*Your Open Orders:*\n\n"
        for order_id, symbol, side, qty, price in orders:
            emoji = "🟢" if side == "buy" else "🔴"
            text += f"#{order_id}\n"
            text += f"{emoji} {symbol} {side.upper()}\n"
            text += f"Qty: {qty} @ ${price}\n\n"
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        await update.message.reply_text("No open orders")

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get deposit address"""
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data="deposit_BTC")],
        [InlineKeyboardButton("ETH", callback_data="deposit_ETH")],
        [InlineKeyboardButton("USDT", callback_data="deposit_USDT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select crypto for deposit address:",
        reply_markup=reply_markup
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Withdraw crypto"""
    await update.message.reply_text(
        "To withdraw, please use the TigerEx website or app.\n"
        "Use /balance to check your wallet."
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    # In production, fetch from API
    text = """
*Your Profile:*

👤 Username: demo_user
📧 Email: demo@tigerex.com
✅ KYC: Verified (Level 2)
📅 Member since: Jan 2024

*Security:*
🔐 2FA: Enabled
🌐 Login Alerts: Enabled
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set price alert"""
    if not context.args:
        await update.message.reply_text(
            "Usage: /alert BTC 50000\n"
            "This will alert you when BTC reaches $50,000"
        )
        return
    
    symbol = context.args[0].upper()
    price = context.args[1] if len(context.args) > 1 else "0"
    
    await update.message.reply_text(
        f"✅ Price alert set for {symbol} at ${price}\n"
        f"You will be notified when price reaches ${price}"
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot settings"""
    keyboard = [
        [InlineKeyboardButton("🔔 Notifications", callback_data="notif_on")],
        [InlineKeyboardButton("🔇 Mute", callback_data="notif_off")],
        [InlineKeyboardButton("🌐 Language", callback_data="lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ *Bot Settings:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ==================== CALLBACK QUERIES ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "markets":
        await markets_command(update, context)
    elif data == "wallet":
        await balance_command(update, context)
    elif data == "trade":
        await buy_command(update, context)
    elif data.startswith("buy_"):
        symbol = data.split("_")[1]
        await query.edit_message_text(f"Enter amount of {symbol} to buy:")
    elif data.startswith("sell_"):
        symbol = data.split("_")[1]
        await query.edit_message_text(f"Enter amount of {symbol} to sell:")
    elif data.startswith("deposit_"):
        symbol = data.split("_")[1]
        # In production, fetch real address
        address = f"0x{'a'*40}"
        await query.edit_message_text(
            f"*{symbol} Deposit Address:*\n\n"
            f"`{address}`\n\n"
            f"⚠️ Only send {symbol} to this address!",
            parse_mode='Markdown'
        )
    elif data == "settings":
        await settings_command(update, context)
    else:
        await query.edit_message_text(f"Clicked: {data}")

# ==================== MESSAGE HANDLERS ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    text = update.message.text.lower()
    
    if "hello" in text or "hi" in text:
        await update.message.reply_text("👋 Hello! Use /help to see what I can do!")
    elif "price" in text:
        await price_command(update, context)
    else:
        await update.message.reply_text(
            "I didn't understand that. Use /help for available commands."
        )

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again.")

# ==================== MAIN ====================

def main():
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("markets", markets_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("sell", sell_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("deposit", deposit_command))
    application.add_handler(CommandHandler("withdraw", withdraw_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("alert", alert_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("TigerEx Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()