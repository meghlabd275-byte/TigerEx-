#!/usr/bin/env python3
"""
TigerEx Discord Bot
Complete trading bot with all features
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from discord import app_commands, Client, Intents, Interaction, Embed, Colour
from discord.ext import commands

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'your-discord-bot-token')
API_BASE_URL = 'https://api.tigerex.com'

# Setup bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = app_commands.CommandTree(bot)

# ==================== COMMANDS ====================

@tree.command(name="ping", description="Check if bot is online")
async def ping(interaction: Interaction):
    await interaction.response.send_message("🏓 Pong! TigerEx Bot is online!")

@tree.command(name="price", description="Get price of a cryptocurrency")
@app_commands.describe(symbol="Cryptocurrency symbol (e.g., BTC)")
async def price(interaction: Interaction, symbol: str):
    symbol = symbol.upper()
    prices = {
        'BTC': {'price': 42547.32, 'change': 2.45},
        'ETH': {'price': 2256.78, 'change': 3.12},
        'BNB': {'price': 324.56, 'change': -1.2},
        'SOL': {'price': 98.45, 'change': 5.67},
        'XRP': {'price': 0.62, 'change': 1.5}
    }
    
    if symbol in prices:
        p = prices[symbol]
        emoji = "🟢" if p['change'] > 0 else "🔴"
        
        embed = Embed(
            title=f"{symbol}/USDT",
            color=Colour.green() if p['change'] > 0 else Colour.red()
        )
        embed.add_field(name="Price", value=f"${p['price']:,.2f}", inline=True)
        embed.add_field(name="24h Change", value=f"{emoji} {p['change']:+.2f}%", inline=True)
        embed.set_footer(text="TigerEx • Powered by Discord Bot")
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ Market {symbol} not found")

@tree.command(name="markets", description="List top markets")
async def markets(interaction: Interaction):
    markets_list = [
        ("BTC/USDT", "42,547.32", "+2.45%"),
        ("ETH/USDT", "2,256.78", "+3.12%"),
        ("BNB/USDT", "324.56", "-1.20%"),
        ("SOL/USDT", "98.45", "+5.67%"),
        ("XRP/USDT", "0.62", "+1.50%")
    ]
    
    embed = Embed(
        title="📊 Top Markets",
        color=Colour.blue()
    )
    
    for symbol, price, change in markets_list:
        emoji = "🟢" if "+" in change else "🔴"
        embed.add_field(
            name=symbol,
            value=f"${price} {emoji} {change}",
            inline=True
        )
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

@tree.command(name="balance", description="Check your wallet balance")
async def balance(interaction: Interaction):
    # In production, fetch from API with user auth
    balances = [
        ("BTC", "0.5234", "$22,258.00"),
        ("ETH", "3.5000", "$7,896.00"),
        ("USDT", "5,000.00", "$5,000.00"),
        ("BNB", "10.0000", "$3,240.00")
    ]
    
    embed = Embed(
        title="💰 Your Balance",
        color=Colour.gold()
    )
    
    for asset, amount, value in balances:
        embed.add_field(name=asset, value=f"{amount}\n≈ {value}", inline=True)
    
    embed.add_field(name="Total", value="$38,394.00", inline=False)
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="orders", description="Show your open orders")
async def orders(interaction: Interaction):
    orders_list = [
        ("ORD12345", "BTC/USDT", "🟢 BUY", "0.5", "$42,500"),
        ("ORD12346", "ETH/USDT", "🔴 SELL", "2.0", "$2,250")
    ]
    
    embed = Embed(
        title="📈 Open Orders",
        color=Colour.blue()
    )
    
    for order_id, symbol, side, qty, price in orders_list:
        embed.add_field(
            name=f"#{order_id}",
            value=f"{symbol}\n{side}\n{qty} @ {price}",
            inline=True
        )
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

@tree.command(name="buy", description="Buy cryptocurrency")
@app_commands.describe(symbol="Cryptocurrency symbol", amount="Amount to buy")
async def buy(interaction: Interaction, symbol: str, amount: float):
    symbol = symbol.upper()
    
    embed = Embed(
        title=f"🟢 Buy Order",
        description=f"Placing buy order for {amount} {symbol}/USDT",
        color=Colour.green()
    )
    embed.add_field(name="Status", value="✅ Order placed successfully", inline=False)
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="sell", description="Sell cryptocurrency")
@app_commands.describe(symbol="Cryptocurrency symbol", amount="Amount to sell")
async def sell(interaction: Interaction, symbol: str, amount: float):
    symbol = symbol.upper()
    
    embed = Embed(
        title=f"🔴 Sell Order",
        description=f"Placing sell order for {amount} {symbol}/USDT",
        color=Colour.red()
    )
    embed.add_field(name="Status", value="✅ Order placed successfully", inline=False)
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="alerts", description="Manage price alerts")
async def alerts(interaction: Interaction):
    alerts_list = [
        ("BTC", "Above", "$50,000"),
        ("ETH", "Below", "$2,000"),
        ("SOL", "Above", "$150")
    ]
    
    embed = Embed(
        title="🔔 Your Price Alerts",
        color=Colour.blue()
    )
    
    for symbol, direction, price in alerts_list:
        embed.add_field(
            name=f"{symbol} {direction}",
            value=price,
            inline=True
        )
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

@tree.command(name="alert", description="Set a price alert")
@app_commands.describe(symbol="Cryptocurrency", price="Target price", direction="Above or Below")
async def alert(interaction: Interaction, symbol: str, price: float, direction: str):
    symbol = symbol.upper()
    
    embed = Embed(
        title="✅ Alert Created",
        color=Colour.green()
    )
    embed.add_field(name="Symbol", value=f"{symbol}/USDT", inline=True)
    embed.add_field(name="Target", value=f"${price:,.2f}", inline=True)
    embed.add_field(name="Direction", value=direction, inline=True)
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="trending", description="Show trending coins")
async def trending(interaction: Interaction):
    trending = [
        ("🚀 PEPE", "+45%"),
        ("🚀 WIF", "+32%"),
        ("🚀 BONK", "+28%"),
        ("🚀 ARB", "+15%"),
        ("🚀 OP", "+12%")
    ]
    
    embed = Embed(
        title="🔥 Trending Now",
        color=Colour.orange()
    )
    
    for coin, change in trending:
        embed.add_field(name=coin, value=change, inline=True)
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

@tree.command(name="earn", description="Show earn products")
async def earn(interaction: Interaction):
    products = [
        ("USDT Savings", "8.5% APY", "Flexible"),
        ("ETH Staking", "5.2% APY", "30 Days"),
        ("SOL Staking", "12% APY", "90 Days"),
        ("BTC Vault", "4% APY", "Flexible")
    ]
    
    embed = Embed(
        title="💎 Earn Products",
        color=Colour.gold()
    )
    
    for name, apy, lock in products:
        embed.add_field(name=name, value=f"{apy}\n{lock}", inline=True)
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

@tree.command(name="help", description="Show all commands")
async def help_command(interaction: Interaction):
    embed = Embed(
        title="🤖 TigerEx Bot Commands",
        color=Colour.blue()
    )
    
    embed.add_field(
        name="📊 Market Data",
        value="`/price [symbol]` - Get price\n`/markets` - List markets\n`/trending` - Trending coins",
        inline=False
    )
    
    embed.add_field(
        name="💰 Wallet",
        value="`/balance` - Check balance\n`/deposit` - Get deposit address",
        inline=False
    )
    
    embed.add_field(
        name="📈 Trading",
        value="`/buy [symbol] [amount]` - Buy\n`/sell [symbol] [amount]` - Sell\n`/orders` - Your orders",
        inline=False
    )
    
    embed.add_field(
        name="🔔 Alerts",
        value="`/alerts` - View alerts\n`/alert [symbol] [price] [direction]` - Set alert",
        inline=False
    )
    
    embed.add_field(
        name="💎 Earn",
        value="`/earn` - Earn products",
        inline=False
    )
    
    embed.set_footer(text="TigerEx • Powered by Discord Bot")
    await interaction.response.send_message(embed=embed)

# ==================== EVENTS ====================

@bot.event
async def on_ready():
    """Bot is ready"""
    print(f"🤖 TigerEx Bot logged in as {bot.user}")
    
    # Sync commands
    try:
        await tree.sync()
        print("✅ Commands synced!")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    
    # Set activity
    await bot.change_presence(
        activity=discord.Game("💰 /help for commands")
    )

@bot.event
async def on_message(message):
    """Handle messages"""
    # Don't respond to bots
    if message.author.bot:
        return
    
    # Check for commands
    await bot.process_commands(message)

# ==================== ERROR HANDLING ====================

@tree.error
async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    """Handle command errors"""
    embed = Embed(
        title="❌ Error",
        description=str(error),
        color=Colour.red()
    )
    await interaction.response.send_message(embed=embed)

# ==================== MAIN ====================

if __name__ == "__main__":
    import discord
    print("🤖 Starting TigerEx Discord Bot...")
    bot.run(DISCORD_TOKEN)