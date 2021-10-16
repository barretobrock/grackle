"""Configuration setup"""
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from grackle._version import get_versions
from grackle.model import Base


class BaseConfig(object):
    """Configuration items common across all config types"""
    _v = get_versions()
    VERSION = _v['version']
    UPDATE_DATE = _v['date']
    PORT = 5006
    # Stuff for frontend
    STATIC_DIR_PATH = '../build'
    TEMPLATE_DIR_PATH = '../templates'
    # backend
    DATA_DIR = os.path.join(os.path.expanduser('~'), 'data')
    BACKUP_DIR = os.path.join(DATA_DIR, 'gnucash_backups')
    KEY_DIR = os.path.join(os.path.expanduser('~'), 'keys')
    GNUCASH_PATH = os.path.join(DATA_DIR, 'gnucash_sqlite.gnucash')
    GNU_LAST_UPDATE = datetime.fromtimestamp(os.path.getmtime(GNUCASH_PATH)) if os.path.exists(GNUCASH_PATH) else None

    DB_PATH = os.path.join(DATA_DIR, 'personalfin.db')
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'DB_PATH at {DB_PATH} invalid...')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    engine = create_engine(SQLALCHEMY_DATABASE_URI, isolation_level='SERIALIZABLE')
    Base.metadata.bind = engine
    SESSION = sessionmaker(bind=engine)
    SECRET_KEY_PATH = os.path.join(KEY_DIR, 'grackle-secret')
    if not os.path.exists(SECRET_KEY_PATH):
        raise FileNotFoundError(f'grackle-secret at {SECRET_KEY_PATH} not found...')
    with open(SECRET_KEY_PATH) as f:
        SECRET_KEY = f.read().strip()


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
