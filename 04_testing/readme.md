Testing
==============
**Домашнее задание 04_testing**

При написании тестов использовался Python 2.7.17

Тестирование API из предыдущего задания 03_oop

В отличие от предыдущего задания, в API были внесены изменения. Для кеширования значения очков и для хранения интересов используется хранилище на Redis.
Конфигурация работы хранилища задается в store.py
Пароль для доступа к Redis по умолчанию расположен в файле conf.json

>Пример файла conf.json:
```json
{
    "password": "your_passwod",
}
```

Запуск всех тестов:
`python2 -m unittest discover`

Запуск unit тестов:
`python2 -m unittest discover tests/unit`

Запуск интеграционных тестов:
`python2 -m unittest discover tests/integration`
