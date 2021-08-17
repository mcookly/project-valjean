#Pull from Splash as the base image
FROM python:3.9.6

#Install needed packages
RUN apt-get update -y

#Set the working directory
WORKDIR /code

# Copy files
COPY requirements.txt .
COPY food_crawler/ ./food_crawler
COPY scrapy.cfg .

# Install all the dependencies (including the custom module)
RUN pip install -r requirements.txt && \
    pip install ./food_crawler/foodhandler

# Run both SDH and NDH spiders
CMD ["food_crawler/crawl.py"]
ENTRYPOINT ["python3"]

# NOTE: make sure to name the image 'crawler'