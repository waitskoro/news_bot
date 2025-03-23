import threading
import time

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.database import Database
from bot.parsers.interfax import Interfax
from bot.parsers.bloomberg import Bloomberg
from bot.parsers.komersant import Kommersant
from bot.handlers.config_parser import Config


class Main:
    def __init__(self):
        self.interfax = None
        self.kommersant = None
        self.bloomberg = None

        self.__database = None
        self.__config = Config()

        self.__user_id = None
        self.__last_message_ids = {}

        self.__init_database()
        self.__init_sources()

        self.__bot = telebot.TeleBot(self.__config.get_token_config())

        self.__bot.message_handler(commands=['start'])(self.start_message)
        self.__bot.callback_query_handler(func=lambda call: True)(self.callback_handler)

    def __init_database(self):
        self.__database = Database(self.__config.get_database_config())
        self.__database.add_source('Коммерсантъ', 'https://www.kommersant.ru/lenta/news?from=lenta_news')
        self.__database.add_source('Интерфакс', 'https://www.interfax.ru/')
        self.__database.add_source('Bloomberg', 'https://www.bloomberg.com/latest?utm_campaign=latest')

    def bloomberg_init(self):
        bloomberg_set = self.__database.get_source('Bloomberg')
        try:
            self.bloomberg = Bloomberg(bloomberg_set.url, self.__database)
        except Exception as e:
            print(f"Ошибка")

    def kommersant_init(self):
        kommersant_set = self.__database.get_source('Коммерсантъ')
        try:
            self.kommersant = Kommersant(kommersant_set.url, self.__database)
        except Exception as e:
            print(f"Ошибка")

    def interfax_init(self):
        intefax_set = self.__database.get_source('Интерфакс')
        try:
            self.interfax = Interfax(intefax_set.url, self.__database)
        except Exception as e:
            print(f"Ошибка")

    def __init_sources(self):
        # Инициализация парсеров (без изменений)
        init_threads = [
            threading.Thread(target=self.bloomberg_init),
            threading.Thread(target=self.kommersant_init),
            threading.Thread(target=self.interfax_init)
        ]

        for thread in init_threads:
            thread.start()

        for thread in init_threads:
            thread.join()

        if not all([self.interfax, self.bloomberg, self.kommersant]):
            raise RuntimeError("Один из парсеров не инициализирован")

        self.start_periodic_scraping()

    def start_periodic_scraping(self):
        """Запускает методы scraping каждые 2 минуты в отдельных потоках."""

        def run_periodically(parser):
            while True:
                try:
                    parser.scraping()
                except Exception as e:
                    print(f"Ошибка в скрапинге {parser.__class__.__name__}: {e}")
                time.sleep(180)  # 3 минуты

        scraping_threads = [
            threading.Thread(target=run_periodically, args=(self.kommersant,), daemon=True),
            threading.Thread(target=run_periodically, args=(self.bloomberg,), daemon=True),
            threading.Thread(target=run_periodically, args=(self.interfax,), daemon=True)
        ]

        for thread in scraping_threads:
            thread.start()

        print("Периодический скрапинг запущен")

    def start_message(self, message):
        self.__user_id = message.chat.id
        self.__database.add_user(message.chat.id, message.chat.username)

        if self.__user_id in self.__last_message_ids:
            try:
                self.__bot.delete_message(
                    chat_id=self.__user_id,
                    message_id=self.__last_message_ids[self.__user_id]
                )
            except telebot.apihelper.ApiException as e:
                print(f"Ошибка удаления сообщения: {e}")

        keyboard = self.__create_updated_keyboard()

        sent_message = self.__bot.send_message(
            message.chat.id,
            "Привет!\nВыбери источник(и) информации от которого ты хочешь получать новости:",
            reply_markup=keyboard
        )

        self.__last_message_ids[self.__user_id] = sent_message.message_id

    def callback_handler(self, call):
        data = call.data
        user_id = call.from_user.id

        if data.startswith("subscribe_"):
            source_id = int(data.split("_")[1])
            try:
                # Переключаем подписку и получаем результат
                result = self.__database.add_subscription(user_id, source_id)

                if result == 'added':
                    # Обновляем интерфейс
                    new_keyboard = self.__create_updated_keyboard()
                    self.__bot.edit_message_reply_markup(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=new_keyboard
                    )
                    self.__bot.answer_callback_query(
                        call.id,
                        "✅ Подписка активирована",
                        show_alert=False
                    )

                elif result == 'removed':
                    # Обновляем интерфейс
                    new_keyboard = self.__create_updated_keyboard()
                    self.__bot.edit_message_reply_markup(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=new_keyboard
                    )
                    self.__bot.answer_callback_query(
                        call.id,
                        "✅ Подписка отменена",
                        show_alert=False
                    )

                else:
                    self.__bot.answer_callback_query(
                        call.id,
                        "❌ Ошибка при изменении подписки",
                        show_alert=True
                    )

            except Exception as e:
                print(f"Ошибка: {e}")
                self.__bot.answer_callback_query(
                    call.id,
                    "❌ Произошла ошибка",
                    show_alert=True
                )

    def __create_updated_keyboard(self):
        subscriptions = self.__database.get_user_subscriptions(self.__user_id)
        subscribed_ids = {sub.source_id for sub in subscriptions}

        sources = self.__database.get_sources()
        buttons = []
        for source in sources:
            prefix = "✅ " if source.id in subscribed_ids else ""
            buttons.append([InlineKeyboardButton(
                text=f"{prefix}{source.name}",
                callback_data=f"subscribe_{source.id}"
            )])
        return InlineKeyboardMarkup(buttons)

    def run(self):
        self.__bot.infinity_polling()


if __name__ == '__main__':
    main = Main()
    main.run()