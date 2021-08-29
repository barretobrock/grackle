import json
from flask import Flask, render_template, Blueprint
import pandas as pd
import plotly
import plotly.express as px


cht = Blueprint('chart', __name__)


@cht.route('/chart1')
def chart1():
    df = pd.DataFrame({
        'Fruit': ['apples', 'oranges', 'bananas', 'apples', 'oranges', 'bananas'],
        'Amount': [4, 1, 2, 2, 4, 5],
        'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
    })
    fig = px.bar(df, x='Fruit', y='Amount', color='City', barmode='group')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html', graphJSON=graphJSON)
