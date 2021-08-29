#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from routes.main import create_app
from grackle.settings import ProductionConfig


if __name__ == '__main__':
    app = create_app(config_class=ProductionConfig)
    app.run(host='127.0.0.1', port=ProductionConfig.PORT, debug=ProductionConfig.DEBUG)
