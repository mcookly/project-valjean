import logging
import scrapy
from datetime import date
from foodhandler import parse_tools, communicator
from scrapy_splash.request import SplashRequest

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
        # This tag *might* work for SDH as well.
        xpath_tag = '//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td'

        # NOTE: Perhaps there is a more efficient way of categorizing
        # the parses. Would a numerical system work more smoothly?
        if self.is_weekend:
            meal_brunch = parse_tools.extract_foods_dict(response_per_meal['brunch'], xpath_tag)
        else:
            meal_breakfast = parse_tools.extract_foods_dict(response_per_meal['breakfast'], xpath_tag)
            meal_lunch = parse_tools.extract_foods_dict(response_per_meal['lunch'], xpath_tag)
        meal_dinner = parse_tools.extract_foods_dict(response_per_meal['dinner'], xpath_tag)

        self.log(' --- Completed second parse. --- ')
        # -------- @ Nick take over from here. ---------
        # Add SQL code to the file 'communicator.py' in foodhandler
        # under write_to_db.
        # communicator.write_to_db()
