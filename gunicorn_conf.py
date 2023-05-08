import json
import multiprocessing
import os

workers_per_core_str = os.getenv('WORKERS_PER_CORE', '2')
web_concurrency_str = os.getenv('WEB_CONCURRENCY', None)
host = os.getenv('HOST', '0.0.0.0')
port = os.getenv('PORT', '8000')
bind_env = os.getenv('BIND', None)
if bind_env:
    use_bind = bind_env
else:
    use_bind = f'{host}:{port}'

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)

# Gunicorn config variables
workers = 1  # web_concurrency
worker_class = 'uvicorn.workers.UvicornWorker'
bind = use_bind
keepalive = 120

# Logging
accesslog = os.getenv('ACCESS_LOG_FILE', '-')
errorlog = os.getenv('LOG_FILE', '-')
capture_output = True
loglevel = os.getenv('LOG_LEVEL', 'info')

# For debugging and testing
log_data = {
    'loglevel': loglevel.lower(),
    'workers': workers,
    'bind': bind,
    # Additional, non-gunicorn variables
    'workers_per_core': workers_per_core,
    'host': host,
    'port': port,
}
print(json.dumps(log_data))

logconfig_dict = {
    'loggers': {
        'gunicorn.error': {
            'propagate': False,
        },
    },
}
