from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

# Таблица для взаимосвязи подписок (фолловеров)
followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    posts = relationship('Post', back_populates='author')
    comments = relationship('Comment', back_populates='author')
    reactions = relationship('Reaction', back_populates='user')
    # Пользователь подписан на других пользователей
    followed = relationship('User', 
                            secondary=followers,
                            primaryjoin=id==followers.c.follower_id,
                            secondaryjoin=id==followers.c.followed_id,
                            backref="followers")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_url = Column(String, nullable=False)
    caption = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    reactions = relationship('Reaction', back_populates='post')

class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    post = relationship('Post', back_populates='comments')
    author = relationship('User', back_populates='comments')

class Reaction(Base):
    __tablename__ = 'reactions'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String, nullable=False)  # Например, "like", "heart", "smile" и т.д.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    post = relationship('Post', back_populates='reactions')
    user = relationship('User', back_populates='reactions')


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)