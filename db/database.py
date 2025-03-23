from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from db.models import Base, Source, News, User, Subscribe


class Database:
    def __init__(self, config):
        self.__engine = create_engine(f"postgresql://"
                                      f"{config['user']}:"
                                      f"{config['password']}@"
                                      f"{config['host']}/"
                                      f"{config['dbname']}")
        Base.metadata.create_all(bind=self.__engine)


    def add_source(self, name, url):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_source = db.query(Source).filter(Source.name == name).first()
            if existing_source:
                print(f"Источник новостей {name} уже существует!")
                return

            new_source = Source(name=name, url=url)
            db.add(new_source)
            db.commit()
            print(f"Источник новостей {name} успешно добавлен!")

    def get_source(self, name):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(Source).filter(func.lower(Source.name) == name.lower()).first()

    def set_news(self, magazine_id, title, url, datetime):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_new = db.query(News).filter(
                func.lower(News.title) == title.lower(),
                News.magazine_id == magazine_id
            ).first()

            if not existing_new:
                new = News(
                    title=title,
                    link=url,
                    datetime=datetime,
                    magazine_id=magazine_id,
                    is_sent=False  # Явно устанавливаем значение
                )
                db.add(new)
                db.commit()

    def add_user(self, telegram_id, username):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_user = db.query(User).filter(func.lower(User.username) == username.lower(),
                                                          User.telegram_id == telegram_id).first()
            if not existing_user:
                user = User(telegram_id=telegram_id, username=username)
                db.add(user)
                db.commit()

    def get_user(self, telegram_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(User).filter(User.telegram_id == telegram_id).first()


    def get_user_subscriptions(self, telegram_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            user = self.get_user(telegram_id=telegram_id)
            if user:
                return db.query(Subscribe).filter(Subscribe.user_id == user.id).all()

    def get_sources(self):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(Source).all()

    def add_subscription(self, telegram_id: int, magazine_id: int) -> str:
        print(f"Переключение подписки: telegram_id={telegram_id}, magazine_id={magazine_id}")

        user_id = self.get_user(telegram_id=telegram_id).id

        with Session(autoflush=False, bind=self.__engine) as db:
            try:
                sub = db.query(Subscribe).filter_by(user_id=user_id, magazine_id=magazine_id).first()

                if sub:
                    db.delete(sub)
                    db.commit()
                    print("Подписка успешно удалена")
                    return 'removed'
                else:
                    new_sub = Subscribe(user_id=user_id, magazine_id=magazine_id)
                    db.add(new_sub)
                    db.commit()
                    print("Подписка успешно добавлена")
                    return 'added'

            except Exception as e:
                print(f"Ошибка: {str(e)}")
                db.rollback()
                return 'error'

    def get_unsent_news(self):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(News).filter(
                News.is_sent.is_(False) | News.is_sent.is_(None)
            ).all()

    def mark_news_as_sent(self, news_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            news = db.query(News).filter(News.id == news_id).first()
            if news:
                news.is_sent = True
                db.commit()

    def get_subscribers_by_source(self, magazine_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(Subscribe).filter(Subscribe.magazine_id == magazine_id).all()

    def get_source_by_id(self, source_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(Source).filter(Source.id == source_id).first()

    def get_latest_news_by_sources(self, source_ids, limit=5):
        with Session(autoflush=False, bind=self.__engine) as db:
            return (db.query(News)
                    .filter(News.magazine_id.in_(source_ids))
                    .order_by(News.datetime.desc())
                    .limit(limit)
                    .all())

    def get_user_by_id(self, user_id):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(User).filter(User.id == user_id).first()

    def remove_all_subscriptions(self, telegram_id):
        """Удаляет все подписки пользователя"""
        with Session(autoflush=False, bind=self.__engine) as db:
            user = self.get_user(telegram_id)
            if user:
                db.query(Subscribe).filter(Subscribe.user_id == user.id).delete()
                db.commit()
                return True
            return False




