#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from scoring import get_interests, get_score
import re

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

email_pattern = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
phone_pattern = re.compile(
    r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$")


def error(err_code, msg=None):
    if msg is None:
        msg = ERRORS.get(err_code, "Unknown error")
    return (msg, err_code)


class Field(object):
    def __init__(self, required=False, nullable=False):
        self.value = None
        self.required = required
        self.nullable = nullable

    def __get__(self, obj, type=None):
        return self.value

    def __set__(self, obj, value):
        if not self.nullable and not value:
            raise ValueError("Can't be empty")

        self.value = value


class CharField(Field):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if not isinstance(value, str):
            raise TypeError('CharField value must be str type')

        super(CharField, self).__set__(obj, value)


class ArgumentsField(Field):
    def __set__(self, obj, value):
        if not isinstance(value, dict):
            raise TypeError('ArgumentsField value must be dict type')
        super(ArgumentsField, self).__set__(obj, value)


class EmailField(CharField):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if value == '' and not self.nullable:
            raise ValueError("EmailField can't be empty")
        if value == '' or email_pattern.match(value):
            self.value = value
            return
        else:
            raise ValueError('Not email')


class PhoneField(Field):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if value == '' and not self.nullable:
            raise ValueError("PhoneField can't be empty")
        value = str(value)
        if value == '' or phone_pattern.match(value):
            self.value = value
            return
        else:
            raise ValueError('Not phone number')


class DateField(Field):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if not self.nullable and not value:
            raise ValueError("Date can't be empty")

        if not value:
            self.value = None
            return

        self.value = datetime.strptime(value, '%d.%m.%Y')


class BirthDayField(Field):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if not self.nullable and value == '':
            raise ValueError("Date can't be empty")
        elif value == '':
            self.value = None
            return

        date = datetime.strptime(value, '%d.%m.%Y')
        now = datetime.now()

        full_years = now.year - date.year
        if now - datetime(now.year, date.month, date.day) > timedelta(0):
            full_years -= 1

        if full_years >= 70:
            raise ValueError("Sorry, but too old")

        self.value = date.date()


class GenderField(Field):
    def __set__(self, obj, value):
        if value is None:
            self.value = value
            return

        if value not in GENDERS:
            raise TypeError("Unknown gender type")
        if not self.nullable and value is UNKNOWN:
            raise ValueError("GenderField can't be UNKNOWN")

        self.value = value


class ClientIDsField(Field):
    def __set__(self, obj, value):
        if not isinstance(value, list):
            raise TypeError('ClientIDsField value must be list type')
        for i in value:
            if not isinstance(i, int):
                raise TypeError('Items in ClientIDsField must be integer type')

        super(ClientIDsField, self).__set__(obj, value)


class MetaRequest(type):
    def __new__(mcs, name, bases, attrs):
        request_fields = []
        for key, value in attrs.items():
            if isinstance(value, Field):
                request_fields.append((key, value))
        attrs['request_fields'] = request_fields

        return super(MetaRequest, mcs).__new__(mcs, name, bases, attrs)


class Request(object):
    __metaclass__ = MetaRequest

    def __init__(self, request):
        for field_name, obj in self.request_fields:
            value = request.get(field_name, None)
            if value is None and obj.required:
                raise ValueError("'%s' field is required" % field_name)
            else:
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
            try:
                setattr(self, field_name, value)
            except:
                raise ValueError("'%s' field is not valid" % field_name)

    def get_none_empty_fields(self):
        fields = {}
        for field_name, _ in self.request_fields:
            value = getattr(self, field_name)
            if value is not None:
                fields[field_name] = value

        return fields

    def field_set_valid(self):
        return True


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def get_response(self, ctx, store, method, is_admin=False):
        resp = {}
        for cid in self.client_ids:
            resp[cid] = method(store, cid)

        ctx['nclients'] = len(self.client_ids)
        return resp


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def get_response(self, ctx, store, method, is_admin=False):
        resp = {}
        fields = self.get_none_empty_fields()
        if is_admin:
            resp['score'] = 42
        else:
            resp['score'] = method(store, **fields)
        ctx['has'] = fields.keys()
        return resp

    def field_set_valid(self):
        valid_pairs = (('phone', 'email'), ('first_name',
                                            'last_name'), ('gender', 'birthday'))
        fields = self.get_none_empty_fields().keys()
        for field_1, field_2 in valid_pairs:
            if field_1 in fields and field_2 in fields:
                return True
        return False


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.now().strftime(
            "%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(
            request.account + request.login + SALT).hexdigest()

    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    try:
        validated_request = MethodRequest(request['body'])
    except Exception, e:
        logging.exception("can't validate request")
        return error(INVALID_REQUEST, str(e))

    if not check_auth(validated_request):
        return error(FORBIDDEN)

    METHODS = {
        'online_score': (OnlineScoreRequest, get_score),
        'clients_interests': (ClientsInterestsRequest, get_interests)
    }

    if validated_request.method not in METHODS:
        return error(INVALID_REQUEST, 'Method not implemented')

    arg_validator, method = METHODS[validated_request.method]

    try:
        validated_arguments = arg_validator(validated_request.arguments)
    except Exception, e:
        logging.exception("can't validate request")
        return error(INVALID_REQUEST, str(e))

    if validated_arguments.field_set_valid():
        response = validated_arguments.get_response(
            ctx, store, method, validated_request.is_admin)
        code = OK
    else:
        return error(INVALID_REQUEST, "Not enoth data in request")

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler,
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" %
                         (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(
                code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
