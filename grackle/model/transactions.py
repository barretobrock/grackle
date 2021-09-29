import enum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Boolean,
    Text,
    VARCHAR,
    Float,
    TIMESTAMP,
    Enum
)
from sqlalchemy.orm import relationship
from .base import Base


class ReconciledStates(enum.Enum):
    """Reconciliation states"""
    n = 'NotReconciled'
    c = 'Cleared'
    y = 'Reconciled'


class TableTransaction(Base):
    """Transaction table"""
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(VARCHAR)
    transaction_date = Column(TIMESTAMP, nullable=False)
    splits = relationship('TableTransactionSplit', back_populates='transaction')
    is_scheduled = Column(Boolean, default=False)
    desc = Column(Text)


class TableTransactionSplit(Base):
    """Transaction Split table"""
    transaction_split_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_key = Column(Integer, ForeignKey('transaction.transaction_id'), nullable=False)
    transaction = relationship('TableTransaction', back_populates='splits')
    account_key = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    account = relationship('TableAccount', back_populates='transaction_splits')
    reconciled_state = Column(Enum(ReconciledStates), default=ReconciledStates.n, nullable=False)
    is_credit = Column(Boolean)
    memo = Column(VARCHAR)
    invoice_no = Column(VARCHAR)    # Optional reference to an invoice that the transaction settled
    amount = Column(Float, nullable=False)
