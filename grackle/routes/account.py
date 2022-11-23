from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
)

from grackle.model import (
    TableAccount,
    TableTransaction,
    TableTransactionSplit,
)

account = Blueprint('account', __name__)


def get_db():
    return current_app.config['db']


@account.route('/api/accounts', methods=['GET'])
def get_accounts() -> Response:
    """Get all accounts from db"""
    accounts = get_db().session.query(TableAccount).all()
    names = [
        {'id': x.account_id, 'name': x.fullname} for x in accounts
    ]

    return jsonify({'accounts': names})


# ---- VIEWS
@account.route('/api/account/transactions/<int:account_id>', methods=['GET'])
def account_transactions(account_id: int) -> Response:
    """Retrieves all transactions for the given account"""
    splits = get_db().session.query(TableTransactionSplit).filter(
        TableTransactionSplit.account_key == account_id
    ) \
        .join(TableTransaction, TableTransactionSplit.transaction) \
        .order_by(TableTransaction.transaction_date.asc()).all()

    # TODO: For first item in split, get the closing balance for the previous day to carry forward

    account_splits = []
    balance = 0
    for split in splits:
        balance = balance - abs(split.amount) if split.is_credit else balance + abs(split.amount)
        account_splits.append({
            'id': split.transaction_split_id,
            'transaction_id': split.transaction_key,
            'transaction_date': split.transaction.transaction_date.strftime('%F'),
            'is_credit': split.is_credit,
            'desc': split.transaction.desc,
            'reconciled': split.reconciled_state.name,
            'invoice': split.invoice_no,
            'amount': split.amount,
            'balance': balance
        })

    return jsonify({'splits': account_splits})
