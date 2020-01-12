Учебный HTTP сервер
-------------------------------------------------------

Асинхронный HTTP сервер, с прменением метода обработки входящих соединений с помощью механизма epoll.
Обработку соединений обрабатывают несколько потоков, количество которых можно задать в файле конфигурации либо через командную строку при запуске.

Результат нагрузочного тестирования при обработке соединений в 1 поток:
```
izvezdin@iNote:~$ ab -n 50000 -c 100 -r http://localhost:8000/httptest/wikipedia_russia.html
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        iZvezdin
Server Hostname:        localhost
Server Port:            8000

Document Path:          /httptest/wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      100
Time taken for tests:   28.947 seconds
Complete requests:      50000
Failed requests:        1
   (Connect: 0, Receive: 1, Length: 0, Exceptions: 0)
Total transferred:      47745850000 bytes
HTML transferred:       47741200000 bytes
Requests per second:    1727.27 [#/sec] (mean)
Time per request:       57.895 [ms] (mean)
Time per request:       0.579 [ms] (mean, across all concurrent requests)
Transfer rate:          1610745.53 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.1      1       5
Processing:     0   57   3.5     56     120
Waiting:        0    2   2.4      2      66
Total:          0   58   3.5     57     120

Percentage of the requests served within a certain time (ms)
  50%     57
  66%     58
  75%     58
  80%     59
  90%     61
  95%     66
  98%     68
  99%     69
 100%    120 (longest request)
```
