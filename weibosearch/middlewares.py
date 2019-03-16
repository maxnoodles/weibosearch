# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import json
import logging

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