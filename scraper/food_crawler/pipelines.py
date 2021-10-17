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
        self.logger = logging.getLogger(__name__)
        # This loads the Firebase credentials from the env
        cred = credentials.ApplicationDefault()
        try:
            firebase_admin.initialize_app(cred)
        except ValueError:
            # If Firebase is already initialized, then move on.
            pass
        self.logger.info("Opened Firebase session successfully")

    def open_spider(self, spider):
        self.date = date.today()
        self.client = firestore.client()
        self.col = self.client.collection(f'foods-{spider.name}')
        self.meals = list()

    def close_spider(self, spider):
        # Delete any old categories from the previous day
        def clean_db(collection):
            self.logger.info(f"Cleaning {collection.id}...")
            yesterday = str(self.date - timedelta(days=1))
            old_cats = collection.where('date', '==', yesterday).stream()
            for old_cat in old_cats:
                old_cat.reference.delete()
            self.logger.info(f"Cleaned {collection.id}")

        def update_meals(meals, collection, name):
            self.logger.info(f"Updating meals for {collection.id}...")
            collection.document("META-meals").set({
                'dh': name,
                'meals': meals
            })
            self.logger.info(f"Updating {collection.id}")

        clean_db(self.col)
        update_meals(self.meals, self.col, spider.name)
        self.client.close()
        self.logger.info("Closed Firebase session successfuly")

    def process_item(self, item, spider):
        # Items are category collections. See items.py for more details.
        item_dh = item['dining_hall']

        # Keep track of meals for each dining hall to read on the web app.
        if item['meal'] not in self.meals:
            self.meals.append(item['meal'])
        
        self.col.document(item['meal'] + '-' + item['name']).set({
            'name': item['name'],
            'foods': item['foods'],
            'date': str(self.date),
            'dh': item['dining_hall'],
            'meal': item['meal']
        })
        return item
