# Инструкция по использованию анализатора логов

При написании анализаторов логов использовался Python 3.7.3

Настройки по умолчанию:
```json
{
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "REPORT_TEMPLATE": "./report.html",
    "ERROR_RATE": 0.25
}
```

* REPORT_SIZE - количество URL с самым большим временем запроса, которые попадают в отчеты
* REPORT_DIR - директория, в которую анализатор складывает отчеты
* LOG_DIR - директория поиска логов, во вложенных директориях поиск не производится
* REPORT_TEMPLATE - шаблон отчета
* ERROR_RATE - порог ошибок парсинга лога, при котором отчет не будет сформирован

В шаблоне должна присутствовать строка $table_json, которая заменяется на список словарей со статистическими данными, представленными в виде JSON строки

Анализатор записывает отчет о своей работе в лог файл analyzer.log

Для запуска анализатора с настройками по умолчанию:

`python3 log_analyzer.py`

Настройки можно переопределить в отдельном файле в JSON формате (образец представлен выше) и передать анализатору с помощью параметра --config

`python3 log_analyzer.py --config config.json`
