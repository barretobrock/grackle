from flask import (
    Response,
    Blueprint,
    request,
    make_response,
    current_app,
    jsonify
)
from grackle.model import TableTransaction

transaction = Blueprint('transaction', __name__)


def get_db():
    return current_app.config['db']


@transaction.route('/api/transactions/descriptions', methods=['GET'])
def get_transaction_descriptions():
    transactions = get_db().session.query(TableTransaction).group_by(TableTransaction.desc).all()
    names = [
        {'id': x.transaction_id, 'desc': x.desc} for x in transactions
    ]
    return jsonify({'transactions': names})


@transaction.route('/api/transaction/new', methods=['POST'])
def transaction_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@transaction.route('/api/transaction/edit/<int:transaction_id>', methods=['POST'])
def transaction_edit(transaction_id: int) -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # Get the transaction
    transaction = get_db().session.query(TableTransaction).filter(
        TableTransaction.transaction_id == transaction_id).one_or_none()
    if transaction is None:
        # TODO: Not found error response
        return make_response('', 404)
    data = request.get_json()

    # TODO: parse the transaction description, date, splits, etc into items to feed into th

    return make_response('', 200)


@transaction.route('/api/transaction/delete/<int:transaction_id>', methods=['POST'])
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