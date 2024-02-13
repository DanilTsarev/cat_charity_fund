from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.abstract_base import AbstractBase


class Donation(AbstractBase):

    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
