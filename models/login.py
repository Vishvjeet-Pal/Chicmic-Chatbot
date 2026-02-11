from sqlalchemy import Column, Integer, String 
from database import Base

class Login(Base):
    __tablename__="login"

    l_id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String)
    category = Column(String, index=True)
    