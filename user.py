from sqlalchemy import Column, Integer, String

from base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    tg_id = Column(Integer, nullable=False)
    inn = Column(Integer)
    phone = Column(String)