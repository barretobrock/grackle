from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired


class SelectMvB(FlaskForm):
    """Month v. budget form"""
    year = SelectField(
        label='Year',
        validators=[DataRequired()],
        default=datetime.today().year,
        choices=range(2021, datetime.today().year + 1)
    )
    month = SelectField(
        label='Month',
        validators=[DataRequired()],
        default=datetime.today().month,
        choices=range(1, 13)
    )
    budget_name = SelectField(
        label='Budget Name',
        validators=[DataRequired()],
    )

    submit = SubmitField('Submit')
