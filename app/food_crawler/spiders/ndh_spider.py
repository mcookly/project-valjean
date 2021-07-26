import scrapy
import json
from base64 import b64decode
from datetime import date
from scrapy_splash.request import SplashRequest

# NOTE: Uses a flimsy method for relative paths and may break when using docker or
# Google Cloud.
with open('./food_crawler/lua_scripts/nav_to_dh_menu.lua', 'r') as openfile:
    script_nav_to_dh_menu = openfile.read()
with open('./food_crawler/lua_scripts/record_meal_elements.lua', 'r') as openfile:
    script_record_meal_elements = openfile.read()

class NDHSPIDER(scrapy.Spider):
    name = "ndh"
    allowed_domains = ['nutrition.nd.edu']
    # Both NDH and SDH spiders will start from this URL.
    url = 'http://nutrition.nd.edu/NetNutrition/1'

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

        filename = 'result_meal.html'
        visdebug_filename = 'log.png'
        debug_img = b64decode(response.data['png'])
        CURRENT_DATE = date.today().strftime('%A, %B %-d, %Y')

        # Find index for the current day
        for i in range(1, 8):
            day = response.css(f'div.cbo_nn_menuTableDiv tr:nth-child({i}) td.cbo_nn_menuCell td::text').get()
            if day == CURRENT_DATE:
                self.log(f'Found the current day ({day}) at index {i}.')
                break

        with open(visdebug_filename, 'wb') as f:
            f.write(debug_img)
        self.log(f'Saved file {filename}')

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
                'weekend': False
            })
    
    def parse_meals(self, response):
        # Parses the food items from each meal at NDH.
        visdebug_filename = 'log_2.png'
        rb = response.data
        self.log(rb.keys())
        # debug_img = b64decode(response.data['png'])
        # with open(visdebug_filename, 'wb') as f:
        #     f.write(debug_img)
        self.log('Activated!')