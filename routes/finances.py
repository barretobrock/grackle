import re
from datetime import datetime, timedelta
import pandas as pd
from flask import (
    render_template,
    Blueprint,
    flash,
    redirect,
    url_for
)
from sqlalchemy.sql import and_
from grackle.model import TableTransactions, AccountClass, TableInvoices, TableInvoiceEntries
import routes.app as rapp


fin = Blueprint('finances', __name__)


@fin.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error_msg=e), 404


@fin.route('/refresh')
def refresh_book():
    # TODO Optionally tie this in with the upload endpoint and have separate endpoints to
    #  refresh specific parts if not all are needed (transactions, invoices, etc)
    # current_app.config['GNC'].refresh_book()
    flash('Financial data refresh successful.', 'alert alert-success')
    return redirect(url_for('main.index'))


@fin.route('/mvm/<string:p1>/<string:p2>')
def get_mvm(p1: str, p2: str):
    """For rendering a month v month comparison"""
    # Confirm strings are of MM-YYYY format
    if any([re.match(r'\d{2}-\d{4}', x) is None for x in [p1, p2]]):
        return page_not_found(ValueError(f'One or more of the provided values did not match '
                                         f'the expected syntax: mm-yyyy: "{p1}", "{p2}"'))
    df = pd.DataFrame()
    for p in [p1, p2]:
        p_mm, p_yy = [int(x) for x in p.split('-')]
        # Collect the 1st period's data
        p_st = datetime(p_yy, p_mm, 1)
        p_end = (p_st + timedelta(days=33)).replace(day=1) - timedelta(days=1)
        p_data = rapp.db.session.query(TableTransactions).filter(
            and_(TableTransactions.transaction_date >= p_st, TableTransactions.transaction_date <= p_end)).all()
        if len(p_data) == 0:
            df = df.append(pd.DataFrame({'period': p}, index=[0]))
        for row in p_data:
            if row.account.account_class not in [AccountClass.INCOME, AccountClass.EXPENSE]:
                continue
            if row.account.account_currency.name not in ['USD']:
                continue
            # Load data into dataframe
            df = df.append(pd.DataFrame({
                'period': p,
                'class': row.account.account_class.name,
                'account': row.account.friendly_name,
                'amt': row.amount,
                'cur': row.account.account_currency.name,
            }, index=[0]))
    # Consolidate the dataframe
    pivoted = df.pivot_table(index=['class', 'account'], columns=['period'],
                             values='amt', aggfunc='sum').fillna(0).reset_index()
    # Add in a delta column
    pivoted['change'] = pivoted[p1] - pivoted[p2]
    # Ensure column order (p1 is always the focus, p2 always the comparison)
    pivoted = pivoted[['class', 'account', p1, p2, 'change']]
    # Split into separate income / expenses; invert income, as it typically is negative
    income_df = pivoted.loc[pivoted['class'] == 'INCOME', ].drop('class', axis=1).apply(
        lambda x: x * -1 if x.dtype.kind in 'iufc' else x)
    expense_df = pivoted.loc[pivoted['class'] == 'EXPENSE', ].drop('class', axis=1)
    # Sum income / expenses
    income_df = income_df.append(income_df.sum(numeric_only=True), ignore_index=True).fillna('Total')
    expense_df = expense_df.append(expense_df.sum(numeric_only=True), ignore_index=True).fillna('Total')
    return render_template('compare.html', income_df=income_df, expense_df=expense_df)


@fin.route('/mvb/<string:period>')
def get_mvb(period: str):
    """For rendering a month v budget comparison"""
    # TODO: here
    pass


@fin.route('/budget-analysis')
def budget_analysis():
    """For rendering a broad graphic analysis of spend over the months compared to set budgets"""
    # TODO: here
    pass


@fin.route('/invoices')
def get_invoices():
    """For rendering a list of invoices, marking which ones might be due"""
    # Query all invoices
    invoices = rapp.db.session.query(TableInvoices).order_by(TableInvoices.invoice_no.desc()).all()

    return render_template('invoices.html', invoices=invoices)


@fin.route('/invoice/<string:invoice_no>')
def get_invoice(invoice_no: str):
    """For rendering an individual invoice"""
    invoice = rapp.db.session.query(TableInvoices).filter(TableInvoices.invoice_no == invoice_no).one_or_none()
    return render_template('invoice.html', invoice=invoice)
