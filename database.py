import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Using SQLite for now, easy to switch to PostgreSQL by changing the DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///finance_tracker.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
    expenses = relationship("Expense", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    category = Column(String)
    date = Column(Date)
    notes = Column(String)
    type = Column(String) # 'Expense' or 'Income'
    
    user = relationship("User", back_populates="expenses")

class Portfolio(Base):
    __tablename__ = "portfolio"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_type = Column(String) # mutual fund, stock, crypto
    category = Column(String) # large cap, mid cap, small cap, flexi cap
    name = Column(String)
    invested_amount = Column(Float)
    current_value = Column(Float)
    
    user = relationship("User", back_populates="portfolios")

def init_db():
    Base.metadata.create_all(bind=engine)
