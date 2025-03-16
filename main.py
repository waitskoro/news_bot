import json
import telebot
from telebot import types

def download_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

class Main:
    def __init__(self):
        self.__config = download_config('config.json')
        self.__bot = telebot.TeleBot(self.__config['token'])

        self.__bot.message_handler(commands=['start'])(self.start_message)

    def run(self):
        self.__bot.infinity_polling()

    def start_message(self, message):
        self.__bot.send_message(message.chat.id, "Hello! Welcome to the bot.")

if __name__ == '__main__':
    main = Main()
    main.run()