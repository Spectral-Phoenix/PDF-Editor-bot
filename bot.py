import os
import telebot
from dotenv import load_dotenv
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome! Send me a PDF file and the page numbers to trim (e.g., '1-5').")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        if message.document.mime_type == 'application/pdf':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('input.pdf', 'wb') as file:
                file.write(downloaded_file)

            bot.reply_to(message, "PDF file received. Now send me the page numbers to trim (e.g., '1-5').")
        else:
            bot.reply_to(message, "Please send a PDF file.")
    except Exception as e:
        logger.error(f"Error in handle_document: {e}")
        bot.reply_to(message, "An error occurred while processing the document. Please try again.")

@bot.message_handler(func=lambda message: True)
def handle_page_numbers(message):
    page_numbers = message.text.split('-')
    if len(page_numbers) == 2:
        try:
            start_page = int(page_numbers[0])
            end_page = int(page_numbers[1])

            with open('input.pdf', 'rb') as file:
                pdf_reader = PdfFileReader(file)
                pdf_writer = PdfFileWriter()

                for page in range(start_page - 1, end_page):
                    pdf_writer.addPage(pdf_reader.getPage(page))

                with open('output.pdf', 'wb') as output_file:
                    pdf_writer.write(output_file)

                with open('output.pdf', 'rb') as file:
                    bot.send_document(message.chat.id, file)

            os.remove('input.pdf')
            os.remove('output.pdf')
        except Exception as e:
            logger.error(f"Error in handle_page_numbers: {e}")
            bot.reply_to(message, f"An error occurred: {str(e)}")
    else:
        bot.reply_to(message, "Invalid page numbers format. Please provide the page numbers in the format '1-5'.")

bot.polling(none_stop=True)
