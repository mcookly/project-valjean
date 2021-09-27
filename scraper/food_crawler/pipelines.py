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
        # Display target DNS for Splash
        logging.info('Using "' + os.environ.get('SPLASH_IP') + '" for Splash IP.')
        # This loads the Firebase credentials from the env
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        logging.info("Opened Firebase session successfully")

    def open_spider(self, spider):
        self.date = date.today()
        self.client = firestore.client()
        self.north_col = self.client.collection('foods-North')
        self.south_col = self.client.collection('foods-South')
        self.meals_north = list()
        self.meals_south = list()

    def close_spider(self, spider):
        # Delete any old categories from the previous day
        def clean_db(collection):
            logging.info(f"Cleaning {collection.id}...")
            yesterday = str(self.date - timedelta(days=1))
            old_cats = collection.where('date', '==', yesterday).stream()
            for old_cat in old_cats:
                old_cat.reference.delete()
            logging.info(f"Cleaned {collection.id}")

        def update_meals(meals, collection, name):
            logging.info(f"Updating meals for {collection.id}...")
            collection.document("META-meals").set({
                'dh': name,
                'meals': meals
            })
            logging.info(f"Updating {collection.id}")

        clean_db(self.north_col)
        clean_db(self.south_col)
        update_meals(self.meals_north, self.north_col, 'North')
        update_meals(self.meals_south, self.south_col, 'South')
        self.client.close()
        logging.info("Closed Firebase session successfuly")

    def process_item(self, item, spider):
        # Items are category collections. See items.py for more details.
        item_dh = item['dining_hall']
        if item_dh == 'North':
            dh_col = self.north_col
            meals_list = self.meals_north
        elif item_dh == 'South':
            dh_col = self.south_col
            meals_list = self.meals_south

        # Keep track of meals for each dining hall to read on the web app.
        if item['meal'] not in meals_list:
            meals_list.append(item['meal'])
        
        dh_col.document(item['meal'] + '-' + item['name']).set({
            'name': item['name'],
            'foods': item['foods'],
            'date': str(self.date),
            'dh': item['dining_hall'],
            'meal': item['meal']
        })
        return item
