import firebase_admin, os
from firebase_admin import credentials, firestore
from datetime import datetime
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class FoodCrawlerPipeline:
    def __init__(self):
        # Initialize pipeline here
        CUR_DIR = os.getcwd()
        AUTH_PATH = os.path.join(CUR_DIR, 'food_crawler/SECRETS/firebase_key.json')
        cred = credentials.Certificate(AUTH_PATH)
        firebase_admin.initialize_app(cred)
    
    def open_spider(self, spider):
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.client = firestore.client()
        self.collection = self.client.collection('scraped-' + self.date)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Each food item has a unique ID to prevent any overwriting if both
        # DHs have identical foods. Another option would be to use
        # subcollections.
        self.collection.add({
            'name': item['name'],
            'category': item['category'],
            'date': self.date,
            'dh': item['dining_hall'],
            'meal': item['meal']
        })
        return item
