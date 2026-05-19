# Telegram Growth Bot 🚀
### By Saajwal Budhana

Automated Telegram growth tips bot with USDT TRC20 payment system.

---

## Files Structure
```
telegram_growth_bot/
├── bot.py          # Main bot logic
├── database.py     # SQLite database
├── payment.py      # USDT payment checker
├── tips.py         # All growth tips content
├── requirements.txt
├── Procfile        # Railway config
└── .env.example    # Environment variables template
```

---

## Step 1 — Create Your Bot

1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Give it a name: `Saajwal Growth Bot`
4. Give it a username: `SaajwalGrowthBot`
5. Copy the **TOKEN** — you'll need it

---

## Step 2 — Get Your Admin ID

1. Open Telegram → search **@userinfobot**
2. Send `/start`
3. Copy your **ID number** (e.g. 123456789)

---

## Step 3 — Deploy on Railway

1. Go to **railway.app** → Sign up free
2. Click **New Project** → **Deploy from GitHub**
3. Upload these files to a GitHub repo first (or use Railway CLI)
4. In Railway project → **Variables** tab → Add these:

```
BOT_TOKEN = (your bot token from BotFather)
WALLET_ADDRESS = TTWYTUp1VEbTkQJcwnmujwsfKJ6Ud3Y3au
ADMIN_ID = (your Telegram ID number)
SUPPORT_USERNAME = SaajwalBudhana
```

5. Railway will auto-deploy — your bot goes live! ✅

---

## Step 4 — Upload to GitHub (Easy Way)

1. Go to **github.com** → New repository → Name: `growth-bot`
2. Upload all files
3. Connect GitHub repo to Railway

---

## How It Works

```
User → /start → Sees plans
User → Selects plan → Gets wallet address
User → Sends USDT → Clicks "I've Sent Payment"
Bot → Checks TronScan API automatically
Bot → Activates subscription ✅
Bot → Sends daily tips at 9 AM UTC
```

---

## Bot Commands

- `/start` — Main menu
- `/tips` — Get instant tip (subscribers only)
- `/stats` — Admin only: see revenue & user stats

---

## Revenue Potential

| Subscribers | Plan | Monthly |
|------------|------|---------|
| 100 | Basic $5 | $500 |
| 50 | Pro $10 | $500 |
| 25 | Premium $20 | $500 |
| **175 total** | **Mixed** | **$1,500** |

With your 30k YouTube subscribers → very achievable! 💰

---

## Support
Contact: @SaajwalBudhana
