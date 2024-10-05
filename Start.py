from tg_bot import Bot
from my_tokens import spreadsheet_id, gemini_token, bot_token


class Start:
    def __init__(self):
        self.bot = Bot(bot_token, gemini_token, spreadsheet_id)

    def start(self):
        self.bot.run()


if __name__ == "__main__":
    Start().start()
