import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from celery import Celery, Task, group, chord

from config import settings

app = Celery(
    'tasks',
    broker=settings.url_redis,
    backend=settings.url_redis,
)


class BaseTask(Task):
    default_retry_delay = 5
    max_retries = 3

    def __init__(self):
        self.name = self.__class__.__name__


    @staticmethod
    def _get_headers(html: bool) -> dict:
        st_accept = "text/html" if html else "application/xml"
        st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (HTML, like Gecko) Version/15.4 Safari/605.1.15"
        headers = {
            "Accept": st_accept,
            "User-Agent": st_useragent
        }
        return headers

    def _fetch_page(self, url: str, html: bool = True) -> str:
        response = requests.get(url, headers=self._get_headers(html))
        return response.text


class ParseHTMLPage(BaseTask):

    def run(self, url: str) -> list[str]:
        html_str = self._fetch_page(url)
        html_urls = self.__parse_html(html_str)

        return group(
            (ParseXMLPage().s(url) for url in html_urls),
        ).delay().get(timeout=30)

    @staticmethod
    def __parse_html(html_str: str) -> list[str]:
        html_page = BeautifulSoup(html_str, 'lxml')
        domain_url = 'https://zakupki.gov.ru'
        urls = []
        div_blocks = html_page.find_all('div', class_='w-space-nowrap ml-auto registry-entry__header-top__icon')
        hrefs = [domain_url + div.find_all('a')[-1].get('href')
                 for div in div_blocks
                 ]
        urls.extend(hrefs)
        return urls


class ParseXMLPage(BaseTask):

    def run(self, html_url: str) -> str:
        xml_url = self.__convert_to_xml(html_url)
        xml_str = self._fetch_page(xml_url, html=False)
        return self.__parse_xml(xml_str)

    @staticmethod
    def __convert_to_xml(url: str) -> str:
        return url.replace('/view.html?', '/viewXml.html?')

    @staticmethod
    def __parse_xml(xml_str: str) -> str:
        xml_page = ElementTree.fromstring(xml_str)
        namespaces = {
            "default": "http://zakupki.gov.ru/oos/EPtypes/1",
            "ns7": "http://zakupki.gov.ru/oos/printform/1",
            "ns2": "http://zakupki.gov.ru/oos/base/1",
            "ns3": "http://zakupki.gov.ru/oos/common/1",
            "ns4": "http://zakupki.gov.ru/oos/types/1",
            "ns5": "http://zakupki.gov.ru/oos/KOTypes/1",
            "ns6": "http://zakupki.gov.ru/oos/CPtypes/1"
        }
        elem = (xml_page.find('default:commonInfo', namespaces)
                .find('default:publishDTInEIS', namespaces))
        return elem.text


class FinallyCompileResult(BaseTask):

    def run(self, results: list[str]):
        return [item for item in results]


class RootTask(BaseTask):

    def run(self, urls: list[str]) -> list[str]:
        return chord(
            (ParseHTMLPage().s(url) for url in urls),
            FinallyCompileResult().s()
        ).delay().get(timeout=30)


app.register_task(ParseHTMLPage())
app.register_task(ParseXMLPage())
app.register_task(FinallyCompileResult())
app.register_task(RootTask())
