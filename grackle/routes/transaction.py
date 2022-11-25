from flask import (
    Blueprint,
    jsonify,
)

from grackle.model import TableTransaction
from grackle.routes.helpers import (
    get_db,
    log_after,
    log_before,
)

transaction = Blueprint('transaction', __name__, url_prefix='/transaction')


@transaction.before_request
def log_before_():
    log_before()


@transaction.after_request
def log_after_(response):
    return log_after(response)


@transaction.route('/all', methods=['GET'])
def get_transactions():
    transactions = get_db().session.query(TableTransaction).group_by(TableTransaction.desc).all()
    names = [
        {'id': x.transaction_id, 'desc': x.desc} for x in transactions
    ]
    return jsonify({'transactions': names})
