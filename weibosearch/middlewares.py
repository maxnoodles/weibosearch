# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import json
import logging
from datetime import datetime, timedelta
from fake_useragent import UserAgent

from scrapy.exceptions import IgnoreRequest


class CookiesMiddleware(object):

    def __init__(self, cookies_pool_url):
        """
        从cookies池接口获取cookies
        :param cookies_pool_url: cookies池地址
        """
        self.logger = logging.getLogger(__name__)
        self.cookies_pool_url = cookies_pool_url

    def _get_random_cookies(self):
        try:
            response = requests.get(self.cookies_pool_url)
            if response.status_code == 200:
                return json.loads(response.text)
        except ConnectionError:
            return None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_pool_url=crawler.settings.get('COOKIES_POOL_URL')
        )

    def process_request(self, request, spider):
        """
        向请求添加cookies
        :param request:
        :param spider:
        :return:
        """
        cookies = self._get_random_cookies()
        if cookies:
            request.cookies = cookies
            self.logger.debug('Using Cookies' + json.dumps(cookies))
        else:
            self.logger.debug('No Valid Cookies')

    def process_response(self, request, response, spider):
        """
        状态码判断
        :param response:
        :param spider:
        :return:
        """
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers['location']
                # 判断cookie是否失效
                if 'login.weibo' in redirect_url or 'login.sina' in redirect_url:
                    self.logger.warning('Updating Cookies!')
                elif 'weibo.cn/security' in redirect_url:
                    self.logger.warning('Now Cookies' + json.dumps(request.cookies))
                    self.logger.warning('Updating Cookies')
                request.cookies = self._get_random_cookies()
                return request
            except Exception:
                raise IgnoreRequest
        elif response.status in [418]:
            return request
        else:
            return response

class UAMiddleware(object):

    def __init__(self):
        self.UA = UserAgent()

    def process_request(self, request, spider):
        if self.UA:
            request.headers['User-Agent'] = self.UA.random
        return None

class ProxyMiddleware(object):

    def __init__(self):
        self.url = 'http://127.0.0.1:5000/random'
        self.no_proxy_time = datetime.now()
        self.recover_interval = 1
        self.timing = 3


    # def process_exception(self, request, exception, spider):
    def process_request(self, request, spider):
        if datetime.now() > (self.no_proxy_time+timedelta(minutes=self.recover_interval)):
            if datetime.now() > (self.no_proxy_time+timedelta(minutes=self.timing)):
                self.no_proxy_time = datetime.now()
            proxy = requests.get(url=self.url).text
            if proxy:
                request.meta['proxy'] = 'http://' + proxy
            return None