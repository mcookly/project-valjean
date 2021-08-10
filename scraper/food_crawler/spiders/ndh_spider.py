import scrapy
import logging
from datetime import date
from scrapy_splash.request import SplashRequest
from scrapy.selector import Selector

def extract_food_cat(html_text):
    """
    Input: html text
    Output: dict with keys as categories and values as lists of foods
    """
    html = Selector(text=html_text) # Creates a selector object for Xpath parsing.
    # NOTE @Nick: feel free to change this data format to whatever works best.
    foods_per_category = dict()
    # Nodes of interest are all td
    td_nodes = html.xpath('//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td')

    for node in td_nodes:
        # Using extract_first() to avoid a list return
        node_class = node.xpath('./@class').extract_first()
        if node_class == 'cbo_nn_itemGroupRow':
            # Found a category
            category = node.xpath('./text()').extract_first()
            foods_per_category[category] = list()
            logging.debug(f'Found category: {category}')
        elif node_class == 'cbo_nn_itemHover':
            # Found a food item under a category
            food_item = node.xpath('./text()').extract_first()
            foods_per_category[category].append(food_item)
            logging.debug(f'    Found food item: {food_item}')
    
    return foods_per_category


# NOTE: Uses a flimsy method for relative paths and may break when using docker or
# Google Cloud.
with open('./food_crawler/scripts/nav_to_dh_menu.lua', 'r') as f:
    script_nav_to_dh_menu = f.read()
with open('./food_crawler/scripts/record_meal_elements.lua', 'r') as f:
    script_record_meal_elements = f.read()

class NDHSPIDER(scrapy.Spider):
    name = "ndh"
    allowed_domains = ['nutrition.nd.edu']
    # Both NDH and SDH spiders will start from this URL.
    url = 'http://nutrition.nd.edu/NetNutrition/1'
    current_day = date.today().strftime('%A, %B %-d, %Y')

    is_weekend = False if date.today().weekday() < 5 else True

    def start_requests(self):
        yield SplashRequest(
            url=self.url,
            callback=self.parse,
            endpoint='execute',
            args={
                'lua_source': script_nav_to_dh_menu,
                'wait': 1,
                'dh': 'tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)',
                'fwd_btn': '.cbo_nn_childUnitsCell > a:nth-child(1)',
                })
                
    def parse(self, response):
        # Parses data from NDH's day/meal selection menu.
        # This extracts the current day's meals' CSS selectors for
        # the next extraction.

        # Find node index for the current day
        for i in range(1, 8):
            day = response.css(f'div.cbo_nn_menuTableDiv tr:nth-child({i}) td.cbo_nn_menuCell td::text').get()
            if day == self.current_day:
                self.log(f'Found the current day ({day}) at node index {i}.')
                break
        self.log(' --- Completed first parse. --- ')
        
        yield SplashRequest(
            url=self.url,
            callback=self.parse_meals,
            endpoint='execute',
            args={
                'lua_source': script_record_meal_elements,
                'wait': 1,
                'dh': 'tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)',
                'fwd_btn': '.cbo_nn_childUnitsCell > a:nth-child(1)',
                'index': i,
                'weekend': self.is_weekend
            })
    
    def parse_meals(self, response):
        # Parses the food items from each meal at NDH and organize
        # into dicts for each meal.

        # Creates a dict: {key: meal, value: html from meal's webpage}
        response_per_meal = response.data

        # NOTE: Perhaps there is a more efficient way of categorizing
        # the parses. Would a numerical system work more smoothly?
        if self.is_weekend:
            meal_brunch = extract_food_cat(response_per_meal['brunch'])
        else:
            meal_breakfast = extract_food_cat(response_per_meal['breakfast'])
            meal_lunch = extract_food_cat(response_per_meal['lunch'])
        meal_dinner = extract_food_cat(response_per_meal['dinner'])

        # -------- @ Nick take over from here. ---------

        self.log(' --- Completed second parse. --- ')
