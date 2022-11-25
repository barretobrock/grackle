from flask import (
    Blueprint,
    current_app,
    render_template,
)

from grackle.core.queries import GrackleQueries
from grackle.model import AccountType
from grackle.routes.helpers import (
    log_after,
    log_before,
)

invc = Blueprint('invoice', __name__, url_prefix='/invoice')


@invc.before_request
def log_before_():
    log_before()


@invc.after_request
def log_after_(response):
    return log_after(response)


@invc.route('/all')
def get_invoices():
    """For rendering a list of invoices, marking which ones might be due"""
    # Query all invoices
    cur_balances = GrackleQueries.get_account_balance(acct_name=['Current', 'Rent'],
                                                      acct_type=AccountType.RECEIVABLE)
    return render_template(
        'invoices.html',
        update_date=current_app.config.get('GNUCASH_LAST_UPDATE').strftime('%F'),
        acct_balances=cur_balances,
        tbl_id_name='invoices-tbl',
        order_list=[0, "asc"],
        invoices=GrackleQueries.get_invoices()
    )


@invc.route('/<string:invoice_no>')
def get_invoice(invoice_no: str):
    """For rendering an individual invoice"""
    invoice, entries = GrackleQueries.get_invoice(invoice_no=invoice_no)
    return render_template(
        'invoice.html',
        tbl_id_name='invoice-tbl',
        order_list=[0, "asc"],
        headers=[
            'Date',
            'Item',
            'Quantity',
            'Price',
            'Discount',
            'Total'
        ],
        invoice=invoice,
        entries=entries
    )
