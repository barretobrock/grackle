from flask import (
    Flask,
    render_template,
    Blueprint,
    request,
    flash,
    redirect,
    url_for
)
from easylogger import Log
from grackle.settings import auto_config

logg = Log('grackle-app', log_to_file=True, log_level_str='DEBUG')
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
        f.save(auto_config.GNUCASH_PATH)
        flash('Uploaded file successfully saved.', 'success')
        return redirect(url_for('main.index'))
    return render_template('index.html')
