import os
import logging
import scrapy
from datetime import date
from foodhandler import parse_tools, communicator
from scrapy_splash.request import SplashRequest

### Load Lua scripts ###
CUR_DIR = os.getcwd()
SCRIPTS_DIR = os.path.join(CUR_DIR, 'food_crawler/scripts')

### Load 'nav_to_dh_menu.lua'
try:
    with open(os.path.join(SCRIPTS_DIR, 'nav_to_dh_menu.lua'), 'r') as f:
        script_nav_to_dh_menu = f.read()
    logging.info('Found Lua script "nav_to_dh_menu" in ' + SCRIPTS_DIR)
except:
    logging.error('Could not find Lua script "nav_to_dh_menu" in ' + SCRIPTS_DIR)

### Load 'record_meal_elements.lua'
try:
    with open(os.path.join(SCRIPTS_DIR, 'record_meal_elements.lua'), 'r') as f:
        script_record_meal_elements = f.read()
    logging.info('Found Lua script "record_meal_elements" in ' + SCRIPTS_DIR)
except:
    logging.error('Could not find Lua script "record_meal_elements" in ' + SCRIPTS_DIR)

class NDHSPIDER(scrapy.Spider):
    ### __init__
    name = "ndh"
    allowed_domains = ['nutrition.nd.edu']
    # Both NDH and SDH spiders will start from this URL.
    url = 'http://nutrition.nd.edu/NetNutrition/1'
    current_day = date.today().strftime('%A, %B %-d, %Y')
    meals_list = tuple()

    # Page selectors
    dining_hall_sel = 'tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)'
    fwd_btn_sel = '.cbo_nn_childUnitsCell > a:nth-child(1)'

    def start_requests(self):
        yield SplashRequest(
            url=self.url,
            callback=self.parse,
            endpoint='execute',
            args={
                'lua_source': script_nav_to_dh_menu,
                'wait': 1,
                'dh': self.dining_hall_sel,
                'fwd_btn': self.fwd_btn_sel,
                })
                
    def parse(self, response):
        # Parses data from NDH's day/meal selection menu.
        # This extracts the current day's meals' CSS selectors for
        # the next extraction.

        # Find node index for the current day
        for i in range(1, 8):
            day = response.css(f'div.cbo_nn_menuTableDiv tr:nth-child({i}) td.cbo_nn_menuCell td::text').get()
            if day == self.current_day:
                logging.info(f'Found the current day ({day}) at node index {i}.')
                break
        # Get list of meals for the day
        # '//a' is cycling through all child nodes under the current day node.
        self.meals_list = response.xpath('//*[@id="MenuList"]/div[2]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr//a/text()').extract()
        logging.info(f'Found {len(self.meals_list)} meal(s): {self.meals_list}')
        logging.info(' --- Completed first parse --- ')
        yield SplashRequest(
            url=self.url,
            callback=self.parse_meals,
            endpoint='execute',
            args={
                'lua_source': script_record_meal_elements,
                'wait': 1,
                'dh': self.dining_hall_sel,
                'fwd_btn': self.fwd_btn_sel,
                'index': i,
                'meals': self.meals_list
            })
    
    def parse_meals(self, response):
        # Parses the food items from each meal at NDH and organize
        # into dicts for each meal.

        # Creates a dict: {key: meal, value: html from meal's webpage}
        response_per_meal = response.data
        # This tag *might* work for SDH as well.
        xpath_tag = '//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td'

        # Extract meal contents
        for meal in self.meals_list:
            logging.debug(f'### {meal} ###')
            parse_tools.extract_foods_dict(response_per_meal[meal], xpath_tag)

        logging.info(' --- Completed second parse --- ')
        # -------- @ Nick take over from here. ---------
        # Add SQL code to the file 'communicator.py' in foodhandler
        # under write_to_db. We could actually just communicate straight to 
        # the db in the for loop above.

        # communicator.write_to_db()  