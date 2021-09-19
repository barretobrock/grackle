import enum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    VARCHAR,
    Float,
    TIMESTAMP,
    Enum
)
from sqlalchemy.orm import relationship
from .base import Base
from .accounts import Currencies


class ReconciledStates(enum.Enum):
    """Reconciliation states"""
    n = 'NotReconciled'
    c = 'Cleared'
    y = 'Reconciled'


class TableTransactions(Base):
    """Transactions table"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(VARCHAR)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('TableAccounts', back_populates='transactions')
    transaction_date = Column(TIMESTAMP, nullable=False)
    reconciled_state = Column(Enum(ReconciledStates), default=ReconciledStates.n, nullable=False)
    desc = Column(Text)
    memo = Column(VARCHAR)
    invoice_id = Column(VARCHAR)    # Optional reference to an invoice that the transaction settled
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currencies), default=Currencies.USD, nullable=False)
