"""Configuration setup"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from grackle._version import get_versions
from grackle.model import Base


class BaseConfig(object):
    """Configuration items common across all config types"""
    _v = get_versions()
    VERSION = _v['version']
    UPDATE_DATE = _v['date']
    STATIC_DIR_PATH = '../static'
    TEMPLATE_DIR_PATH = '../templates'
    DATA_DIR = os.path.join(os.path.expanduser('~'), 'data')
    GNUCASH_PATH = os.path.join(DATA_DIR, 'gnucash_sqlite.gnucash')
    DB_PATH = os.path.join(DATA_DIR, 'personalfin.db')
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'DB_PATH at {DB_PATH} invalid...')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    engine = create_engine(SQLALCHEMY_DATABASE_URI, isolation_level='SERIALIZABLE')
    Base.metadata.bind = engine
    SESSION = sessionmaker(bind=engine)
    PORT = 5006


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    DEBUG = False
