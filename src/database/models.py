import enum

from sqlalchemy import Column, Date, Enum, func, Integer, String, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

# from src.database.db_connect import Base
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
    updated_at = Column('updated_at', DateTime, default=func.now())  # 
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)  # whether the user's email was confirmed


# alembic init migrations
# migrations/env.py ... set
# alembic revision --autogenerate -m 'Init'
# alembic upgrade head
