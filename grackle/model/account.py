import enum

from piecash import AccountType
from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Enum,
    Float,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import Base


class AccountCategory(enum.Enum):
    """A slightly more nuanced way of organizing accounts in a way that better aligns with my reports"""
    CASH = enum.auto()
    CHECKING = enum.auto()
    SAVINGS = enum.auto()
    RECEIVABLE = enum.auto()
    INVESTMENT = enum.auto()

    CREDIT_CARD = enum.auto()
    LOAN = enum.auto()
    MORTGAGE = enum.auto()

    INCOME = enum.auto()
    EXPENSE = enum.auto()

    OTHER = enum.auto()


class Currency(enum.Enum):
    EUR = enum.auto()
    USD = enum.auto()


class TableAccount(Base):
    """Accounts table"""

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    full_name = Column(VARCHAR, nullable=False)
    guid = Column(VARCHAR)
    account_type = Column(Enum(AccountType), nullable=False)
    account_category = Column(Enum(AccountCategory), nullable=False)
    account_currency = Column(Enum(Currency), default=Currency.USD, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    current_balance = Column(Float(2))
    transaction_splits = relationship('TableTransactionSplit', back_populates='account')
    scheduled_transaction_split_templates = relationship('TableScheduledTransactionSplit',
                                                         back_populates='account')
    budgets = relationship('TableBudget', back_populates='account')

    def __init__(self, name: str, full_name: str, account_type: AccountType, account_category: AccountCategory,
                 account_currency: Currency, current_balance: float, guid: str, is_hidden: bool = False):
        self.name = name
        self.full_name = full_name
        self.account_type = account_type
        self.account_category = account_category
        self.account_currency = account_currency
        self.is_hidden = is_hidden
        self.guid = guid
        self.current_balance = current_balance

    def get_full_name(self) -> str:
        return f'{self.full_name}'

    def __repr__(self) -> str:
        return f'<TableAccount(name={self.name}, is_hidden={self.is_hidden})>'
