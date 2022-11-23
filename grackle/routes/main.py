from flask import (
    render_template,
    Blueprint,
    request,
    current_app,
    flash,
    redirect,
    url_for,
)
from grackle.forms import ConfirmRefreshForm
from grackle.core.connect import connect_to_smb, get_files
from grackle.core.gnucash import GNUCashProcessor
from grackle.config import BaseConfig

main = Blueprint('main', __name__)


@main.errorhandler(500)
@main.errorhandler(404)
@main.errorhandler(403)
def handle_err(err):
    current_app.extensions['loguru'].error(err)
    if err.code == 404:
        current_app.extensions['loguru'].error(f'Path requested: {request.path}')
    return render_template(f'errors/{err.code}.html'), err.code


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
            f.save(BaseConfig.GNUCASH_PATH)
            flash('Uploaded file successfully saved.', 'alert alert-success')
            return redirect(url_for('main.refresh_book'))
        flash('Cancelled upload process - Make sure you have a file selected.', 'alert alert-warning')
        return redirect(url_for('main.upload_page'))
    return render_template('index.html')


@main.route('/refresh', methods=['GET', 'POST'])
def refresh_book():
    # TODO Optionally tie this in with the upload endpoint and have separate endpoints to
    #  refresh specific parts if not all are needed (transactions, invoices, etc)
    if request.method == 'POST':
        conn, svc, path = connect_to_smb()
        # Copy file
        get_files(conn, svc_name=svc, source_path=path, dest_path=str(current_app.config.get('GNUCASH_PATH')))
        gnc = GNUCashProcessor(current_app.extensions['loguru'])
        try:
            gnc.entire_etl_process()
            flash('Financial data refresh successful.', 'alert alert-success')
        except Exception as e:
            flash(f'Error! - {e}', 'alert alert-danger')
        return redirect(url_for('main.index'))
    else:
        form = ConfirmRefreshForm()
        return render_template('confirm.html', form=form, template='form-template')

