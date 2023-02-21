import requests
import random
import time
import json
from datetime import datetime
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook, DiscordEmbed

import settings
import nikescraper


def sendDiscordWebhook(item, descriptor=None):
    """
    Send an discord notification to the given webhook with optional descriptor.
    """
    webhook = DiscordWebhook(url=settings.DISCORD_WEBHOOK)
    embed = DiscordEmbed(title=item.name, description=descriptor, url=item.url)
    embed.add_embed_field(name='Price', value="${:,.2f}".format(item.price))
    embed.add_embed_field(name='InStock', value=item.inStock)
    # embed.set_image(url=item.imageUrl)
    embed.set_footer(text='Developed by GitHub:bmiesch')
    embed.set_timestamp()
    webhook.add_embed(embed)

    try:
        response = webhook.execute()
    except Timeout as err:
        print(f'Oops! Connection to Discord timed out: {err}')


def getItemPrice(qstring):
    """
    Send request for an items info and return the price.
    """
    print(qstring)
    try:
        response = requests.request("GET", settings.INFO_URL,
                data="",
                headers=settings.HEADERS.getHeaders(),
                params=qstring)
        response.raise_for_status()
        print(response.status_code)
    except requests.exceptions.RequestException as err:
        print('Error encountered with GET Request test')
        print(err)
    else:
        print('Successful API Call')
        response_dict = response.json()
        price = response_dict['product']['price']['sales']['value']
        return int(price)


def monitor():

    print('''
    -----------Starting Monitoring Items-----------
    ''')

    for qstring in settings.QSTRING_TO_ITEM:
        curItem = settings.QSTRING_TO_ITEM[str(qstring)]
        curPrice = getItemPrice(curItem.qstring)
        
        if curPrice != curItem.price:
            curItem.changePrice(curPrice)
            sendDiscordWebhook(curItem, 'PRICE CHANGE')

        # Sleep between API calls
        time.sleep(random.randint(15, 30))


if __name__ == "__main__":
    settings.init()
    nikescraper.main()
    monitor()