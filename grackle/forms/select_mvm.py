from datetime import (
    datetime,
    timedelta,
)

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired


class SelectMvM(FlaskForm):
    """Month v. month form"""
    focus_yyyy = SelectField(
        label='Focus Year',
        validators=[DataRequired()],
        default=datetime.today().year,
        choices=range(2021, datetime.today().year + 1)
    )
    focus_mm = SelectField(
        label='Focus Month',
        validators=[DataRequired()],
        default=datetime.today().month,
        choices=range(1, 13)
    )

    compare_yyyy = SelectField(
        label='Compare Year',
        validators=[DataRequired()],
        default=(datetime.today().replace(day=1) - timedelta(days=1)).year,
        choices=range(2021, datetime.today().year + 1)
    )
    compare_mm = SelectField(
        label='Compare Month',
        validators=[DataRequired()],
        default=(datetime.today().replace(day=1) - timedelta(days=1)).month,
        choices=range(1, 13)
    )

    submit = SubmitField('Submit')
