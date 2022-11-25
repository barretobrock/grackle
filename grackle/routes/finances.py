from datetime import (
    datetime,
    timedelta,
)
import re
from typing import (
    List,
    Tuple,
)

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
import pandas as pd

from grackle.core.queries import GrackleQueries
from grackle.model import (
    AccountType,
    TableTransactionSplit,
)

fin = Blueprint('finances', __name__)


def get_periods_transactions(period: str) -> List[TableTransactionSplit]:
    """Gets the transactions for the given period in MM-YYYY format"""
    allowed_types = [
        AccountType.LIABILITY,
        AccountType.EXPENSE,
        AccountType.INCOME
    ]
    p_mm, p_yy = [int(x) for x in period.split('-')]
    p_st = datetime(p_yy, p_mm, 1)
    p_end = (p_st + timedelta(days=33)).replace(day=1) - timedelta(days=1)
    p_data = GrackleQueries.get_transactions(start_date=p_st, end_date=p_end, acct_type=allowed_types)
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


def load_data_into_df(query_result: List[TableTransactionSplit], period_name: str) -> \
        Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts the necessary data from the query results, organizes them into a presentation dataframe.
    Returns:
        Tuple[
            first dataframe of transactions organized for presentation,
            second dataframe as summary of income, expense-like and overall figures
        ]
    """
    df = pd.DataFrame()
    row: TableTransactionSplit
    for row in query_result:
        # Load data into dataframe
        new_data = pd.DataFrame({
            'period': period_name,
            'type': row.account.account_type.name,
            'category': row.account.account_category.name,
            'account': row.account.name,
            'full_name': row.account.full_name,
            'amt': row.amount,
            'cur': row.account.account_currency.name,
            'parent': '.'.join(row.account.full_name.split('.')[:-1])
        }, index=[0])
        df = pd.concat([df, new_data])

    income_filter = (df['type'] == 'INCOME')
    expense_filter = (df['type'] != 'INCOME')  # This can often include liabilities
    overall_df = pd.DataFrame(
        {
            'period': period_name,
            'type': x,
            'category': x,
            'amt': df.loc[f, 'amt'].sum()
        } for x, f in zip(['INCOME', 'EXPENSE'], [income_filter, expense_filter])
    )
    if period_name != 'budget':
        # Actual income figures are negative - reverse that here
        overall_df.loc[overall_df['type'] == 'INCOME', 'amt'] *= -1
        df.loc[df['type'] == 'INCOME', 'amt'] *= -1
    else:
        # So, for budgets, liabilities are presented as negative :)
        overall_df.loc[overall_df['type'] == 'LIABILITY', 'amt'] *= -1
        df.loc[df['type'] == 'LIABILITY', 'amt'] *= -1

    def handle_add_missing_parent(_df: pd.DataFrame, parent_name: str) -> pd.DataFrame:
        prow = _df.loc[_df['parent'] == parent_name, :].iloc[0]
        psplit = parent_name.split('.')
        pname = psplit[-1]
        parentparent = '.'.join(psplit[:-1])
        _df = pd.concat([_df, pd.DataFrame({
            'period': period_name,
            'type': prow['type'],
            'category': prow['category'],
            'account': pname,
            'full_name': parent_name,
            'amt': 0,
            'cur': 'USD',
            'parent': parentparent
        }, index=[0])], ignore_index=True)
        if '.' in parentparent and parentparent not in _df['full_name'].to_list():
            _df = handle_add_missing_parent(_df, parent_name=parentparent)
        return _df

    parents = df['parent'].unique().tolist()
    for parent in parents:
        if parent not in df['full_name'].to_list():
            # Add a column with the parent there. Make sure the parent of the parent etc. are also in place
            df = handle_add_missing_parent(df, parent_name=parent)
    return df, overall_df


@fin.route('/mvm/<string:p1>/<string:p2>')
def get_mvm(p1: str, p2: str):
    """For rendering a month v month comparison"""
    # Confirm strings are of MM-YYYY format
    if any([re.match(r'\d{2}-\d{4}', x) is None for x in [p1, p2]]):
        return page_not_found(ValueError(f'One or more of the provided values did not match '
                                         f'the expected syntax: mm-yyyy: "{p1}", "{p2}"'))
    df = pd.DataFrame()
    overall_df = pd.DataFrame()
    for p in [p1, p2]:
        df, overall_df = load_data_into_df(query_result=get_periods_transactions(period=p), period_name=p)

    # Consolidate the dataframe
    pivoted = df.pivot_table(index=['type', 'category', 'account'], columns=['period'],
                             values='amt', aggfunc='sum').fillna(0).reset_index()
    # Remove bank, receivable & credit activity
    pivoted = pivoted.loc[~pivoted['type'].isin(['BANK', 'EQUITY', 'CREDIT', 'RECEIVABLE']), :]
    # Income, liability needs to be 'flipped'
    pivoted.loc[pivoted['type'].isin(['INCOME', 'LIABILITY']), [p1, p2]] = \
        pivoted.loc[pivoted['type'].isin(['INCOME', 'LIABILITY']), [p1, p2]] * -1
    # Add in a delta column
    pivoted['change'] = pivoted[p1] - pivoted[p2]
    # Ensure column order (p1 is always the focus, p2 always the comparison)
    pivoted = pivoted[['type', 'category', 'account', p1, p2, 'change']]
    expense_df, income_df, overall_df = prep_compare_dfs(pivoted_df=pivoted, reference_col=p1,
                                                         compare_col=p2)
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
        yyyy = request.values.get('pd-year')
        mm = request.values.get('pd-month')
        period = f'{int(mm):02d}-{yyyy}'
        return redirect(url_for('finances.get_mvb', period=period))
    else:
        years = [i + 2020 for i in range(datetime.now().year - 2020 + 1)]
        return render_template('select-mvb.html', years=years, current=datetime.now())


def prep_compare_dfs(pivoted_df: pd.DataFrame, overall_df: pd.DataFrame, reference_col: str = 'budget',
                     compare_col: str = 'actual') -> \
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Cleans and organizes the pivoted dataframe, splits into expense income and overall dfs"""
    # Split into separate income / expenses; invert income, as it typically is negative
    income_df = pivoted_df.loc[pivoted_df['category'] == 'INCOME', ]
    expense_df = pivoted_df.loc[pivoted_df['category'].isin(['EXPENSE', 'LOAN', 'MORTGAGE']), ]

    # Add in Totals to inc/exp dfs from overall
    income_df = pd.concat([income_df, overall_df.loc[overall_df['type'] == 'INCOME', :]], ignore_index=True).fillna('')
    expense_df = pd.concat([expense_df, overall_df.loc[overall_df['type'] == 'EXPENSE', :]], ignore_index=True).fillna('')

    # Get total profit / loss for both budgeted & actual
    overall_df = pd.concat([overall_df, pd.DataFrame({
        'type': 'P/L',
        'account': 'P/L',
        'full_name': 'Total',
        'level': 0,
        compare_col: overall_df[compare_col].diff().values[-1],
        reference_col: overall_df[reference_col].diff().values[-1],
        'change': overall_df['change'].diff().values[-1],
    }, index=[0])], ignore_index=True)
    return expense_df, income_df, overall_df


@fin.route('/mvb/<string:period>')
def get_mvb(period: str):
    """For rendering a month v budget comparison"""
    # Confirm strings are of MM-YYYY format
    if re.match(r'\d{2}-\d{4}', period) is None:
        return page_not_found(ValueError(f'The provided value did not match the '
                                         f'expected syntax: mm-yyyy: "{period}"'))
    p_mm, p_yy = [int(x) for x in period.split('-')]
    actual_df, overall_actual_df = load_data_into_df(query_result=get_periods_transactions(period=period),
                                                     period_name='actual')

    # Collect the budget for the target period
    b_data = GrackleQueries.get_budget_data_for_month(mm=p_mm, yyyy=p_yy)
    budget_df, overall_budget_df = load_data_into_df(query_result=b_data, period_name='budget')

    df = pd.concat([actual_df, budget_df], ignore_index=True)
    pivoted = df.pivot_table(index=['type', 'category', 'parent', 'account', 'full_name'], columns=['period'],
                             values='amt', aggfunc='sum').fillna(0).reset_index()
    pivoted = pivoted.loc[pivoted['parent'] != '', :].reset_index(drop=True)
    pivoted['level'] = pivoted['full_name'].str.count(r'\.')
    for i, row in pivoted.iterrows():
        name = row['full_name']
        for per in ['actual', 'budget']:
            row[per] = pivoted.loc[pivoted['full_name'].str.startswith(name), per].sum()
        pivoted.iloc[i] = row
    pivoted = pivoted.sort_values('full_name')

    # Add in a delta column
    pivoted['change'] = pivoted['actual'] - pivoted['budget']

    # Work on overalls
    overall_df = pd.concat([overall_actual_df, overall_budget_df], ignore_index=True)
    overall_df = overall_df.pivot_table(index=['type'], columns='period', values='amt').reset_index()
    overall_df['change'] = overall_df['actual'] - overall_df['budget']
    overall_df['account'] = overall_df['type']
    overall_df['full_name'] = 'Total'
    overall_df['level'] = 0

    expense_df, income_df, overall_df = prep_compare_dfs(
        pivoted_df=pivoted, overall_df=overall_df, reference_col='budget', compare_col='actual'
    )

    return render_template(
        'compare.html',
        title=f'Budget v. Actual: {period}',
        headers=['account', 'actual', 'budget', 'change'],
        income_df=income_df,
        expense_df=expense_df,
        overall_df=overall_df
    )
