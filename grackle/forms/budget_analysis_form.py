from datetime import (
    datetime,
    timedelta,
)

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    SelectMultipleField,
    SubmitField,
)
from wtforms.validators import DataRequired

from grackle.model import (
    AccountCategory,
    AccountType,
)


class BudgetAnalysisForm(FlaskForm):
    """Budget analysis form"""
    start_date = DateField(
        label='Start Date',
        validators=[DataRequired()],
        default=(datetime.today().replace(day=1) - timedelta(days=90)).replace(day=1),
        format='%Y-%m-%d'
    )
    account_type = SelectField(
        label='Account Type',
        validators=[DataRequired()],
        choices=['None'] + [x.name for x in list(AccountType)],
        default='None'
    )
    account_category = SelectField(
        label='Account Category',
        validators=[DataRequired()],
        choices=['None'] + [x.name for x in list(AccountCategory)],
        default='None'
    )
    accounts = SelectMultipleField(
        label='Account Names',
        validators=[DataRequired()],
    )

    submit = SubmitField('Submit')

    # def __init__(self, acct_list: List[str]):
    #     super().__init__()
    #     self.accounts.data = acct_list
