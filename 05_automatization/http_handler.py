import logging
import os

import config

SERVER_NAME = 'iZvezdin server'

ROOT = config.DOCUMENT_ROOT

HTTP_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE',
                'CONNECT', 'OPTIONS', 'TRACE', 'PATCH')
ACCEPT_VERSIONS = ('HTTP/1.0', 'HTTP/1.1')
STATUS_MESSAGES = {
    200: 'OK',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error'
}

MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash',
    '.txt': 'text/plain'
}


def set_root(path):
    global ROOT
    path = os.path.abspath(path)
    if os.path.exists(path):
        ROOT = path
    else:
        raise Exception('Path not found')


class HttpRequest():
    def __init__(self, method, url, headers, body=None):
        self._method = method
        self._url = url
        self._body = body


class HttpException(Exception):
    pass


def make_response(version, status, headers, body=b''):

    response = [
        f'{version} {status} {STATUS_MESSAGES[status]}',
        *[': '.join(i) for i in headers.items()],
        '\r\n'
    ]
    response = '\r\n'.join(response)
    return response.encode('utf-8') + body

def get_filename(url):
    file_name = url.split('?')[0]

    file_name = os.path.join(ROOT, file_name)
    file_name = os.path.abspath(file_name)
    
    if os.path.isdir(file_name):
        file_name = os.path.join(file_name, config.INDEX_FILE)
    
    if not file_name.startswith(ROOT):
        file_name = ''

    return file_name

def get_mime_type(file_name):
    _, extension = os.path.splitext(file_name)

    return MIME_TYPES.get(extension.lower(), 'text/plain')

def get_head(url):
    file_name = get_filename(url)
    headers = {}


    if os.path.isfile(file_name):
        headers['Content-Type'] = get_mime_type(os.path.basename(file_name))
        status = 200
    else:
        status = 404
    
    return file_name, status, headers

def get(url):
    body = b''
    file_name, status, headers = get_head(url)
    if status == 200:
        try:
            with open(file_name, 'rb') as f:
                body = f.read()
            headers['Content-Length'] = str(len(body))
        except PermissionError:
            status = 403
        except Exception as e:
            logging.exception(e)
            status = 500

    return (status, headers, body)


def head(url):
    file_name, status, headers = get_head(url)
    body = b''
    if status == 200:
        headers['Content-Length'] = str(os.stat(file_name).st_size)
    return (status, headers, body)


def status_405(url):
    status = 405
    body = b'Method Not Allowed'
    headers = {
        'Content-Type': 'text/plain',
        'Content-Length': str(len(body))
    }

    return (status, headers, body)


METHODS = {
    'GET': get,
    'HEAD': head
}


def handle_http(request):
    url = request['url']
    url = url[1:]

    method = METHODS.get(request['method'], status_405)

    status, headers, body = method(url)
    
    headers['Server'] = SERVER_NAME

    return make_response(request['version'], status, headers, body)


def decode_url(url):
    codes = url.split('%')
    if (len(codes) == 1):
        return url

    url = [codes[0]]
    for code in codes[1:]:
        url.append(bytes.fromhex(code[:2]).decode('utf-8') + code[2:])

    return ''.join(url)


def parse_http_request(raw_request):
    request = raw_request.decode('utf-8')
    if '\r\n' in request:
        request, headers = request.split('\r\n', 1)
        headers = headers.split('\r\n')
    else:
        headers = []

    try:
        method, url, version = request.split()
    except ValueError:
        HttpException("Wrong HTTP request")

    if method not in HTTP_METHODS:
        raise HttpException("Wrong HTTP method")

    if version not in ACCEPT_VERSIONS:
        raise HttpException("Wrong HTTP version")

    try:
        headers = dict(l.split(': ') for l in headers)
        length = headers.get('Content-Length', None)
        if length:
            headers['Content-Length'] = int(length)
    except:
        raise HttpException("Wrong HTTP header")

    try:
        url = decode_url(url)
    except:
        raise HttpException("Wrong URL")

    return {
        'method': method,
        'url': url,
        'version': version,
        'headers': headers
    }
