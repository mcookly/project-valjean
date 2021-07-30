#Pull from Splash as the base image
FROM python:3.9.6

#Install needed packages
RUN apt-get update -y

#Set the working directory
WORKDIR /code

# Copy requirements.txt first
COPY requirements.txt .

# Install all the dependencies
RUN pip install -r requirements.txt

#copy all the files
COPY food_crawler/ ./food_crawler
COPY scrapy.cfg .

#Run the command
CMD ["scrapy", "crawl", "ndh"]