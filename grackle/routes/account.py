from flask import (
    Response,
    Blueprint,
    request,
    make_response,
    current_app,
    jsonify
)
from grackle.model import (
    TableAccount,
    TableTransaction,
    TableTransactionSplit
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


@account.route('/api/account/new', methods=['POST'])
def account_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@account.route('/api/account/edit/<int:account_id>', methods=['POST'])
def account_edit(account_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # Get the transaction
    transaction = get_db().session.query(TableAccount).filter(
        TableAccount.account_id == account_id).one_or_none()
    if transaction is None:
        # TODO: Not found error response
        return make_response('', 404)
    data = request.get_json()

    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@account.route('/api/account/delete/<int:account_id>', methods=['POST'])
def account_delete(account_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # data = request.get_json()
    # # TODO: get a confirmation code generated from react to ensure this wasn't done in error
    # # Get the transaction
    # transaction = db.session.query(TableAccount).filter(
    #     TableAccount.account_id == account_id).one_or_none()
    # if transaction is None:
    #     # TODO: Not found error response
    #     return make_response('', 404)

    return make_response('', 200)


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


@account.route('/api/account/reconcile/<int:account_id>', methods=['GET'])
def account_reconciliation(account_id: int) -> Response:
    """"""
    return make_response('', 200)
