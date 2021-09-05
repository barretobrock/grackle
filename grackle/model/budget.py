from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    VARCHAR,
    Float
)
from sqlalchemy.orm import relationship
from .base import Base


class TableBudget(Base):
    """Budget table"""
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('TableAccounts', back_populates='budgets')
    name = Column(VARCHAR, nullable=False)
    amount = Column(Float(2), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
