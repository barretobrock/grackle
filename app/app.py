from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from easylogger import Log
from grackle.settings import auto_config
from .api import api
from .main import main
from .chart import cht
from .finances import fin


db = SQLAlchemy()


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app
    config_class = kwargs.pop('config_class', auto_config)
    app = Flask(__name__, static_folder=config_class.STATIC_DIR_PATH, static_url_path='/',
                template_folder=config_class.TEMPLATE_DIR_PATH)
    app.logger = Log('grackle.app', log_level_str=config_class.LOG_LEVEL)
    app.config.from_object(config_class)
    # Initialize things that supports app

    db.init_app(app)
    # Register routes
    for rt in [api, main, cht, fin]:
        app.register_blueprint(rt)

    return app
