import time
from typing import Dict
from flask import (
    Flask,
    Response,
    render_template,
    Blueprint,
    request,
    make_response,
    flash,
    redirect,
    url_for,
    current_app,
    jsonify
)
from flask_sqlalchemy import SQLAlchemy
from grackle.model import (
    TableAccount,
    TableTransaction,
    TableTransactionSplit,
    TableScheduledTransaction,
    TableScheduledTransactionSplit
)
from grackle.settings import auto_config

api = Blueprint('api', __name__)


def get_db() -> SQLAlchemy:
    return current_app.config['db']


@api.route('/api/time')
def get_current_time() -> Dict[str, float]:
    time.sleep(3)
    return {'time': time.time()}


# ---- TRANSACTIONS
@api.route('/api/transactions/descriptions', methods=['GET'])
def get_transaction_descriptions():
    transactions = get_db().session.query(TableTransaction).group_by(TableTransaction.desc).all()
    names = [{'id': x.transaction_id, 'desc': x.desc} for x in transactions]
    return jsonify({'transactions': names})


@api.route('/api/transaction/new', methods=['POST'])
def transaction_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@api.route('/api/transaction/edit/<int:transaction_id>', methods=['POST'])
def transaction_edit(transaction_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # Get the transaction
    transaction = db.session.query(TableTransaction).filter(
        TableTransaction.transaction_id == transaction_id).one_or_none()
    if transaction is None:
        # TODO: Not found error response
        return make_response('', 404)
    data = request.get_json()

    # TODO: parse the transaction description, date, splits, etc into items to feed into th
    
    return make_response('', 200)


@api.route('/api/transaction/delete/<int:transaction_id>', methods=['POST'])
def transaction_delete(transaction_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: get a confirmation code generated from react to ensure this wasn't done in error
    # # Get the transaction
    # session = get_session()
    # transaction = session.query(TableTransaction).filter(
    #     TableTransaction.transaction_id == transaction_id).one_or_none()
    # if transaction is None:
    #     # TODO: Not found error response
    #     return make_response('', 404)

    return make_response('', 200)


# ---- SCHEDULED TRANSACTIONS
@api.route('/api/scheduled_transaction/new', methods=['POST'])
def scheduled_transaction_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    
    return make_response('', 200)


@api.route('/api/scheduled_transaction/edit/<int:transaction_id>', methods=['POST'])
def scheduled_transaction_edit(transaction_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # Get the transaction
    # session = get_session()
    # transaction = session.query(TableScheduledTransaction).filter(
    #     TableScheduledTransaction.scheduled_transaction_id == transaction_id).one_or_none()
    # if transaction is None:
    #     # TODO: Not found error response
    #     return make_response('', 404)
    # data = request.get_json()

    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@api.route('/api/scheduled_transaction/delete/<int:transaction_id>', methods=['POST'])
def scheduled_transaction_delete(transaction_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # data = request.get_json()
    # # TODO: get a confirmation code generated from react to ensure this wasn't done in error
    # # Get the transaction
    # session = get_session()
    # transaction = session.query(TableScheduledTransaction).filter(
    #     TableScheduledTransaction.scheduled_transaction_id == transaction_id).one_or_none()
    # if transaction is None:
    #     # TODO: Not found error response
    #     return make_response('', 404)

    return make_response('', 200)


# ---- ACCOUNTS
@api.route('/api/accounts', methods=['GET'])
def get_accounts() -> Response:
    """Get all accounts from db"""
    accounts = get_db().session.query(TableAccount).all()
    names = [{'id': x.account_id, 'name': x.fullname} for x in accounts]
    
    return jsonify({'accounts': names})


@api.route('/api/account/new', methods=['POST'])
def account_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@api.route('/api/account/edit/<int:account_id>', methods=['POST'])
def account_edit(account_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # Get the transaction
    transaction = db.session.query(TableAccount).filter(
        TableAccount.account_id == account_id).one_or_none()
    if transaction is None:
        # TODO: Not found error response
        return make_response('', 404)
    data = request.get_json()

    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@api.route('/api/account/delete/<int:account_id>', methods=['POST'])
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
@api.route('/api/account/transactions/<int:account_id>', methods=['GET'])
def account_transactions(account_id: int) -> Response:
    """Retrieves all transactions for the given account"""
    splits = get_db().session.query(TableTransactionSplit).filter(
        TableTransactionSplit.account_key == account_id
    )\
        .join(TableTransaction, TableTransactionSplit.transaction)\
        .order_by(TableTransaction.transaction_date.asc()).all()

    #TODO: For first item in split, get the closing balance for the previous day to carry forward

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


@api.route('/api/account/reconcile/<int:account_id>', methods=['GET'])
def account_reconciliation(account_id: int) -> Response:
    """"""
    return make_response('', 200)
