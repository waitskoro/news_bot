from sqlalchemy import BigInteger, Integer, String, Text, Column, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))

    subscriptions = relationship('Subscribe', back_populates='user')


class Source(Base):
    __tablename__ = 'Source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False, unique=True)

    news = relationship('News', back_populates='source')
    subscriptions = relationship('Subscribe', back_populates='source')


class News(Base):
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    link = Column(Text, nullable=False, unique=True)
    datetime = Column(DateTime, nullable=False)
    magazine_id = Column(Integer, ForeignKey('Source.id'), nullable=False)

    source = relationship('Source', back_populates='news')


class Subscribe(Base):
    __tablename__ = 'Subscribes'
    __table_args__ = (
        UniqueConstraint('user_id', 'magazine_id', name='unique_subscription'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    magazine_id = Column(Integer, ForeignKey('Source.id'), nullable=False)

    user = relationship('User', back_populates='subscriptions')
    source = relationship('Source', back_populates='subscriptions')