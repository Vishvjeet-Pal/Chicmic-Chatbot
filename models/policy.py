from sqlalchemy import Column, Integer, String 
from database import Base

class Policy(Base):
    __tablename__="policy"

    p_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    category = Column(String, index=True)
    