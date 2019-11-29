Scoring API
==============
**Домашнее задание 03_oop**

При написании API использовался Python 2.7.16

API представляет собой учебно-тренеровочный интерфейс для выдачи данных сервиса скоринга. 
Доступ к API осуществляется с помощью HTTP POST запроса в формате JSON, в теле которого находятся данные для доступа к сервису, метод, который необходиомо вызвать и аргументы для этого метода.

>Пример запроса для вызова метода online_score:
```json
{
    "account": "account",
    "login": "login",
    "method": "online_score",
    "token": "token",
    "arguments": {
        "phone": "phone num",
        "email": "your@email.com", 
        "first_name": "your first name",
        "last_name": "your first name",
        "birthday": "birthday",
        "gender": 0
    }
}
```
>Пример запроса для вызова метода online_score:
```json
{
    "account": "account",
    "login": "login",
    "method": "online_score",
    "token": "token",
    "arguments": {
        "client_ids": [1,2,3,4],
        "date": "date"
    }
}
```

По умолчанию сервис запускается на порту 8080 и произодит логгирование в стандартный вывод
Для указания порта и файла для логирования, их необходимо передать с помощью опций командной строки.

Ключи опций: 
```
  -h, --help            show this help message and exit
  -p PORT, --port=PORT  
  -l LOG, --log=LOG 
```

Запуск сервера  с настройками по умолчанию:

`python2 api.py`


