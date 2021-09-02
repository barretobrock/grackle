import os
from shutil import copyfile
from datetime import datetime
from typing import List, Dict, Union
import piecash
from piecash.business.invoice import Entry, Invoice
import pandas as pd


class GNUCashProcessor:

    def __init__(self, csv_path: str, book_path: str):
        self.book = None
        self.transactions_df = None
        self.csv_path = csv_path
        self.default_book_path = book_path
        self._read_transactions_df()
        # TODO: download book(structure only?),
        #  upload new book, parse out transactions and move them in to default book

    def refresh_book(self):
        self.book = piecash.open_book(self.default_book_path, readonly=True,
                                      open_if_lock=True)  # type: piecash.core.book.Book
        self.transactions_df = self.get_all_transactions()
        self._save_transactions_df()

    def load_new_book(self, fpath: str):
        if os.path.exists(fpath):
            # Attempt to open the file
            try:
                b = piecash.open_book(fpath, readonly=True, open_if_lock=True)
            except Exception as e:
                # Failed to open... don't overwrite this book with the default
                return False
            # Copy the file to the default path
            copyfile(fpath, self.default_book_path)
            self.refresh_book()
            return True
        else:
            raise FileNotFoundError(f'File at path {fpath} doesn\'t seem to exist.')

    def _save_transactions_df(self):
        """Saves the processed transactions df to csv"""
        self.transactions_df.to_csv(self.csv_path, sep=';', index=False)

    def _read_transactions_df(self):
        """Reads in a previously saved transactions df"""
        if os.path.exists(self.csv_path):
            self.transactions_df = pd.read_csv(self.csv_path, sep=';')
        else:
            # Refresh the data by reading in the book and saving
            self.refresh_book()

    @staticmethod
    def filter_dates(df: pd.DataFrame, start: datetime, end: datetime = None) -> pd.DataFrame:
        if end is not None:
            # Start and end date
            date_mask = (df['date'] >= start) & (df['date'] <= end)
        else:
            date_mask = (df['date'] >= start)
        return df.loc[date_mask]

    def get_all_invoices(self):
        """Collects invoice data and puts it into a dataframe"""
        invoices = self.book.invoices  # type: List[Invoice]
        df = pd.DataFrame()
        for inv in invoices:
            inv_no = inv.id
            entries = inv.entries   # type: List[Entry]
            for entry in entries:
                df.append({
                    'invoice': inv_no,
                    'date': entry.date,
                    'desc': entry.description,
                    'quantity': entry.quantity,
                    'unit price': entry.i_price,
                    'discount': entry.i_discount,
                    'total': entry.quantity * entry.i_price * (1 - entry.i_discount)
                }, ignore_index=True)

    def get_all_transactions(self, start: datetime = None, end: datetime = None) -> \
            pd.DataFrame:
        df = pd.DataFrame()
        for acc in self.book.accounts:
            if acc.commodity.mnemonic == 'template':
                # Bypass stored scheduled transactions
                continue
            acc_df = pd.DataFrame({
                'name': acc.name,
                'type': acc.type,
                'cur': acc.commodity.mnemonic,
                'fullname': acc.fullname,
                'is_hidden': acc.hidden
            }, index=[0])
            if len(acc.splits) > 0:
                # Add transations
                trans_df = pd.DataFrame()
                for splt in acc.splits:
                    trans_df = trans_df.append({
                        'fullname': acc.fullname,
                        'date': splt.transaction.post_date,
                        'desc': splt.transaction.description,
                        'memo': splt.memo,
                        'reconcile_state': splt.reconcile_state,
                        'amt': splt.value
                    }, ignore_index=True)
                merged = acc_df.merge(trans_df, on='fullname', how='left')
                df = df.append(merged)

        df['fullname'] = df.fullname.str.replace(':', '.')
        df['date'] = pd.to_datetime(df['date'])

        # Assign my categories to the dataframe
        categories = {
            'CHECKING': r'(.*Current Assets.*CHK)',
            'SAVINGS': r'(.*Current Assets.*(MM|SAV).*)',
            'CREDITCARD': r'(.*Liabilities.Credit Cards.*)'
        }
        df['category'] = 'OTHER'
        for k, v in categories.items():
            df.loc[df['fullname'].str.match(v), 'category'] = k

        df = df.reset_index(drop=True)
        if start is not None:
            return self.filter_dates(df, start, end)
        return df
