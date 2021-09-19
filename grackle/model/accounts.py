import enum
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base


class AccountClass(enum.Enum):
    """A more traditional way of classifying accounts"""
    ASSET = 1
    LIABILITY = 2
    EQUITY = 3
    INCOME = 4
    EXPENSE = 5
    CASH = 6
    BANK = 7
    RECEIVABLE = 8
    STOCK = 9
    CREDIT = 10


class AccountCategory(enum.Enum):
    """A slightly more nuanced way of organizing accounts in a way that better aligns with my reports"""
    CHECKING = 1
    SAVINGS = 2
    CREDIT_CARD = 3
    LOAN = 4
    OTHER = 5


class Currencies(enum.Enum):
    EUR = 1
    GBP = 2
    USD = 3


class TableAccounts(Base):
    """Accounts table"""
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_class = Column(Enum(AccountClass), nullable=False)
    account_category = Column(Enum(AccountCategory), nullable=False)
    account_currency = Column(Enum(Currencies), default=Currencies.USD, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    transactions = relationship('TableTransactions', back_populates='account')
    budgets = relationship('TableBudget', back_populates='account')
    fullname = Column(VARCHAR, nullable=False)
    friendly_name = Column(VARCHAR, nullable=False)
