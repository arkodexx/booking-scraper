## 🕷️ Featured Project: Booking.com Scraper

A Python-based web scraper that extracts **hotel listings, prices, ratings, and availability** from Booking.com.

### Features
- Extract hotel names, locations, prices, ratings and links
- Saves data into **CSV/JSON** for easy analysis
- Implements basic **rate-limiting and headers** to avoid being blocked
- Ready for integration with **data analysis or visualization pipelines**

### Technologies
- Python 🐍
- `Scrapy`, `scrapy-playwright`
- `asyncio` for faster scraping

### Usage
git clone https://github.com/yourusername/booking-scraper.git  
cd bookingcrawl  
pip install -r requirements.txt  
playwright install chromium  
Dont forget to change how much pages you want in main file  
scrapy crawl crawler -o data.json(or .csv if you need)  
