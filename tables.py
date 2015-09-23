# import os
# import sys
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine

Base = declarative_base()

class Donation(Base):
  __tablename__ = 'donation'

  id                 = Column(Integer, primary_key=True)
  trigger_comment_id = Column(String(30), nullable=False) # The reddit comment ID that triggered Charity-Bot
  user_id            = Column(String(50), nullable=False) # A UUID that we generate to link donation confirmations to donation_id. Looks like: f6decf46-613f-11e5-b5ec-3c970e4cfa1a
  donation_id        = Column(Integer, nullable=True) # The donation ID that just giving gives back to us. We query this to find out the donation status. Looks like: 35533643
  charity_id         = (Integer) # The charity being donated to
  
  # Donator and parent_commenter usernames
  donator            = Column(String(30), nullable=False)
  parent_commenter   = Column(String(30), nullable=False)
  
  donation_url_sent  = Column(Boolean) # Donation url sent via pm
  donator_is_root    = Column(Boolean)




