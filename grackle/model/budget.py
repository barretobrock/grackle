import enum
from sqlalchemy import Column, Integer, ForeignKey, Text, VARCHAR, Float, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from .base import Base


class BudgetClasses(enum.Enum):
    """Budget classes"""
    MONTHLY = 'MONTHLY'
    QUARTERLY = 'QUARTERLY'
    ANNUAL = 'ANNUAL'


class TableBudget(Base):
    """Budget table"""
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    budget_class = Column(Enum(BudgetClasses), default=BudgetClasses.MONTHLY, nullable=False)
    amount = Column(Float(2), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)

