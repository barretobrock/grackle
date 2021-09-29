import enum
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from .base import Base


class AccountClass(enum.Enum):
    """A more traditional way of classifying accounts"""
    ASSET = enum.auto()
    LIABILITY = enum.auto()
    EQUITY = enum.auto()
    INCOME = enum.auto()
    EXPENSE = enum.auto()
    CASH = enum.auto()
    BANK = enum.auto()
    RECEIVABLE = enum.auto()
    STOCK = enum.auto()
    CREDIT = enum.auto()


class AccountCategory(enum.Enum):
    """A slightly more nuanced way of organizing accounts in a way that better aligns with my reports"""
    CHECKING = enum.auto()
    SAVINGS = enum.auto()
    CREDIT_CARD = enum.auto()
    LOAN = enum.auto()
    OTHER = enum.auto()


class Currencies(enum.Enum):
    EUR = enum.auto()
    GBP = enum.auto()
    USD = enum.auto()


class TableAccount(Base):
    """Accounts table"""

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    account_class = Column(Enum(AccountClass), nullable=False)
    account_category = Column(Enum(AccountCategory), nullable=False)
    account_currency = Column(Enum(Currencies), default=Currencies.USD, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    transaction_splits = relationship('TableTransactionSplit', back_populates='account')
    scheduled_transaction_split_templates = relationship('TableScheduledTransactionSplit',
                                                         back_populates='account')
    budgets = relationship('TableBudget', back_populates='account')
    fullname = Column(VARCHAR, nullable=False)
    friendly_name = Column(VARCHAR, nullable=False)
