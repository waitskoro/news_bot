import telebot

from src.config_parser import Config
from src.database import Database


class Main:
    def __init__(self):
        self.__config = Config()

        self.__database = Database(self.__config.get_database_config())
        self.__bot = telebot.TeleBot(self.__config.get_token_config())

        self.__bot.message_handler(commands=['start'])(self.start_message)

    def run(self):
        self.__bot.infinity_polling()

    def start_message(self, message):
        self.__bot.send_message(message.chat.id, "Hello! Welcome to the bot.")
        self.__database.add_user(message.chat.username)

if __name__ == '__main__':
    main = Main()
    main.run()