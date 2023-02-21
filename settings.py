from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import time
import os
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import drivergen

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]

class Listing:

    def __init__(self, name, sku, price, id, inStock, size=None):
        self.name = name
        self.sku = sku
        self.price = price
        self.pid = id
        self.inStock = inStock

    def UpdateSize(self, size):
        self.size = size
    
    # {"dwvar_1000102660_color":"BV2654-010","dwvar_1000102660_size":"S","pid":"1000054139","quantity":"1"}
    def createQueryStrings(self):
        """create a list of query strings for given Listing"""
        ans = []
        color = "dwvar_" + self.pid + "_color"
        for size in SIZES:
            self.UpdateSize(size)
            idk = "dwvar_" + self.pid  + "_size"
            temp = {
                color : self.sku,
                idk : size,
                "pid": self.pid,
                "quantity" : "1"
            }
            ans.append(temp)
        return ans

# Variants of the listing (sizes, colors, etc..)
class Item():

    def __init__(self, name, sku, priceInt, size, url, imageUrl, uuid, pid, inStock, qstring):
        self.name = name
        self.sku = sku # each color has a different sku
        self.price = priceInt
        self.size = size 
        self.url = url
        self.imageUrl = imageUrl
        self.uuid = uuid
        self.pid = pid
        self.inStock = inStock
        self.qstring = qstring

    def changePrice(self, newPrice):
        self.price = newPrice


class Header():

    def __init__(self):
        self.user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
        # self.userAgent = self.getUserAgent()
        self.header = {
            "cookie": self.genCookieNoProxy(),
            "authority": "",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "referer": "",
            "user-agent": "",
            "x-requested-with": "XMLHttpRequest"
        }

    def getHeaders(self):
        return self.header

    def getRandomUserAgent(self):
        return self.user_agent_rotator.get_random_user_agent()

    def parseCookie(self, cookieList):
        ans = ""
        for cookie in cookieList:
            name = cookie['name']
            value = cookie['value']
            cur = name + '=' + value
            ans += cur + '; '
        return ans[:-2]

    def genCookieNoProxy(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options) 
        driver.get('')
        time.sleep(20)
        cookie = self.parseCookie(driver.get_cookies())
        driver.quit()
        print(cookie)
        return cookie

    def genCookieUseProxy(self):
        driver = drivergen.get_chromedriver(use_proxy=True)
        time.sleep(5)
        driver.get('')
        print(driver.execute_script("return navigator.userAgent;"))
        time.sleep(20)
        cookie = self.parseCookie(driver.get_cookies())
        driver.quit()
        print(cookie)
        return cookie


def init():
    global SKU_TO_LISTING
    global QSTRING_TO_ITEM
    global SIZES
    global HEADERS
    global DISCORD_WEBHOOK
    global INFO_URL
    global NUM_LISTINGS_TO_CHECK

    SKU_TO_LISTING = {}
    QSTRING_TO_ITEM = {}
    SIZES = ["S", "M", "L", "XL"]

    HEADERS = Header()

    DISCORD_WEBHOOK = ''
    INFO_URL = ''
    NUM_NIKE_LISTINGS_TO_CHECK = 2