from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from db.models import Base, Source, News


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

    def set_news(self, source_id, title, url, datetime):
        with Session(autoflush=False, bind=self.__engine) as db:
            existing_new = db.query(News).filter(func.lower(News.title) == title.lower(),
                                                          News.magazine_id == source_id).first()

            if not existing_new:
                new = News(title=title, link=url, datetime=datetime, magazine_id=source_id)
                db.add(new)
                db.commit()
