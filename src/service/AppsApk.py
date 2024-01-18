import os
import requests

from time import strftime, sleep
from icecream import ic
from pyquery import PyQuery
from requests import Response

from src.utils.logs import logger
from src.utils.corrector import vname
from src.utils.fileIO import File
class AppsApk:
    def __init__(self) -> None:

        self.__file = File()

        self.MAIN_DOMAIN = 'www.appsapk.com'
        self.MAIN_URL = 'https://www.appsapk.com'
        
        ...

    def __retry(self, url: str, retry_interval: int = 10) -> Response:

        while True:
            try:
                response = requests.get(url)

                ic(response)
                if response.status_code == 200: return response
                if response.status_code == 500: return False

                ic(response.text)

                sleep(retry_interval)


            except Exception as err:
                ic(err)
                sleep(retry_interval)
        ...


    def __extract_app(self, url_app: str) -> None:
        response = self.__retry(url_app)
        html = PyQuery(response.text)

        

        ...

    def main(self):

        page = 1
        while True:
            url = f'{self.MAIN_URL}/page/{page}'
            ic(url)

            response = self.__retry(url)
            html = PyQuery(response.text)

            apps = html.find('article.vce-post.post.type-post.status-publish.format-standard.has-post-thumbnail.hentry h2 a')
            for app in apps:
                ic(PyQuery(app).attr('href'))



            if not apps: break
            break


        ...