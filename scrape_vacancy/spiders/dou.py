import time
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Response, TextResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class DouSpider(scrapy.Spider):
    name = "dou"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = ["https://jobs.dou.ua/vacancies/?category=Python"]
    ukrainian_months = {
        "січня": "January", "лютого": "February", "березня": "March",
        "квітня": "April", "травня": "May", "червня": "June",
        "липня": "July", "серпня": "August", "вересня": "September",
        "жовтня": "October", "листопада": "November", "грудня": "December"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.quit()

    def start_requests(self):
        url = self.start_urls[0]
        self.driver.get(url)
        while True:
            try:
                more_button = WebDriverWait(self.driver, 10).until(
                    ec.visibility_of_element_located((By.CLASS_NAME, "more-btn"))
                )
                if more_button.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView();", more_button)

                    link = more_button.find_element(By.TAG_NAME, "a")
                    link.click()

                    time.sleep(1)
                else:
                    break

            except Exception as e:
                print("\n", e, "\n")
                break

        html = self.driver.page_source
        response = TextResponse(url=url, body=html, encoding="utf-8")
        yield from self.parse(response)

    def parse(self, response: Response, **kwargs) -> Response:
        for vacancy in response.css("li.l-vacancy"):
            url = vacancy.css("a.vt::attr(href)").get()
            if url:
                yield response.follow(
                    url, callback=self._parse_single_vacancy
                )

    def translate_date(self, date_str):
        for ukr, eng in self.ukrainian_months.items():
            date_str = date_str.replace(ukr, eng)
        return datetime.strptime(date_str, "%d %B %Y").date()

    def _parse_single_vacancy(self, response: Response) -> dict:
        salary = response.css("span.salary::text").get()
        if not salary:
            salary = "Unknown"

        description = response.css(".vacancy-section").get()
        soup = BeautifulSoup(description, "html.parser")
        description = soup.get_text().strip()

        yield {
            "title": response.css("h1.g-h2::text").get(),
            "url": response.url,
            "location": response.css("span.place.bi::text").get(),
            "company": response.css("div.l-n a::text").get(),
            "publication_data": self.translate_date(
                response.css(".date::text").get().strip()
            ),
            "salary": salary,
            "description": description,
        }
