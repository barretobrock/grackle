from flask import (
    Blueprint,
    Response,
    make_response,
)

from grackle.model import TableScheduledTransaction
from grackle.routes.helpers import (
    get_db,
    log_after,
    log_before,
)

sched_transaction = Blueprint('scheduled_transaction', __name__, url_prefix='/scheduled_transaction')


@sched_transaction.before_request
def log_before_():
    log_before()


@sched_transaction.after_request
def log_after_(response):
    return log_after(response)


@sched_transaction.route('/all')
def get_scheduled_transactions() -> Response:
    """Take in a new transaction, parse info into splits and write to db"""
    # data = request.get_json()
    # # TODO: get a confirmation code generated from react to ensure this wasn't done in error
    # # Get the transaction
    # session = get_session()
    _ = get_db().session.query(TableScheduledTransaction).all()
    # if transaction is None:
    #     # TODO: Not found error response
    #     return make_response('', 404)

    return make_response('', 200)
