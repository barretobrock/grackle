#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from routes.app import create_app
from grackle.settings import auto_config


if __name__ == '__main__':
    os.environ['GRACKLE_ENV'] = 'PRODUCTION'
    app = create_app(config_class=auto_config)
    app.run(host='0.0.0.0', port=auto_config.PORT, debug=auto_config.DEBUG)
