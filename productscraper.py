import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import settings


def scrapeNikeListings():
    """
    Scrape [settings.NUM_LISTINGS_TO_CHECK] Nike products from website and add a listing for each.
    """
    s = requests.session()
    html = s.get('' + settings.NUM_NIKE_LISTINGS_TO_CHECK,
                headers=settings.HEADERS.getHeaders(),
                timeout=120)
    soup = BeautifulSoup(html.text, 'html.parser')
    array = soup.find_all('div', {'class': 'col-6 col-lg-4'})

    print(len(array))

    for item in array:

        data = json.loads(item.find('div', {'class': 'grid-tile product'})['data-impressiondata'])
        if data['productCategory'] != 'Nike Shoes':
            temp_listing = settings.Listing(data['name'], data['productVariant'], data['price'], data['id'], not data['productOutOfStock'] )
            settings.SKU_TO_LISTING[temp_listing.sku] = temp_listing
    
    print("Finished Scraping Nike Products")
    s.close()


def loadItemInfo(response_dict, qstring):
    """
    Create an item from the response info and load into ITEMS list and SKU_TO_PRICE dictionary.
    """
    name = response_dict['product']['brand'] + ' ' + response_dict['product']['productName']
    price = response_dict['product']['price']['sales']['value']
    priceInt = int(price)
    # productPriceFormatted = "${:,.2f}".format(pro2ductPrice)
    sku = response_dict['product']['vendorStyle']
    url = '' +  response_dict['product']['selectedProductUrl']
    imageUrl = response_dict['product']['images']['small'][0]['absUrl']
    uuid = response_dict['product']['uuid']
    pid = settings.SKU_TO_LISTING[sku].pid
    size = settings.SKU_TO_LISTING[sku].size
    inStock =  not response_dict['product']['gtm']['productOutOfStock']

    item = settings.Item(name, sku, priceInt, size, url, imageUrl, uuid, pid, inStock, qstring)

    settings.QSTRING_TO_ITEM[str(qstring)] = item
    return item


def getListingInfo(queryStrings):
    """
    Send request for each of the Listing variants in queryStrings.
    """
    for qstring in queryStrings:
        try:
            response = requests.request("GET", settings.INFO_URL,
                    data="",
                    headers=settings.HEADERS.getHeaders(),
                    params=qstring)
            response.raise_for_status()
            print(response.status_code)
            time.sleep(random.randint(15, 30))
        except requests.exceptions.RequestException as err:
            print('Error encountered with GET Request test2')
            print(err)
        else:
            loadItemInfo(response.json(), qstring)
            print('Successful API Call')


def loadListings():
    """
    For each listing, load each Item (variation).
    """
    for cur_listing_sku in settings.SKU_TO_LISTING:
        getListingInfo(settings.SKU_TO_LISTING[cur_listing_sku].createQueryStrings())

    print('''
    -----------Finished Scraping and Loading Nike Products-----------
    ''')


def main():
    scrapeNikeListings()
    loadListings()