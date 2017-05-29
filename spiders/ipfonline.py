import scrapy
import re
import math

class Ipfonlineitem(scrapy.Item):
    Comp_Name = scrapy.Field()
    Products = scrapy.Field()
    Phone = scrapy.Field()
    Landing_Url = scrapy.Field()
    Product_Image_url = scrapy.Field()
    Product_Profile = scrapy.Field()

class IpfonlineSpider (scrapy.Spider):
    name = "ipfonline_spider"
    allowed_domains = ['http://www.ipfonline.com']
    start_urls = ['http://www.ipfonline.com/categories']

    def parse(self, response):
        href_links = response.xpath('//div[@class="panel-body"]//a/@href').extract()

        for href in href_links:
            yield scrapy.Request(url=href, dont_filter=True, callback=self._parse_links)

    def _parse_links(self, response):

        total_products = re.search('Found (.*?) products,', response.xpath('//div[@class="sections"][2]//h6/text()').extract()[0], re.DOTALL).group(1)
        for index in range(0, int(math.ceil(int(total_products)/9))):
            if((index*9) >= int(total_products)):
                yield scrapy.Request(url=response.url + '/' + total_products, dont_filter=True, callback=self._parse_product_links)
            else:
                yield scrapy.Request(url=response.url + '/' + str(index*9), dont_filter=True, callback=self._parse_product_links)

    def _parse_product_links(self, response):
        href_links = response.xpath('//div[@class="blogposttwo"]//strong//a[@class="searchclick"]/@href').extract()

        for href in href_links:
            yield scrapy.Request(url=href, dont_filter=True, callback=self._parse_data)

    def _parse_data(self, response):
        item = Ipfonlineitem()
        full_url = response.url

        item['Comp_Name'] = response.xpath('//div[@class="sections"]//strong/text()').extract()[0]
        item['Products'] = response.xpath('//div[@class="blogposttwo"]//ul//li//a/text()').extract()[3]
        item['Phone'] = response.xpath('//li[@id="phonenumber"]/text()').extract()[0].replace('\r\n', '').replace('\t', '')
        item['Product_Image_url'] = response.xpath('//div[@class="sections"][2]//img/@src').extract()
        item['Product_Profile'] = response.xpath('//div[@id="myModalProfile"]//div[@class="modal-body"]/p/node()[normalize-space()]').extract()[0]

        item['Landing_Url'] = response.url
        yield item