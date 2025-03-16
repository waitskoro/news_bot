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

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)