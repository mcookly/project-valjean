import firebase_admin, os
from firebase_admin import credentials, firestore
from datetime import timedelta, date
import logging
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class FoodCrawlerPipeline:
    def __init__(self):
        # This loads the Firebase credentials from the env
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        logging.info("Opened Firebase session successfully")

    def open_spider(self, spider):
        self.date = date.today()
        self.client = firestore.client()
        self.north_col = self.client.collection('North')
        self.south_col = self.client.collection('South')

    def close_spider(self, spider):
        # Delete any old categories from the previous day
        def clean_db(collection):
            logging.info(f"Cleaning {collection.id}...")
            yesterday = str(self.date - timedelta(days=1))
            old_cats = collection.where('date', '==', yesterday).stream()
            for old_cat in old_cats:
                old_cat.reference.delete()
            logging.info(f"Cleaned {collection.id}")
        clean_db(self.north_col)
        clean_db(self.south_col)
        self.client.close()
        logging.info("Closed Firebase session successfuly")

    def process_item(self, item, spider):
        # Items are category collections. See items.py for more details.
        item_dh = item['dining_hall']
        if item_dh == 'North':
            dh_col = self.north_col
        elif item_dh == 'South':
            dh_col = self.south_col

        dh_col.document(item['meal'] + '-' + item['name']).set({
            'name': item['name'],
            'foods': item['foods'],
            'date': str(self.date),
            'dh': item['dining_hall'],
            'meal': item['meal']
        })
        return item
