import time

from flask import (
    current_app,
    g,
    request,
)
from pukr import PukrLog


def get_db():
    return current_app.config['db']


def get_app_logger() -> PukrLog:
    return current_app.extensions['loguru']


# Apply some timing functions
def log_before():
    g.start_time = time.perf_counter()


def log_after(response):
    total_time = time.perf_counter() - g.start_time
    time_ms = int(total_time * 1000)
    get_app_logger().info(f'Timing: {time_ms}ms [{request.method}] {request.path}')
    return response
