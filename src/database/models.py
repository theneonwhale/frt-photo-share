import enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TransformationsType(enum.Enum):
    basic: str = 'basic'
    avatar: str = 'avatar'
    gray: str = 'gray'
    cartoon: str = 'cartoon'
    sepia: str = 'sepia'
    old: str = 'old'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)


image_m2m_tag = Table('image_m2m_tag',
                      Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('image_d', Integer, ForeignKey('images.id', ondelete="CASCADE")),
                      Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
                      )


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    type = Column('TransformationsType', Enum(TransformationsType), default=TransformationsType.basic)
    link = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship("User", backref="images")
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False, unique=True)