FROM python:3.9.6-slim

#Install needed packages
RUN apt-get update -y

#Set the working directory
WORKDIR /code

# Copy files
COPY requirements.txt .
COPY food_crawler/ ./food_crawler
COPY scrapy.cfg .

# Install all the dependencies
RUN pip install -r requirements.txt

# Run both SDH and NDH spiders
CMD ["scrapy", "crawl", "dining_halls"]

# NOTE: make sure to name the image 'scraper'