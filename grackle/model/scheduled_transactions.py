import enum
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    VARCHAR,
    Float,
    TIMESTAMP,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from .base import Base


class ScheduleFrequencies(enum.Enum):
    """Reconciliation states"""
    WEEKLY = enum.auto()
    MONTHLY = enum.auto()
    QUARTERLY = enum.auto()
    ANNUALLY = enum.auto()


class TableScheduledTransaction(Base):
    """Transactions table"""

    scheduled_transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    frequency = Column(Enum(ScheduleFrequencies), default=ScheduleFrequencies.MONTHLY, nullable=False)
    split_templates = relationship('TableScheduledTransactionSplit', back_populates='scheduled_transaction')
    start_date = Column(TIMESTAMP, nullable=False)
    create_n_days_before = Column(Integer, default=30, nullable=False)
    desc = Column(Text)


class TableScheduledTransactionSplit(Base):
    """Scheduled Transaction split table

    This stores a template of each split
    """

    scheduled_split_id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_transaction_key = Column(Integer, ForeignKey('scheduled_transaction.scheduled_transaction_id'),
                                       nullable=False)
    scheduled_transaction = relationship('TableScheduledTransaction', back_populates='split_templates')
    account_key = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    account = relationship('TableAccount', back_populates='scheduled_transaction_split_templates')
    amount = Column(Float, nullable=False)
    is_credit = Column(Boolean)
    memo = Column(VARCHAR)
