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
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base


class TableInvoice(Base):
    """Invoices table"""

    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(VARCHAR, nullable=False)
    entries = relationship('TableInvoiceEntry', back_populates='invoice')
    created_date = Column(TIMESTAMP, nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_date = Column(TIMESTAMP)
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_date = Column(TIMESTAMP)
    notes = Column(Text)

    @hybrid_property
    def total(self) -> float:
        return sum([x.total for x in self.entries])

    @total.expression
    def total(cls) -> float:
        return sum([x.total for x in cls.entries])


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
