from flask import Flask
from pukr import get_logger, InterceptHandler
from grackle.config import ProductionConfig
from grackle.flask_base import db
from grackle.routes.account import account
from grackle.routes.invoices import invc
from grackle.routes.main import main
from grackle.routes.chart import chart
from grackle.routes.finances import fin
from grackle.routes.transaction import transaction
from grackle.routes.scheduled_transaction import sched_transaction

ROUTES = [
    account,
    chart,
    fin,
    invc,
    main,
    sched_transaction,
    transaction
]


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app
    config_class = kwargs.pop('config_class', ProductionConfig)
    app = Flask(__name__, static_folder=config_class.STATIC_DIR_PATH, static_url_path='/',
                template_folder=config_class.TEMPLATE_DIR_PATH)
    app.config.from_object(config_class)

    # Initialize things that supports app
    db.init_app(app)

    logger = get_logger('grackle', app.config.get('LOG_DIR'), show_backtrace=True, base_level='DEBUG')
    logger.debug('Logger started. Binding to app handler.')
    app.logger.addHandler(InterceptHandler(logger=logger))
    app.extensions.setdefault('loguru', logger)

    # Register routes
    for rt in ROUTES:
        app.register_blueprint(rt)

    app.config['db'] = db

    return app
