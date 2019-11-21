#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from statistics import median
import os
import re
from datetime import datetime
from string import Template
import json
import logging
import sys
import argparse
from collections import namedtuple, defaultdict

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


DEFAULT_CONFIG_PATH = './'

log_config = {
    "FILE": "./analyzer.log",
    "FORMAT": "[%(asctime)s] %(levelname).1s %(message)s",
    "LEVEL": logging.INFO
}

URL_IDX = 6
REQ_TIME_IDX = -1


def get_config_file_from_com_line():
    parser = argparse.ArgumentParser(description='Log analyzer')
    parser.add_argument('-c', '--config', type=str,
                        help='config file in JSON format')
    args = parser.parse_args()

    return args.config


def parse_config_file(config_file):
    filename = os.path.join(DEFAULT_CONFIG_PATH, config_file)

    with open(filename, mode='rt', encoding='utf-8') as f:
        conf = f.read()
    conf = json.loads(conf)

    if isinstance(conf, dict) is not True:
        raise Exception(f'can\'t use "{config_file}" config file')

    return conf


def get_config():
    config = {
        "REPORT_SIZE": 10,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
        "REPORT_TEMPLATE": "./report.html",
        "ERROR_RATE": 0.25,
    }
    config_file = get_config_file_from_com_line()
    if config_file:
        logging.info('using config file "%s"', config_file)

        config.update(parse_config_file(config_file))

    return config


def parse_record(rec):
    fields = rec.split()
    url = ''
    req_time = 0.0

    try:
        url = fields[URL_IDX].strip('"')
        req_time = fields[REQ_TIME_IDX]
        req_time = float(req_time)
    except:
        return None

    return (url, req_time)


def file_reader(file_name):
    ext = file_name.split('.')[-1]
    open_func = gzip.open if ext == 'gz' else open

    try:
        with open_func(file_name, mode='rt', encoding='utf-8') as f:
            for line in f:
                yield line
    except Exception as e:
        logging.error(
            'error while reading file "%s", exception: %s', file_name, str(e))


def parse_log(file_reader):
    urls = defaultdict(lambda: {
        'count': 0,
        'time_sum': 0.0,
        'times': [],
        'time_max': 0.0,
    })

    sum_req_time = 0.0
    req_count = 0
    error_count = 0

    for line in file_reader:
        req_count += 1

        req = parse_record(line)
        if req is None:
            error_count += 1
            continue

        url, req_time = req

        sum_req_time += req_time

        url_stat = urls[url]
        url_stat['count'] += 1
        url_stat['time_sum'] += req_time
        url_stat['times'].append(req_time)
        url_stat['time_max'] = req_time if req_time > url_stat['time_max'] else url_stat['time_max']
        urls[url] = url_stat

    return (dict(urls), sum_req_time, req_count, error_count)


def get_statistic(urls, sum_time, req_count):
    for stat in urls.values():
        stat['count_perc'] = stat['count']*100/req_count
        stat['time_perc'] = stat['time_sum']*100/sum_time
        stat['time_avg'] = stat['time_sum']/stat['count']
        stat['time_med'] = median(stat['times'])
        del stat['times']
    return urls


def find_log(path):
    Log = namedtuple('Log', ['name', 'date'])

    last_name = ''
    last_date = None

    try:
        file_list = os.listdir(path)
    except FileNotFoundError:
        logging.error(f'directory {path} not found')
    else:
        for file_name in file_list:
            matches = re.findall(
                r'^nginx-access-ui.log-(\d{8})(.gz)?$', file_name)
            if matches:
                try:
                    log_date = datetime.strptime(matches[0][0], '%Y%m%d')
                except ValueError:
                    continue
                if last_date is None or log_date > last_date:
                    last_date = log_date
                    last_name = file_name

    return Log(last_name, last_date)


def report_exist(rep_name):
    return os.path.exists(rep_name) and os.path.isfile(rep_name)


def get_stats_list(stat_dict):
    stat_list = []
    for key in stat_dict:
        val = stat_dict[key]
        val['url'] = key
        stat_list.append(val)

    return stat_list


def report_render(urls_stat, rep_name, rep_templ):

    with open(rep_templ, mode='rt', encoding='utf-8') as f:
        templ_str = f.read()

    templ = Template(templ_str)
    rep_json = json.dumps(get_stats_list(urls_stat))
    report = templ.safe_substitute(table_json=rep_json)

    os.makedirs(os.path.dirname(rep_name), exist_ok=True)

    with open(rep_name, mode='wt', encoding='utf-8',) as f:
        f.write(report)


def main(config):

    log = find_log(config['LOG_DIR'])

    if not log.name:
        logging.info('log file not found')
        sys.exit('log file not found')

    logging.info('last log file: %s', log.name)

    rep_name = os.path.join(
        config['REPORT_DIR'], log.date.strftime('report-%Y.%m.%d.html'))

    if report_exist(rep_name):
        logging.info('report for "%s" exist', log.name)
        return

    reader = file_reader(os.path.join(config['LOG_DIR'], log.name))

    urls_stat, sum_time, req_count, error_count = parse_log(reader)

    if req_count == 0:
        logging.error('log file is empty')
        print('log file is empty')
        return

    if error_count/req_count > config['ERROR_RATE']:
        logging.error('error rate exceeded %s value', config['ERROR_RATE'])
        return

    urls_stat = dict(sorted(urls_stat.items(), key=lambda t: t[1]['time_sum'], reverse=True)[
        :config['REPORT_SIZE']])

    urls_stat = get_statistic(urls_stat, sum_time, req_count)

    try:
        report_render(urls_stat, rep_name, config['REPORT_TEMPLATE'])
    except:
        logging.exception("can't render report")
        sys.exit("can't render report")
    else:
        logging.info(f"report {rep_name} successfully created")
        print(f"report {rep_name} successfully created")


if __name__ == "__main__":
    logging.basicConfig(filename=log_config['FILE'], format=log_config['FORMAT'],
                        level=log_config['LEVEL'], datefmt='%Y.%m.%d %H:%M:%S')

    try:
        config = get_config()
    except:
        logging.exception("can't read config file")
        sys.exit("can't read config file")

    try:
        main(config)
    except:
        logging.exception('unhandled error')
        sys.exit('unhandled error')
