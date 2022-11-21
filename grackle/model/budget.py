from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    VARCHAR,
    Float
)
from sqlalchemy.orm import relationship
from .base import Base


class TableBudget(Base):
    """Budget table"""

    budget_id = Column(Integer, primary_key=True, autoincrement=True)
    account_key = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    account = relationship('TableAccount', back_populates='budgets')
    name = Column(VARCHAR, nullable=False)
    amount = Column(Float(2), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    def __init__(self, name: str, amount: float, year: int, month: int):
        self.name = name
        self.amount = amount
        self.year = year
        self.month = month

    def __repr__(self) -> str:
        return f'<TableBudget(name={self.name}, mm-yyyy={self.month}-{self.year})>'
