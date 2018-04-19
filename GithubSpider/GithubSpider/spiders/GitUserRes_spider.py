import scrapy
from scrapy.selector import Selector
from GithubSpider.items import UserItem
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
import re

host = "https://github.com"

class UserResSpider(scrapy.Spider):
    name = "GitUserRes"
    allowed_domains = ['github.com']
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Content-Type":" application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }
    start_urls = ["https://github.com/Linwenye"]
    # rules = (
    #     Rule(SgmlLinkExtractor(allow=(r'http://github\.com/^((?!\?$).)*$\?tab=following'))),
    # )

    def parse(self, response):
        filename = response.url
        sel = Selector(response)
        item = UserItem()
        item['name'] = sel.xpath('//div/h1[@class="vcard-names"]/span[@class="p-nickname vcard-username d-block"]/text()').extract()
        # get repo address
        res =host+sel.xpath('//div/nav/a[.//text()[normalize-space(.)="Repositories"]]/@href').extract()[0]
        # print(res)
        yield scrapy.Request(res, meta={'item': item}, callback=self.repList_parse)
        # item['resposity'] = {'a':1,'b':2}

        # test = sel.xpath('http://github\.com/ .*[^\?]$\?tab=following').extract()
        # print(test)
        # print(item['name'])
        # print(len(item['resposity']))
        # print("test----------------------")
        # return item

    def repList_parse(self,response):
        item = response.meta['item']
        sel = Selector(response)
        repList = sel.xpath('//div[@id="user-repositories-list"]/ul/li/div/h3/a/@href')
        item['repository']=[]
        # print(len(repList))
        for i in repList:
            repAddr = host+i.extract()
            # item['repository'].append([repAddr,0])
            yield scrapy.Request(repAddr,meta={'item': item}, callback=self.getCommit_parse)

        # print("test")
        for i in item['repository']:
            print(i)

        #
        # return item

    def getCommit_parse(self,response):
        item = response.meta['item']
        sel = Selector(response)
        # last = len(item['repository'])-1
        commitNum = sel.xpath('//div/ul[@class="numbers-summary"]/li[@class="commits"]/a/span/text()').extract()
        # commitNum.strip()
        commitNum = re.sub(r'\s+','', str(commitNum))
        commitNum = "".join(commitNum.split("\\n"))
        # commitNum = re.sub(r'\n', '', str(commitNum))
        url = sel.xpath('//head/link[@rel="canonical"]/@href').extract()
        # print(str(url)+commitNum)
        item['repository'].append([url,commitNum])

        return item

    def parse_2(self,response):
        filename = response.url
        sel = Selector(response)
        item = UserItem()
        item['name'] = sel.xpath(
            '//div/a[@class="d-inline-block no-underline mb-1"]/span[@class="f4 link-gray-dark"]/text()').extract()
        item['resposity'] = {'a': 1, 'b': 2}
        print("test following-----------------")
        print(item['name'])
        print(len(item['resposity']))
        print("test----------------------")
        # with open(filename, 'wb') as f:
        #     f.write(response.body)