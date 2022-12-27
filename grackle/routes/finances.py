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
from grackle.forms import (
    SelectMvB,
    SelectMvM,
)
from grackle.model import (
    AccountType,
    Currency,
    TableTransactionSplit,
)
from grackle.routes.helpers import (
    log_after,
    log_before,
)

fin = Blueprint('finances', __name__)


def get_periods_transactions(period: str, is_excl_repays: bool = True, currency: str = None) -> \
        List[TableTransactionSplit]:
    """Gets the transactions for the given period in MM-YYYY format"""
    allowed_types = [
        AccountType.LIABILITY,
        AccountType.EXPENSE,
        AccountType.INCOME
    ]
    excl_repays = r'%.MPO.%' if is_excl_repays else None
    p_mm, p_yy = [int(x) for x in period.split('-')]
    p_st = datetime(p_yy, p_mm, 1)
    p_end = (p_st + timedelta(days=33)).replace(day=1) - timedelta(days=1)
    p_data = GrackleQueries.get_transactions(start_date=p_st, end_date=p_end, acct_type=allowed_types,
                                             acct_currs=currency,
                                             acct_excl_like=excl_repays)
    return p_data


def load_query_data_into_df(query_result: List[TableTransactionSplit], period_name: str) -> \
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


def prep_compare_dfs(raw_df: pd.DataFrame, overall_df: pd.DataFrame, reference_col: str = 'budget',
                     compare_col: str = 'actual') -> \
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Cleans and organizes the pivoted dataframe, splits into expense income and overall dfs"""

    pivoted_df = raw_df.pivot_table(index=['type', 'category', 'parent', 'account', 'full_name'],
                                    columns=['period'], values='amt', aggfunc='sum').fillna(0).reset_index()
    pivoted_df = pivoted_df.loc[pivoted_df['parent'] != '', :].reset_index(drop=True)
    pivoted_df['level'] = pivoted_df['full_name'].str.count(r'\.')
    for i, row in pivoted_df.iterrows():
        name = row['full_name']
        for per in [compare_col, reference_col]:
            row[per] = pivoted_df.loc[pivoted_df['full_name'].str.startswith(name), per].sum()
        pivoted_df.iloc[i] = row
    pivoted_df = pivoted_df.sort_values('full_name')

    # Add in a delta column
    pivoted_df['change'] = pivoted_df[compare_col] - pivoted_df[reference_col]
    pivoted_df = pivoted_df[['type', 'category', 'parent', 'account', 'full_name', compare_col, reference_col,
                             'change', 'level']]

    # Work on overalls
    overall_df = overall_df.pivot_table(index=['type'], columns='period', values='amt').reset_index()
    overall_df['change'] = overall_df[compare_col] - overall_df[reference_col]
    overall_df['account'] = overall_df['type']
    overall_df['full_name'] = 'Total'
    overall_df['level'] = 0

    # Split into separate income / expenses; invert income, as it typically is negative
    income_df = pivoted_df.loc[pivoted_df['category'] == 'INCOME', ]
    expense_df = pivoted_df.loc[pivoted_df['category'].isin(['EXPENSE', 'LOAN', 'MORTGAGE']), ]

    # Add in Totals to inc/exp dfs from overall
    income_df = pd.concat([income_df, overall_df.loc[overall_df['type'] == 'INCOME', :]],
                          ignore_index=True).fillna('')
    expense_df = pd.concat([expense_df, overall_df.loc[overall_df['type'] == 'EXPENSE', :]],
                           ignore_index=True).fillna('')

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

    # Ensure overall columns are ordered properly
    overall_df = overall_df[['type', 'account', 'full_name', compare_col, reference_col, 'change', 'level']]
    return expense_df, income_df, overall_df


def page_not_found(e):
    return render_template('errors/404.html', error_msg=e), 404


@fin.before_request
def log_before_():
    log_before()


@fin.after_request
def log_after_(response):
    return log_after(response)


@fin.route('/select-mvm', methods=['GET', 'POST'])
def select_mvm():
    """Page to select months to compare"""
    form = SelectMvM()
    if request.method == 'POST':
        p1_yyyy = form.focus_yyyy.data
        p1_mm = int(form.focus_mm.data)
        p2_yyyy = form.compare_yyyy.data
        p2_mm = int(form.compare_mm.data)
        p1 = f'{p1_mm:02d}-{p1_yyyy}'
        p2 = f'{p2_mm:02d}-{p2_yyyy}'
        curr = form.currencies.data
        is_excl_repays = form.excl_repayments.data
        return redirect(url_for('finances.get_mvm', p1=p1, p2=p2, currency=curr, is_excl_repays=is_excl_repays))
    else:
        currs = [x.name for x in list(Currency)]
        form.currencies.choices = currs
        form.currencies.default = currs[1]
        return render_template('select-mvm.html', form=form)


@fin.route('/select-mvb', methods=['GET', 'POST'])
def select_mvb():
    """Page to select month to compare with budget"""
    form = SelectMvB()
    if request.method == 'POST':
        yyyy = form.year.data
        mm = form.month.data
        period = f'{int(mm):02d}-{yyyy}'
        return redirect(url_for('finances.get_mvb', period=period))
    else:
        form.budget_name.choices = GrackleQueries.get_budget_names()
        form.budget_name.default = GrackleQueries.get_budget_names()[0]
        return render_template('select-mvb.html', form=form)


@fin.route('/mvm/<string:p1>/<string:p2>')
def get_mvm(p1: str, p2: str):
    """For rendering a month v month comparison"""
    # Confirm strings are of MM-YYYY format
    if any([re.match(r'\d{2}-\d{4}', x) is None for x in [p1, p2]]):
        return page_not_found(ValueError(f'One or more of the provided values did not match '
                                         f'the expected syntax: mm-yyyy: "{p1}", "{p2}"'))
    curr = request.args.get('currency', Currency.USD.name)
    is_excl_repays = request.args.get('is_excl_repays', 'True') == 'True'
    df_list = []
    overall_df_list = []
    for p in [p1, p2]:
        transactions = get_periods_transactions(period=p, is_excl_repays=is_excl_repays, currency=curr)
        df, overall_df = load_query_data_into_df(query_result=transactions, period_name=p)
        df_list.append(df)
        overall_df_list.append(overall_df)

    df = pd.concat(df_list, ignore_index=True)
    overall_df = pd.concat(overall_df_list, ignore_index=True)
    expense_df, income_df, overall_df = prep_compare_dfs(raw_df=df, overall_df=overall_df, reference_col=p2,
                                                         compare_col=p1)
    return render_template(
        'compare.html',
        title=f'{p1} v. {p2}',
        headers=['account', p1, p2, 'change'],
        income_df=income_df,
        expense_df=expense_df,
        overall_df=overall_df
    )


@fin.route('/mvb/<string:period>')
def get_mvb(period: str):
    """For rendering a month v budget comparison"""
    # Confirm strings are of MM-YYYY format
    if re.match(r'\d{2}-\d{4}', period) is None:
        return page_not_found(ValueError(f'The provided value did not match the '
                                         f'expected syntax: mm-yyyy: "{period}"'))
    p_mm, p_yy = [int(x) for x in period.split('-')]
    actual_df, overall_actual_df = load_query_data_into_df(
        query_result=get_periods_transactions(period=period),
        period_name='actual'
    )

    # Collect the budget for the target period
    budget_df, overall_budget_df = load_query_data_into_df(
        query_result=GrackleQueries.get_budget_data_for_month(mm=p_mm, yyyy=p_yy),
        period_name='budget'
    )

    df = pd.concat([actual_df, budget_df], ignore_index=True)
    overall_df = pd.concat([overall_actual_df, overall_budget_df], ignore_index=True)

    expense_df, income_df, overall_df = prep_compare_dfs(
        raw_df=df, overall_df=overall_df, reference_col='budget', compare_col='actual'
    )

    return render_template(
        'compare.html',
        title=f'Budget v. Actual: {period}',
        headers=['account', 'actual', 'budget', 'change'],
        income_df=income_df,
        expense_df=expense_df,
        overall_df=overall_df
    )
