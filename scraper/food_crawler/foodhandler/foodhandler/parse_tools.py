import logging

from scrapy.selector.unified import _response_from_text
from food_crawler.items import FoodCategory
from scrapy.selector import Selector
from scrapy.loader import ItemLoader

### Categorize foods per the category listed by Notre Dame
def extract_foods_dict(html=None, tag=None, meal='', dh=''):
    """Create dict of foods per categry.
    Takes: HTML body (str), selector tag (Xpath; str), returns: dict {category: [foods]}
    """
    # A small debug measure
    if not html or not tag:
        logging.error('Either the HTML or Xpath selector is empty. Aborting...')
        return None

    html = Selector(text=html) # Creates a selector object for Xpath parsing.
    # NOTE @Nick: feel free to change this data format to whatever works best.
    # foods_per_category = dict()
    # For NDH, nodes of interest are all td
    td_nodes = html.xpath(tag)

    for node in td_nodes:
        cat = ItemLoader(item=FoodCategory(), response=html) # Init food item for item pipeline
        cat.add_value('foods', 'boop')
        cat['meal'] = meal
        cat["dining_hall"] = dh

        # Using extract_first() to avoid a list return
        node_class = node.xpath('./@class').extract_first()
        if node_class == 'cbo_nn_itemGroupRow':
            # Found a category
            cat['name'] = node.xpath('./text()').extract_first()
            # foods_per_category[category] = list()
            logging.debug(f'Found category: {cat["name"]}')
        elif node_class == 'cbo_nn_itemHover':
            # Found a food item under a category
            cat['foods'].add(node.xpath('./text()').extract_first())
            # foods_per_category[category].append(food_item)
            logging.debug(f'    Found food item: {cat["foods"]}')
        return cat.load_item()
    # return foods_per_category