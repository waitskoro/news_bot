import threading
import time
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from db.database import Database
from bot.parsers.interfax import Interfax
from bot.parsers.bloomberg import Bloomberg
from bot.parsers.komersant import Kommersant
from bot.handlers.config_parser import Config


def log_message(message):
    print(f"[LOG] {message}")

def log_error(error):
    print(f"[ERROR] {error}")

class Main:
    def __init__(self):
        self.__db_user_id = None
        self.parsers = {}
        self.__database = None
        self.__config = Config()
        self.__user_id = None
        self.__last_message_ids = {}

        self.__init_database()
        self.__init_sources()

        self.__bot = telebot.TeleBot(self.__config.get_token_config())

        self.__bot.message_handler(commands=['start'])(self.start_message)
        self.__bot.callback_query_handler(func=lambda call: True)(self.callback_handler)

        self.start_news_distribution()
        self.__bot.message_handler(commands=['news'])(self.send_latest_news)
        self.__bot.message_handler(content_types=['text'])(self.handle_text_message)

    def __init_database(self):
        self.__database = Database(self.__config.get_database_config())
        sources = [
            ('Коммерсантъ', 'https://www.kommersant.ru/lenta/news?from=lenta_news'),
            ('Интерфакс', 'https://www.interfax.ru/'),
            ('Bloomberg', 'https://www.bloomberg.com/latest?utm_campaign=latest')
        ]
        for name, url in sources:
            self.__database.add_source(name, url)

    def send_latest_news(self, message):
        try:
            user_id = message.chat.id
            subscriptions = self.__database.get_user_subscriptions(user_id)

            if not subscriptions:
                self.__bot.send_message(user_id, "Вы не подписаны ни на один источник.")
                return

            source_ids = [sub.magazine_id for sub in subscriptions]
            latest_news = self.__database.get_latest_news_by_sources(source_ids)

            if not latest_news:
                self.__bot.send_message(user_id, "Пока нет новостей по вашим подпискам.")
                return

            news_by_source = {}
            for news in latest_news:
                source = self.__database.get_source_by_id(news.magazine_id)
                if source.name not in news_by_source:
                    news_by_source[source.name] = []
                news_by_source[source.name].append(news)

            response = []
            for source, news_list in news_by_source.items():
                response.append(f"📰 *{source}*")
                for news in news_list:
                    domain = self.extract_domain(news.link)
                    short_link = f"[{domain}]({news.link})"
                    response.append(f"• {news.title} {short_link}")
                response.append("")

            self.__bot.send_message(
                user_id,
                "\n".join(response),
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except Exception as e:
            log_error(f"Ошибка при отправке новостей: {e}")

    def __create_keyboard(self, keyboard_type='main'):
        if keyboard_type == 'main':
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            keyboard.add("📰 Новости", "⚙️ Настройки", "🚫 Стоп")
            return keyboard
        elif keyboard_type == 'subscriptions':
            subscriptions = self.__database.get_user_subscriptions(self.__user_id)
            subscribed_ids = {sub.magazine_id for sub in subscriptions}
            sources = self.__database.get_sources()
            buttons = []
            for source in sources:
                prefix = "✅ " if source.id in subscribed_ids else ""
                buttons.append([InlineKeyboardButton(
                    text=f"{prefix}{source.name}",
                    callback_data=f"subscribe_{source.id}"
                )])
            return InlineKeyboardMarkup(buttons)

    def start_news_distribution(self):
        def distribution_loop():
            while True:
                try:
                    unsent_news = self.__database.get_unsent_news()
                    for news in unsent_news:
                        subscribers = self.__database.get_subscribers_by_source(news.magazine_id)
                        source = self.__database.get_source_by_id(news.magazine_id)
                        domain = self.extract_domain(news.link)

                        message = (
                            f"🚨 *Новая новость от {source.name}!*\n"
                            f"{news.title}\n"
                            f"[{domain}]({news.link})"
                        )

                        for subscriber in subscribers:
                            user = self.__database.get_user_by_id(subscriber.user_id)
                            if user:
                                try:
                                    self.__bot.send_message(
                                        user.telegram_id,
                                        message,
                                        parse_mode='Markdown',
                                        disable_web_page_preview=True
                                    )
                                except Exception as e:
                                    log_error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")

                        self.__database.mark_news_as_sent(news.id)
                except Exception as e:
                    log_error(f"Ошибка в цикле рассылки: {e}")
                time.sleep(60)

        threading.Thread(target=distribution_loop, daemon=True).start()

    @staticmethod
    def extract_domain(url):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain

    def __init_parser(self, source_name, parser_class):
        source = self.__database.get_source(source_name)
        try:
            self.parsers[source_name] = parser_class(source.url, self.__database)
        except Exception as e:
            log_error(f"Ошибка инициализации парсера {source_name}: {e}")

    def __init_sources(self):
        parsers = {
            'Bloomberg': Bloomberg,
            'Коммерсантъ': Kommersant,
            'Интерфакс': Interfax
        }

        init_threads = []
        for source_name, parser_class in parsers.items():
            thread = threading.Thread(target=self.__init_parser, args=(source_name, parser_class))
            init_threads.append(thread)
            thread.start()

        for thread in init_threads:
            thread.join()

        if not all(self.parsers.values()):
            raise RuntimeError("Один из парсеров не инициализирован")

        self.start_periodic_scraping()

    def start_periodic_scraping(self):
        def run_periodically(parser):
            while True:
                try:
                    parser.scraping()
                except Exception as e:
                    log_error(f"Ошибка в скрапинге {parser.__class__.__name__}: {e}")
                time.sleep(180)  # 3 минуты

        scraping_threads = []
        for parser in self.parsers.values():
            thread = threading.Thread(target=run_periodically, args=(parser,), daemon=True)
            scraping_threads.append(thread)
            thread.start()

        print("Периодический скрапинг запущен")

    def start_message(self, message):
        self.__user_id = message.chat.id
        self.__database.add_user(message.chat.id, message.chat.username)

        self.delete_last_message(self.__user_id)

        sent_message = self.__bot.send_message(
            message.chat.id,
            "Привет!\nВыбери источник(и) информации от которого ты хочешь получать новости:",
            reply_markup=self.__create_keyboard('subscriptions')
        )

        self.__last_message_ids[self.__user_id] = sent_message.message_id

    def handle_text_message(self, message):
        text = message.text.strip().lower()
        log_message(f"Получено сообщение: {text}")

        if text == "📰 новости":
            self.send_latest_news(message)
        elif text == "⚙️ настройки":
            self.show_settings(message)
        elif text == "🚫 стоп":
            self.stop_subscriptions(message)
        else:
            self.__bot.send_message(
                message.chat.id,
                "Используйте кнопки меню для управления",
                reply_markup=self.__create_keyboard('main')
            )

    def show_settings(self, message):
        try:
            self.__user_id = message.chat.id
            log_message(f"Показ настроек для пользователя {self.__user_id}")

            self.delete_last_message(self.__user_id)

            sent_message = self.__bot.send_message(
                message.chat.id,
                "Управление подписками:",
                reply_markup=self.__create_keyboard('subscriptions')
            )

            self.__last_message_ids[self.__user_id] = sent_message.message_id

        except Exception as e:
            log_error(f"Ошибка в show_settings: {e}")
            self.__bot.send_message(
                message.chat.id,
                "⚠️ Произошла ошибка при загрузке настроек",
                reply_markup=self.__create_keyboard('main')
            )

    def stop_subscriptions(self, message):
        user_id = message.chat.id
        log_message(f"Попытка отписки для пользователя {user_id}")

        try:
            success = self.__database.remove_all_subscriptions(user_id)
            if success:
                self.__bot.send_message(
                    user_id,
                    "✅ Все подписки отменены. Вы больше не будете получать новости.",
                    reply_markup=self.__create_keyboard('main')
                )
            else:
                self.__bot.send_message(
                    user_id,
                    "❌ У вас нет активных подписок",
                    reply_markup=self.__create_keyboard('main')
                )
        except Exception as e:
            log_error(f"Ошибка отписки: {e}")
            self.__bot.send_message(
                user_id,
                "⚠️ Произошла ошибка при отмене подписок",
                reply_markup=self.__create_keyboard('main')
            )

    def callback_handler(self, call):
        data = call.data
        user_id = call.from_user.id

        if data.startswith("subscribe_"):
            magazine_id = int(data.split("_")[1])
            try:
                result = self.__database.add_subscription(user_id, magazine_id)
                new_keyboard = self.__create_keyboard('subscriptions')
                self.__bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=new_keyboard
                )
                self.__bot.answer_callback_query(
                    call.id,
                    f"✅ Подписка {'активирована' if result == 'added' else 'отменена'}",
                    show_alert=False
                )
            except Exception as e:
                log_error(f"Ошибка: {e}")
                self.__bot.answer_callback_query(
                    call.id,
                    "❌ Произошла ошибка",
                    show_alert=True
                )

    def delete_last_message(self, user_id):
        if user_id in self.__last_message_ids:
            try:
                self.__bot.delete_message(
                    chat_id=user_id,
                    message_id=self.__last_message_ids[user_id]
                )
            except telebot.apihelper.ApiException as e:
                log_error(f"Ошибка удаления сообщения: {e}")

    def run(self):
        self.__bot.infinity_polling()


if __name__ == '__main__':
    main = Main()
    main.run()