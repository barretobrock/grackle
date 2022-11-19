"""Configuration setup"""
import os
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from grackle import __version__, __update_date__
from grackle.model import Base


class BaseConfig(object):
    """Configuration items common across all config types"""
    VERSION = __version__
    UPDATE_DATE = __update_date__
    PORT = 5006
    # Stuff for frontend
    STATIC_DIR_PATH = '../build'
    TEMPLATE_DIR_PATH = '../templates'

    HOME = Path().home()
    KEY_DIR = HOME.joinpath('keys')
    DATA_DIR = HOME.joinpath('data')
    LOG_DIR = HOME.joinpath('logs')

    BACKUP_DIR = DATA_DIR.joinpath('gnucash_backups')
    BACKUP_DIR.touch(exist_ok=True)
    GNUCASH_PATH = DATA_DIR.joinpath('gnucash_sqlite.gnucash')
    GNUCASH_LAST_UPDATE = datetime.fromtimestamp(os.path.getmtime(GNUCASH_PATH))

    # backend
    DB_PATH = DATA_DIR.joinpath('grackle.sqlite')
    if not DB_PATH.exists():
        DB_PATH.touch(exist_ok=True)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    engine = create_engine(SQLALCHEMY_DATABASE_URI, isolation_level='SERIALIZABLE')
    Base.metadata.bind = engine
    SESSION = sessionmaker(bind=engine)
    SECRET_KEY_PATH = KEY_DIR.joinpath('grackle-secret')
    if not SECRET_KEY_PATH.exists():
        raise FileNotFoundError(f'grackle-secret at {SECRET_KEY_PATH} not found...')
    with SECRET_KEY_PATH.open() as f:
        SECRET_KEY = f.read().strip()


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
