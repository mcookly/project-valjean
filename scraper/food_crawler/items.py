# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class FoodCategory(scrapy.Item):
    # FoodItem properties
    name = scrapy.Field()
    dining_hall = scrapy.Field()
    meal = scrapy.Field()
    foods = scrapy.Field()