import requests
import logging
import time
import re as r
import pandas as pd 
import numpy as np 

from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from requests import RequestException

logging.basicConfig()
logger = logging.getLogger('News Crawler')
logger.setLevel(logging.DEBUG)


file = open('failedUrl.txt', 'a')
client = MongoClient(port = 27017)
db = client.news


def web_crawl(url):
    try:
        response = requests.get(url, timeout = 5)
        if response.status_code is not 200:
            logger.warn('Failed to fetch data from url: %s' %url)
            file.write(url+"\n")
            return    
    except RequestException:
        logger.warn('Failed to get connection to web server')
        file.write(url+"\n")
        return

    try:    
        soup = bs(response.text, 'html.parser')
        content = soup.find(class_ = "article-content")
        article = content.findAll('p')
        article_data = ''
        for para in article:
            s = str(para)
            tags = r.findall('<.+?>', s)
            for tag in tags:
                s= s.replace(tag, '')
            article_data += s
    except Exception:
        logger.warn('Failed to parse data')
        file.write(url+"\n")

    try:
        data = {
            'url': url,
            'article' : article_data
        }
        result = db.articles.insert_one(data)
    except Exception as e:
        logger.warn('Failed to insert data into mongodb')




if __name__ == '__main__':
    df = pd.read_csv('half1_2.csv')
    urls = np.array(df)
    for i in range(len(urls)):
        url = urls[i][1]
        web_crawl(url)
        if i % float(20) == 0:
            logger.info('%d pieces of new are fetched' %i)
        time.sleep(3)


