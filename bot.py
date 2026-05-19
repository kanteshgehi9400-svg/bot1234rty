import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from database import Database
from payment import PaymentChecker
from tips import GROWTH_TIPS, PRO_TIPS, PREMIUM_TIPS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
WAITING_CHANNEL = 1
WAITING_PAYMENT = 2

db = Database()
payment_checker = PaymentChecker()

PLANS = {
    "basic": {"name": "Basic", "price": 5, "days": 30, "tips": "basic"},
    "pro": {"name": "Pro", "price": 10, "days": 30, "tips": "pro"},
    "premium": {"name": "Premium", "price": 20, "days": 30, "tips": "premium"},
}

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "TTWYTUp1VEbTkQJcwnmujwsfKJ6Ud3Y3au")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username or user.first_name)

    keyboard = [
        [InlineKeyboardButton("📦 View Plans", callback_data="plans")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
        [InlineKeyboardButton("💡 Free Tips", callback_data="free_tips")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Welcome to *Telegram & WhatsApp Growth Bot*, {user.first_name}!\n\n"
        "🚀 I help you grow your Telegram channel with *real strategies* used by top creators.\n\n"
        "✅ Daily growth tips\n"
        "✅ Engagement strategies\n"
        "✅ Content planning\n"
        "✅ Monetization advice\n\n"
        "Choose an option below to get started:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "plans":
        await show_plans(query)
    elif data == "status":
        await show_status(query)
    elif data == "free_tips":
        await show_free_tips(query)
    elif data == "support":
        await show_support(query)
    elif data.startswith("buy_"):
        plan_key = data.replace("buy_", "")
        await start_purchase(query, context, plan_key)
    elif data == "check_payment":
        await check_user_payment(query, context)
    elif data == "back":
        await back_to_main(query)


async def show_plans(query):
    keyboard = [
        [InlineKeyboardButton("⭐ Basic — $5/month", callback_data="buy_basic")],
        [InlineKeyboardButton("🔥 Pro — $10/month", callback_data="buy_pro")],
        [InlineKeyboardButton("💎 Premium — $20/month", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📦 *Our Growth Plans*\n\n"
        "⭐ *Basic — $5/month*\n"
        "• Daily growth tips\n"
        "• Basic engagement strategies\n"
        "• Content ideas\n\n"
        "🔥 *Pro — $10/month*\n"
        "• Everything in Basic\n"
        "• Advanced growth hacks\n"
        "• Viral content formulas\n"
        "• Weekly strategy review\n\n"
        "💎 *Premium — $20/month*\n"
        "• Everything in Pro\n"
        "• Monetization strategies\n"
        "• Personal channel audit tips\n"
        "• Priority support\n"
        "• Exclusive insider tricks\n\n"
        "🔒 Payment via *USDT TRC20* — Safe & Fast",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def start_purchase(query, context, plan_key):
    plan = PLANS[plan_key]
    context.user_data["selected_plan"] = plan_key

    keyboard = [
        [InlineKeyboardButton("✅ I've Sent Payment", callback_data="check_payment")],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="plans")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"💳 *Payment for {plan['name']} Plan — ${plan['price']}*\n\n"
        f"Send exactly *${plan['price']} USDT TRC20* to:\n\n"
        f"`{WALLET_ADDRESS}`\n\n"
        "📋 *Steps:*\n"
        "1️⃣ Copy the wallet address above\n"
        "2️⃣ Send exact amount via Binance or any TRC20 wallet\n"
        "3️⃣ Click 'I've Sent Payment' below\n"
        "4️⃣ Wait 1-5 mins for confirmation\n\n"
        "⚠️ *Important:* Send exact amount only\n"
        "🌐 Network: *TRC20 (Tron)* — NOT ERC20",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def check_user_payment(query, context):
    user_id = query.from_user.id
    plan_key = context.user_data.get("selected_plan", "basic")
    plan = PLANS[plan_key]

    await query.edit_message_text(
        "🔍 *Checking your payment...*\n\n"
        "Please wait a moment ⏳",
        parse_mode="Markdown"
    )

    # Check payment via TronScan API
    payment_confirmed = await payment_checker.check_payment(user_id, plan["price"])

    if payment_confirmed:
        expiry = datetime.now() + timedelta(days=plan["days"])
        db.activate_user(user_id, plan_key, expiry)

        keyboard = [[InlineKeyboardButton("🚀 Get My Tips Now!", callback_data="status")]]
        await query.edit_message_text(
            f"🎉 *Payment Confirmed! Welcome to {plan['name']}!*\n\n"
            f"✅ Your subscription is active for *{plan['days']} days*\n"
            f"📅 Expires: {expiry.strftime('%d %b %Y')}\n\n"
            "You'll receive daily growth tips automatically!\n"
            "Use /tips anytime to get instant tips 💡",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Notify admin
        if ADMIN_ID:
            await context.bot.send_message(
                ADMIN_ID,
                f"💰 New Payment!\n"
                f"User: @{query.from_user.username or query.from_user.first_name}\n"
                f"Plan: {plan['name']} — ${plan['price']}\n"
                f"ID: {user_id}"
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Check Again", callback_data="check_payment")],
            [InlineKeyboardButton("📞 Contact Support", callback_data="support")],
        ]
        await query.edit_message_text(
            "⏳ *Payment Not Found Yet*\n\n"
            "Possible reasons:\n"
            "• Transaction still processing (wait 2-5 mins)\n"
            "• Wrong network used (must be TRC20)\n"
            "• Wrong amount sent\n\n"
            "Please check and try again, or contact support.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_status(query):
    user_id = query.from_user.id
    user = db.get_user(user_id)

    if not user or not user.get("plan"):
        keyboard = [
            [InlineKeyboardButton("📦 View Plans", callback_data="plans")],
            [InlineKeyboardButton("💡 Free Tips", callback_data="free_tips")],
        ]
        await query.edit_message_text(
            "📊 *Your Status*\n\n"
            "❌ No active subscription\n\n"
            "Get a plan to receive daily growth tips and strategies!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    expiry = user.get("expiry")
    days_left = (expiry - datetime.now()).days if expiry else 0

    keyboard = [[InlineKeyboardButton("💡 Get Tips Now", callback_data="free_tips")]]
    await query.edit_message_text(
        f"📊 *Your Subscription*\n\n"
        f"✅ Plan: *{user['plan'].capitalize()}*\n"
        f"📅 Days Left: *{days_left} days*\n"
        f"📅 Expires: {expiry.strftime('%d %b %Y') if expiry else 'N/A'}\n\n"
        "Use /tips anytime to get your daily growth tip!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_free_tips(query):
    import random
    tip = random.choice(GROWTH_TIPS["free"])
    keyboard = [
        [InlineKeyboardButton("🔥 Get More Tips (Pro)", callback_data="plans")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
    ]
    await query.edit_message_text(
        f"💡 *Free Growth Tip*\n\n{tip}\n\n"
        "📈 Upgrade to Pro/Premium for advanced daily tips!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_support(query):
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    await query.edit_message_text(
        "📞 *Support*\n\n"
        "For any issues contact:\n"
        f"👤 @{os.getenv('SUPPORT_USERNAME', 'SaajwalBudhana')}\n\n"
        "⏰ Response time: Within 24 hours",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_to_main(query):
    keyboard = [
        [InlineKeyboardButton("📦 View Plans", callback_data="plans")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
        [InlineKeyboardButton("💡 Free Tips", callback_data="free_tips")],
        [InlineKeyboardButton("📞 Support", callback_data="support")],
    ]
    await query.edit_message_text(
        "🏠 *Main Menu*\n\n"
        "Choose an option below:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user or not user.get("plan"):
        await update.message.reply_text(
            "❌ You need an active subscription to get tips!\n\n"
            "Use /start to view plans.",
            parse_mode="Markdown"
        )
        return

    plan = user.get("plan", "basic")
    import random

    if plan == "premium":
        all_tips = GROWTH_TIPS["free"] + PRO_TIPS + PREMIUM_TIPS
    elif plan == "pro":
        all_tips = GROWTH_TIPS["free"] + PRO_TIPS
    else:
        all_tips = GROWTH_TIPS["free"] + GROWTH_TIPS["basic"]

    tip = random.choice(all_tips)
    await update.message.reply_text(
        f"💡 *Your Growth Tip*\n\n{tip}\n\n"
        "📈 Keep growing! Use /tips anytime for more.",
        parse_mode="Markdown"
    )


async def send_daily_tips(context: ContextTypes.DEFAULT_TYPE):
    """Send daily tips to all active subscribers"""
    import random
    active_users = db.get_active_users()

    for user in active_users:
        try:
            plan = user.get("plan", "basic")
            if plan == "premium":
                all_tips = GROWTH_TIPS["free"] + PRO_TIPS + PREMIUM_TIPS
            elif plan == "pro":
                all_tips = GROWTH_TIPS["free"] + PRO_TIPS
            else:
                all_tips = GROWTH_TIPS["free"] + GROWTH_TIPS["basic"]

            tip = random.choice(all_tips)
            await context.bot.send_message(
                user["user_id"],
                f"🌅 *Daily Growth Tip*\n\n{tip}\n\n"
                "📈 Consistency is key! See you tomorrow 🚀",
                parse_mode="Markdown"
            )
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send tip to {user['user_id']}: {e}")


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    stats = db.get_stats()
    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"👥 Total Users: {stats['total']}\n"
        f"✅ Active Subs: {stats['active']}\n"
        f"⭐ Basic: {stats['basic']}\n"
        f"🔥 Pro: {stats['pro']}\n"
        f"💎 Premium: {stats['premium']}\n"
        f"💰 Est. Monthly: ${stats['revenue']}",
        parse_mode="Markdown"
    )


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not set!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tips", tips_command))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Daily tips at 9 AM UTC
    job_queue = app.job_queue
    job_queue.run_daily(send_daily_tips, time=datetime.strptime("09:00", "%H:%M").time())

    logger.info("Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
