from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from grackle.core.connect import (
    connect_to_smb,
    get_files,
)
from grackle.core.gnucash import GNUCashProcessor
from grackle.forms import ConfirmRefreshForm
from grackle.routes.helpers import (
    get_app_logger,
    log_after,
    log_before,
)

main = Blueprint('main', __name__)


@main.before_request
def log_before_():
    log_before()


@main.after_request
def log_after_(response):
    return log_after(response)


@main.errorhandler(500)
@main.errorhandler(404)
@main.errorhandler(403)
def handle_err(err):
    _log = get_app_logger()
    _log.error(err)
    if err.code == 404:
        _log.error(f'Path requested: {request.path}')
    return render_template(f'errors/{err.code}.html'), err.code


@main.route('/')
@main.route('/home')
def index():
    return render_template('index.html')


@main.route('/refresh', methods=['GET', 'POST'])
def refresh_book():
    # TODO Optionally tie this in with the upload endpoint and have separate endpoints to
    #  refresh specific parts if not all are needed (transactions, invoices, etc)
    _log = get_app_logger()
    form = ConfirmRefreshForm()
    if request.method == 'POST':
        if not form.confirm.data:
            flash('Bypassing refresh...', 'alert alert-info')
            return redirect(url_for('main.index'))
        conn, svc, path = connect_to_smb()
        # Copy file
        get_files(conn, svc_name=svc, source_path=path, dest_path=str(current_app.config.get('GNUCASH_PATH')))
        gnc = GNUCashProcessor(_log)
        try:
            gnc.entire_etl_process()
            flash('Financial data refresh successful.', 'alert alert-success')
        except Exception as e:
            flash(f'Error! - {e}', 'alert alert-danger')
        return redirect(url_for('main.index'))
    else:

        return render_template('confirm.html', form=form, template='form-template')
