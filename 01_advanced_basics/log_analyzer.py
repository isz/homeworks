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
    if len(sys.argv) >= 3:
        for i in range(len(sys.argv)-1):
            if sys.argv[i] == '--config':
                return sys.argv[i+1]

    return ''


def parse_config_file(config_file):
    try:
        with open(DEFAULT_CONFIG_PATH + config_file, mode='rt', encoding='utf-8') as f:
            conf = f.read()
    except FileNotFoundError:
        raise Exception(f'config file "{config_file}" not found')

    try:
        conf = json.loads(conf)
    except:
        raise Exception(f'config "{config_file}" not in JSON format')

    if type(conf) is not dict:
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

        try:
            config.update(parse_config_file(config_file))
        except Exception as e:
            raise e

    return config


def parse_record(rec):
    fields = rec.split()
    url = ''
    req_time = 0.0

    try:
        url = fields[URL_IDX].strip('"')
        req_time = fields[REQ_TIME_IDX]
    except IndexError:
        raise Exception("can't parse log record")

    try:
        req_time = float(req_time)
    except ValueError:
        raise Exception("cant't read request time")

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
    urls = {}
    sum_req_time = 0.0
    req_count = 0
    error_count = 0

    for line in file_reader:
        try:
            url, req_time = parse_record(line)
        except:
            error_count += 1
            continue

        req_count += 1
        sum_req_time += req_time
        url_stat = urls.get(url, {
            'count': 0,
            'time_sum': 0.0,
            'times': [],
            'time_max': 0.0,
        })
        url_stat['count'] += 1
        url_stat['time_sum'] += req_time
        url_stat['times'].append(req_time)
        url_stat['time_max'] = req_time if req_time > url_stat['time_max'] else url_stat['time_max']
        urls[url] = url_stat

    return (urls, sum_req_time, req_count, error_count)


def get_statistic(urls, sum_time, req_count):
    for stat in urls.values():
        stat['count_perc'] = stat['count']*100/req_count
        stat['time_perc'] = stat['time_sum']*100/sum_time
        stat['time_avg'] = stat['time_sum']/stat['count']
        stat['time_med'] = median(stat['times'])
        del stat['times']


def find_log(path):
    last_name = ''
    last_date = None
    try:
        _, _, file_list = next(os.walk(path))
    except StopIteration:
        raise Exception(f'log dir "{path}" does not exist')
    else:
        for file_name in file_list:
            if re.match(r'nginx-access-ui.log-\d{8}(.gz){,1}$', file_name):
                log_date = datetime.strptime(
                    re.findall(r'\d{8}', file_name)[0], '%Y%m%d')
                if last_date is None or log_date > last_date:
                    last_date = log_date
                    last_name = file_name
    return (last_name, last_date)


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
    try:
        with open(rep_templ, mode='rt', encoding='utf-8') as f:
            templ_str = f.read()
    except FileNotFoundError:
        logging.error('report template "%s" does not exist', rep_templ)
        return

    templ = Template(templ_str)
    rep_json = json.dumps(get_stats_list(urls_stat))
    report = templ.safe_substitute(table_json=rep_json)

    try:
        os.makedirs(os.path.dirname(rep_name), exist_ok=True)
    except Exception as e:
        logging.error("can't create report directory, exception: %s", str(e))

    try:
        with open(rep_name, mode='wt', encoding='utf-8',) as f:
            f.write(report)
    except Exception as e:
        logging.error('error while writing report, exception: %s', str(e))


def main():
    logging.basicConfig(filename=log_config['FILE'], format=log_config['FORMAT'],
                        level=log_config['LEVEL'], datefmt='%Y.%m.%d %H:%M:%S')

    try:
        try:
            config = get_config()
        except Exception as e:
            logging.error(str(e))
            sys.exit("can't read config file")

        try:
            log_name, log_date = find_log(config['LOG_DIR'])
        except Exception as e:
            logging.error(str(e))
            return

        if not log_name:
            logging.info('log file not found')
            return

        logging.info('last log file: %s', log_name)

        rep_name = config['REPORT_DIR'] + '/' + \
            log_date.strftime('report-%Y.%m.%d.html')
        if report_exist(rep_name):
            logging.info('report for "%s" exist', log_name)
            return

        reader = file_reader(config['LOG_DIR']+'/'+log_name)
        urls_stat, sum_time, req_count, error_count = parse_log(reader)

        if error_count/req_count > config['ERROR_RATE']:
            logging.error('error rate exceeded %s value', config['ERROR_RATE'])
            return

        urls_stat = dict(sorted(urls_stat.items(), key=lambda t: t[1]['time_sum'], reverse=True)[
            :config['REPORT_SIZE']])

        get_statistic(urls_stat, sum_time, req_count)
        report_render(urls_stat, rep_name, config['REPORT_TEMPLATE'])

    except Exception as e:
        logging.exception('unhandled exception')


if __name__ == "__main__":
    main()
