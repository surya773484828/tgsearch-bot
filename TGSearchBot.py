# TGSearchBot.py
# Paste this file into your GitHub repo exactly as-is.
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== CONFIG - edit ONLY usernames/links if they change ==========
CHANNEL_1_YT = "https://youtube.com/@ambarstoryuniverse?si=aHVtS0Dd7gyTp_K4"   # Channel 1 -> YouTube
CHANNEL_2 = "@LootPeLootDealsOfficial"   # Channel 2 -> Telegram
CHANNEL_3 = "@AmbarStoryUniverseOfficial" # Channel 3 -> Telegram

OKSEARCH_LINK = "https://t.me/OKSearch?start=8286109879"

# Refer & Earn promotional message (bot username shown as clickable link)
REFER_TEXT = (
    "📌 टेलीग्राम का सब कुछ मिलेगा सेकंड्स में!\n"
    "TGsearch Bot से कोई भी Story, Movie, Anime, Lecture या Course सबकुछ तुरंत ढूंढो। 😍\n"
    "💰 Refer & Earn से बढ़िया पैसे भी कमाओ। जल्दी फायदा उठाओ और दोस्तों को भी बताओ!\n"
    "👉 <a href=\"https://t.me/tgsearchingg_Bot\">@tgsearchingg_Bot</a>"
)
# ======================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set. Exiting.")
    raise SystemExit("Set BOT_TOKEN as environment variable on Render before running.")

def main_keyboard():
    kb = [
        [InlineKeyboardButton("Channel 1", url=CHANNEL_1_YT)],
        [InlineKeyboardButton("Channel 2", url=f"https://t.me/{CHANNEL_2.lstrip('@')}")],
        [InlineKeyboardButton("Channel 3", url=f"https://t.me/{CHANNEL_3.lstrip('@')}")],
        [InlineKeyboardButton("I joined ✅", callback_data="check_join")],
        [InlineKeyboardButton("Refer & Earn", callback_data="refer")]
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Welcome! 🎯\n"
        "This is TGSearch Bot.\n"
        "Type any search word (e.g. \"music\", \"news\") and I’ll show results.\n\n"
        "𝐒𝐡𝐚𝐫𝐞 𝐓𝐆𝐬𝐞𝐚𝐫𝐜𝐡 𝐛𝐨𝐭 𝐰𝐢𝐭𝐡 𝟏𝟎 𝐏𝐞𝐫𝐬𝐨𝐧𝐬.\n"
        "𝐘𝐨𝐮 𝐰𝐢𝐥𝐥 𝐄𝐚𝐫𝐧 𝟐𝟎/- 𝐩𝐞𝐫 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥.\n"
        "𝐌𝐢𝐧𝐢𝐦𝐮𝐦 𝐰𝐢𝐭𝐡𝐝𝐫𝐚𝐰𝐚𝐥 𝐚𝐦𝐨𝐮𝐧𝐭 𝐢𝐬 𝟐𝟎𝟎/-\n\n"
        "Join Channels To use this Bot."
    )
    # Include clickable channel usernames below (HTML)
    channels_html = (
        f"\n\nChannels:\n"
        f"<a href=\"https://t.me/{CHANNEL_2.lstrip('@')}\">{CHANNEL_2}</a>\n"
        f"<a href=\"https://t.me/{CHANNEL_3.lstrip('@')}\">{CHANNEL_3}</a>"
    )
    await update.message.reply_text(text + channels_html, reply_markup=main_keyboard(), parse_mode="HTML")

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    channels = [CHANNEL_2, CHANNEL_3]  # verify membership in these two channels
    verified_all = True
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ("creator", "administrator", "member", "restricted"):
                verified_all = False
                break
        except Exception as e:
            logger.warning("get_chat_member failed for %s: %s", ch, e)
            verified_all = False
            break

    if verified_all:
        # Send bold OkSearch link (HTML)
        await query.edit_message_text(f"<b>Click The Link And Start Searching {OKSEARCH_LINK}</b>", parse_mode="HTML")
    else:
        await query.edit_message_text(
            "You are not yet a member of both required channels. Please join both channels and press I joined again.",
            reply_markup=main_keyboard()
        )

async def refer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Send forwardable promotional message (HTML so the @ appears as a link)
    await query.message.reply_text(REFER_TEXT, parse_mode="HTML")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When user types any text, check membership; if verified send OkSearch link,
    # otherwise prompt to join (same behavior as I joined button).
    user = update.message.from_user
    user_id = user.id

    channels = [CHANNEL_2, CHANNEL_3]
    verified_all = True
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ("creator", "administrator", "member", "restricted"):
                verified_all = False
                break
        except Exception as e:
            logger.warning("get_chat_member failed for %s: %s", ch, e)
            verified_all = False
            break

    if verified_all:
        await update.message.reply_text(f"<b>Click The Link And Start Searching {OKSEARCH_LINK}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("Please join the required channels to use this bot.", reply_markup=main_keyboard())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join_callback, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(refer_callback, pattern="^refer$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
