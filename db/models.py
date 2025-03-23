from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    subscribes = relationship("Subscription", back_populates="user")

class NewsSources(Base):
    __tablename__ = "news_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    link = Column(String)
    subscribes = relationship("Subscription", back_populates="source")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_id = Column(Integer, ForeignKey("news_sources.id"))
    user = relationship("User", back_populates="subscribes")
    source = relationship("NewsSources", back_populates="subscribes")