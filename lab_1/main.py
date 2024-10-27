import requests
from bs4 import BeautifulSoup
import pandas as pd

def product_extraction(product):
    name_link = product.select_one('.wd-entities-title a')
    cart_link = product.select_one('.wd-add-btn a').get("href")
    name = name_link.text.strip()
    link = name_link.get("href")
    prices = product.select('.woocommerce-Price-amount')  
    regular_price = None
    discount_price = None
    if len(prices) == 1:
        regular_price = prices[0].text.strip()
    elif len(prices) == 2:
        regular_price = prices[0].select_one('bdi').text.strip()
        discount_price = prices[1].select_one('bdi').text.strip()

    product_dict = {
        "ProductName": name,
        "RegularPrice": regular_price,
        "DiscountPrice": discount_price,
        "ProductLink": link,
        "CartLink": cart_link
    }

    return product_dict




initial_URL = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/"
res = requests.get(initial_URL)

print(res.status_code)



soup = BeautifulSoup(res.text, "html.parser")
# TO CREATE THE PAGES THAT NEED TO BE FETCHED, I need to get the number of pages firstly
exact_class = 'page-numbers'
pagination_items = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == [exact_class])
last_page = pagination_items[-1].text
paginated_URLs = []
base_paginated_URL = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/page/"
products_scraped = []
for page_number in range(int(last_page)):
  url = f"{base_paginated_URL}{page_number+1}/" 
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  products = soup.select('.product')
  for product in products:
    result = product_extraction(product)
    products_scraped.append(result)
    
    
pd_data = pd.DataFrame(products_scraped)
pd_data.to_csv('clever_shop.csv', index=False)