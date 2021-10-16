import os
import re
import functools
from shutil import copyfile
from datetime import datetime
from typing import (
    List,
    Dict,
    Union,
    Optional
)
from sqlalchemy.orm import Session
from easylogger import Log
import piecash
from piecash.core.book import (
    Book,
    Account,
    Split
)
from piecash.business.invoice import (
    Entry,
    Invoice
)
from grackle.model import (
    TableAccount,
    TableBudget,
    TableInvoice,
    TableInvoiceEntry,
    TableTransaction,
    TableTransactionSplit,
    Currencies,
    ReconciledStates,
    AccountClass,
    AccountCategory
)
import grackle.settings as gsettings


class GNUCashProcessor:

    class _Decorators(object):
        @classmethod
        def check_book(cls, func):
            """Checks if book is read in and sets up the session"""
            @functools.wraps(func)
            def wrap(self, *args, **kwargs):
                if self.book is None:
                    self.refresh_book()
                return func(self, *args, **kwargs)
            return wrap

    def __init__(self, parent_log: Log = None):
        self.log = Log(parent_log, child_name=self.__class__.__name__, log_level_str='DEBUG')
        self.book = None                # type: Optional[Book]
        self.session = None             # type: Optional[Session]
        self.book_last_updated = datetime.fromtimestamp(
            os.path.getmtime(gsettings.auto_config.GNUCASH_PATH))   # type: Optional[datetime]

    def refresh_book(self):
        self.book = piecash.open_book(gsettings.auto_config.GNUCASH_PATH, readonly=True,
                                      open_if_lock=True)
        self.session = gsettings.auto_config.SESSION()
        self.book_last_updated = datetime.fromtimestamp(
            os.path.getmtime(gsettings.auto_config.GNUCASH_PATH))

    def load_new_book(self, fpath: str):
        if os.path.exists(fpath):
            # Attempt to open the file
            try:
                b = piecash.open_book(fpath, readonly=True, open_if_lock=True)
            except Exception as e:
                # Failed to open... don't overwrite this book with the default
                return False
            # Copy existing file to backups, append timestamp to end of file name
            newfile = f'gnucash_web_{datetime.now():%F_%T}.gnucash'
            copyfile(gsettings.auto_config.GNUCASH_PATH, os.path.join(gsettings.auto_config.BACKUP_DIR, newfile))
            # Copy the file to the default path
            copyfile(fpath, gsettings.auto_config.GNUCASH_PATH)
            self.refresh_book()
            return True
        else:
            raise FileNotFoundError(f'File at path {fpath} doesn\'t seem to exist.')

    @_Decorators.check_book
    def etl_accounts_transactions_budget(self):
        """Routine to collect and store account details, transactions and budget info"""
        acc_mapping = {
            AccountCategory.CHECKING: r'(.*Current Assets.*CHK)',
            AccountCategory.SAVINGS: r'(.*Current Assets.*(MM|SAV).*)',
            AccountCategory.CREDIT_CARD: r'(.*Liabilities.Credit Cards.*)',
            AccountCategory.LOAN: r'(.*Liabilities.Loans.*)'
        }

        transaction_rows = []

        acc: Account
        for acc in self.book.accounts:
            self.log.debug(f'Working on: {acc.fullname}')
            if acc.commodity.mnemonic == 'template' or acc.type == 'STOCK':
                # Bypass stored scheduled transactions and stocks for now
                continue
            acc_class = AccountClass[acc.type.upper()]
            acc_cat = AccountCategory.OTHER
            acc_cur = Currencies[acc.commodity.mnemonic]
            for k, v in acc_mapping.items():
                if re.match(v, acc.fullname) is not None:
                    acc_cat = k
                    break

            # Determine friendly name
            fullname = acc.fullname.replace(':', '.')
            name_splits = fullname.split('.')
            if len(name_splits) == 1:
                friendly_name = fullname
            elif acc_class in (AccountClass.EXPENSE, AccountClass.INCOME):
                friendly_name = '-'.join(name_splits[1:])
            elif len(name_splits) > 2:
                # ALE all have two leading groups that aren't necessarily important
                #   in differentiating the names in, say, a graph
                friendly_name = '-'.join(name_splits[2:])
            else:
                friendly_name = '-'.join(name_splits)
            acc_obj = TableAccount(account_class=acc_class, account_category=acc_cat,
                                   account_currency=acc_cur, is_hidden=acc.hidden,
                                   fullname=fullname, friendly_name=friendly_name)
            if len(acc.budget_amounts) > 0:
                for bdg in acc.budget_amounts:
                    bdg_year = bdg.budget.recurrence.recurrence_period_start.year
                    bdg_month = bdg.period_num + 1
                    # Record budget
                    budget = TableBudget(name=bdg.budget.name, amount=bdg.amount, year=bdg_year, month=bdg_month)
                    acc_obj.budgets.append(budget)

            split: Split
            for split in acc.splits:
                invoice_no = ''
                if split.lot is not None:
                    for lot in split.lot.slots:
                        if lot.name == 'gncInvoice':
                            # Transaction for invoice - get invoice number(s)
                            invoice = lot.value.get('invoice-guid', None)
                            if invoice is not None:
                                invoice_no = invoice.id
                value = split.value

                transaction = next(iter(x for x in transaction_rows if x.guid == split.transaction_guid), None)
                if transaction is None:
                    transaction = TableTransaction(
                        guid=split.transaction_guid,
                        transaction_date=split.transaction.post_date,
                        desc=split.transaction.description
                    )
                    transaction_rows.append(transaction)
                transaction_split = TableTransactionSplit(
                    transaction=transaction,
                    reconciled_state=ReconciledStates[split.reconcile_state],
                    is_credit=split.is_credit,
                    memo=split.memo,
                    invoice_no=invoice_no,
                    amount=value
                )
                acc_obj.transaction_splits.append(transaction_split)
            self.session.add(acc_obj)
        self.session.add_all(transaction_rows)
        self.session.commit()

    @_Decorators.check_book
    def etl_invoices(self):
        """Routine to collect and store all invoices"""
        # This is where we'll store rows that are ready to add to the database
        invoices = self.book.invoices
        invoice: Invoice
        for invoice in invoices:
            if invoice.id == '000001':
                # Unclosed test invoice?
                continue
            related_transactions = self.session.query(TableTransactionSplit).filter(
                TableTransactionSplit.invoice_no == invoice.id).all()
            if len(related_transactions) > 0:
                is_paid = any(x.amount < 0 for x in related_transactions)
                pmt_date = related_transactions[0].transaction.transaction_date
            else:
                is_paid = False
                pmt_date = None
            invoice_obj = TableInvoice(invoice_no=invoice.id, created_date=invoice.date_opened,
                                       is_posted=invoice.date_posted is not None, posted_date=invoice.date_posted,
                                       is_paid=is_paid, paid_date=pmt_date, notes=invoice.notes)
            i_entries = invoice.entries
            entry: Entry
            for entry in i_entries:
                entry_obj = TableInvoiceEntry(invoice_key=invoice_obj.invoice_id, transaction_date=entry.date,
                                              description=entry.description, quantity=entry.quantity,
                                              unit_price=entry.i_price, discount=entry.i_discount)
                invoice_obj.entries.append(entry_obj)
            self.session.add(invoice_obj)
            self.session.commit()
