from src import AppsApk
from src import logger

from time import perf_counter

if __name__ == '__main__':
    start = perf_counter()
    logger.info('Scraping start..')

    app = AppsApk()
    app.main()

    logger.info('scraping is complete')
    logger.info(f'Scraping time: {perf_counter() - start}')