from datetime import datetime
import enum

from sqlalchemy import (
    TIMESTAMP,
    VARCHAR,
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class ReconciledState(enum.Enum):
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

    def __init__(self, transaction_date: datetime, desc: str, guid: str):
        self.transaction_date = transaction_date
        self.desc = desc
        self.guid = guid

    def __repr__(self) -> str:
        return f'<TableTransaction(date={self.transaction_date} desc={self.desc[:20]})>'


class TableTransactionSplit(Base):
    """Transaction Split table"""
    transaction_split_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_key = Column(Integer, ForeignKey('transaction.transaction_id'), nullable=False)
    transaction = relationship('TableTransaction', back_populates='splits')
    account_key = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    account = relationship('TableAccount', back_populates='transaction_splits')
    reconciled_state = Column(Enum(ReconciledState), default=ReconciledState.n, nullable=False)
    is_credit = Column(Boolean)
    memo = Column(VARCHAR)
    invoice_no = Column(VARCHAR)    # Optional reference to an invoice that the transaction settled
    amount = Column(Float, nullable=False)

    def __init__(self, amount: float, is_credit: bool, memo: str, reconciled_state: ReconciledState,
                 invoice_no: str = None, transaction: TableTransaction = None):
        self.amount = amount
        self.is_credit = is_credit
        self.memo = memo
        self.reconciled_state = reconciled_state
        self.invoice_no = invoice_no
        self.transaction = transaction

    def __repr__(self) -> str:
        return f'<TableTransactionSplit(amount={self.amount} is_credit={self.is_credit})>'
