#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from routes.main import create_app
from grackle.settings import DevelopmentConfig


if __name__ == '__main__':
    app = create_app(config_class=DevelopmentConfig)
    app.run(host='127.0.0.1', port=DevelopmentConfig.PORT, debug=DevelopmentConfig.DEBUG)
