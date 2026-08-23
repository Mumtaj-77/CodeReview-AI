from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50))
    filename = Column(String(255))
    total_bugs = Column(Integer, default=0)
    total_security = Column(Integer, default=0)
    total_fixes = Column(Integer, default=0)
    severity = Column(String(50))
    model_used = Column(String(100))
    review_time = Column(Float)
    report = Column(JSON)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default=func.now())

class BugRecord(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, index=True)
    line = Column(Integer)
    severity = Column(String(50))
    category = Column(String(100))
    description = Column(Text)
    fix = Column(Text)