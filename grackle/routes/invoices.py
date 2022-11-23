from flask import (
    Blueprint,
    current_app,
    render_template,
)
from sqlalchemy.sql import and_

from grackle.model import (
    AccountType,
    TableAccount,
    TableInvoice,
)

invc = Blueprint('invoice', __name__, url_prefix='/invoice')


def get_db():
    return current_app.config['db']


@invc.route('/all')
def get_invoices():
    """For rendering a list of invoices, marking which ones might be due"""
    # Query all invoices
    cur_balances = get_db().session.query(TableAccount.name, TableAccount.current_balance).filter(and_(
        TableAccount.name.in_(['MPO-Current', 'MPO-Rent']),
        TableAccount.account_type == AccountType.receivable
    )).all()
    invoices = get_db().session.query(TableInvoice).order_by(TableInvoice.invoice_no.desc()).limit(10).all()
    return render_template(
        'invoices.html',
        update_date=current_app.config.get('GNUCASH_LAST_UPDATE').strftime('%F'),
        acct_balances=cur_balances,
        tbl_id_name='invoices-tbl',
        order_list=[0, "asc"],
        invoices=invoices
    )


@invc.route('/<string:invoice_no>')
def get_invoice(invoice_no: str):
    """For rendering an individual invoice"""
    invoice: TableInvoice
    invoice = get_db().session.query(TableInvoice).filter(TableInvoice.invoice_no == invoice_no).one_or_none()
    entries_list = [{
        'transaction_date': f'{x.transaction_date:%F}',
        'desc': x.description,
        'qty': f'{x.quantity:.2f}',
        'unit_price': f'{x.unit_price:.2f}',
        'discount': f'{x.discount:.2f}',
        'total': f'{x.total:.2f}',
    } for x in invoice.entries if x.quantity != 0]
    return render_template(
        'invoice.html',
        tbl_id_name='invoice-tbl',
        order_list=[0, "asc"],
        header_maps={
            'Date': {'col': 'transaction_date'},
            'Item': {'col': 'desc'},
            'Quantity': {'col': 'qty'},
            'Price': {'col': 'unit_price'},
            'Discount': {'col': 'discount'},
            'Total': {'col': 'total'}
        },
        entries_list=entries_list,
        invoice=invoice
    )
