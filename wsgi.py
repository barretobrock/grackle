from pukr import get_logger

from grackle.routes.app import create_app
from grackle.config import ProductionConfig

app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    log = get_logger(log_name='grackle-api', log_dir_path=ProductionConfig.LOG_DIR.joinpath('logs/grackle'))
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)
