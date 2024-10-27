import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def product_extraction(product):
    name_link = product.select_one('.wd-entities-title a')
    cart_link = product.select_one('.wd-add-btn a').get("href")
    name = name_link.text.strip()
    link = name_link.get("href")
    prices = product.select('.woocommerce-Price-amount')  
    regular_price = None
    discount_price = None
    
    if len(prices) == 1:
        regular_price = prices[0].select_one('bdi').text.strip()
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

def fetch_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.select('.product')
    return [product_extraction(product) for product in products]

initial_URL = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/"
res = requests.get(initial_URL)
print(res.status_code)

soup = BeautifulSoup(res.text, "html.parser")
exact_class = 'page-numbers'
pagination_items = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') == [exact_class])
last_page = int(pagination_items[-1].text)

base_paginated_URL = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/page/"
paginated_URLs = [f"{base_paginated_URL}{page_number + 1}/" for page_number in range(last_page)]

products_scraped = []

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(fetch_page, url): url for url in paginated_URLs}
    
    for future in as_completed(futures):
        try:
            result = future.result()
            products_scraped.extend(result)
        except Exception as e:
            print(f"Error occurred while fetching {futures[future]}: {e}")

# Save to CSV
pd_data = pd.DataFrame(products_scraped)
pd_data.to_csv('clever_shop-paralel.csv', index=False)
