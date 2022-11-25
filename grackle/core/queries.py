from datetime import datetime
from typing import (
    List,
    Tuple,
    TypedDict,
    Union,
)

from sqlalchemy.sql import and_

from grackle.model import (
    AccountCategory,
    AccountType,
    TableAccount,
    TableBudget,
    TableInvoice,
    TableInvoiceEntry,
    TableTransaction,
    TableTransactionSplit,
)
from grackle.routes.helpers import get_db


class InvoiceItemDict(TypedDict):
    transaction_date: str
    description: str
    quantity: float
    unit_price: float
    discount: float
    total: float


class GrackleQueries:

    @classmethod
    def _build_account_filters(cls, acct_name: Union[str, List[str]] = None,
                               acct_category: Union[AccountCategory, List[AccountCategory]] = None,
                               acct_type: Union[AccountType, List[AccountType]] = None) -> List:
        filters = []
        if acct_name is not None:
            if isinstance(acct_name, list):
                filt = TableAccount.name.in_(acct_name)
            else:
                filt = TableAccount.name == acct_name
            filters.append(filt)
        if acct_category is not None:
            if isinstance(acct_category, list):
                filt = TableAccount.account_category.in_(acct_category)
            else:
                filt = TableAccount.account_category == acct_category
            filters.append(filt)
        if acct_type is not None:
            if isinstance(acct_type, list):
                filt = TableAccount.account_type.in_(acct_type)
            else:
                filt = TableAccount.account_type == acct_type
            filters.append(filt)
        return filters

    @classmethod
    def get_invoice(cls, invoice_no: str) -> Tuple[TableInvoice, List[TableInvoiceEntry]]:
        invoice: TableInvoice
        invoice = get_db().session.query(TableInvoice).\
            join(TableInvoiceEntry, TableInvoice.invoice_id == TableInvoiceEntry.invoice_key).\
            filter(and_(
                TableInvoice.invoice_no == invoice_no,
                TableInvoiceEntry.quantity != 0
            )).one_or_none()

        return invoice, [x for x in invoice.entries]

    @classmethod
    def get_invoices(cls, limit: int = 10) -> List[TableInvoice]:
        return get_db().session.query(TableInvoice).order_by(TableInvoice.invoice_no.desc()).limit(limit).all()

    @classmethod
    def get_account_balance(cls, acct_name: Union[str, List[str]] = None,
                            acct_category: Union[AccountCategory, List[AccountCategory]] = None,
                            acct_type: Union[AccountType, List[AccountType]] = None) -> List[Tuple[str, float]]:
        filters = cls._build_account_filters(acct_name=acct_name, acct_category=acct_category, acct_type=acct_type)
        return get_db().session.query(TableAccount.name, TableAccount.current_balance).filter(*filters).all()

    @classmethod
    def get_transactions(cls, acct_name: Union[str, List[str]] = None,
                         acct_category: Union[AccountCategory, List[AccountCategory]] = None,
                         acct_type: Union[AccountType, List[AccountType]] = None,
                         start_date: datetime = None, end_date: datetime = None) -> \
            List[TableTransactionSplit]:
        filters = cls._build_account_filters(acct_name=acct_name, acct_category=acct_category, acct_type=acct_type)

        if start_date is not None:
            filters.append(
                TableTransaction.transaction_date >= start_date
            )
        if end_date is not None:
            filters.append(
                TableTransaction.transaction_date <= end_date
            )
        transactions = get_db().session.query(TableTransactionSplit).\
            join(TableAccount, TableAccount.account_id == TableTransactionSplit.account_key).\
            join(TableTransaction, TableTransaction.transaction_id == TableTransactionSplit.transaction_key).\
            filter(and_(
                *filters
            )).all()

        return transactions

    @classmethod
    def get_budget_data_for_month(cls, mm: int, yyyy: int) -> List[TableBudget]:
        return get_db().session.query(TableBudget).filter(and_(
                TableBudget.month == mm,
                TableBudget.year == yyyy
            )).all()
