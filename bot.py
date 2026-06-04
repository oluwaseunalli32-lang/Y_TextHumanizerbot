import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Enable logging to track down any issues
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables from Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
    welcome_text = (
        "🤖 **Welcome to the Y Text Humanizer!**\n\n"
        "Send me any AI-generated text, and I will rewrite it to sound completely "
        "natural, human, and conversational while keeping your original meaning intact."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def humanize_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes the user's text using Gemini."""
    user_text = update.message.text
    
    # Send a placeholder typing action so the user knows the bot is working
    await update.message.reply_chat_action(action="typing")

    try:
        # Use the ultra-stable model layout
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are an expert human editor. Rewrite the user's text to make it sound "
                "completely human, natural, and conversational. Remove typical AI structures, "
                "clichés, repetitive phrasing, and overly robotic transitions. Keep the original core "
                "message, facts, and intent perfectly intact. Provide ONLY the final edited text."
            )
        )

        response = model.generate_content(user_text)
        humanized_text = response.text
        
        await update.message.reply_text(humanized_text)

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("⚠️ Sorry, I encountered an error while rewriting your text. Please try again later.")

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        logger.error("Missing environment variables! Make sure TELEGRAM_TOKEN and GEMINI_API_KEY are in Render settings.")
        return

    # Create the Telegram Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, humanize_text))

    # Run the bot using polling
    logger.info("Starting bot polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
