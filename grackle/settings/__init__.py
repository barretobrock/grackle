import os
from .config import DevelopmentConfig, ProductionConfig, BaseConfig

config_space = os.getenv('GRACKLE_ENV', 'DEVELOPMENT')
if config_space == 'DEVELOPMENT':
    auto_config = DevelopmentConfig
elif config_space == 'PRODUCTION':
    auto_config = ProductionConfig
