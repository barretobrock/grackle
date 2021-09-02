from flask import render_template, Blueprint, current_app, flash, redirect, url_for


fin = Blueprint('finances', __name__)


@fin.route('/refresh')
def refresh_book():
    current_app.config['GNC'].refresh_book()
    flash('Financial data refresh successful.', 'success')
    return redirect(url_for('main.index'))


@fin.route('/invoices')
def get_invoices():
    """For rendering a list of invoices, marking which ones might be due"""
    # TODO: invoice collection and display logic here
    pass


@fin.route('/invoice/<int:invoice_no>')
def get_invoice(invoice_no: int):
    """For rendering an individual invoice"""
    # TODO: invoice collection and display logic here
    pass
