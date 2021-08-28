#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['GRACKLE_ENV'] = "PRODUCTION"
from grackle.app import app


@app.route('/')
def index():
    return 'CAH'


if __name__ == '__main__':
    app.run(port=5006)
