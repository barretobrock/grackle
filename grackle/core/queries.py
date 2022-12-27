from datetime import datetime
from typing import (
    List,
    Tuple,
    TypedDict,
    Union,
)

from sqlalchemy.sql import (
    and_,
    distinct,
    not_,
)

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
                               acct_full_name: Union[str, List[str]] = None,
                               acct_category: Union[AccountCategory, List[AccountCategory]] = None,
                               acct_type: Union[AccountType, List[AccountType]] = None,
                               acct_currs: Union[str, List[str]] = None) -> List:
        attrs = {
            TableAccount.name: acct_name,
            TableAccount.full_name: acct_full_name,
            TableAccount.account_category: acct_category,
            TableAccount.account_type: acct_type,
            TableAccount.account_currency: acct_currs
        }
        filters = []

        for tbl_attr, attr in attrs.items():
            if attr is not None:
                if isinstance(attr, list):
                    filt = tbl_attr.in_(attr)
                else:
                    filt = tbl_attr == attr
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
                         acct_full_name: Union[str, List[str]] = None,
                         acct_category: Union[AccountCategory, List[AccountCategory]] = None,
                         acct_type: Union[AccountType, List[AccountType]] = None,
                         start_date: datetime = None, end_date: datetime = None, acct_excl_like: str = None,
                         acct_currs: List[str] = None) -> \
            List[TableTransactionSplit]:
        filters = cls._build_account_filters(acct_name=acct_name, acct_full_name=acct_full_name,
                                             acct_category=acct_category, acct_type=acct_type,
                                             acct_currs=acct_currs)
        if acct_excl_like is not None:
            filters.append(
                not_(TableAccount.full_name.like(acct_excl_like))
            )
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

    @classmethod
    def get_budget_names(cls) -> List[str]:
        return [x[0] for x in get_db().session.query(distinct(TableBudget.name)).order_by(TableBudget.name.asc()).all()]

    @classmethod
    def get_account_names(cls) -> List[str]:
        return [x.full_name for x in get_db().session.query(TableAccount.full_name).all()]
