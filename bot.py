# bot.py
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from db import init_db, SessionLocal, users, jobs
from fetcher import run_job_fetch
from autofill import autofill_job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Simple in-memory user profile for demo. Later read/write to DB.
USER_PROFILE = {
    "full_name": "Kalaiyarasan S",
    "email": "kalaiyarasansinfo@gmail.com",
    "phone": "+916383247700",
    "location": "Coimbatore"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I will find jobs for you. Use /list to view jobs, /fetch to run fetch now.")

async def fetch_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = run_job_fetch()
    await update.message.reply_text(f"Fetched {count} jobs.")

async def list_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess = SessionLocal()
    rows = sess.execute(jobs.select().order_by(jobs.c.fetched_at.desc()).limit(10)).fetchall()
    sess.close()
    if not rows:
        await update.message.reply_text("No jobs found yet. Use /fetch.")
        return
    for r in rows:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Apply (Auto-fill)", callback_data=f"apply:{r.id}")]])
        text = f"*{r.title}* — {r.company}\n{r.location}\n{r.link}"
        await update.message.reply_markdown(text, reply_markup=kb)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("apply:"):
        job_db_id = int(data.split(":",1)[1])
        await q.edit_message_text("Starting autofill (semi-auto). I'll send the filled page screenshot and the link.")
        success, info = autofill_job(job_db_id, USER_PROFILE)
        if success:
            await context.bot.send_message(q.from_user.id, f"Autofill done. Open the link and verify before final submit:\n{info['url']}")
            if info.get("screenshot_path"):
                await context.bot.send_photo(q.from_user.id, photo=open(info["screenshot_path"], "rb"))
        else:
            await context.bot.send_message(q.from_user.id, f"Autofill failed: {info.get('error')}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start /fetch /list")

def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fetch", fetch_now))
    app.add_handler(CommandHandler("list", list_jobs))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(CommandHandler("help", help_cmd))

    # scheduler to run fetch periodically
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_job_fetch, "interval", minutes=30)
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
