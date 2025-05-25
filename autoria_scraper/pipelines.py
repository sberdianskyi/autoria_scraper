# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


class AutoRiaScraperPipeline:
    def __init__(self):
        dbname = os.environ["POSTGRES_DB"]
        username = os.environ["POSTGRES_USER"]
        password = os.environ["POSTGRES_PASSWORD"]
        host = os.environ["POSTGRES_HOST"]

        self.connection = psycopg2.connect(
            host=host,
            user=username,
            password=password,
            dbname=dbname,
        )

        self.curr = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(
            """
            CREATE TABLE IF NOT EXISTS cars(
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE,
                title VARCHAR(255),
                price_usd INTEGER,
                odometer INTEGER,
                username VARCHAR(255),
                phone_number VARCHAR(255),
                image_url VARCHAR(255),
                images_count INTEGER,
                car_number VARCHAR(255),
                car_vin VARCHAR(255),
                datetime_found TIMESTAMP
            )
            """
        )

        self.connection.commit()

    def process_item(self, item, spider):
        try:
            self.curr.execute("SELECT url FROM cars WHERE url = %s", (item["url"],))
            exists = self.curr.fetchone()

            if not exists:
                self.curr.execute(
                    """
                    INSERT INTO cars(
                        url, title, price_usd, odometer, username,
                        phone_number, image_url, images_count,
                        car_number, car_vin, datetime_found
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        item["url"],
                        item["title"],
                        item["price_usd"],
                        item["odometer"],
                        item["username"],
                        item["phone_number"],
                        item["image_url"],
                        item["images_count"],
                        item["car_number"],
                        item["car_vin"],
                        item["datetime_found"],
                    ),
                )
                self.connection.commit()
                spider.logger.info(f"New record added: {item['url']}")
            else:
                spider.logger.info(f"The record already exists: {item['url']}")
        except Exception as e:
            spider.logger.error(f"Error saving to DB: {e}")
            self.connection.rollback()
        return item

    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()
