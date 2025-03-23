from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from db.models import Base, User, Subscription, NewsSources


class Database:
    def __init__(self, config):
        self.__engine = create_engine(f"postgresql://"
                                      f"{config['user']}:"
                                      f"{config['password']}@"
                                      f"{config['host']}/"
                                      f"{config['dbname']}")
        Base.metadata.create_all(bind=self.__engine)

    def get_user(self, username):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_user = db.query(User).filter(User.username == username).first()
            return existing_user.id

    def add_user(self, user_id, username):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_user = db.query(User).filter(User.username == username,
                                                  User.id == user_id).first()
            if existing_user:
                print(f"Пользователь {username} уже существует!")
                return

            user = User(id = user_id, username=username)
            db.add(user)
            db.commit()
            print(f"Пользователь {username} успешно добавлен!")

    def add_subscription(self, user_id: int, source_id: int) -> str:
        print(f"Переключение подписки: user_id={user_id}, source_id={source_id}")

        with Session(autoflush=False, bind=self.__engine) as db:
            try:
                # Ищем существующую подписку
                sub = db.query(Subscription).filter_by(
                    user_id=user_id,
                    source_id=source_id
                ).first()

                if sub:
                    db.delete(sub)
                    db.commit()
                    print("Подписка успешно удалена")
                    return 'removed'
                else:
                    new_sub = Subscription(user_id=user_id, source_id=source_id)
                    db.add(new_sub)
                    db.commit()
                    print("Подписка успешно добавлена")
                    return 'added'

            except Exception as e:
                print(f"Ошибка: {str(e)}")
                db.rollback()
                return 'error'

    def add_source(self, name, link):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_source = db.query(NewsSources).filter(NewsSources.name == name).first()
            if existing_source:
                print(f"Источник новостей {name} уже существует!")
                return

            new_source = NewsSources(name=name, link=link)
            db.add(new_source)
            db.commit()
            print(f"Источник новостей {name} успешно добавлен!")

    def get_sources(self):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(NewsSources).all()

    def get_user_subscriptions(self, user_id: int):
        with Session(autoflush=False, bind=self.__engine) as db:
            return db.query(Subscription).filter(Subscription.user_id == user_id).all()