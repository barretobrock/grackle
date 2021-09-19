import os
from typing import List
from easylogger import Log
from grackle.settings import auto_config
from grackle.model import (
    Base,
    TableAccounts,
    TableBudget,
    TableInvoices,
    TableInvoiceEntries,
    TableTransactions
)
from grackle.core import GNUCashProcessor


class ETL:
    """For holding all the various ETL processes, delimited by table name or function of data stored"""
    TABLES = [
        TableAccounts.__tablename__,
        TableBudget.__tablename__,
        TableInvoices.__tablename__,
        TableInvoiceEntries.__tablename__,
        TableTransactions.__tablename__
    ]

    def __init__(self, tables: List[str] = None, parent_log: Log = None):
        self.log = Log(parent_log, child_name='etl')

        self.log.debug('Opening up the database...')
        self.session, self.eng = auto_config.SESSION(), auto_config.engine

        # Determine tables to drop
        if tables is None:
            tables = self.TABLES
        self.log.debug(f'Dropping tables: {tables} from db...')
        tbl_objs = []
        for table in tables:
            tbl_objs.append(Base.metadata.tables.get(table))
        Base.metadata.drop_all(self.eng, tables=tbl_objs)
        self.log.debug('Establishing database...')
        Base.metadata.create_all(self.eng)

        self.log.debug('Reading in gnucash file')
        self.gnc = GNUCashProcessor(parent_log=self.log)


if __name__ == '__main__':
    os.environ['GRACKLE_ENV'] = 'DEVELOPMENT'
    etl = ETL(tables=ETL.TABLES)
    etl.gnc.etl_accounts_transactions_budget()
    etl.gnc.etl_invoices()
