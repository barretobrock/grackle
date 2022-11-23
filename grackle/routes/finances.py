import re
from datetime import datetime, timedelta
from typing import List
import pandas as pd
from flask import (
    render_template,
    current_app,
    Blueprint,
    redirect,
    url_for,
    request
)
from sqlalchemy.sql import and_
from grackle.model import (
    TableTransaction,
    TableTransactionSplit,
    TableBudget
)


fin = Blueprint('finances', __name__)


def get_db():
    return current_app.config['db']


def get_periods_transations(period: str) -> List[TableTransactionSplit]:
    """Gets the transactions for the given period in MM-YYYY format"""
    p_mm, p_yy = [int(x) for x in period.split('-')]
    p_st = datetime(p_yy, p_mm, 1)
    p_end = (p_st + timedelta(days=33)).replace(day=1) - timedelta(days=1)
    p_data = get_db().session.query(TableTransactionSplit) \
        .join(TableTransaction, TableTransactionSplit.transaction_key == TableTransaction.transaction_id) \
        .filter(and_(
            TableTransaction.transaction_date >= p_st,
            TableTransaction.transaction_date <= p_end)
        ).all()
    return p_data


def page_not_found(e):
    return render_template('errors/404.html', error_msg=e), 404


@fin.route('/select-mvm', methods=['GET', 'POST'])
def select_mvm():
    """Page to select months to compare"""
    if request.method == 'POST':
        p_list = []
        for i in range(1, 3):
            yyyy = request.values.get(f'p{i}-year')
            mm = request.values.get(f'p{i}-month')
            p_list.append(f'{int(mm):02d}-{yyyy}')
        p1, p2 = p_list
        return redirect(url_for('finances.get_mvm', p1=p1, p2=p2))
    else:
        years = [i + 2020 for i in range(datetime.now().year - 2020 + 1)]
        return render_template('select-mvm.html', years=years, current=datetime.now(),
                               previous=(datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1))


def load_data_into_df(df: pd.DataFrame, query_result: List[TableTransactionSplit], period_name: str) -> \
        pd.DataFrame:
    row: TableTransactionSplit
    for row in query_result:
        # Load data into dataframe
        new_data = pd.DataFrame({
            'period': period_name,
            'type': row.account.account_type.name,
            'category': row.account.account_category.name,
            'account': row.account.name,
            'amt': row.amount,
            'cur': row.account.account_currency.name,
        }, index=[0])
        df = pd.concat([df, new_data])
    return df


@fin.route('/mvm/<string:p1>/<string:p2>')
def get_mvm(p1: str, p2: str):
    """For rendering a month v month comparison"""
    # Confirm strings are of MM-YYYY format
    if any([re.match(r'\d{2}-\d{4}', x) is None for x in [p1, p2]]):
        return page_not_found(ValueError(f'One or more of the provided values did not match '
                                         f'the expected syntax: mm-yyyy: "{p1}", "{p2}"'))
    df = pd.DataFrame()
    for p in [p1, p2]:
        df = load_data_into_df(df, query_result=get_periods_transations(period=p), period_name=p)

    # Consolidate the dataframe
    pivoted = df.pivot_table(index=['type', 'category', 'account'], columns=['period'],
                             values='amt', aggfunc='sum').fillna(0).reset_index()
    # Remove bank, receivable & credit activity
    pivoted = pivoted.loc[~pivoted['type'].isin(['bank', 'equity', 'credit', 'receivable']), :]
    # Income, liability needs to be 'flipped'
    pivoted.loc[pivoted['type'].isin(['income', 'liability']), [p1, p2]] = \
        pivoted.loc[pivoted['type'].isin(['income', 'liability']), [p1, p2]] * -1
    # Add in a delta column
    pivoted['change'] = pivoted[p1] - pivoted[p2]
    # Ensure column order (p1 is always the focus, p2 always the comparison)
    pivoted = pivoted[['type', 'category', 'account', p1, p2, 'change']]
    # Split into separate income / expenses; invert income, as it typically is negative
    income_df = pivoted.loc[pivoted['category'] == 'INCOME', ].drop(['type', 'category'], axis=1)
    expense_df = pivoted.loc[pivoted['category'] != 'INCOME', ].drop(['type', 'category'], axis=1)
    # Sum income / expenses
    income_df = pd.concat([income_df, pd.DataFrame([income_df.sum(numeric_only=True)])],
                          ignore_index=True).fillna('Total')
    expense_df = pd.concat([expense_df, pd.DataFrame([expense_df.sum(numeric_only=True)])],
                           ignore_index=True).fillna('Total')
    # Get total profit / loss for both budgeted & actual
    overall_df = pd.concat([
        income_df.loc[income_df['account'] == 'Total', :],
        expense_df.loc[expense_df['account'] == 'Total', :]
    ])
    overall_df = pd.concat([overall_df, pd.DataFrame([overall_df[[p1, p2]].diff().iloc[1] * -1])])
    overall_df['account'] = ['Income', 'Expense', 'P/L']
    overall_df['change'] = overall_df[p1] - overall_df[p2]
    return render_template(
        'compare.html',
        title=f'{p1} v. {p2}',
        income_df=income_df,
        expense_df=expense_df,
        overall_df=overall_df
    )


@fin.route('/select-mvb', methods=['GET', 'POST'])
def select_mvb():
    """Page to select month to compare with budget"""
    if request.method == 'POST':
        yyyy = request.values.get(f'pd-year')
        mm = request.values.get(f'pd-month')
        period = f'{int(mm):02d}-{yyyy}'
        return redirect(url_for('finances.get_mvb', period=period))
    else:
        years = [i + 2020 for i in range(datetime.now().year - 2020 + 1)]
        return render_template('select-mvb.html', years=years, current=datetime.now())


@fin.route('/mvb/<string:period>')
def get_mvb(period: str):
    """For rendering a month v budget comparison"""
    # Confirm strings are of MM-YYYY format
    if re.match(r'\d{2}-\d{4}', period) is None:
        return page_not_found(ValueError(f'The provided value did not match the '
                                         f'expected syntax: mm-yyyy: "{period}"'))
    df = pd.DataFrame()
    p_mm, p_yy = [int(x) for x in period.split('-')]
    df = load_data_into_df(df, query_result=get_periods_transations(period=period), period_name='actual')

    # Collect the budget for the target period
    b_data = get_db().session.query(TableBudget).filter(
        and_(TableBudget.month == p_mm, TableBudget.year == p_yy)).all()
    df = load_data_into_df(df, query_result=b_data, period_name='budget')

    # Consolidate the dataframe
    pivoted = df.pivot_table(index=['type', 'category', 'account'], columns=['period'],
                             values='amt', aggfunc='sum').fillna(0).reset_index()
    # Remove bank, receivable & credit activity
    pivoted = pivoted.loc[~pivoted['type'].isin(['bank', 'equity', 'credit', 'receivable']), :]
    # Income, liability needs to be 'flipped'
    pivoted.loc[pivoted['type'].isin(['income', 'liability']), 'actual'] = \
        pivoted.loc[pivoted['type'].isin(['income', 'liability']), 'actual'] * -1
    # Add in a delta column
    pivoted['change'] = pivoted['actual'] - pivoted['budget']

    # Ensure column order (p1 is always the focus, p2 always the comparison)
    pivoted = pivoted[['type', 'category', 'account', 'budget', 'actual', 'change']]
    # Split into separate income / expenses; invert income, as it typically is negative
    income_df = pivoted.loc[pivoted['category'] == 'INCOME', ].drop(['type', 'category'], axis=1)
    expense_df = pivoted.loc[pivoted['category'] != 'INCOME', ].drop(['type', 'category'], axis=1)
    # Sum income / expenses
    income_df = pd.concat([income_df, pd.DataFrame([income_df.sum(numeric_only=True)])],
                          ignore_index=True).fillna('Total')
    expense_df = pd.concat([expense_df, pd.DataFrame([expense_df.sum(numeric_only=True)])],
                           ignore_index=True).fillna('Total')
    # Get total profit / loss for both budgeted & actual
    overall_df = pd.concat([
        income_df.loc[income_df['account'] == 'Total', :],
        expense_df.loc[expense_df['account'] == 'Total', :]
    ])
    overall_df = pd.concat([overall_df, pd.DataFrame([overall_df[['budget', 'actual']].diff().iloc[1] * -1])])
    overall_df['account'] = ['Income', 'Expense', 'P/L']
    overall_df['change'] = overall_df['actual'] - overall_df['budget']

    return render_template(
        'compare.html',
        title=f'Budget v. Actual: {period}',
        income_df=income_df,
        expense_df=expense_df,
        overall_df=overall_df
    )
