import os

def current_execution_env():
    return os.environ.get('EXECUTION_ENV', 'LOCAL')