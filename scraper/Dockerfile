#Pull from Splash as the base image
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
# SIMULTANEOUSLY = crawl_sim.py ~ 29s
# SEQUENTIALLY = crawl_seq.py ~ 26s
CMD ["scrapy", "crawl", "dining_halls"]

# NOTE: make sure to name the image 'scraper'