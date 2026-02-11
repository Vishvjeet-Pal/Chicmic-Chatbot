from sqlalchemy import Column, Integer, String 
from database import Base

class PersonalInfo(Base):
    __tablename__="personal_info"

    p_id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String)
    category = Column(String, index=True)
    