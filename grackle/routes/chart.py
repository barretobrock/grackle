from datetime import datetime
import json

from flask import (
    Blueprint,
    flash,
    render_template,
)
import plotly
import plotly.graph_objs as go

from grackle.core.charting import ChartPrep
from grackle.core.queries import GrackleQueries
from grackle.forms.budget_analysis_form import BudgetAnalysisForm
from grackle.model import AccountCategory
from grackle.routes.helpers import (
    log_after,
    log_before,
)

chart = Blueprint('chart', __name__, url_prefix='/chart')


@chart.before_request
def log_before_():
    log_before()


@chart.after_request
def log_after_(response):
    return log_after(response)


@chart.route('/overview')
def overview():
    pass
    # TODO: Dashed line for extrapolating (moving average?) the next n_days,
    #  second stacked area graph for savings accounts,
    #  use the account name instead of the full name in the graph
    groups = {}
    for cat in [AccountCategory.CHECKING, AccountCategory.SAVINGS]:
        transactions = GrackleQueries.get_transactions(acct_category=cat)
        df = ChartPrep.get_balances(transactions=transactions, split_future=False)
        fig = ChartPrep.plot_timeseries(df, n_days_ma=14, as_area=cat == AccountCategory.SAVINGS)
        fig.update_layout(title=f'{cat.name.title()} Account History', xaxis_title='Date',
                          yaxis_title='USD', hovermode='x',
                          template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        groups[cat.name] = graphJSON

    return render_template('chart.html', graph_dict=groups)


@chart.route('/budget-analysis', methods=['GET', 'POST'])
def budget_analysis():
    """Provides analysis of monthly spend per account as box & whisker plot"""
    form = BudgetAnalysisForm()
    form.accounts.choices = GrackleQueries.get_account_names()

    if form.validate_on_submit():
        if form.account_category.data == 'None':
            form.account_category.data = None
        if form.account_type.data == 'None':
            form.account_type.data = None
        transactions = GrackleQueries.get_transactions(
            acct_type=form.account_type.data,
            acct_category=form.account_category.data,
            acct_full_name=form.accounts.data,
            start_date=form.start_date.data
        )
        if len(transactions) == 0:
            flash('No transactions found matching that criteria.', 'alert alert-info')
            return render_template('budget-analysis.html', graphJSON=None, form=form)
        df = ChartPrep.get_monthly_activity(transactions=transactions)
        fig = go.Figure()
        for acct in df['account'].unique().tolist():
            # Get subset of transactions associated with acount
            subset = df.loc[df['account'] == acct, 'amt']
            fig.add_trace(
                go.Box(x=subset, name=acct)
            )
        fig.update_layout(xaxis_title='Account', yaxis_title='USD', height=700,
                          template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('budget-analysis.html', graphJSON=graphJSON, form=form)

    return render_template('budget-analysis.html', graphJSON=None, form=form)


@chart.route('/budget-over-time')
def budget_ot():
    # TODO: Make a chart of budget v. actual diffs over time to see how they've progressed
    pass


@chart.route('/monthly-activity')
def show_monthly_activity(account_name: str, start_date: datetime = None):
    if start_date is None:
        start_date = datetime(2020, 1, 1)
    transactions = GrackleQueries.get_transactions(acct_name=account_name, start_date=start_date)
    return transactions
