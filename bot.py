import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

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
        # Prompt engineering to make Gemini behave like a text humanizer
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an expert editor. Your task is to rewrite the user's text to make it sound "
                    "completely human, natural, and conversational. Remove any typical AI phrasing, "
                    "clichés, repetitive structures, or overly robotic transitions. Maintain the core "
                    "message, facts, and intent of the original text, but make the flow flawless and engaging."
                ),
                temperature=0.7,
            )
        )
        
        humanized_text = response.text
        await update.message.reply_text(humanized_text)

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("⚠️ Sorry, I encountered an error while rewriting your text. Please try again later.")

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        logger.error("Missing environment variables!")
        return

    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, humanize_text))

    # Run the bot using polling
    application.run_polling()

if __name__ == "__main__":
    main()
