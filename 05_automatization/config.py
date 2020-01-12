import logging

'''
Настройка логирования
'''
LOG_FILE = None
LOG_FMT = "[%(asctime)s] %(levelname).1s %(message)s"
LOG_DATE_FMT = "%Y.%m.%d %H:%M:%S"
LOG_LEVEL = logging.ERROR

'''
Параметры HTTPсервера
'''
ADDRESS = 'localhost'
PORT = 8000
DOCUMENT_ROOT = '.'
WORKERS = 1
MAX_WORKERS = 100
BACKLOG_CONNECTIONS = 100

INDEX_FILE = 'index.html'

CONNECTION_TIMEOUT = 1
