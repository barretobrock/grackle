import json
from flask import (
    render_template,
    Blueprint
)
import plotly
import plotly.graph_objs as go
# from grackle.core.charting import ChartPrep
from grackle.model import (
    TableAccount,
    AccountCategory
)
from grackle.forms import (
    BudgetAnalysisForm
)
import app.app as grapp


chart = Blueprint('charts', __name__)


@chart.route('/overview')
def overview():
    pass
    # TODO: Dashed line for extrapolating (moving average?) the next n_days,
    #  second stacked area graph for savings accounts,
    #  use the account name instead of the full name in the graph
    # groups = {}
    # for cat in [AccountCategory.CHECKING, AccountCategory.SAVINGS]:
    #     acct_objs = grapp.db.session.query(TableAccount).filter(TableAccount.account_category == cat).all()
    #     accts = [x.friendly_name for x in acct_objs]
    #     df = ChartPrep.get_balances(friendly_name=accts, split_future=cat == AccountCategory.CHECKING)
    #     fig = ChartPrep.plot_timeseries(df, n_days_ma=14, as_area=cat == AccountCategory.SAVINGS)
    #     fig.update_layout(title=f'{cat.name.title()} Account History', xaxis_title='Date',
    #                       yaxis_title='USD', hovermode='x')
    #     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #     groups[cat.name] = graphJSON
    #
    # return render_template('chart.html', graph_dict=groups)


@chart.route('/budget-analysis', methods=['GET', 'POST'])
def budget_analysis():
    """Provides analysis of monthly spend per account as box & whisker plot"""
    pass
    # form = BudgetAnalysisForm()
    # if form.validate_on_submit():
    #     df = ChartPrep.get_monthly_activity(form.account_regex.data)
    #     fig = go.Figure()
    #     for acct in df['account'].unique().tolist():
    #         # Get subset of transactions associated with acount
    #         subset = df.loc[df['account'] == acct, 'amt']
    #         fig.add_trace(
    #             go.Box(x=subset, name=acct)
    #         )
    #     fig.update_layout(xaxis_title='Account', yaxis_title='USD', height=700)
    #     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #     return render_template('budget-analysis.html', graphJSON=graphJSON, form=form)
    # return render_template('budget-analysis.html', graphJSON=None, form=form)


@chart.route('/budget-over-time')
def budget_ot():
    # TODO: Make a chart of budget v. actual diffs over time to see how they've progressed
    pass

