import scrapy
from scrapy.selector import Selector
from GithubSpider.items import UserItem
from GithubSpider.items import RepItem
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
import re
import time

host = "https://github.com"
date = "Apr 1,2018"
dateF = time.strptime(date, "%b %d,%Y")
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
    start_urls = ["https://github.com/snicoll"]


    # rules = (
    #     Rule(SgmlLinkExtractor(allow=(r'http://github\.com/^((?!\?$).)*$\?tab=following'))),
    # )

    def parse(self, response):
        filename = response.url
        sel = Selector(response)
        uItem = UserItem()

        uItem['name'] = sel.xpath('//div/h1[@class="vcard-names"]/span[@class="p-nickname vcard-username d-block"]/text()').extract()
        uItem['repository'] = []
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

    # get Repository list
    def repList_parse(self,response):
        uItem = response.meta['uItem']
        sel = Selector(response)
        repList = sel.xpath('//div[@id="user-repositories-list"]/ul/li/div/h3/a/@href')

        # print(len(repList))
        for i in repList:
            rItem = RepItem();
            repAddr = host+i.extract()
            rItem['name'] = i.extract()
            rItem['addr'] = repAddr
            # item['repository'].append([repAddr,0])
            # TODO
            yield scrapy.Request(repAddr,meta={'uItem': uItem, 'rItem': rItem}, callback=self.getCommit_parse)
        # div[@class="container-lg clearfix px-3 mt-4"]/div[@class="position-relative"]/
        pageList = sel.xpath('//div[@id="user-repositories-list"]/div[@class="paginate-container"]/'
                             'div[@class="pagination"]/a[@class="next_page"]/@href').extract()
        # print(str(len(pageList))+"get!!!--")
        if len(pageList) != 0:
            nextPageUrl = host + pageList[0]
            print(nextPageUrl + "????test")
            yield scrapy.Request(str(nextPageUrl) , meta={'uItem': uItem}, callback=self.repList_parse)


        # print("test")
        # for i in uItem['repository']:
        #     print(i['name']+i['commitNum'])

        #
        # return item

    def getCommit_parse(self, response):
        # print("hello~~~~~~~~~~~~~~~~~~~~~~~")
        uItem = response.meta['uItem']
        rItem = response.meta['rItem']
        sel = Selector(response)
        # rItem = RepItem();
        # last = len(item['repository'])-1
        commitNum = sel.xpath('//div/ul[@class="numbers-summary"]/li[@class="commits"]/a/span/text()').extract()
        commitPage = host+sel.xpath('//div/ul[@class="numbers-summary"]/li[@class="commits"]/a/@href').extract()[0]
        # commitNum.strip()
        commitNum = re.sub(r'\s+', '', str(commitNum))
        commitNum = "".join(commitNum.split("\\n"))
        rItem['commitNum'] = commitNum
        rItem['cmmtNum2Date'] = 0
        rItem['cmmtNumFDate'] = 0
        rItem['limitDate'] = date
        # commitNum = re.sub(r'\n', '', str(commitNum))
        # url = sel.xpath('//head/link[@rel="canonical"]/@href').extract()
        # print(str(url)+commitNum)

        # print(commitPage+"--------------------------------------------test1")
        yield scrapy.Request(commitPage, meta={ 'rItem': rItem}, callback=self.getCmmt2Date_parse)
        # print(str(rItem['name']) + str(rItem['cmmtNum2Date']) + "test------=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        uItem['repository'].append([rItem['name'], rItem])

        # rItem['cmmtNum2Date'] = rItem['commitNum'] - rItem['cmmtNumFDate']
        # return uItem

    def getCmmt2Date_parse(self,response):
        # uItem = response.meta['uItem']
        rItem = response.meta['rItem']
        sel = Selector(response)

        # commit Num before date
        cmmtNum = 0

        dateList = sel.xpath('//div[@class="commits-listing commits-listing-padded js-navigation-container js-active-navigation-container"]/div[@class="commit-group-title"]/text()').extract()
        # print(str(len(dateList))+"________________"+ rItem['name'])
        for i in range(len(dateList)):
            if i % 2 is 0:
                continue
            # print(str(dateList[i])+"_______________________")
            strList = dateList[i].split(" ")
            # print(str(len(strList))+"test=============")
            tempDate = strList[2]+" " + strList[3]+strList[4].split('\n')[0]
            # print(dateList[i] + "-------=-=-=-=-=-=-test")
            tempDateF = time.strptime(tempDate,"%b %d,%Y")
            if int(time.mktime(tempDateF)) - int(time.mktime(dateF)) < 0:
                # print( "________________" + rItem['name'])
                # the index of array in the xpath is begin from 1.not 0
                cmmtList = sel.xpath('//div[@class="commits-listing commits-listing-padded js-navigation-container js-active-navigation-container"]/ol[' + str(i//2+1) + ']/li').extract()

                # cmmtList = cmmtList.xpath('>li').extract()
                # print(cmmtList+"??????????")
                print(str( len(cmmtList))+"________________" + rItem['name'])
                cmmtNum += len(cmmtList)
            # if cmmtNum is 0:
            #     return



        rItem['cmmtNum2Date'] += cmmtNum

        print(str(rItem['name']) +"   "+ str(rItem['cmmtNum2Date']) + "   test------=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        hasOlder = sel.xpath('//div[@class="paginate-container"]/div[@class="pagination"]/a/text()').extract()
        # if len(hasOlder) is 1:
        #     print(hasOlder[0]+"!!!!!!!@#$!@#")
        if len(hasOlder) is 1 and str(hasOlder[0]) == 'Older':
            # print("get!---------------------------------------------11")
            olderPage = sel.xpath('//div[@class="paginate-container"]/div[@class="pagination"]/a/@href').extract()[0]
            yield scrapy.Request(olderPage, meta={ 'rItem': rItem}, callback=self.getCmmt2Date_parse,dont_filter=True)
        elif len(hasOlder) is 2 and str(hasOlder[1]) == 'Older':
            # print("get!=------------------22")
            #
            olderPage = sel.xpath('//div[@class="paginate-container"]/div[@class="pagination"]/a/@href').extract()[1]
            yield scrapy.Request(olderPage, meta={ 'rItem': rItem}, callback=self.getCmmt2Date_parse,dont_filter=True)
        # return
            # print(tempDate+"------------------------------------------test")

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