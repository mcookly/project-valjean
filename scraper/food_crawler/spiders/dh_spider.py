import os, logging, scrapy
from datetime import date
from food_crawler.items import FoodCategory
from scrapy_splash.request import SplashRequest
from scrapy.selector import Selector

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

class DHSPIDER(scrapy.Spider):
    name = "dining_halls"
    allowed_domains = ['nutrition.nd.edu']
    # Both NDH and SDH spiders will start from this URL.
    url = 'http://nutrition.nd.edu/NetNutrition/1'
    current_day = date.today().strftime('%A, %B %-d, %Y')
    meals_list = tuple()
    # Page selectors
    wait_time = 1
    dining_hall_sel = {
        'South': 'tr.cbo_nn_unitsPrimaryRow:nth-child(5) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)',
        'North': 'tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)'
    }
    fwd_btn_sel = '.cbo_nn_childUnitsCell > a:nth-child(1)'

    def start_requests(self):
        for dh in self.dining_hall_sel.keys():
            yield SplashRequest(
                url=self.url,
                callback=self.parse,
                endpoint='execute',
                dont_filter=True,
                meta={'dh': dh},
                args={
                    'lua_source': script_nav_to_dh_menu,
                    'wait': self.wait_time,
                    'dh': self.dining_hall_sel[dh],
                    'fwd_btn': self.fwd_btn_sel,
                    })
                
    def parse(self, response):
        # Parses data from SDH's day/meal selection menu.
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
        self.meals_list = response.xpath(f'//*[@id="MenuList"]/div[2]/table/tbody/tr[{i}]/td/table/tbody/tr[2]/td/table/tbody/tr//a/text()').extract()
        logging.info(f'Found {len(self.meals_list)} meal(s): {self.meals_list}')
        logging.info(' --- Completed first parse --- ')

        dining_hall = response.meta.get('dh')
        yield SplashRequest(
            url=self.url,
            callback=self.parse_meals,
            endpoint='execute',
            dont_filter=True,
            meta={'dh': dining_hall},
            args={
                'lua_source': script_record_meal_elements,
                'wait': self.wait_time,
                'dh': self.dining_hall_sel[dining_hall],
                'fwd_btn': self.fwd_btn_sel,
                'index': i,
                'meals': self.meals_list
            })
    
    def parse_meals(self, response):
        # Parses the food items from each meal and sends results through the
        # item pipeline to be uploaded to Firebase.

        response_data = response.data
        xpath_tag = '//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td'
        # Extract meal contents
        for meal in self.meals_list:
            meal_data = Selector(text=response_data[meal])
            # For both DH, nodes of interest are all td
            td_nodes = meal_data.xpath(xpath_tag)

            for i in range(len(td_nodes)):
                # Using extract_first() to avoid list return of a single item.
                node = td_nodes[i]
                if node.xpath('./@class').extract_first() == 'cbo_nn_itemGroupRow':
                    # Found a category
                    cat_item = FoodCategory() # Init category for item pipeline
                    cat_name = node.xpath('./text()').extract_first()
                    if cat_name[0] == '*':
                        cat_name = cat_name[1:-1] # Trims '*' from category
                    cat_item['name'] = cat_name
                    cat_item['meal'] = meal
                    cat_item["dining_hall"] = response.meta.get('dh')

                    foods = set()
                    for j in range(i+1, len(td_nodes)):
                        # Cycle through future td's to find meals
                        mini_node = td_nodes[j]
                        mini_node_class = mini_node.xpath('./@class').extract_first()
                        if mini_node_class == 'cbo_nn_itemHover':
                            # Found a food item under a category
                            foods.add(mini_node.xpath('./text()').extract_first())
                        elif mini_node_class == 'cbo_nn_itemGroupRow':
                            cat_item["foods"] = foods
                            yield cat_item
                            break # Stop at next category

        logging.info(' --- Completed second parse --- ')