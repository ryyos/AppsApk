import os
import requests

from datetime import datetime, timezone
import datetime as date
from time import strftime, sleep, time
from icecream import ic
from pyquery import PyQuery
from requests import Session, Response
from fake_useragent import FakeUserAgent
from concurrent.futures import ThreadPoolExecutor, wait

from src.utils.logs import logger
from src.utils.corrector import vname
from src.utils.fileIO import File
class AppsApk:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent()
        self.__session = Session()
        self.__executor = ThreadPoolExecutor()

        self.MAIN_DOMAIN = 'www.appsapk.com'
        self.MAIN_URL = 'https://www.appsapk.com'
        self.MAIN_PATH = 'data'
        self.PIC = 'Rio Dwi Saputra'
        
        ...
    
    
    def __logging(self, 
                  path: str, 
                  url: str, 
                  total: int, 
                  failed: int, 
                  success: int,
                  name_error: str,
                  message: str) -> None:
        
        content = {
              "source": url,
              "total_data": total,
              "total_data_berhasil_diproses": success,
              "total_data_gagal_diproses": failed,
              "PIC": self.PIC,
              "name_error": name_error,
              "message": message
            }
        
        with open(path, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')
        ...


    def __create_dir(self, raw_data: dict) -> str:
        try: os.makedirs(f'{self.MAIN_PATH}/data_raw/review_appsapks/{vname(raw_data["reviews_name"].lower())}/json')
        except Exception: ...
        finally: return f'{self.MAIN_PATH}/data_raw/review_appsapks/{vname(raw_data["reviews_name"].lower())}/json'
        ...


    def __convert_path(self, path: str) -> str:
        
        path = path.split('/')
        path[1] = 'data_clean'
        return '/'.join(path)
        ...


    def __retry(self, url: str, retry_interval: int = 10) -> Response:

        while True:
            try:
                response = self.__session.get(url=url, headers={"User-Agent": self.__faker.random})

                logger.info(f'request to: {url}')
                logger.info(f'reponse: {response.status_code}')
                print()

                if response.status_code == 200: return response
                if response.status_code == 500: return response

                logger.warning(f'request to: {url}')
                logger.warning(f'reponse: {response.status_code}')
                print()

                ic(response.text)

                sleep(retry_interval)

            except Exception as err:

                logger.error(f'request to: {url}')
                logger.error(f'reponse: {err}')
                print()

                sleep(retry_interval)
        ...


    def __convert_time(self, times: str) -> int:
        dt = date.datetime.fromisoformat(times)
        dt = dt.replace(tzinfo=timezone.utc) 

        return int(dt.timestamp())


    def __extract_app(self, url_app: str) -> None:

        comment_page = 1
        all_review = 0
        total_review = 0
        while True:

            url_review = f'{url_app}comment-page-{comment_page}/#comments'
            response = self.__retry(url_review)
            if response != 200:
                self.__logging(url=url_app,
                               name_error="Internal Server Error",
                               message=response.text,
                               total=total_review,
                               path='logs/logs.txt',
                                success=all_review,
                               failed=total_review - all_review)
                
            app = PyQuery(response.text)

            comment_page +=1
        
            if not app.find('ul[class="comment-list"] > li'): break

            total_review = int(app.find('h3[class="comment-title main-box-title"]').text().split(' ')[0])
            logger.info(f'total review: {total_review}')
            logger.info(f'url_review: {url_review}')

            for review in app.find('ul[class="comment-list"] > li'):

                results = {
                    "link": self.MAIN_URL,
                    "domain": self.MAIN_DOMAIN,
                    "tag": [PyQuery(tag).text() for tag in app.find('a[rel="tag"]')],
                    "crawling_time": strftime('%Y-%m-%d %H:%M:%S'),
                    "crawling_time_epoch": int(time()),
                    "path_data_raw": "string",
                    "path_data_clean": "string",
                    "reviews_name": app.find('h1[class="entry-title"]').text(),
                    "location_reviews": None,
                    "category_reviews": "application",
                
                    "total_reviews": total_review,
                    "reviews_rating": {
                    "total_rating": None,
                    "detail_total_rating": [
                        {
                        "score_rating": None,
                        "category_rating": None
                        }
                    ]
                    },
                    "detail_application": {
                      vname(PyQuery(detail).find('strong').text()): PyQuery(detail).text().replace(PyQuery(detail).find('strong').text(), '').replace('\n', '')\
                        for detail in app.find('div[class="details"]')
                    },
                    "detail_reviews": {
                    "username_reviews": PyQuery(list(PyQuery(review).find('div[class="comment-author vcard"] > b'))[0]).text(),
                    "image_reviews": PyQuery(review).find('div[class="app-icon"]').attr('src'),
                    "created_time": PyQuery(list(PyQuery(review).find('div[class="comment-metadata"] time'))[0]).attr('datetime').split('+')[0].replace('T', ' '),
                    "created_time_epoch": self.__convert_time(PyQuery(list(PyQuery(review).find('div[class="comment-metadata"] time'))[0]).attr('datetime')),
                    "email_reviews": None,
                    "company_name": None,
                    "location_reviews": None,
                    "title_detail_reviews": None,
                    "reviews_rating": None,
                    "detail_reviews_rating": [
                        {
                        "score_rating": None,
                        "category_rating": None
                        }
                    ],
                    "total_likes_reviews": None,
                    "total_dislikes_reviews": None,
                    "total_reply_reviews": 0,
                    "content_reviews": PyQuery(list(PyQuery(review).find('div[class="comment-content"]'))[0]).text(),
                    "reply_content_reviews": [],
                    "date_of_experience": PyQuery(list(PyQuery(review).find('div[class="comment-metadata"] time'))[0]).attr('datetime').split('+')[0].replace('T', ' '),
                    "date_of_experience_epoch": self.__convert_time(PyQuery(list(PyQuery(review).find('div[class="comment-metadata"] time'))[0]).attr('datetime'))
                    }
                }

                all_review+=1

                logger.info(f'username: {results["detail_reviews"]["username_reviews"]}')

                ic(bool(PyQuery(review).find('ul[class="children"]')))
                if PyQuery(review).find('ul[class="children"]'):
                    child = PyQuery(review).find('ul[class="children"]')
                    for reply in PyQuery(child).find('li'):
                        all_review+=1
                        results["detail_reviews"]["total_reply_reviews"] +=1
                        results["detail_reviews"]["reply_content_reviews"].append({
                            "username_reply_reviews": PyQuery(reply).find('div[class="comment-author vcard"] > b').text(),
                            "content_reviews": PyQuery(reply).find('div[class="comment-content"]').text()
                        })

                path = f'{self.__create_dir(results)}/{vname(results["detail_reviews"]["username_reviews"])}.json'

                results.update({
                    "path_data_raw": path,
                    "path_data_clean": self.__convert_path(path)
                })

                results["detail_application"].update({
                    "descriptions": app.find('#description').text()
                })

                self.__file.write_json(path, results)
                ...

        self.__logging(url=url_app, 
                       name_error=None,
                       message='success',
                       total=total_review,
                       path='logs/logs.txt',
                        success=all_review,
                       failed=total_review - all_review)
            
        ...

    def main(self):

        page = 1
        task_executor = []
        while True:
            url = f'{self.MAIN_URL}/page/{page}'
            ic(url)

            response = self.__retry(url)
            html = PyQuery(response.text)

            apps = html.find('article.vce-post.post.type-post.status-publish.format-standard.has-post-thumbnail.hentry h2 a')
            
            for app in apps:
                ic(PyQuery(app).attr('href'))
                task_executor.append(self.__executor.submit(self.__extract_app, PyQuery(app).attr('href')))

                # self.__extract_app(PyQuery(app).attr('href'))

            if not apps: break

        wait(task_executor)
        self.__executor.shutdown(wait=True)
        ...