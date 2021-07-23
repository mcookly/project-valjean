import scrapy
import json
from scrapy_splash.request import SplashRequest
from datetime import date

script_nav_to_meals = """
function main(splash, args)
    splash.images_enabled = false
    local results = {}
    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))
    btn_ndh = splash:select('tr.cbo_nn_unitsAlternateRow:nth-child(2) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)')
    btn_ndh:mouse_click()
    assert(splash:wait(0.5))
    btn_ndh_menus = splash:select('.cbo_nn_childUnitsCell > a:nth-child(1)')
    btn_ndh_menus:mouse_click()
    assert(splash:wait(0.5))
    meal_selection_page = splash:html()
    btn_breakfast = splash:select('tr.cbo_nn_menuPrimaryRow:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1)')
    btn_breakfast:mouse_click()
    meal_breakfast_page = splash:html()

    results = {meal_selection_page, meal_breakfast_page}

    return results
end
"""
"""assert(splash:wait(0.5))
  btn3 = splash:select('tr.cbo_nn_menuPrimaryRow:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1)')
  btn3:mouse_click()"""

class NDHSPIDER(scrapy.Spider):
    name = "ndh"
    allowed_domains = ['nutrition.nd.edu']

    def start_requests(self):
        # Both NDH and SDH spiders will start from this URL.
        url = 'http://nutrition.nd.edu/NetNutrition/1'
        yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': script_nav_to_meals}
        )
        yield SplashRequest()

    def parse(self, response):
        filename = 'result_meal.html'
        with open(filename, 'wb') as f:
            f.write(response.text)
        self.log(f'Saved file {filename}')