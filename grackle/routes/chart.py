import json
from datetime import datetime as dt
from typing import List, Union, Dict
from flask import render_template, Blueprint, current_app
from sqlalchemy.sql import func
import pandas as pd
import plotly
import plotly.graph_objs as go
from grackle.core import ChartPrep
from grackle.model import (
    TableAccounts,
    AccountCategory
)
import grackle.routes.app as grapp


cht = Blueprint('charts', __name__)


@cht.route('/overview')
def overview():
    # TODO: Dashed line for extrapolating (moving average?) the next n_days,
    #  second stacked area graph for savings accounts,
    #  use the account name instead of the full name in the graph
    groups = {}
    for cat in [AccountCategory.CHECKING, AccountCategory.SAVINGS]:
        acct_objs = grapp.db.session.query(TableAccounts).filter(TableAccounts.account_category == cat).all()
        accts = [x.friendly_name for x in acct_objs]
        df = ChartPrep.get_balances(friendly_name=accts, split_future=cat == AccountCategory.CHECKING)
        fig = ChartPrep.plot_timeseries(df, n_days_ma=14, as_area=cat == AccountCategory.SAVINGS)
        fig.update_layout(title=f'{cat.name.title()} Account History', xaxis_title='Date',
                          yaxis_title='USD', hovermode='x')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        groups[cat.name] = graphJSON

    return render_template('chart.html', graph_dict=groups)


@cht.route('/budget')
def budget_over_time():
    # TODO: Make a chart of budget v. actual diffs over time to see how they've progressed
    pass
