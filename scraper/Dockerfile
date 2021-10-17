FROM python:3.9.6-slim
# NOTE: python-slim may ~not~ be the most optimal image, but it doesn't
# seem to break anything right now, so let's keep using it.

# Update system
RUN apt-get update -y && apt-get clean

# Set the working directory
WORKDIR /code

# Copy configs
COPY scrapy.cfg /code/scrapy.cfg
COPY requirements.txt /code/requirements.txt

# Install all the dependencies
RUN pip install -r requirements.txt

# Copy source files
COPY food_crawler/ ./food_crawler

# Run both SDH and NDH spiders
CMD ["python3", "food_crawler/crawl.py"]

# NOTE: make sure to name the image 'scraper'