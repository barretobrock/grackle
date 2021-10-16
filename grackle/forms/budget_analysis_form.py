from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BudgetAnalysisForm(FlaskForm):
    """Budget analysis form"""
    account_regex = StringField(
        'Account Filter',
        [DataRequired()]
    )
    submit = SubmitField('Submit')
