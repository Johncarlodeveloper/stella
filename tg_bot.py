import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

from DataManager import DataManager
from Image import Image


class Bot:
    def __init__(self, api_key: str, gemini_token: str, spreadsheet_id: str):
        self.data = DataManager("./credentials.json", spreadsheet_id)
        self.token = api_key
        self.image = Image(gemini_token)
        self.user_id = None
        self.description = (
            "🤖 *Hello, I am Stella!*\n\n"
            "This bot is designed to assist you in managing cheque processing tasks. "
            "Please use the buttons below to interact with me.\n\n"
            "Make sure the image is captured in a well-lit area and is clear to retrieve accurate results."
        )
        self.start_keyboard = [
            [
                InlineKeyboardButton("Add new cheque", callback_data='cheques')
            ]
        ]
        self.batch_data = []  # Store extracted data in a batch list

    async def start(self, update: Update, context: CallbackContext) -> None:
        reply_markup = InlineKeyboardMarkup(self.start_keyboard)
        await update.message.reply_text(self.description, reply_markup=reply_markup, parse_mode='Markdown')

    async def button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()  # Acknowledge the callback

        if query.data == 'cheques':
            # Start batch processing mode
            context.user_data['awaiting_cheque_images'] = True
            keyboard = [
                [InlineKeyboardButton("Cancel", callback_data='start')],
                [InlineKeyboardButton("Push", callback_data='process_batch')]
            ]
            await query.edit_message_text(
                text="📮 Once you send an image, I will automatically delete it from this chat after reading it.\n\n"
                     "🤖 Please wait while I process the images before pushing....\n",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data == 'process_batch':
            # Process all images in the batch
            self.data.update_data(self.batch_data)  # Save batch data to CSV
            self.batch_data = []  # Clear batch data after processing
            keyboard = [
                [InlineKeyboardButton("Add another batch", callback_data='cheques')],
                [InlineKeyboardButton("Back", callback_data='start')]
            ]
            await query.edit_message_text(text="\n 🚀 Push complete!\n",
                                          reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data == 'start':
            context.user_data['awaiting_cheque_images'] = False  # Reset batch mode state
            await self.start_from_button(query)

    async def handle_image(self, update: Update, context: CallbackContext) -> None:
        self.user_id = update.message.from_user.id
        print(f"User {self.user_id} sent an image.")  # Debugging print statement

        # Store the message ID for deletion later
        message_id = update.message.message_id

        # Check if awaiting batch images
        if context.user_data.get('awaiting_cheque_images'):
            photo = update.message.photo[-1]  # Get the highest resolution photo
            file = await context.bot.get_file(photo.file_id)
            downloaded_file = await file.download_as_bytearray()

            file_path = "cheque_image.jpg"  # Save the image temporarily
            with open(file_path, "wb") as f:
                f.write(downloaded_file)

            # Process the image and extract data
            extracted_data = self.image.extract_data(file_path)

            # Clean up by removing the temporary file
            os.remove(file_path)

            # Add to batch data list
            self.batch_data.append(extracted_data.split(" // "))  # Convert to list format for CSV row

            # Delete the user message after processing
            await context.bot.delete_message(chat_id=self.user_id, message_id=message_id)
        else:
            print("State is not set for awaiting_cheque_images.")  # Debugging print statement

    async def start_from_button(self, query: Update) -> None:
        reply_markup = InlineKeyboardMarkup(self.start_keyboard)
        await query.edit_message_text(self.description, reply_markup=reply_markup, parse_mode='Markdown')

    def run(self):
        # Create the application and add handlers
        application = Application.builder().token(self.token).build()

        # Use the user_data dictionary to keep track of states
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CallbackQueryHandler(self.button))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))

        # Start the bot
        application.run_polling()
