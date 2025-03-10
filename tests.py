import pytest
from unittest.mock import patch, MagicMock
from tasks import ParseHTMLPage, ParseXMLPage, RootTask
from config import settings
import requests


# Фикстура для инициализации Celery в eager-режиме
@pytest.fixture(scope='module')
def celery_config():
    return {
        'task_always_eager': True,
        'broker_url': settings.url_redis,
        'result_backend': settings.url_redis
    }


# Фикстура для мока HTTP-запросов
@pytest.fixture
def mock_requests():
    with patch('tasks.requests.get') as mock_get:
        yield mock_get


def test_parse_html_page(mock_requests):
    # Мокаем HTML-страницу
    test_html = """
    <html>
        <div class="w-space-nowrap ml-auto registry-entry__header-top__icon">
            <a href="/view.html?1"></a>
            <a href="/target.html?link1"></a>
        </div>
        <div class="w-space-nowrap ml-auto registry-entry__header-top__icon">
            <a href="/view.html?2"></a>
            <a href="/target.html?link2"></a>
        </div>
    </html>
    """

    result = ParseHTMLPage()._parse_html(test_html)

    expected = [
        'https://zakupki.gov.ru/target.html?link1',
        'https://zakupki.gov.ru/target.html?link2'
    ]
    assert result == expected


def test_parse_xml_page(mock_requests):
    # Мокаем XML-ответ
    test_xml = """
    <root>
        <default:commonInfo xmlns:default="http://zakupki.gov.ru/oos/EPtypes/1">
            <default:publishDTInEIS>2023-10-05</default:publishDTInEIS>
        </default:commonInfo>
    </root>
    """
    mock_requests.return_value.text = test_xml

    result = ParseXMLPage().run('http://html.url')

    assert result == '2023-10-05'


def test_error_handling(mock_requests):
    # Тестируем обработку ошибок
    mock_requests.side_effect = requests.exceptions.RequestException('Test error')

    with pytest.raises(Exception):
        ParseHTMLPage().run('http://invalid.url')


def test_xml_conversion():
    url = 'http://test.com/view.html?param=123'
    result = ParseXMLPage._convert_to_xml(url)
    assert result == 'http://test.com/viewXml.html?param=123'


def test_headers_generation():
    headers_html = ParseHTMLPage()._get_headers(html=True)
    headers_xml = ParseHTMLPage()._get_headers(html=False)

    assert headers_html['Accept'] == 'text/html'
    assert headers_xml['Accept'] == 'application/xml'
    assert 'Mozilla/5.0' in headers_html['User-Agent']


def test_empty_result(mock_requests):
    # Тест на пустой результат парсинга HTML
    mock_requests.return_value.text = '<html></html>'
    result = ParseHTMLPage().run('http://empty.url')
    assert result == []