# GithubSpider
-一个简单的Scrapy爬虫

##一些小注意点
1.  使用数组形式标示xpath的时候，xpath中的表达式数组下标从1开始，如第一个a元素应该是a[1]
2.  yield 到 parser 中的 item 在调用这个yield 的方法中似乎无法同步（不知道这么标示正不正确，类似赋值传递？python不熟悉。。）
3.  对于数组类型的item，在给它添加元素之前需要先定义成数组形式 ，类似item['list'] = []
4.  使用scrapy 大量扒取数据可能发生429 错误，解决方法如下（抄袭）：
  在middleware.py 中添加类：
    class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429:
            self.crawler.engine.pause()
            time.sleep(60) # If the rate limit is renewed in a minute, put 60 seconds, and so on.
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response
      在settings.py中激活：
        DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'GithubSpider.middlewares.TooManyRequestsRetryMiddleware': 543,
      }
    解决
