from flask import (
    Blueprint,
    current_app,
    jsonify,
)

from grackle.model import TableTransaction

transaction = Blueprint('transaction', __name__, url_prefix='/transaction')


def get_db():
    return current_app.config['db']


@transaction.route('/all', methods=['GET'])
def get_transactions():
    transactions = get_db().session.query(TableTransaction).group_by(TableTransaction.desc).all()
    names = [
        {'id': x.transaction_id, 'desc': x.desc} for x in transactions
    ]
    return jsonify({'transactions': names})
