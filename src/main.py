import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.config_parser import Config
from src.database import Database


class Main:
    def __init__(self):
        self.__database = None
        self.__config = Config()

        self.__init_database()

        self.__bot = telebot.TeleBot(self.__config.get_token_config())

        self.__bot.message_handler(commands=['start'])(self.start_message)

    def __init_database(self):
        self.__database = Database(self.__config.get_database_config())
        self.__database.add_source('Российская газета', 'https://www.rg.ru/news/')
        self.__database.add_source('Интерфакс', 'https://www.interfax.ru/')

    def start_message(self, message):
        self.__database.add_user(message.chat.username)

        sources = self.__database.get_sources()
        buttons_list = []
        for source in sources:
            buttons_list.append([InlineKeyboardButton(text=source.name, callback_data=source.name)])

        keyboard_inline_buttons = InlineKeyboardMarkup(buttons_list)
        self.__bot.send_message(message.chat.id, "Привет! \n"
                                                      "Выбери источник(и) информации от которого "
                                                      "ты хочешь получать новости:",
                                                      reply_markup=keyboard_inline_buttons)

    def run(self):
        self.__bot.infinity_polling()

if __name__ == '__main__':
    main = Main()
    main.run()