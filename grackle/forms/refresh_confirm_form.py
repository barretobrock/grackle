from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    SubmitField
)
from wtforms.validators import DataRequired


class ConfirmRefreshForm(FlaskForm):
    """KeyGen form"""
    confirm = BooleanField(
        label='Are you sure?',
        validators=[DataRequired()],
    )
    submit = SubmitField('Submit')