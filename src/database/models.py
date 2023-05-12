import enum

from sqlalchemy import Column, Boolean, Date, DateTime, Enum, ForeignKey, func, Integer, String, Table 
from sqlalchemy.orm import relationship, declarative_base  # ?!
from sqlalchemy.ext.declarative import declarative_base  # ?!
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

# from src.database.db import Base
Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class User(Base):
    """Base User class."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # not 10, because store hash, not password
    created_at = Column('crated_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)  # whether the user's email was confirmed


class TransformationsType(enum.Enum):
    basic: str = 'basic'
    avatar: str = 'avatar'
    black_white: str = 'black_white'
    delete_bg: str = 'delete_bg'
    cartoonify: str = 'cartoonify'
    oil_paint: str = 'oil_paint'
    sepia: str = 'sepia'
    vector: str = 'vector'
    outline: str = 'outline'


image_m2m_tag = Table('image_m2m_tag',
                      Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('image_d', Integer, ForeignKey('images.id', ondelete="CASCADE")),
                      Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
                      )


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    type = Column('TransformationsType', Enum(TransformationsType), default=TransformationsType.basic)
    link = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', backref="images")
    tags = relationship('Tag', secondary=image_m2m_tag, backref='images')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False, unique=True)


# alembic init migrations
# migrations/env.py ... set
# alembic revision --autogenerate -m 'Init'
# alembic upgrade head
