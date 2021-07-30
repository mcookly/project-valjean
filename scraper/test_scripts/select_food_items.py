import ast
from scrapy.selector import Selector
with open('../results.html', 'r') as f:
    results = f.read()

# Convert the str representation of the dict into an actual Python dict.
rd = ast.literal_eval(results)

dinner = rd['lunch']

html = Selector(text=dinner)
category = html.xpath('//tr[td[@class="cbo_nn_itemGroupRow"]][2]/td/text()').extract()
food_items = html.xpath('//tr[@class="cbo_nn_menuPrimaryRow" or @class="cbo_nn_menuAlternateRow"]').extract()
test = html.xpath('//table[@class="cbo_nn_itemGridTable"]/tbody/tr[3]/@class').extract()

items = html.xpath('//table[@class="cbo_nn_itemGridTable"]/tbody/tr//td')
foods_per_category = dict()
for item in items:
    # print(item)
    # print(item.xpath('./@class').extract())
    node_class = item.xpath('./@class').extract_first()
    # print(node_class)
    if node_class == 'cbo_nn_itemGroupRow':
        category = item.xpath('./text()').extract_first()
        foods_per_category[category] = list()
        print(f'Found category: {category}')
    elif node_class == 'cbo_nn_itemHover':
        food_item = item.xpath('./text()').extract_first()
        foods_per_category[category].append(food_item)
        print(f'    Found food item: {food_item}')
    # print(item.xpath('./*/@class').extract())