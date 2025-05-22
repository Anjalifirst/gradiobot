from dotenv import load_dotenv
import os
from multimodal_working import gemini_response

load_dotenv(verbose=True)  # Loads variables from .env file

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a message and I'll reply.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    gr_message = {"text": user_text, "files": []}
    history = []  # Or implement user-specific history later
    
    # Call your existing gemini_response function
    reply = gemini_response(gr_message, history)

    # If gemini_response returns a string, send it back to user
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot started...")
    app.run_polling()
