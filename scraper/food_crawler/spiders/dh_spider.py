import os, logging, scrapy
from datetime import date
from food_crawler.items import FoodCategory
from scrapy_splash.request import SplashRequest
from scrapy.selector import Selector

class DHSPIDER(scrapy.Spider):
    ### __init__
    def __init__(self, *args, **kwargs):
        # Display target DNS for Splash
        self.logger.debug('Using "' + os.environ.get('SPLASH_IP') + '" for Splash IP.')
        
        ## Load Lua scripts
        CUR_DIR = os.getcwd()
        SCRIPTS_DIR = os.path.join(CUR_DIR, 'food_crawler/scripts')

        # Load 'nav_to_dh_menu.lua'
        try:
            with open(os.path.join(SCRIPTS_DIR, 'nav_to_dh_menu.lua'), 'r') as f:
                self.script_nav_to_dh_menu = f.read()
            self.logger.debug('Found Lua script "nav_to_dh_menu" in ' + SCRIPTS_DIR)
        except:
            self.logger.critical('Could not find Lua script "nav_to_dh_menu" in ' + SCRIPTS_DIR)

        # Load 'record_meal_elements.lua'
        try:
            with open(os.path.join(SCRIPTS_DIR, 'record_meal_elements.lua'), 'r') as f:
                self.script_record_meal_elements = f.read()
            self.logger.debug('Found Lua script "record_meal_elements" in ' + SCRIPTS_DIR)
        except:
            self.logger.critical('Could not find Lua script "record_meal_elements" in ' + SCRIPTS_DIR)
    
    ## Init variables
    name = "dining_halls"
    allowed_domains = ['nutrition.nd.edu']
    # Both NDH and SDH spiders will start from this URL.
    url = 'http://nutrition.nd.edu/NetNutrition/1'
    current_day = date.today().strftime('%A, %B %-d, %Y')
    meals_list = tuple()
    # Page selectors
    wait_time = float(os.environ.get('SPIDER_WAIT_TIME'))
    splash_timeout = float(os.environ.get('SPLASH_TIMEOUT'))
    dining_hall_sel = {
        'South': 'tr.cbo_nn_unitsPrimaryRow:nth-child(5) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)',
        'North': 'tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)'
    }
    fwd_btn_sel = '.cbo_nn_childUnitsCell > a:nth-child(1)'

    def start_requests(self):
        for dh in self.dining_hall_sel.keys():
            self.logger.info(f'[{dh}]: Beginning first parse...')
            yield SplashRequest(
                url=self.url,
                callback=self.parse,
                endpoint='execute',
                dont_filter=True,
                meta={'dh': dh},
                args={
                    'lua_source': self.script_nav_to_dh_menu,
                    'wait': self.wait_time,
                    'timeout': self.splash_timeout,
                    'dh': self.dining_hall_sel[dh],
                    'fwd_btn': self.fwd_btn_sel,
                    })
                
    def parse(self, response):
        # Parses data from SDH's day/meal selection menu.
        # This extracts the current day's meals' CSS selectors for
        # the next extraction.
        dining_hall = response.meta.get('dh')

        # Find node index for the current day
        for i in range(1, 8):
            day = response.css(f'div.cbo_nn_menuTableDiv tr:nth-child({i}) td.cbo_nn_menuCell td::text').get()
            if day == self.current_day:
                self.logger.debug(f'[{dining_hall}]: Found the current day ({day}) at node index {i}.')
                break
        # Get list of meals for the day
        # '//a' is cycling through all child nodes under the current day node.
        self.meals_list = response.xpath(f'//*[@id="MenuList"]/div[2]/table/tbody/tr[{i}]/td/table/tbody/tr[2]/td/table/tbody/tr//a/text()').extract()
        self.logger.debug(f'[{dining_hall}]: Found {len(self.meals_list)} meal(s): {self.meals_list}')
        self.logger.info(f'[{dining_hall}]: Completed first parse')

        yield SplashRequest(
            url=self.url,
            callback=self.parse_meals,
            endpoint='execute',
            dont_filter=True,
            meta={'dh': dining_hall},
            args={
                'lua_source': self.script_record_meal_elements,
                'wait': self.wait_time,
                'timeout': self.splash_timeout,
                'dh': self.dining_hall_sel[dining_hall],
                'fwd_btn': self.fwd_btn_sel,
                'index': i,
                'meals': self.meals_list
            })
    
    def parse_meals(self, response):
        # Parses the food items from each meal and sends results through the
        # item pipeline to be uploaded to Firebase. (This triple for-loop
        # is killing me, but is there any other way???)

        response_data = response.data
        xpath_tag = '//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td'
        # Extract meal contents
        for meal in self.meals_list:
            meal_data = Selector(text=response_data[meal])
            
            cat_class = 'cbo_nn_itemGroupRow' # This designates a category
            food_class = 'cbo_nn_itemHover'  # This designates a food

            # For both DH, nodes of interest are all <td>
            td_nodes = meal_data.xpath(xpath_tag)
            n_cats = td_nodes.xpath('./@class').extract().count(cat_class)
            self.logger.info(f'[{response.meta.get("dh")}]: Found {n_cats} categories')
            

            for _ in range(n_cats):
                # Loop only the number of categories
                cat_node = td_nodes[0]
                cat_name = cat_node.xpath('./text()').extract_first()
                cat_item = FoodCategory() # Init category for item pipeline

                self.logger.debug(f'Found category: {cat_name} in {meal}')

                # Iterate through items
                foods = set()
                for i in range(1, len(td_nodes)):
                    # Start one past the current category node
                    node = td_nodes[i]
                    node_class = node.xpath('./@class').extract_first()
                    if node_class == food_class:
                        # Found a food item under a category
                        foods.add(node.xpath('./text()').extract_first())
                    elif node_class == cat_class:
                        # Found the next class
                        break

                # Prep and send item to pipeline  
                if cat_name[0] == '*':
                    cat_name = cat_name[1:-1] # Trims '*' from category
                cat_name = cat_name.replace('/', '-')
                # Firebase does not allow for '/' in document IDs
                cat_item['name'] = cat_name
                cat_item['meal'] = meal
                cat_item['dining_hall'] = response.meta.get('dh')
                cat_item['foods'] = foods
                yield cat_item
                  
                # Prep for next loop
                td_nodes = td_nodes[i:]

        self.logger.info(f'[{response.meta.get("dh")}]: Completed second parse')