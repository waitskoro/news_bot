import time

import requests
from bs4 import BeautifulSoup


class RGRU:
    def __init__(self):
        self.__url = 'https://www.rg.ru/news/'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'
        }

    