from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from grackle.settings import auto_config
from .main import main
from .chart import cht
from .finances import fin


db = SQLAlchemy()


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app
    config_class = kwargs.pop('config_class', auto_config)
    app = Flask(__name__, static_folder=config_class.STATIC_DIR_PATH,
                template_folder=config_class.TEMPLATE_DIR_PATH)
    app.config.from_object(config_class)
    # Initialize things that supports app

    db.init_app(app)
    # Register routes
    for rt in [main, cht, fin]:
        app.register_blueprint(rt)

    return app
