import logging
from scrapy.selector import Selector

### Categorize foods per the category listed by Notre Dame
def extract_foods_dict(html=None, tag=None):
    """Create dict of foods per categry.
    Input: HTML body (str), selector tag (Xpath; str)
    Returns: dict {category: [foods]}
    """
    logging.info("blah")
    return None