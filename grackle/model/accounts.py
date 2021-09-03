import enum
from sqlalchemy import Column, Integer, ForeignKey, Text, VARCHAR, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base


class AccountClass(enum.Enum):
    """A more traditional way of classifying accounts"""
    ASSET = 'ASSET'
    LIABILITY = 'LIABILITY'
    EQUITY = 'EQUITY'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'


class AccountCategory(enum.Enum):
    """A slightly more nuanced way of organizing accounts in a way that better aligns with my reports"""
    LOAN = 'LOAN'
    CREDIT_CARD = 'CREDIT_CARD'


class Currencies(enum.Enum):
    EUR = 'EUR'
    GBP = 'GBP'
    USD = 'USD'


class TableAccounts(Base):
    """Accounts table"""
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_class = Column(Enum(AccountClass), nullable=False)
    account_category = Column(Enum(AccountCategory), nullable=False)
    account_currency = Column(Enum(Currencies), default=Currencies.USD, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    transactions = relationship('TableTransactions', back_populates='account')
    fullname = Column(VARCHAR, nullable=False)

    @hybrid_property
    def friendly_name(self) -> str:
        name_splits = self.fullname.split('.')
        if self.account_class in (AccountClass.EXPENSE, AccountClass.INCOME):
            return '-'.join(name_splits[1:])
        # ALE all have two leading groups that aren't necessarily important
        #   in differentiating the names in, say, a graph
        return '-'.join(name_splits[2:])
