from flask import Flask, render_template, Blueprint, request, flash
from flask_sqlalchemy import SQLAlchemy
from easylogger import Log
from grackle.settings import BaseConfig
from .chart import cht


logg = Log('grackle-app', log_to_file=True, log_level_str='DEBUG')
db = SQLAlchemy()
main = Blueprint('main', __name__)


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app
    config_class = kwargs.pop('config_class', BaseConfig)
    app = Flask(__name__, static_folder=config_class.STATIC_DIR_PATH,
                template_folder=config_class.TEMPLATE_DIR_PATH)
    app.config.from_object(config_class)
    # Initialize things that supports app
    db.init_app(app)
    # Register routes
    for rt in [main, cht]:
        app.register_blueprint(rt)

    return app


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
        f.save(BaseConfig.GNUCASH_PATH)
        flash('Uploaded file successfully saved.')

