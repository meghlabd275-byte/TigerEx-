#!/usr/bin/env python3
"""
TigerEx Crypto Education System
Comprehensive educational platform for cryptocurrency trading and blockchain
"""

from fastapi import FastAPI, HTTPException, Depends
from admin.admin_routes import router as admin_router
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query

# @file main.py
# @author TigerEx Development Team
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Crypto Education System",
    description="Comprehensive educational platform for cryptocurrency and blockchain",
    version="1.0.0"
)

app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Course Categories
class CourseCategory(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    TRADING = "trading"
    BLOCKCHAIN = "blockchain"
    Defi = "defi"
    NFT = "nft"
    SECURITY = "security"
    REGULATIONS = "regulations"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# Course Models
class Lesson(BaseModel):
    id: str
    title: str
    content: str
    duration_minutes: int
    video_url: Optional[str] = None
    resources: List[Dict[str, str]] = []

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class Quiz(BaseModel):
    id: str
    title: str
    questions: List[QuizQuestion]
    passing_score: int = 70

class Course(BaseModel):
    id: str
    title: str
    description: str
    category: CourseCategory
    difficulty: DifficultyLevel
    duration_hours: float
    lessons: List[Lesson]
    quiz: Optional[Quiz] = None
    prerequisites: List[str] = []
    tags: List[str] = []
    instructor: str
    rating: float = 0.0
    enrolled_count: int = 0

class UserProgress(BaseModel):
    user_id: str
    course_id: str
    lesson_progress: Dict[str, bool] = {}
    quiz_score: Optional[int] = None
    completed: bool = False
    started_at: datetime
    completed_at: Optional[datetime] = None

# Comprehensive Course Content
COURSES = {
    # BEGINNER COURSES
    "crypto-101": Course(
        id="crypto-101",
        title="Cryptocurrency Fundamentals",
        description="Learn the basics of cryptocurrency, blockchain technology, and digital assets",
        category=CourseCategory.BEGINNER,
        difficulty=DifficultyLevel.BEGINNER,
        duration_hours=4,
        instructor="TigerEx Academy",
        rating=4.8,
        enrolled_count=45000,
        tags=["basics", "fundamentals", "bitcoin", "blockchain"],
        prerequisites=[],
        lessons=[
            Lesson(
                id="crypto-101-1",
                title="What is Cryptocurrency?",
                content="""# What is Cryptocurrency?

Cryptocurrency is a digital or virtual currency that uses cryptography for security and operates on decentralized networks, typically based on blockchain technology.

## Key Concepts:
- **Decentralization**: No central authority controls the currency
- **Blockchain**: A distributed ledger that records all transactions
- **Cryptography**: Advanced encryption techniques secure transactions
- **Mining**: Process of validating transactions and creating new coins

## Types of Cryptocurrencies:
1. **Coins** - Native tokens like BTC, ETH
2. **Tokens** - Built on existing blockchains like USDT (ERC-20)

## Popular Cryptocurrencies:
- Bitcoin (BTC) - First and largest by market cap
- Ethereum (ETH) - Smart contract platform
- Tether (USDT) - Stablecoin pegged to USD
- BNB - Binance's native token
""",
                duration_minutes=20,
                video_url="https://example.com/videos/crypto-101-1",
                resources=[
                    {"type": "article", "title": "History of Bitcoin", "url": "/resources/bitcoin-history"},
                    {"type": "glossary", "title": "Crypto Terms", "url": "/glossary"}
                ]
            ),
            Lesson(
                id="crypto-101-2",
                title="How Blockchain Works",
                content="""# How Blockchain Works

Blockchain is a distributed ledger technology that records transactions across multiple computers.

## Core Components:
1. **Blocks**: Groups of transactions
2. **Chain**: Linked blocks using cryptographic hashes
3. **Nodes**: Computers that maintain the network
4. **Consensus**: Agreement on transaction validity

## How Transactions Work:
1. User initiates a transaction
2. Transaction is broadcast to the network
3. Nodes verify the transaction
4. Transaction is added to a block
5. Block is added to the chain permanently

## Consensus Mechanisms:
- **Proof of Work (PoW)**: Mining, energy-intensive
- **Proof of Stake (PoS)**: Validators stake coins
- **Delegated PoS**: Elected validators
""",
                duration_minutes=25,
                video_url="https://example.com/videos/crypto-101-2",
                resources=[]
            ),
            Lesson(
                id="crypto-101-3",
                title="Setting Up Your First Wallet",
                content="""# Setting Up Your First Wallet

A cryptocurrency wallet allows you to store, send, and receive digital assets.

## Types of Wallets:
1. **Hot Wallets**: Online, convenient but less secure
2. **Cold Wallets**: Offline, most secure
3. **Hardware Wallets**: Physical devices like Ledger/Trezor
4. **Software Wallets**: Apps and browser extensions

## Popular Wallet Options:
- MetaMask (Ethereum ecosystem)
- Trust Wallet (Mobile)
- Ledger (Hardware)
- Trezor (Hardware)

## Security Best Practices:
- Never share your private keys
- Enable 2FA
- Backup your recovery phrase
- Use hardware wallets for large amounts
""",
                duration_minutes=30,
                video_url="https://example.com/videos/crypto-101-3",
                resources=[]
            ),
            Lesson(
                id="crypto-101-4",
                title="Buying Your First Crypto",
                content="""# Buying Your First Cryptocurrency

A step-by-step guide to purchasing your first digital asset.

## Where to Buy:
1. **Centralized Exchanges (CEX)**
   - Binance, Coinbase, Kraken
   - Easy to use, high liquidity
   
2. **Decentralized Exchanges (DEX)**
   - Uniswap, PancakeSwap
   - More privacy, advanced features

3. **Peer-to-Peer (P2P)**
   - Direct with other users
   - More payment options

## Step-by-Step Process:
1. Create account on exchange
2. Complete KYC verification
3. Add payment method
4. Buy USDT first (easiest)
5. Transfer to wallet or trade

## Tips for Beginners:
- Start with small amounts
- Only invest what you can afford
- Do your own research
- Use dollar-cost averaging
""",
                duration_minutes=25,
                video_url="https://example.com/videos/crypto-101-4",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="crypto-101-quiz",
            title="Cryptocurrency Fundamentals Quiz",
            passing_score=70,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="What is the largest cryptocurrency by market cap?",
                    options=["Ethereum", "Bitcoin", "Tether", "BNB"],
                    correct_answer=1,
                    explanation="Bitcoin (BTC) is the largest cryptocurrency by market capitalization."
                ),
                QuizQuestion(
                    id="q2",
                    question="What technology underlies most cryptocurrencies?",
                    options=["Cloud Computing", "Blockchain", "AI", "IoT"],
                    correct_answer=1,
                    explanation="Blockchain is the distributed ledger technology that powers most cryptocurrencies."
                ),
                QuizQuestion(
                    id="q3",
                    question="What is a private key?",
                    options=["Public address", "Password to exchange", "Secret key for signing transactions", "Email"],
                    correct_answer=2,
                    explanation="A private key is a secret key that allows you to sign transactions and access your funds."
                ),
                QuizQuestion(
                    id="q4",
                    question="Which consensus mechanism uses mining?",
                    options=["Proof of Stake", "Proof of Work", "Delegated PoS", "None"],
                    correct_answer=1,
                    explanation="Proof of Work (PoW) uses mining to validate transactions and create new blocks."
                ),
                QuizQuestion(
                    id="q5",
                    question="What is a hardware wallet?",
                    options=["Online wallet", "Software app", "Physical device for storing crypto", "Bank account"],
                    correct_answer=2,
                    explanation="Hardware wallets are physical devices that securely store your private keys offline."
                )
            ]
        )
    ),
    
    # TRADING COURSES
    "trading-101": Course(
        id="trading-101",
        title="Crypto Trading Basics",
        description="Learn how to trade cryptocurrencies profitably with fundamental and technical analysis",
        category=CourseCategory.TRADING,
        difficulty=DifficultyLevel.BEGINNER,
        duration_hours=6,
        instructor="TigerEx Trading Academy",
        rating=4.9,
        enrolled_count=32000,
        tags=["trading", "technical-analysis", "bullish", "bearish"],
        prerequisites=["crypto-101"],
        lessons=[
            Lesson(
                id="trading-101-1",
                title="Understanding Trading Pairs",
                content="""# Understanding Trading Pairs

A trading pair consists of two cryptocurrencies that can be traded against each other.

## Common Trading Pairs:
- BTC/USDT - Bitcoin vs Tether
- ETH/USDT - Ethereum vs Tether
- BNB/USDT - BNB vs Tether

## Quote and Base Currency:
- **Base Currency**: First currency (e.g., BTC in BTC/USDT)
- **Quote Currency**: Second currency (e.g., USDT)

## Reading Prices:
If BTC/USDT = 50,000, it means 1 BTC = 50,000 USDT

## Volume and Liquidity:
- High volume = Easier to buy/sell
- Low volume = Slippage risk
""",
                duration_minutes=20,
                video_url="https://example.com/videos/trading-101-1",
                resources=[]
            ),
            Lesson(
                id="trading-101-2",
                title="Order Types Explained",
                content="""# Order Types in Crypto Trading

Understanding different order types is crucial for successful trading.

## Market Orders:
- Execute immediately at best available price
- Used when speed is priority
- No price guarantee

## Limit Orders:
- Execute only at specified price or better
- More control over entry/exit
- May not execute if price not reached

## Stop-Loss Orders:
- Automatic sell when price drops to level
- Limits losses in volatile market
- Essential for risk management

## Stop-Limit Orders:
- Combines stop-loss and limit orders
- More precise execution price
- May not execute if price gaps

## Advanced Orders:
- OCO (One Cancels Other)
- Trailing Stop
- Time-in-force (GTC, IOC, FOK)
""",
                duration_minutes=30,
                video_url="https://example.com/videos/trading-101-2",
                resources=[]
            ),
            Lesson(
                id="trading-101-3",
                title="Technical Analysis Basics",
                content="""# Technical Analysis Basics

Learn to read charts and identify trading opportunities.

## Chart Types:
1. **Candlestick Charts** - Most popular
2. **Line Charts** - Simple trend view
3. **OHLC Charts** - Open, High, Low, Close

## Key Concepts:
- **Support**: Price floor where buying pressure
- **Resistance**: Price ceiling where selling pressure
- **Trend**: Direction of price movement

## Common Patterns:
- Head and Shoulders
- Double Top/Bottom
- Triangles
- Flags and Pennants

## Indicators:
- Moving Averages (MA, EMA)
- RSI (Relative Strength Index)
- MACD
- Bollinger Bands
""",
                duration_minutes=45,
                video_url="https://example.com/videos/trading-101-3",
                resources=[]
            ),
            Lesson(
                id="trading-101-4",
                title="Risk Management",
                content="""# Risk Management in Crypto Trading

Protecting your capital is the most important aspect of trading.

## Position Sizing:
- Never risk more than 1-2% per trade
- Calculate position size based on stop-loss
- Formula: Position Size = Risk Amount / (Entry - Stop Loss)

## Risk-Reward Ratio:
- Always aim for at least 1:2 ratio
- Potential reward should exceed risk
- Use technical analysis to identify targets

## Diversification:
- Don't put all eggs in one basket
- Spread across different assets
- Consider correlation

## Common Mistakes:
- Overtrading
- No stop-loss
- FOMO buying
- Revenge trading
- Ignoring risk management
""",
                duration_minutes=35,
                video_url="https://example.com/videos/trading-101-4",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="trading-101-quiz",
            title="Trading Basics Quiz",
            passing_score=70,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="In BTC/USDT, which is the base currency?",
                    options=["USDT", "BTC", "Both", "Neither"],
                    correct_answer=1,
                    explanation="In a trading pair, the base currency is the first one - BTC in BTC/USDT."
                ),
                QuizQuestion(
                    id="q2",
                    question="What is a stop-loss order?",
                    options=["Buy at market", "Sell automatically at price level", "Limit buy order", "Market buy"],
                    correct_answer=1,
                    explanation="A stop-loss automatically sells when price reaches a specified level to limit losses."
                ),
                QuizQuestion(
                    id="q3",
                    question="What percentage of portfolio should you risk per trade?",
                    options=["10%", "25%", "1-2%", "50%"],
                    correct_answer=2,
                    explanation="Professional traders risk only 1-2% of their portfolio per trade."
                ),
                QuizQuestion(
                    id="q4",
                    question="What is support in technical analysis?",
                    options=["Price ceiling", "Price floor", "Volume", "Market cap"],
                    correct_answer=1,
                    explanation="Support is a price level where buying pressure tends to prevent further price decline."
                ),
                QuizQuestion(
                    id="q5",
                    question="What minimum risk-reward ratio is recommended?",
                    options=["1:1", "1:2", "1:0.5", "1:5"],
                    correct_answer=1,
                    explanation="A minimum 1:2 risk-reward ratio means potential reward is twice the risk."
                )
            ]
        )
    ),
    
    # Defi COURSE
    "defi-101": Course(
        id="defi-101",
        title="DeFi (Decentralized Finance) Masterclass",
        description="Master decentralized finance: yield farming, lending, staking, and DeFi protocols",
        category=CourseCategory.DEFI,
        difficulty=DifficultyLevel.INTERMEDIATE,
        duration_hours=8,
        instructor="TigerEx DeFi Expert",
        rating=4.7,
        enrolled_count=18000,
        tags=["defi", "yield-farming", "lending", "staking", "uniswap"],
        prerequisites=["crypto-101"],
        lessons=[
            Lesson(
                id="defi-101-1",
                title="Introduction to DeFi",
                content="""# Introduction to Decentralized Finance

DeFi aims to recreate traditional financial services using blockchain technology.

## What is DeFi?
- No intermediaries (banks, brokers)
- Open to anyone with wallet
- Transparent and programmable
- Global and borderless

## Key DeFi Components:
1. **Stablecoins**: USDT, USDC, DAI
2. **Lending Protocols**: Aave, Compound
3. **DEXs**: Uniswap, SushiSwap
4. **Yield Farming**: Yearn, Curve
5. **Insurance**: Nexus Mutual

## Benefits:
- Higher yields than traditional
- No KYC required
- 24/7 market access
- Composability
""",
                duration_minutes=30,
                video_url="https://example.com/videos/defi-101-1",
                resources=[]
            ),
            Lesson(
                id="defi-101-2",
                title="Using Decentralized Exchanges",
                content="""# Using Decentralized Exchanges (DEX)

DEXs allow peer-to-peer trading without intermediaries.

## How DEX Works:
1. Connect wallet
2. Select trading pair
3. Set slippage tolerance
4. Approve tokens
5. Swap tokens

## Popular DEXs:
- **Uniswap** (Ethereum)
- **PancakeSwap** (BSC)
- **SushiSwap** (Multi-chain)
- **Curve** (Stablecoins)

## Key Concepts:
- **AMM**: Automated Market Maker
- **Liquidity Pool**: Token pairs provided by users
- **Slippage**: Difference between expected and actual price
- **Liquidity Provider (LP)**: Token suppliers

## LP Tokens:
- Earn fees from trades
- Can be staked for more yield
- Impermanent loss risk
""",
                duration_minutes=40,
                video_url="https://example.com/videos/defi-101-2",
                resources=[]
            ),
            Lesson(
                id="defi-101-3",
                title="Lending and Borrowing",
                content="""# Lending and Borrowing in DeFi

Earn interest on crypto or borrow against collateral.

## Lending Protocols:
- **Aave**: Market leading, flash loans
- **Compound**: Simple, reliable
- **Cream**: Higher yields

## How Lending Works:
1. Deposit collateral
2. Earn interest automatically
3. Withdraw anytime (if not borrowed)

## How Borrowing Works:
1. Deposit collateral (ETH, BTC, etc.)
2. Borrow up to 75% of value
3. Pay interest to lenders
4. Risk of liquidation if ratio drops

## Important Metrics:
- **LTV**: Loan-to-Value ratio
- **Liquidation Threshold**: When position closes
- **APY**: Annual Percentage Yield
""",
                duration_minutes=35,
                video_url="https://example.com/videos/defi-101-3",
                resources=[]
            ),
            Lesson(
                id="defi-101-4",
                title="Yield Farming Strategies",
                content="""# Yield Farming Strategies

Maximize returns by moving assets between protocols.

## Yield Sources:
1. Lending interest
2. Trading fees (LP)
3. Staking rewards
4. Governance token incentives

## Strategy Types:
- **Single Staking**: Simple, lower risk
- **LP Farming**: Higher APY, impermanent loss
- **Auto-Compounding**: Reinvests rewards
- **Leverage Farming**: Borrow to increase exposure

## Risk Management:
- Impermanent loss
- Smart contract risk
- Token volatility
- Liquidation risk

## Best Practices:
- Start with small amounts
- Use trusted protocols
- Track gas fees
- Diversify strategies
""",
                duration_minutes=45,
                video_url="https://example.com/videos/defi-101-4",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="defi-101-quiz",
            title="DeFi Fundamentals Quiz",
            passing_score=70,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="What does DeFi stand for?",
                    options=["Defined Finance", "Decentralized Finance", "Digital Finance", "Distributed Finance"],
                    correct_answer=1,
                    explanation="DeFi stands for Decentralized Finance - financial services built on blockchain."
                ),
                QuizQuestion(
                    id="q2",
                    question="What is an AMM?",
                    options=["American Money Market", "Automated Market Maker", "Asset Management Module", "Auto Minting Machine"],
                    correct_answer=1,
                    explanation="AMM (Automated Market Maker) uses liquidity pools instead of order books."
                ),
                QuizQuestion(
                    id="q3",
                    question="What is impermanent loss?",
                    options=["Permanent loss of funds", "Temporary loss from holding tokens in LP", "Trading fees loss", "Gas fees"],
                    correct_answer=1,
                    explanation="Impermanent loss occurs when token price changes differ in LP vs holding."
                ),
                QuizQuestion(
                    id="q4",
                    question="What happens if your loan collateral drops below liquidation threshold?",
                    options=["Nothing", "Position automatically closed", "Get more time", "Rewards increase"],
                    correct_answer=1,
                    explanation="Your position gets liquidated and collateral is sold to repay the loan."
                ),
                QuizQuestion(
                    id="q5",
                    question="What are LP tokens?",
                    options=["Loyalty Points", "Liquidity Provider tokens", "Limited Partnership", "Litecoin Proxy"],
                    correct_answer=1,
                    explanation="LP tokens represent your share of a liquidity pool and earn fees."
                )
            ]
        )
    ),
    
    # SECURITY COURSE
    "security-101": Course(
        id="security-101",
        title="Cryptocurrency Security Mastery",
        description="Protect your digital assets with advanced security practices and wallet safety",
        category=CourseCategory.SECURITY,
        difficulty=DifficultyLevel.BEGINNER,
        duration_hours=3,
        instructor="TigerEx Security Team",
        rating=4.9,
        enrolled_count=28000,
        tags=["security", "wallets", "scams", "phishing", "2fa"],
        prerequisites=[],
        lessons=[
            Lesson(
                id="security-101-1",
                title="Securing Your Wallet",
                content="""# Securing Your Cryptocurrency Wallet

Your wallet security is paramount for protecting your assets.

## Wallet Security Essentials:
1. **Never share private keys**
2. **Backup recovery phrase**
3. **Use hardware wallets for large amounts**
4. **Enable 2FA everywhere

## Recovery Phrase Best Practices:
- Write on paper (multiple copies)
- Store in safe deposit box
- Never digitally (no screenshots)
- Never share with anyone

## Hot vs Cold Storage:
- **Hot Wallet**: Online, convenient, smaller amounts
- **Cold Wallet**: Offline, secure, large amounts

## Hardware Wallet Setup:
1. Buy from official source
2. Verify seal
3. Create new wallet
4. Write down recovery phrase
5. Update firmware
""",
                duration_minutes=25,
                video_url="https://example.com/videos/security-101-1",
                resources=[]
            ),
            Lesson(
                id="security-101-2",
                title="Avoiding Scams and Phishing",
                content="""# Avoiding Scams and Phishing

Learn to identify and avoid common cryptocurrency scams.

## Common Scam Types:
1. **Phishing Emails**: Fake login pages
2. **Fake Exchanges**: Steal deposits
3. **Rug Pulls**: Developers abandon project
4. **Ponzi Schemes**: Too good to be true
5. **Fake Wallets**: Malicious apps

## Red Flags:
- Guaranteed returns
- Pressure to act fast
- Unsolicited messages
- Unknown developers
- No code audit

## Protection Tips:
- Verify URLs carefully
- Use bookmarks for exchanges
- Check SSL certificates
- Never click suspicious links
- Verify before sending funds

## Reporting Scams:
- Report to exchange
- File police report
- Warn community
- Document everything
""",
                duration_minutes=30,
                video_url="https://example.com/videos/security-101-2",
                resources=[]
            ),
            Lesson(
                id="security-101-3",
                title="Multi-Signature Security",
                content="""# Multi-Signature Security

Add extra layers of protection with multi-sig wallets.

## What is Multi-Sig?
- Requires multiple signatures to transact
- Like a joint bank account
- Prevents single point of failure

## Use Cases:
1. **Personal**: Different devices
2. **Business**: Multiple approvals
3. **Family**: Estate planning

## Multi-Sig Solutions:
- **Gnosis Safe**: Popular for teams
- **Casa**: Consumer-friendly
- **BitGo**: Enterprise grade
- **Native exchange**: Some exchanges offer

## Setup Process:
1. Choose platform
2. Add signers (wallets)
3. Set required signatures
4. Test with small amount
5. Fund properly
""",
                duration_minutes=25,
                video_url="https://example.com/videos/security-101-3",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="security-101-quiz",
            title="Security Quiz",
            passing_score=80,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="Should you share your private keys?",
                    options=["Yes, with family", "No, never", "Only with exchanges", "With friends"],
                    correct_answer=1,
                    explanation="Private keys should NEVER be shared with anyone - they grant full access to your funds."
                ),
                QuizQuestion(
                    id="q2",
                    question="What's the best storage for large amounts?",
                    options=["Hot wallet", "Exchange", "Hardware wallet", "Paper wallet"],
                    correct_answer=2,
                    explanation="Hardware wallets are the most secure for storing large amounts of cryptocurrency."
                ),
                QuizQuestion(
                    id="q3",
                    question="What is a rug pull?",
                    options=["Trading strategy", "Developers abandon and take funds", "Stop loss", "Market correction"],
                    correct_answer=1,
                    explanation="A rug pull is when developers create a token, attract investment, then abandon the project."
                ),
                QuizQuestion(
                    id="q4",
                    question="What does multi-sig mean?",
                    options=["Multiple signatures required", "Single signature", "No signature needed", "Auto signature"],
                    correct_answer=0,
                    explanation="Multi-sig requires multiple private keys to authorize a transaction."
                )
            ]
        )
    ),
    
    # NFT COURSE
    "nft-101": Course(
        id="nft-101",
        title="NFT Essentials",
        description="Learn about Non-Fungible Tokens: creation, trading, and investment strategies",
        category=CourseCategory.NFT,
        difficulty=DifficultyLevel.BEGINNER,
        duration_hours=4,
        instructor="TigerEx NFT Academy",
        rating=4.6,
        enrolled_count=22000,
        tags=["nft", "digital-art", "collectibles", "metaverse", "gaming"],
        prerequisites=[],
        lessons=[
            Lesson(
                id="nft-101-1",
                title="What is an NFT?",
                content="""# What is an NFT?

Non-Fungible Tokens represent unique digital ownership.

## Key Characteristics:
- **Unique**: Each token is one-of-a-kind
- **Verifiable**: Blockchain confirms authenticity
- **Transferable**: Can be bought/sold/traded
- **Programmable**: Can have built-in royalties

## NFT Standards:
- **ERC-721**: Ethereum standard for unique tokens
- **ERC-1155**: Multi-token standard (gaming)
- **BEP-721**: Binance Smart Chain

## NFT Types:
1. **Art**: Digital artwork
2. **Collectibles**: Digital trading cards
3. **Gaming Items**: In-game assets
4. **Music**: Audio files
5. **Domain Names**: .eth, .crypto
6. **Virtual Land**: Metaverse parcels

## Use Cases:
- Digital art ownership
- Gaming assets
- Identity verification
- Membership/access
- Event tickets
""",
                duration_minutes=25,
                video_url="https://example.com/videos/nft-101-1",
                resources=[]
            ),
            Lesson(
                id="nft-101-2",
                title="Buying and Selling NFTs",
                content="""# Buying and Selling NFTs

Navigate the NFT marketplace like a pro.

## Where to Buy:
1. **Marketplaces**
   - OpenSea (largest)
   - Blur (trading-focused)
   - Magic Eden (Solana)
   - Foundation (curated)

2. **Mint Dates**
   - New project launches
   - Fair mint = random
   - Dutch auction = price drops
   - Whitelist = guaranteed

## Evaluation Factors:
- **Rarity**: How unique?
- **Utility**: What can you do?
- **Community**: Discord size/activity
- **Team**: Verified creators?
- **History**: Past sales data

## Selling:
- Set floor price
- Use gas-efficient times
- Consider royalties (usually 5-10%)
- List on multiple marketplaces
""",
                duration_minutes=30,
                video_url="https://example.com/videos/nft-101-2",
                resources=[]
            ),
            Lesson(
                id="nft-101-3",
                title="Creating Your Own NFT",
                content=""""# Creating Your Own NFT

Mint your first NFT with this comprehensive guide.

## Preparation:
1. Create wallet (MetaMask)
2. Buy small amount of native gas token
3. Connect to marketplace

## Minting Process:
1. Upload image/video/audio
2. Add metadata (name, description)
3. Choose blockchain
4. Set royalties (usually 5-10%)
5. Pay minting fee

## File Formats:
- Images: PNG, JPG, GIF, SVG
- Video: MP4, WebM (under 100MB)
- Audio: MP3, WAV (under 100MB)

## Best Practices:
- High quality images
- Detailed descriptions
- Social links
- Reveal date option
- Edition count

## Costs:
- Gas fees vary by blockchain
- Ethereum = higher fees
- Polygon = near free
- Solana = low fees
""",
                duration_minutes=35,
                video_url="https://example.com/videos/nft-101-3",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="nft-101-quiz",
            title="NFT Basics Quiz",
            passing_score=70,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="What does NFT stand for?",
                    options=["New File Token", "Non-Fungible Token", "Network File Transfer", "New Finance Token"],
                    correct_answer=1,
                    explanation="NFT stands for Non-Fungible Token - a unique digital asset."
                ),
                QuizQuestion(
                    id="q2",
                    question="Which standard is used for NFTs on Ethereum?",
                    options=["ERC-20", "ERC-721", "ERC-1155", "BEP-20"],
                    correct_answer=1,
                    explanation="ERC-721 is the standard for unique NFTs on Ethereum."
                ),
                QuizQuestion(
                    id="q3",
                    question="What is floor price?",
                    options=["Highest price", "Lowest asking price", "Average price", "Mint price"],
                    correct_answer=1,
                    explanation="Floor price is the lowest price at which an NFT collection is currently listed."
                ),
                QuizQuestion(
                    id="q4",
                    question="What are royalties in NFT context?",
                    options=["Taxes", "Creator fees on resales", "Marketplace fees", "Gas fees"],
                    correct_answer=1,
                    explanation="Royalties are fees creators receive from secondary market sales (usually 5-10%)."
                )
            ]
        )
    ),
    
    # ADVANCED TRADING
    "advanced-trading": Course(
        id="advanced-trading",
        title="Advanced Trading Strategies",
        description="Master advanced trading techniques: derivatives, margin, algorithmic trading",
        category=CourseCategory.TRADING,
        difficulty=DifficultyLevel.ADVANCED,
        duration_hours=10,
        instructor="TigerEx Pro Traders",
        rating=4.8,
        enrolled_count=12000,
        tags=["advanced", "futures", "options", "margin", "algorithmic"],
        prerequisites=["trading-101"],
        lessons=[
            Lesson(
                id="advanced-1",
                title="Margin Trading Deep Dive",
                content="""# Margin Trading Deep Dive

Trade with borrowed funds to amplify your position.

## What is Margin Trading?
- Borrow funds to increase position
- Leverage amplifies gains AND losses
- Higher risk, higher reward

## Key Concepts:
- **Initial Margin**: Required collateral
- **Maintenance Margin**: Minimum to keep position
- **Leverage**: 2x to 100x depending on asset
- **Liquidation**: Position closed when equity drops

## Long vs Short:
- **Long**: Buy now, sell later (bullish)
- **Short**: Sell now, buy later (bearish)

## Risk Management:
- Never risk more than you can afford
- Use stop-losses
- Monitor liquidation price
- Understand funding rates
""",
                duration_minutes=45,
                video_url="https://example.com/videos/advanced-1",
                resources=[]
            ),
            Lesson(
                id="advanced-2",
                title="Futures Trading",
                content="""# Futures Trading Explained

Trade cryptocurrency futures contracts.

## What are Futures?
- Agreement to buy/sell at future date
- Price prediction on direction
- No ownership of underlying asset

## Types:
1. **Perpetual**: No expiration, funding fees
2. **Quarterly**: Expire every 3 months

## Key Metrics:
- **Open Interest**: Total open positions
- **Funding Rate**: Cost to hold position
- **Mark Price**: Fair price (liquidations)
- **Index Price**: Average spot price

## Strategies:
- Trend following
- Range trading
- Breakout trading
- Hedge existing positions
""",
                duration_minutes=50,
                video_url="https://example.com/videos/advanced-2",
                resources=[]
            ),
            Lesson(
                id="advanced-3",
                title="Options Trading",
                content="""# Options Trading Fundamentals

Buy and sell options contracts for flexible strategies.

## Options Basics:
- **Call**: Right to buy
- **Put**: Right to sell
- **Premium**: Price of option

## Key Terms:
- **Strike Price**: Exercise price
- **Expiration**: When option expires
- **ITM**: In the money
- **OTM**: Out of the money

## Strategies:
1. **Long Call**: Bullish, limited risk
2. **Long Put**: Bearish, limited risk
3. **Covered Call**: Income generation
4. **Protective Put**: Insurance
5. **Straddle**: Volatility play

## Greeks:
- **Delta**: Price sensitivity
- **Theta**: Time decay
- **Vega**: Volatility sensitivity
- **Gamma**: Delta change rate
""",
                duration_minutes=55,
                video_url="https://example.com/videos/advanced-3",
                resources=[]
            ),
            Lesson(
                id="advanced-4",
                title="Algorithmic Trading Basics",
                content="""# Introduction to Algorithmic Trading

Automate your trading with algorithms.

## What is Algo Trading?
- Automated trading based on rules
- Removes emotional decisions
- Backtest strategies
- 24/7 execution

## Common Strategies:
1. **Trend Following**: MA crossovers
2. **Mean Reversion**: Price returns to average
3. **Arbitrage**: Price differences
4. **Market Making**: Provide liquidity

## Building Blocks:
- Data feeds
- Signal generation
- Position sizing
- Risk management
- Execution engine

## Tools:
- TradingView (Pine Script)
- Python (Backtrader, Zipline)
- MetaTrader
- Custom solutions
""",
                duration_minutes=60,
                video_url="https://example.com/videos/advanced-4",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="advanced-quiz",
            title="Advanced Trading Quiz",
            passing_score=75,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="What is leverage in margin trading?",
                    options=["Borrowed amount", "Multiplier that amplifies position", "Interest rate", "Collateral"],
                    correct_answer=1,
                    explanation="Leverage multiplies your position size, amplifying both gains and losses."
                ),
                QuizQuestion(
                    id="q2",
                    question="What is a long position?",
                    options=["Selling short", "Buying expecting price to rise", "Holding stablecoins", "Using leverage"],
                    correct_answer=1,
                    explanation="A long position means buying an asset expecting its price to increase."
                ),
                QuizQuestion(
                    id="q3",
                    question="What is a call option?",
                    options=["Right to sell", "Right to buy", "Obligation to buy", "Future contract"],
                    correct_answer=1,
                    explanation="A call option gives the holder the right (not obligation) to buy an asset."
                ),
                QuizQuestion(
                    id="q4",
                    question="What is funding rate in perpetual futures?",
                    options=["Trading fee", "Periodic payment between long/short traders", "Liquidation fee", "Maker rebate"],
                    correct_answer=1,
                    explanation="Funding rate is a periodic payment between long and short traders to keep prices aligned."
                ),
                QuizQuestion(
                    id="q5",
                    question="What is backtesting?",
                    options=["Live trading", "Testing strategy on historical data", "Paper trading", "Forward testing"],
                    correct_answer=1,
                    explanation="Backtesting evaluates a trading strategy using historical market data."
                )
            ]
        )
    ),
    
    # BLOCKCHAIN FUNDAMENTALS
    "blockchain-101": Course(
        id="blockchain-101",
        title="Blockchain Technology Deep Dive",
        description="Understand blockchain architecture, consensus, and development",
        category=CourseCategory.BLOCKCHAIN,
        difficulty=DifficultyLevel.INTERMEDIATE,
        duration_hours=6,
        instructor="TigerEx Blockchain Team",
        rating=4.7,
        enrolled_count=15000,
        tags=["blockchain", "development", "smart-contracts", "consensus"],
        prerequisites=["crypto-101"],
        lessons=[
            Lesson(
                id="blockchain-1",
                title="Blockchain Architecture",
                content="""# Blockchain Architecture Deep Dive

Understanding the technical foundations of blockchain.

## Core Components:
1. **Blocks**: Data containers
   - Header (hash, timestamp, etc.)
   - Transactions
   - Merkle Root
   
2. **Chain**: Linked blocks
   - Cryptographic hashing
   - Immutability
   
3. **Network**: Distributed nodes
   - Full nodes
   - Light nodes
   - Mining nodes

## Data Structures:
- **Hash**: Digital fingerprint
- **Merkle Tree**: Transaction organization
- **State Trie**: Account balances

## Types of Blockchains:
- **Public**: Anyone can join
- **Private**: Permissioned
- **Consortium**: Multiple organizations
""",
                duration_minutes=40,
                video_url="https://example.com/videos/blockchain-1",
                resources=[]
            ),
            Lesson(
                id="blockchain-2",
                title="Consensus Mechanisms",
                content="""# Consensus Mechanisms Explained

How blockchains agree on the state of the network.

## Proof of Work (PoW):
- Miners solve complex puzzles
- High energy consumption
- Most secure
- Examples: Bitcoin, (formerly) Ethereum

## Proof of Stake (PoS):
- Validators stake coins
- Energy efficient
- Examples: Ethereum (after merge), Cardano

## Other Mechanisms:
- **Delegated PoS**: Tron, EOS
- **Proof of Authority**: Private chains
- **Byzantine Fault Tolerance**: Enterprise

## Finality:
- PoW: Probabilistic (6+ confirmations)
- PoS: Deterministic (epochs, slots)
- BFT: Quick finality
""",
                duration_minutes=35,
                video_url="https://example.com/videos/blockchain-2",
                resources=[]
            ),
            Lesson(
                id="blockchain-3",
                title="Smart Contract Development",
                content="""# Introduction to Smart Contracts

Self-executing programs on the blockchain.

## What are Smart Contracts?
- Code deployed to blockchain
- Execute automatically
- Immutable once deployed
- Transparent and auditable

## Popular Platforms:
1. **Ethereum**: First and largest
2. **Solana**: High throughput
3. **Avalanche**: Low fees
4. **Polygon**: Ethereum scaling

## Development Basics:
1. Learn Solidity (Ethereum)
2. Use Remix IDE
3. Test on testnets
4. Deploy to mainnet

## Key Concepts:
- Gas optimization
- Security auditing
- Upgradeability
- Oracle integration
""",
                duration_minutes=45,
                video_url="https://example.com/videos/blockchain-3",
                resources=[]
            ),
            Lesson(
                id="blockchain-4",
                title="Layer 2 Solutions",
                content="""# Layer 2 Scaling Solutions

Scale blockchain without compromising security.

## The Scaling Problem:
- Limited transactions per second
- High fees during congestion
- Slow confirmation times

## Layer 2 Solutions:
1. **Rollups**: 
   - Optimistic Rollups
   - zkRollups
   
2. **Sidechains**:
   - Polygon PoS
   - Gnosis Chain
   
3. **State Channels**:
   - Lightning Network (Bitcoin)
   - Raiden (Ethereum)

## Benefits:
- Lower fees
- Faster transactions
- Mainnet security
- EVM compatibility
""",
                duration_minutes=40,
                video_url="https://example.com/videos/blockchain-4",
                resources=[]
            )
        ],
        quiz=Quiz(
            id="blockchain-quiz",
            title="Blockchain Quiz",
            passing_score=70,
            questions=[
                QuizQuestion(
                    id="q1",
                    question="What is a Merkle Tree used for?",
                    options=["Encryption", "Organizing transactions efficiently", "Storing balances", "Mining"],
                    correct_answer=1,
                    explanation="Merkle Tree organizes transactions into a tree structure for efficient verification."
                ),
                QuizQuestion(
                    id="q2",
                    question="Which consensus uses mining?",
                    options=["Proof of Stake", "Proof of Work", "Delegated PoS", "Proof of Authority"],
                    correct_answer=1,
                    explanation="Proof of Work uses mining to validate transactions and create new blocks."
                ),
                QuizQuestion(
                    id="q3",
                    question="What are smart contracts?",
                    options=["Legal contracts", "Self-executing code on blockchain", "Trading bots", "Wallets"],
                    correct_answer=1,
                    explanation="Smart contracts are self-executing programs deployed on a blockchain."
                ),
                QuizQuestion(
                    id="q4",
                    question="What problem do Layer 2 solutions solve?",
                    options=["Security", "Scalability", "Privacy", "Decentralization"],
                    correct_answer=1,
                    explanation="Layer 2 solutions primarily address blockchain scalability (throughput and fees)."
                )
            ]
        )
    )
}

# User progress storage (in-memory for demo)
user_progress: Dict[str, UserProgress] = {}

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crypto-education"}

@app.get("/api/v1/courses")
async def get_courses(
    category: Optional[CourseCategory] = None,
    difficulty: Optional[DifficultyLevel] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    """Get all available courses"""
    courses = list(COURSES.values())
    
    # Filter by category
    if category:
        courses = [c for c in courses if c.category == category]
    
    # Filter by difficulty
    if difficulty:
        courses = [c for c in courses if c.difficulty == difficulty]
    
    # Search
    if search:
        search = search.lower()
        courses = [c for c in courses if search in c.title.lower() or search in c.description.lower()]
    
    # Limit
    courses = courses[:limit]
    
    return {
        "success": True,
        "count": len(courses),
        "courses": [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "category": c.category,
                "difficulty": c.difficulty,
                "duration_hours": c.duration_hours,
                "instructor": c.instructor,
                "rating": c.rating,
                "enrolled_count": c.enrolled_count,
                "tags": c.tags,
                "lessons_count": len(c.lessons),
                "has_quiz": c.quiz is not None
            }
            for c in courses
        ]
    }

@app.get("/api/v1/courses/{course_id}")
async def get_course(course_id: str):
    """Get course details with lessons"""
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = COURSES[course_id]
    return {
        "success": True,
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "difficulty": course.difficulty,
            "duration_hours": course.duration_hours,
            "instructor": course.instructor,
            "rating": course.rating,
            "enrolled_count": course.enrolled_count,
            "tags": course.tags,
            "prerequisites": course.prerequisites,
            "lessons": [
                {
                    "id": l.id,
                    "title": l.title,
                    "duration_minutes": l.duration_minutes,
                    "has_video": l.video_url is not None,
                    "resources_count": len(l.resources)
                }
                for l in course.lessons
            ],
            "quiz": {
                "id": course.quiz.id,
                "title": course.quiz.title,
                "questions_count": len(course.quiz.questions),
                "passing_score": course.quiz.passing_score
            } if course.quiz else None
        }
    }

@app.get("/api/v1/courses/{course_id}/lessons/{lesson_id}")
async def get_lesson(course_id: str, lesson_id: str):
    """Get lesson content"""
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = COURSES[course_id]
    lesson = next((l for l in course.lessons if l.id == lesson_id), None)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return {
        "success": True,
        "lesson": {
            "id": lesson.id,
            "title": lesson.title,
            "content": lesson.content,
            "duration_minutes": lesson.duration_minutes,
            "video_url": lesson.video_url,
            "resources": lesson.resources,
            "course_id": course_id,
            "course_title": course.title
        }
    }

@app.get("/api/v1/courses/{course_id}/quiz")
async def get_course_quiz(course_id: str):
    """Get course quiz (without correct answers)"""
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = COURSES[course_id]
    if not course.quiz:
        raise HTTPException(status_code=404, detail="No quiz available")
    
    return {
        "success": True,
        "quiz": {
            "id": course.quiz.id,
            "title": course.quiz.title,
            "questions_count": len(course.quiz.questions),
            "passing_score": course.quiz.passing_score,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options
                }
                for q in course.quiz.questions
            ]
        }
    }

@app.post("/api/v1/courses/{course_id}/quiz/submit")
async def submit_quiz(course_id: str, answers: Dict[str, int]):
    """Submit quiz answers"""
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = COURSES[course_id]
    if not course.quiz:
        raise HTTPException(status_code=404, detail="No quiz available")
    
    quiz = course.quiz
    correct = 0
    
    for question in quiz.questions:
        if question.id in answers and answers[question.id] == question.correct_answer:
            correct += 1
    
    score = int((correct / len(quiz.questions)) * 100)
    passed = score >= quiz.passing_score
    
    return {
        "success": True,
        "score": score,
        "passed": passed,
        "correct_answers": correct,
        "total_questions": len(quiz.questions),
        "explanations": [
            {
                "question_id": q.id,
                "explanation": q.explanation,
                "correct_answer": q.options[q.correct_answer]
            }
            for q in quiz.questions
        ]
    }

@app.get("/api/v1/categories")
async def get_categories():
    """Get all course categories"""
    return {
        "success": True,
        "categories": [
            {"id": cat.value, "name": cat.value.title(), "description": get_category_description(cat.value)}
            for cat in CourseCategory
        ]
    }

def get_category_description(category: str) -> str:
    descriptions = {
        "beginner": "Start your crypto journey with fundamentals",
        "intermediate": "Deepen your knowledge with practical skills",
        "advanced": "Master advanced trading and development",
        "trading": "Learn to trade profitably",
        "blockchain": "Understand blockchain technology",
        "defi": "Explore decentralized finance",
        "nft": "Dive into NFTs and digital collectibles",
        "security": "Protect your digital assets",
        "regulations": "Understand legal compliance"
    }
    return descriptions.get(category, "")

@app.get("/api/v1/progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get user learning progress"""
    user_key = f"user_{user_id}"
    if user_key not in user_progress:
        return {
            "success": True,
            "courses_completed": 0,
            "courses_in_progress": 0,
            "total_lessons_completed": 0,
            "quizzes_passed": 0,
            "courses": []
        }
    
    progress = user_progress[user_key]
    return {
        "success": True,
        "progress": progress
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8091))
    uvicorn.run(app, host="0.0.0.0", port=port)