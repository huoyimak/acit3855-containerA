from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class Calories(Base):
    """ Calories """

    __tablename__ = "calories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(250), nullable=False)
    calories = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, user_id, user_name, calories, timestamp):
        """ Initializes a calories reading """
        self.user_id = user_id
        self.user_name = user_name
        self.calories = calories
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a calories reading """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['user_name'] = self.user_name
        dict['calories'] = self.calories
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
