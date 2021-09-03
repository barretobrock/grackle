import enum
from sqlalchemy import Column, Integer, ForeignKey, Text, VARCHAR, Float, Enum, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base


class TableInvoices(Base):
    """Invoices table"""
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(VARCHAR, nullable=False)
    entries = relationship('TableInvoiceEntries', back_populates='invoice')
    created_date = Column(TIMESTAMP, nullable=False)
    is_posted = Column(Boolean, nullable=False)
    posted_date = Column(TIMESTAMP)
    is_paid = Column(Boolean, nullable=False)
    paid_date = Column(TIMESTAMP)


class TableInvoiceEntries(Base):
    """Entries in invoices"""
    __tablename__ = 'invoice_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    invoice = relationship('TableInvoices', back_populates='entries')
    transaction_date = Column(TIMESTAMP, nullable=False)
    description = Column(VARCHAR, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float(2), nullable=False)
    discount = Column(Float(2), nullable=False)

    @hybrid_property
    def total(self) -> float:
        return self.quantity * self.unit_price * (1 - self.discount)

