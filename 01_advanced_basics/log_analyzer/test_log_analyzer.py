import unittest
from log_analyzer import find_log, report_exist, parse_log, get_statistic, report_render
import os
from datetime import datetime
import json


class TestLogAnalizer(unittest.TestCase):
    path = './test/'

    def setUp(self):
        os.makedirs(self.path, exist_ok=True)

    def tearDown(self):
        os.removedirs(self.path)
        
    def test_find_log(self):
        
        files = [
            'nginx-access-ui.log-20170630.gz',
            'nginx-access-ui.log-20170629.gz',
            'nginx-access-ui.log-20170730',
            'nginx-access-ui.log-20170730.gz2',
            'nginx-access-ui.log-2017073'
        ]

        open(self.path + files[0], 'a').close()
        open(self.path + files[1], 'a').close()
        self.assertEqual(find_log(self.path),
                         (files[0], datetime(2017, 6, 30)))
        open(self.path + files[2], 'a').close()
        self.assertEqual(find_log(self.path),
                         (files[2], datetime(2017, 7, 30)))
        open(self.path + files[3], 'a').close()
        self.assertEqual(find_log(self.path),
                         (files[2], datetime(2017, 7, 30)))
        open(self.path + files[4], 'a').close()
        self.assertEqual(find_log(self.path),
                         (files[2], datetime(2017, 7, 30)))

        for f in files:
            os.remove(self.path+f)

    def test_report_exist(self):
        os.makedirs(self.path, exist_ok=True)
        rep_name = self.path + 'report-2017.06.30.html'
        open(rep_name, 'a').close()
        self.assertTrue(report_exist(rep_name))
        self.assertFalse(report_exist(self.path + 'report-2017.06.31.html'))
        os.remove(rep_name)

    def test_parse_log(self):
        records = [
            '0.0.0.0 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/test" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 1.0',
            '0.0.0.0 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/test" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 1.0',
            '0.0.0.0 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/test" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 1.0',
            '0.0.0.0 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/test" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 1.0'

        ]
        urls = {
            '/api/test': {
                'count': 4,
                'time_sum': 4.0,
                'times': [1.0, 1.0, 1.0, 1.0],
                'time_max': 1.0,
            }
        }

        sum_req_time = 4.0
        req_count = 4
        error_count = 0
        self.assertEqual(parse_log(records),
                         (urls, sum_req_time, req_count, error_count))

    test_stat = {
        '/api/test': {
            'count': 4,
            'time_sum': 4.0,
            'time_max': 1.0,
            'count_perc': 100.0,
            'time_perc': 100.0,
            'time_avg': 1.0,
            'time_med':  1.0,
        }
    }

    def test_get_statistic(self):
        urls = {
            '/api/test': {
                'count': 4,
                'time_sum': 4.0,
                'times': [1.0, 1.0, 1.0, 1.0],
                'time_max': 1.0,
            }
        }
        sum_req_time = 4.0
        req_count = 4

        get_statistic(urls, sum_req_time, req_count)

        self.assertEqual(urls, self.test_stat)

    def test_report_render(self):
        template = '$table_json'
        test_report = json.dumps([{
            'count': 4,
            'time_sum': 4.0,
            'time_max': 1.0,
            'count_perc': 100.0,
            'time_perc': 100.0,
            'time_avg': 1.0,
            'time_med':  1.0,
            'url': '/api/test'
        }])
        with open(self.path+'report_template', mode='wt', encoding='utf-8') as t:
            t.write(template)

        report_render(self.test_stat, self.path+'test_report',
                      self.path+'report_template')

        with open(self.path+'test_report', mode='rt', encoding='utf-8') as r:
            report = r.read()
        self.assertEqual(report, test_report)

        os.remove(self.path+'test_report')
        os.remove(self.path+'report_template')


if __name__ == "__main__":
    unittest.main()
