from typing import List

from pukr import (
    PukrLog,
    get_logger,
)

from grackle.config import DevelopmentConfig
from grackle.model import (
    Base,
    TableAccount,
    TableBudget,
    TableInvoice,
    TableInvoiceEntry,
    TableScheduledTransaction,
    TableScheduledTransactionSplit,
    TableTransaction,
    TableTransactionSplit,
)


class DBAdmin:
    """For holding all the various ETL processes, delimited by table name or function of data stored"""
    TABLES = [
        TableAccount,
        TableBudget,
        TableInvoice,
        TableInvoiceEntry,
        TableScheduledTransaction,
        TableScheduledTransactionSplit,
        TableTransaction,
        TableTransactionSplit
    ]

    def __init__(self, parent_log: PukrLog, tables: List = None):
        self.log = parent_log.bind(child_name=self.__class__.__name__)

        self.log.debug('Opening up the database...')
        self.session, self.eng = DevelopmentConfig.SESSION(), DevelopmentConfig.engine
        self.tables = tables
        if tables is None:
            self.tables = self.TABLES

    def drop_and_recreate(self):
        # Determine tables to drop
        self.log.debug(f'Dropping tables: {self.tables} from db...')
        tbl_objs = []
        for table in self.tables:
            tbl_objs.append(Base.metadata.tables.get(table.__tablename__))
        Base.metadata.drop_all(self.eng, tables=tbl_objs)
        self.log.debug('Establishing database...')
        Base.metadata.create_all(self.eng)


if __name__ == '__main__':

    test_log = get_logger('etl', base_level='DEBUG')
    db = DBAdmin(test_log, tables=DBAdmin.TABLES)
