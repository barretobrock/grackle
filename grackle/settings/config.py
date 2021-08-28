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
    STATIC_DIR_PATH = '../../static'
    TEMPLATE_DIR_PATH = '../../templates'
    DB_PATH = os.path.join(os.path.expanduser('~'), *['data', 'personalfin.db'])
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'DB_PATH at {DB_PATH} invalid...')
    DB_URI = f'sqlite:///{DB_PATH}'
    engine = create_engine(DB_URI, isolation_level='SERIALIZABLE')
    Base.metadata.bind = engine
    SESSION = sessionmaker(bind=engine)
    PORT = 5006


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    DEBUG = False
