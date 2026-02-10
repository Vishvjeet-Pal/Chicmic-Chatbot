from sqlalchemy import Column, String, Integer
from database import Base

class FAQ(Base):
    __tablename__="help"

    q_id=Column(Integer, primary_key=True, index=True)
    question=Column(String, index=True)
    answer=Column(String)
