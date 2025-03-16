from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, Column, Integer, String


class Database:
    def __init__(self, config):
        self.__engine = create_engine(f"postgresql://{config['user']}:"
                                      f"{config['password']}@"
                                      f"{config['host']}/"
                                      f"{config['dbname']}")
        Base.metadata.create_all(bind=self.__engine)

    def add_user(self, username):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"Пользователь {username} уже существует!")
                return

            user = User(username=username)
            db.add(user)
            db.commit()
            print(f"Пользователь {username} успешно добавлен!")

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

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)

class NewsSources(Base):
    __tablename__ = "news_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    link = Column(String)