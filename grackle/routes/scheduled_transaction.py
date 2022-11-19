from flask import (
    Response,
    Blueprint,
    request,
    make_response,
    current_app
)

sched_transaction = Blueprint('scheduled_transaction', __name__)


def get_db():
    return current_app.config['db']


@sched_transaction.route('/api/scheduled_transaction/new', methods=['POST'])
def scheduled_transaction_new() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    data = request.get_json()
    # TODO: parse the transaction description, date, splits, etc into items to feed into the

    return make_response('', 200)


@sched_transaction.route('/api/scheduled_transaction/edit/<int:transaction_id>', methods=['POST'])
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


@sched_transaction.route('/api/scheduled_transaction/delete/<int:transaction_id>', methods=['POST'])
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