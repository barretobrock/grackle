import os
import re
from typing import List
from easylogger import Log
import piecash
from piecash.core.book import (
    Book,
    Account,
    Split
)
from piecash.business.invoice import (
    Invoice,
    Entry
)
from grackle.settings import auto_config
from grackle.model import (
    Base,
    TableAccounts,
    TableBudget,
    TableInvoices,
    TableInvoiceEntries,
    TableTransactions,
    Currencies,
    ReconciledStates,
    AccountClass,
    AccountCategory
)


class ETL:
    """For holding all the various ETL processes, delimited by table name or function of data stored"""
    account_tables = ['accounts']
    budget_tables = ['budgets']
    invoice_tables = ['invoices', 'invoice_entries']
    transaction_tables = ['transactions']

    def __init__(self, tables: List[str]):
        self.log = Log('etl', log_level_str='DEBUG', log_to_file=True)

        self.log.debug('Opening up the database...')
        self.session, self.eng = auto_config.SESSION(), auto_config.engine

        # Determine tables to drop
        self.log.debug(f'Dropping tables: {tables} from db...')
        tbl_objs = []
        for table in tables:
            tbl_objs.append(Base.metadata.tables.get(table))
        Base.metadata.drop_all(self.eng, tables=tbl_objs)
        self.log.debug('Establishing database...')
        Base.metadata.create_all(self.eng)

        self.log.debug('Reading in gnucash file')
        self.book = piecash.open_book(auto_config.GNUCASH_PATH, readonly=True, open_if_lock=True)  # type: Book

    def etl_accounts_transactions_budget(self):
        """Routine to collect and store account details, transactions and budget info"""
        acc_mapping = {
            AccountCategory.CHECKING: r'(.*Current Assets.*CHK)',
            AccountCategory.SAVINGS: r'(.*Current Assets.*(MM|SAV).*)',
            AccountCategory.CREDIT_CARD: r'(.*Liabilities.Credit Cards.*)',
            AccountCategory.LOAN: r'(.*Liabilities.Loans.*)'
        }
        acc: Account
        for acc in self.book.accounts:
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
            acc_obj = TableAccounts(account_class=acc_class, account_category=acc_cat,
                                    account_currency=acc_cur, is_hidden=acc.hidden, fullname=acc.fullname)
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
                t = TableTransactions(guid=split.transaction_guid, transaction_date=split.transaction.post_date,
                                      reconciled_state=ReconciledStates[split.reconcile_state],
                                      desc=split.transaction.description, memo=split.memo, invoice_id=invoice_no,
                                      amount=split.value)
                acc_obj.transactions.append(t)
            self.session.add(acc_obj)
        self.session.commit()

    def etl_invoices(self):
        """Routine to collect and store all invoices"""
        # This is where we'll store rows that are ready to add to the database
        invoices = self.book.invoices
        invoice: Invoice
        for invoice in invoices:
            if invoice.id == '000001':
                # Unclosed test invoice?
                continue
            related_transactions = self.session.query(TableTransactions).filter(
                TableTransactions.invoice_id == invoice.id).all()
            if len(related_transactions) > 0:
                is_paid = any(x.amount < 0 for x in related_transactions)
                pmt_date = related_transactions[0].transaction_date
            else:
                is_paid = False
                pmt_date = None
            invoice_obj = TableInvoices(invoice_no=invoice.id, created_date=invoice.date_opened,
                                        is_posted=invoice.date_posted is not None, posted_date=invoice.date_posted,
                                        is_paid=is_paid, paid_date=pmt_date)
            i_entries = invoice.entries
            entry: Entry
            for entry in i_entries:
                entry_obj = TableInvoiceEntries(invoice_id=invoice_obj.id, transaction_date=entry.date,
                                                description=entry.description, quantity=entry.quantity,
                                                unit_price=entry.i_price, discount=entry.i_discount)
                invoice_obj.entries.append(entry_obj)
            self.session.add(invoice_obj)
            self.session.commit()


if __name__ == '__main__':
    os.environ['GRACKLE_ENV'] = 'DEVELOPMENT'
    table_list = ETL.account_tables + ETL.budget_tables + ETL.invoice_tables + ETL.transaction_tables
    etl = ETL(tables=table_list)
    etl.etl_accounts_transactions()
    etl.etl_invoices()
