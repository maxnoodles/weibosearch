# 微博搜索关键字的爬虫
python3.6 + scrapy + scrapy-redis + request

使用了随机代理中间件，随机cookies中间件, 随机UA中间键

scrapy-redis分布式爬取

weibo封IP,返回418(一个茶壶)，不过解封比较快，代理中间件中会先用本地IP爬1分钟(本地很快),然后用网上抓取免费代理(较慢)爬2分钟再切回来。

吐槽，微博搜索关键字开放数据太少了,不管是weibo.cn，还是weibo.com, 还是m.weibo.cn
