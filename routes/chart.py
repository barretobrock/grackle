import json
from datetime import datetime as dt
from typing import List, Union, Dict
from flask import render_template, Blueprint, current_app
import pandas as pd
import plotly
import plotly.graph_objs as go


cht = Blueprint('charts', __name__)
DEFAULT_COLORS = [
    'rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)', 'rgb(214, 39, 40)', 'rgb(148, 103, 189)',
    'rgb(140, 86, 75)', 'rgb(227, 119, 194)', 'rgb(127, 127, 127)', 'rgb(188, 189, 34)', 'rgb(23, 190, 207)'
]


def prep_timeseries(df: pd.DataFrame, group_cols: Union[List[str], str], date_col: str = 'date',
                    agg_dict: Dict[str, str] = None) -> pd.DataFrame:
    """Preps a dataframe for time series plotting"""
    if agg_dict is None:
        # Use default
        agg_dict = {
            'amt': 'sum'
        }
    if date_col not in group_cols:
        group_cols.append(date_col)
    grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)
    # Remove date col from list before pivoting
    _ = group_cols.pop(group_cols.index(date_col)) if date_col in group_cols else None
    # Pivot the grouping so it's one column per item
    pivoted = grouped.pivot(values='amt', index=date_col, columns=group_cols).fillna(0).cumsum().reset_index()
    p_future = pivoted.loc[pivoted['date'].dt.date >= dt.now().date()]
    # Move the values from today onward to a new column
    pivoted = pd.merge(pivoted, pivoted.loc[pivoted['date'].dt.date >= dt.now().date()], how='left', on='date', suffixes=('', '_future'))
    pivoted.loc[p_future.index, p_future.columns[1:]] = None
    # TODO: grab the last 'past' data row with data on it and copy
    #  to the 'future' column so the chart will be continuous
    return pivoted


@cht.route('/overview')
def overview():
    # TODO: Dashed line for extrapolating (moving average?) the next n_days,
    #  second stacked area graph for savings accounts,
    #  use the account name instead of the full name in the graph
    df = current_app.config['GNC'].transactions_df.copy()
    df = df.loc[df['category'] == 'CHECKING']
    accts = df['fullname'].unique().tolist()
    pivoted = prep_timeseries(df, ['fullname', 'date'])
    fig = go.Figure()
    for i, col in enumerate(pivoted.columns.tolist()[1:]):
        if col in accts:
            # This is past data
            color = DEFAULT_COLORS[i]
            line = dict(color=color)
        else:
            # Likely future data. Look up the color for the account minus '_future'
            color = DEFAULT_COLORS[accts.index(col.replace('_future', ''))]
            line = dict(color=color, dash='dot')
        fig.add_trace(
            go.Scatter(x=pivoted['dte'], y=pivoted[col], name=col, mode='lines', line=line)
        )
    fig.update_layout(title='Checking Accts History', xaxis_title='Date', yaxis_title='USD')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html', graphJSON=graphJSON)
