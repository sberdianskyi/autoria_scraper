import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scrapy
from scrapy.http import Response

from autoria_scraper.items import AutoriaScraperItem
from datetime import datetime


class CarSpider(scrapy.Spider):
    name = "car"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        self.driver = uc.Chrome(
            options=options,
        )

    def close_spider(self, spider):
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.close()
                self.driver.quit()
            except:
                pass

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        car_links = response.css("a.m-link-ticket")

        for link in car_links:
            car_url = link.attrib["href"]
            yield response.follow(car_url, self.parse_car)

        next_page = response.css("span.page-item.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_car(self, response: Response):

        item = AutoriaScraperItem()

        item["url"] = response.url
        item["title"] = response.css("h1.head").xpath("string()").get().strip()

        price_str = response.css("div.price_value strong::text").get()
        item["price_usd"] = int(price_str.replace("$", "").replace(" ", ""))

        odometer_str = response.css("div.base-information.bold .size18::text").get()
        item["odometer"] = int(odometer_str.strip()) * 1000

        username = response.css("div.seller_info_name a::text").get()
        if not username:
            username = response.css("div.seller_info_name::text").get()
        item["username"] = username.strip()

        try:
            self.driver.get(response.url)
            wait = WebDriverWait(self.driver, 15)

            show_phone_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.phone_show_link"))
            )
            show_phone_button.click()
            time.sleep(1)

            phone_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.phone.bold"))
            )

            phone = phone_element.get_attribute("data-phone-number")

            if phone and any(c.isdigit() for c in phone):
                phone = "".join(c for c in phone if c.isdigit())
                item["phone_number"] = f"+38{phone}"
            else:
                item["phone_number"] = None

        except Exception as e:
            item["phone_number"] = None

        item["image_url"] = response.css(
            "div.carousel-inner picture:first-child source::attr(srcset)"
        ).get()

        images_count_str = response.css(
            "div.preview-gallery.mhide a.show-all.link-dotted::text"
        ).get()

        item["images_count"] = (
            int(images_count_str.split()[2])
            if images_count_str
            else len(response.css("div.preview-gallery.mhide a.photo-74x56"))
        )

        car_number = response.css("span.state-num::text").get()
        item["car_number"] = None if not car_number else car_number

        vin = response.css("span.label-vin::text").get()
        if not vin:
            vin = response.css("span.vin-code::text").get()
        item["car_vin"] = vin

        item["datetime_found"] = datetime.now()

        return item
