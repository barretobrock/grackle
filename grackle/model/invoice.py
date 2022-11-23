from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    VARCHAR,
    Float,
    TIMESTAMP,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import select, func
from .base import Base


class TableInvoice(Base):
    """Invoices table"""

    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(VARCHAR, nullable=False)
    entries = relationship('TableInvoiceEntry', back_populates='invoice', lazy='dynamic')
    created_date = Column(TIMESTAMP, nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_date = Column(TIMESTAMP)
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_date = Column(TIMESTAMP)
    notes = Column(Text)

    def __init__(self, invoice_no: str, created_date: datetime,
                 posted_date: datetime = None, is_paid: bool = False, pmt_date: datetime = None,
                 notes: str = None):
        self.invoice_no = invoice_no
        self.created_date = created_date
        self.is_posted = posted_date is not None
        self.posted_date = posted_date
        self.is_paid = is_paid
        self.paid_date = pmt_date
        self.notes = notes

    @hybrid_property
    def total(self) -> float:
        if self.entries.count() == 0:
            return 0
        return sum([x.total for x in self.entries])

    @total.expression
    def total(cls):
        return (
            select([func.sum(TableInvoiceEntry.total)]).
            where(TableInvoiceEntry.invoice_key == cls.invoice_id).label('total')
        )

    def __repr__(self) -> str:
        return f'<TableInvoice(no={self.invoice_no} created={self.created_date} is_posted={self.is_posted} ' \
               f'is_paid={self.is_paid})>'


class TableInvoiceEntry(Base):
    """Entries in invoices"""

    invoice_entry_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_key = Column(Integer, ForeignKey('invoice.invoice_id'), nullable=False)
    invoice = relationship('TableInvoice', back_populates='entries')
    transaction_date = Column(TIMESTAMP, nullable=False)
    description = Column(VARCHAR, nullable=False)
    quantity = Column(Float(2), default=1.0, nullable=False)
    unit_price = Column(Float(2), nullable=False)
    discount = Column(Float(2), nullable=False)

    @hybrid_property
    def total(self) -> float:
        return self.quantity * self.unit_price * (1 - self.discount)

    @total.expression
    def total(cls) -> float:
        return cls.quantity * cls.unit_price * (1 - cls.discount)

    def __init__(self, transaction_date: datetime, description: str, quantity: float, unit_price: float,
                 discount: float):
        self.transaction_date = transaction_date
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount

    def __repr__(self) -> str:
        return f'<TableInvoiceEntry(date={self.transaction_date} desc={self.description[:20]} ' \
               f'amt={self.total} discount={self.discount:.2%})>'
