# Парсер сайта государственных закупок (ЕИС)

### Описание

Данный проект выполнен в рамках тестового задания. Основные задачи были следующими:
- написать алгоритм парсинга данных;
- разбить алгоритм на задачи celery (в виде классов) и наладить параллельную обработку HTML страниц и XML;
- Написать тесты.


### Стек
- python - язык разработки
- BeautifulSoup - библиотека для парсинга HTML страниц
- xml.etree.ElementTree - для парсинга XML страниц
- Redis - для запуска воркера celery

### Запуск
Сперва убедитесь, что установлен [Docker](https://docs.docker.com/engine/install/). Запустите Redis
```bash
$ docker compose up -d
```

Если необходимо измнеить настройки подключения к Redis, то скопируйте .env.template, переименуйте его в .env и заполните
```python
REDIS_HOST = '0.0.0.0'  # Хост для подключения к Redis
REDIS_PORT = '6379'     # Порт для подключения к Redis
REDIS_NUM_DB = '0'      # Номер БД Redis
```

В файле main.py добавьте URL адресы в списке urls, которые нужно спарсить
```python
from tasks import RootTask

def main():
    urls = [
        "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=&morphology=on&search-filter=Дате+обновления&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=&publishDateTo=&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&okpd2Ids=&okpd2IdsCodes=",
        "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=&morphology=on&search-filter=Дате+обновления&pageNumber=2&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=&publishDateTo=&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&okpd2Ids=&okpd2IdsCodes=",
    ]
    result = RootTask().s(urls).delay()

    list_result = result.get(timeout=30)
    end_result = [item for item in list_result]
    print(end_result)

if __name__ == '__main__':
    main()

```

Запустите worker celery
```bash
celery -A tasks worker --loglevel=info --pool=gevent --concurrency=10 --without-heartbeat --queues=celery
```

После чего запустите сам скрипт
```bash
python main.py
```

Спустя время в консоль должен выйти следующий результат

```bash
['2025-03-07T22:54:31.410+11:00', '2025-02-12T16:26:04.243+10:00', '2025-03-06T22:38:40.937+10:00', '2025-03-10T20:43:34.226+09:00', '2025-03-10T21:29:01.023+12:00', '2025-03-10T21:15:42.875+10:00', '2025-02-27T10:19:26.147+09:00', '2025-02-26T18:30:31.165+09:00', '2025-02-25T16:57:23.969+09:00', '2025-03-10T20:36:16.914+08:00', '2025-02-27T12:01:36.081+08:00', '2025-03-10T20:26:49.529+08:00', '2025-03-07T15:12:54.540+08:00', '2025-03-10T16:25:53.550+10:00', '2025-03-10T16:02:44.195+08:00', '2025-02-26T15:23:29.933+08:00', '2025-03-10T20:03:08.275+11:00', '2025-03-10T20:01:17.596+11:00', '2025-02-27T17:51:00.252+08:00', '2025-03-10T19:59:40.057+11:00']
```

### О себе
Целеустремленный Python разработчик - альтруист, ищущий оффер мечты.

Занимаюсь разработкой более 2х лет, умею: писать чистый код, проводить code review, взаимодействовать со сторонними API, разрабатывать RESTful API, писать unit тесты, работать в команде, декомпозировать сложные задачи. Также имею 3 года опыта работы в нефтяной и тепловых компаниях,

Реализовал 5 проектов 1 из них коммерческий (парсер для компании АНО "Центр развития"), 1 командный (интернет магазин бытовой техники), 1 для личных целей (телеграмм бот для учета заправленного топлива), остальные учебные.

Выбор нового направления в качестве python разработчика, обусловлен тем, что разработчик творческая и в то же время техническая профессия. Разработка дает возможность делать жизнь проще как для бизнеса, так и для людей.

Telegram: https://t.me/ReBiwer
Github: https://github.com/ReBiwer
