# -*- coding: utf-8 -*-
from scrapy import Spider, FormRequest, Request
import re
from weibosearch.items import WeibosearchItem

class WeiboSpider(Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog'
    max_page = 200
    keywords = ['000001']

    def start_requests(self):
        """
        使用关键字搜索，post提交
        :return:
        """
        for keyword in self.keywords:
            url = '{url}?keyword={keyword}'.format(url=self.search_url, keyword=keyword)
            for page in range(self.max_page+1):
                data = {
                    'mp':str(100),
                    'page':str(self.max_page)
                }

                yield FormRequest(url=url, formdata=data, callback=self.parse_index)


    def parse_index(self, response):
        """
        提取评论链接（详情页）
        :param response:
        :return:
        """
        weibos = response.xpath('//div[@class="c" and contains(@id, "M_")]')
        for weibo in weibos:
            is_forward = bool(weibo.xpath('.//span[@class="cmt"]').get())
            if is_forward:
                detail_url = weibo.xpath('.//a[contains(., "原文评论[")]//@href').get()
            else:
                detail_url = weibo.xpath('.//a[contains(., "评论[")]/@href').get()
                # print(detail_url)
            yield Request(url=detail_url, callback=self.parse_detail)

    def parse_detail(self, response):
        """
        提取详情页信息
        :return:
        """
        id = re.search('comment/(.*?)\?' ,response.url).group(1)
        url = response.url
        content = ''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').get())
        like_count = response.xpath('//a[contains(., "赞[")]//text()').re_first('赞\[(.*?)\]')
        forward_count = response.xpath('//a[contains(., "转发[")]//text()').re_first('转发\[(.*?)\]')
        comment_count = response.xpath('//span[contains(., "评论[")]//text()').re_first('评论\[(.*?)\]')
        date = response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').get(default=None)
        user = response.xpath('//div[@id="M_"]/div[1]/a/text()').get()

        # print(id, user, content, data, like_count, forward_count, comment_count)
        item = WeibosearchItem()
        for field in item.fields:
            try:
                item[field] = eval(field)
            except NameError:
                self.logger.debug('Field is not Defined: ' + field)
        yield item


