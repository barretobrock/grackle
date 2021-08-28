from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from easylogger import Log
from .settings import auto_config


logg = Log('grackle-app', log_to_file=True)

logg.debug('Starting up app...')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = auto_config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


