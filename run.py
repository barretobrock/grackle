#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pukr import get_logger

from grackle.config import ProductionConfig
from grackle.routes import create_app

if __name__ == '__main__':
    # Instantiate log here, as the hosts API is requested to communicate with influx
    log = get_logger(log_name='grackle-api', log_dir_path=ProductionConfig.LOG_DIR.joinpath('logs/grackle'))
    app = create_app(config_class=ProductionConfig)
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)
