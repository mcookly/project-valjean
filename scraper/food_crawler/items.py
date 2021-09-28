# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class FoodItem(scrapy.Item):
    # Individual food items
    dining_hall = scrapy.Field()
    meal = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()

class FoodCategory(scrapy.Item):
    # Organize by category
    foods = scrapy.Field()
    dining_hall = scrapy.Field()
    meal = scrapy.Field()
    name = scrapy.Field()