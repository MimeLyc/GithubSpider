import scrapy
from scrapy.selector import Selector
from GithubSpider.items import UserItem
from GithubSpider.items import RepItem
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
import re

host = "https://github.com"

class UserResSpider(scrapy.Spider):
    #the Name of the Spider,input " python -m  scrapy crawl GitUserRes "in the root of the pro
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
        uItem = UserItem()
        uItem['name'] = sel.xpath('//div/h1[@class="vcard-names"]/span[@class="p-nickname vcard-username d-block"]/text()').extract()
        # get repo address
        res =host+sel.xpath('//div/nav/a[.//text()[normalize-space(.)="Repositories"]]/@href').extract()[0]
        # print(res)
        yield scrapy.Request(res, meta={'uItem': uItem}, callback=self.repList_parse)
        # item['resposity'] = {'a':1,'b':2}

        # test = sel.xpath('http://github\.com/ .*[^\?]$\?tab=following').extract()
        # print(test)
        # print(item['name'])
        # print(len(item['resposity']))
        # print("test----------------------")
        # return item

    def repList_parse(self,response):
        uItem = response.meta['uItem']
        sel = Selector(response)
        repList = sel.xpath('//div[@id="user-repositories-list"]/ul/li/div/h3/a/@href')
        uItem['repository']=[]
        # print(len(repList))
        for i in repList:
            rItem = RepItem();
            repAddr = host+i.extract()
            rItem['name'] = i.extract()
            rItem['addr'] = repAddr
            # item['repository'].append([repAddr,0])
            yield scrapy.Request(repAddr,meta={'uItem': uItem,'rItem':rItem}, callback=self.getCommit_parse)

        # print("test")
        for i in uItem['repository']:
            print(i['name']+i['commitNum'])

        #
        # return item

    def getCommit_parse(self,response):
        uItem = response.meta['uItem']
        rItem = response.meta['rItem']
        sel = Selector(response)
        # rItem = RepItem();
        # last = len(item['repository'])-1
        commitNum = sel.xpath('//div/ul[@class="numbers-summary"]/li[@class="commits"]/a/span/text()').extract()
        # commitNum.strip()
        commitNum = re.sub(r'\s+','', str(commitNum))
        commitNum = "".join(commitNum.split("\\n"))
        rItem['commitNum'] = commitNum
        # commitNum = re.sub(r'\n', '', str(commitNum))
        # url = sel.xpath('//head/link[@rel="canonical"]/@href').extract()
        # print(str(url)+commitNum)
        uItem['repository'].append([rItem['name'],rItem])

        return uItem



    #
    # def parse_2(self,response):
    #     filename = response.url
    #     sel = Selector(response)
    #     item = UserItem()
    #     item['name'] = sel.xpath(
    #         '//div/a[@class="d-inline-block no-underline mb-1"]/span[@class="f4 link-gray-dark"]/text()').extract()
    #     item['resposity'] = {'a': 1, 'b': 2}
    #     print("test following-----------------")
    #     print(item['name'])
    #     print(len(item['resposity']))
    #     print("test----------------------")
    #     # with open(filename, 'wb') as f:
    #     #     f.write(response.body)