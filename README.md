# AutoRia Scraper

Web scraper for collecting car data from AUTO.RIA.com with storage in a cloud database.

## Project Structure

```text
autoria_scraper/ 
├── autoria_scraper/ 
│ ├── init.py 
│ ├── items.py # Data structure definitions 
│ ├── middlewares.py # Middleware components 
│ ├── pipelines.py # Data processing pipelines 
│ ├── settings.py # Project settings 
│ └── spiders/ 
│     ├── init.py 
│     └── car.py # Main spider for data collection 
├── scrapy.cfg # Scrapy configuration 
├── scheduler.py # Task scheduler for automated runs
└── requirements.txt # Project dependencies
```

## Technologies

- Python 3.12
- Scrapy
- PostgreSQL
- Docker

## Installation and Usage

### Option 1: Without Docker

1. Clone the repository:
    ```shell
    git clone https://github.com/sberdianskyi/autoria_scraper.git
    cd autoria_scraper
    ```

2. Create virtual environment and activate it:
    ```shell
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate     # Windows
    ```

3. Install dependencies:
    ```shell
    pip install -r requirements.txt
    ```

4. Create `.env` file with database connection settings (use `.env.example` as a template)

5. Run the scraper:
    ```shell
    scrapy crawl car
    ```
### Option 2: Using Docker
1. Clone the repository:
    ```shell
    git clone <repository-url>
    cd autoria_scraper
    ```

2. Create `.env` file with database connection settings (use `.env.example` as a template)

3. Build and run the Docker container:
    ```shell
    docker-compose build
    docker-compose up
    ```

4. Run the scraper:
    ```shell
    docker-compose exec scraper scrapy crawl car
    ```

Option: You can customize scheduler timing by modifying these variables in .env:
`SCRAPER_EVERYDAY_START_TIME=12:00  # Time to run scraper`
`DUMP_TIME=13:00                    # Time to create DB dump`


* Without Docker: `python scheduler.py`
* With Docker: `docker-compose exec scraper python scheduler.py`

## Data Structure

The collected data is stored in the database with the following schema:
* url: Car URL
* title: Advertisement title
* price_usd: Price in USD
* odometer: Vehicle mileage
* username: Seller name
* phone_number: Contact phone
* image_url: Main image URL
* images_count: Number of images
* car_number: Vehicle registration number(if exists)
* car_vin: Vehicle VIN code
* datetime_found: Timestamp of data collection