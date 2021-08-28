#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from routes.main import create_app
from grackle.settings import DevelopmentC


@app.route('/')
def index():
    return 'CAH'


if __name__ == '__main__':
    app = create_app(config_class=)
