"""Configuration setup"""
from datetime import datetime
import os
import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from grackle import (
    __update_date__,
    __version__,
)
from grackle.model import Base


def get_local_secret_key(path: pathlib.Path) -> str:
    """Grabs a locally-stored secret"""
    if not path.exists():
        raise FileNotFoundError(f'The luks secret key was not found at path: {path}')
    with path.open() as f:
        return f.read().strip()


class BaseConfig(object):
    """Configuration items common across all config types"""
    DEBUG = False
    TESTING = False
    VERSION = __version__
    UPDATE_DATE = __update_date__
    path = pathlib.Path()
    PORT = 5005
    # Stuff for frontend
    STATIC_DIR_PATH = '../static'
    TEMPLATE_DIR_PATH = '../templates'

    HOME = path.home()
    KEY_DIR = HOME.joinpath('keys')
    DATA_DIR = HOME.joinpath('data/grackle')
    LOG_DIR = HOME.joinpath('logs')

    BACKUP_DIR = DATA_DIR.joinpath('gnucash_backups')
    BACKUP_DIR.touch(exist_ok=True)
    GNUCASH_PATH = DATA_DIR.joinpath('gnucash_ro.gnucash')
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
    SECRET_KEY = get_local_secret_key(SECRET_KEY_PATH)


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    DEBUG = True
    DB_SERVER = 'localhost'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    DEBUG = False
    DB_SERVER = '0.0.0.0'
    LOG_LEVEL = 'DEBUG'


class TestConfig(BaseConfig):
    """Configuration for test environment"""
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_SERVER = 'localhost'
    LOG_LEVEL = 'DEBUG'
