from flask import (
    Flask,
    render_template,
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    current_app
)
from grackle.etl import ETL
from grackle.settings import auto_config

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def index():
    return render_template('index.html')


@main.route('/upload')
def upload_page():
    return render_template('upload.html')


@main.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files.get('file')
        if f.filename != '':
            f.save(auto_config.GNUCASH_PATH)
            flash('Uploaded file successfully saved.', 'alert alert-success')
            return redirect(url_for('main.refresh_book'))
        flash('Cancelled upload process - Make sure you have a file selected.', 'alert alert-warning')
        return redirect(url_for('main.upload_page'))
    return render_template('index.html')


@main.route('/refresh')
def refresh_book():
    # TODO Optionally tie this in with the upload endpoint and have separate endpoints to
    #  refresh specific parts if not all are needed (transactions, invoices, etc)
    etl = ETL()
    try:
        etl.gnc.refresh_book()
        etl.gnc.etl_accounts_transactions_budget()
        etl.gnc.etl_invoices()
        flash('Financial data refresh successful.', 'alert alert-success')
    except Exception as e:
        flash(f'Error! - {e}', 'alert alert-danger')
    return redirect(url_for('main.index'))
