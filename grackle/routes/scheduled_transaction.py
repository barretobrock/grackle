from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
)

sched_transaction = Blueprint('scheduled_transaction', __name__, url_prefix='/scheduled_transaction')


def get_db():
    return current_app.config['db']


@sched_transaction.route('/all')
def get_scheduled_transactions() -> Response:
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
