from datetime import (
    datetime,
    timedelta,
)

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired


class BudgetAnalysisForm(FlaskForm):
    """Budget analysis form"""
    start_date = DateField(
        label='Start Date',
        validators=[DataRequired()],
        default=(datetime.today().replace(day=1) - timedelta(days=3)).replace(day=1)
    )
    account_regex = StringField(
        label='Account Filter',
        validators=[DataRequired()],
        default='.*'
    )

    submit = SubmitField('Submit')
