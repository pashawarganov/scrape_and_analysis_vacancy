import scrapy
from scrapy.http import Response


class DouSpider(scrapy.Spider):
    name = "dou"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = ["https://jobs.dou.ua/vacancies/?category=Python"]

    def parse(self, response: Response, **kwargs):
        for vacancy in response.css(".l-vacancy"):
            general = {
                "title": vacancy.css(".vt::text").get(),
                "page": vacancy.css(".vt::attr(href)").get(),
                "company": vacancy.css(".company::text").get().replace(" ", ""),
                "location": vacancy.css(".cities::text").get(),
            }
            detail = {
                "publication date": "",
                "description": "",

            }

            yield general
