from dotenv import load_dotenv
import os
from telegram.constants import ChatAction
import tempfile
import shutil
from multimodal_working import gemini_response, get_latest_pdf_path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

#-------------------------------------------------------------------------------------------------------------------
# Get Telegram Token
load_dotenv(verbose=True)  # Loads variables from .env file
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

#--------------------------------------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a message and I'll reply.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()

    if user_text == "generate pdf":
        pdf_path = get_latest_pdf_path()
        if pdf_path and os.path.exists(pdf_path):
            await update.message.reply_document(document=open(pdf_path, "rb"), caption="Here is your PDF")
        else:
            await update.message.reply_text("No PDF has been generated yet.")
        return
    
    gr_message = {"text": user_text, "files": []}
    history = []  
    
    # Call existing gemini_response function
    reply = gemini_response(gr_message, history)

    # If gemini_response returns a string, send it back to user
    await update.message.reply_text(reply)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        await update.message.reply_text("File upload error.")
        return

    # Let user know it's working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # Download the file to a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, document.file_name)
            file = await document.get_file()
            await file.download_to_drive(file_path)

            print(f"File downloaded to: {file_path}")

            gr_message = {
                "text": update.message.caption or "",
                "files": [file_path],
            }
            history = []
            reply = gemini_response(gr_message, history)

            await update.message.reply_text(reply)
    except Exception as e:
        print(f"Error handling document: {e}")
        await update.message.reply_text("Something went wrong while processing the file.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = update.message.photo
    if not photos:
        await update.message.reply_text("No photo found.")
        return

    # Use the highest resolution photo (last in the list)
    photo = photos[-1]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "uploaded_photo.jpg")
            file = await photo.get_file()
            await file.download_to_drive(file_path)

            print(f"Photo downloaded to: {file_path}")

            gr_message = {
                "text": update.message.caption or "",
                "files": [file_path],
            }
            history = []
            reply = gemini_response(gr_message, history)

            await update.message.reply_text(reply)
    except Exception as e:
        print(f"Error handling photo: {e}")
        await update.message.reply_text("Error processing the image.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started...")
    app.run_polling()

