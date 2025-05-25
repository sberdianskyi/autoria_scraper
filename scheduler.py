from datetime import datetime
import csv
import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


def run_spider():
    project_path = Path(__file__).parent
    subprocess.run(["scrapy", "crawl", "car"], cwd=project_path)


def create_db_dump():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dumps_dir = Path(__file__).parent / "dumps"
    dumps_dir.mkdir(exist_ok=True)
    dump_path = dumps_dir / f"dump_{timestamp}.csv"

    db_host = os.getenv("POSTGRES_HOST")
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_pass = os.getenv("POSTGRES_PASSWORD")

    try:
        conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_pass, host=db_host
        )
        cur = conn.cursor()

        cur.execute("SELECT * FROM cars ORDER BY id")
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

        with open(dump_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Dump successfully created: {dump_path}")

    except psycopg2.Error as e:
        print(f"Error creating dump: {e}")
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


def main():
    scheduler = BlockingScheduler()
    start_time = os.getenv("SCRAPER_EVERYDAY_START_TIME")
    dump_time = os.getenv("DUMP_TIME")

    dump_hour, dump_minute = dump_time.split(":")
    scheduler.add_job(create_db_dump, CronTrigger(hour=dump_hour, minute=dump_minute))
    print(f"A DB dump is scheduled to be created every day at {dump_time}")

    if start_time:
        hour, minute = start_time.split(":")
        print(
            f"The scheduler is running. The parser will be launched daily at {start_time}"
        )
        scheduler.add_job(run_spider, CronTrigger(hour=hour, minute=minute))

    # For interval-based scheduling, uncomment the lines below
    # > import from apscheduler.triggers.interval import IntervalTrigger
    # > put interval_minutes SCRAPER_INTERVAL_MINUTES in .env
    # > create variable interval_minutes=os.getenv(SCRAPER_INTERVAL_MINUTES)
    # else:
    #     print(
    #         f"Планировщик запущен. Парсер будет запускаться каждые {interval_minutes} минут"
    #     )
    #     scheduler.add_job(run_spider, IntervalTrigger(minutes=int(interval_minutes)))

    scheduler.start()


if __name__ == "__main__":
    main()
