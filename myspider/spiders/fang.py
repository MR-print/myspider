import scrapy,re
from myspider.items import NewHouseItem,ESFHouseItem
from scrapy_redis.spiders import RedisSpider

class FangSpider(scrapy.Spider):
    name = 'fang' # 爬虫名字
    allowed_domains = ['fang.com'] # 爬取范围
    # 开始爬取的网址url
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    # 获取新房与为二手房的所有房源链接
    def parse(self,response):
        trs = response.xpath("//div[@class='outCont']//tr")
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            procince_td = tds[0]
            procince_text = procince_td.xpath(".//text()").get()
            procince_text = re.sub(r"\s", "", procince_text)
            if procince_text:
                procince = procince_text
            # 海外除外
            if procince == "其它":
                continue
            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                # print('===================')
                # print('省份:',procince)
                # print('城市:',city)
                # print('城市链接:', city_url)
                #构建新房链接
                url_module = city_url.split("//")
                scheme = url_module[0]
                domain = url_module[1]
                # 北京特例,需要验证
                if "bj." in domain:
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/'
                else:
                    newhouse_url = scheme +"//" +"newhouse." + domain + "house/s/"
                    # 构建二手房链接
                    esf_url = scheme + "//" + "esf." + domain
                # print('新房链接:', newhouse_url)
                # print('二手房链接:', esf_url)

                #解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
                yield scrapy.Request(url=newhouse_url,callback=self.parse_newhouse, meta={"info":(procince, city)})
                yield scrapy.Request(url=esf_url,callback=self.parse_esf, meta={"info":(procince, city)})
            #
            #     break
            # break

    # 获取新房信息
    def parse_newhouse(self, response):
        procince, city = response.meta.get('info')
        # 获取小区信息
        # contains:用于包含标签
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name:
                name = name.strip()
            house_type_list = li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            #去除空白字符
            house_type_list = list(map(lambda x:re.sub(r"\s","", x), house_type_list))
            # 过滤函数：filter（）
            # 几居
            room = list(filter(lambda x:x.endswith("居"),house_type_list))
            # 面积
            area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub("\s|-|/","",area)
            # 地区
            address = li.xpath(".//div[@class='address']/a/@title").get()
            district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
            district = re.search(r".*\[(.+)\].*", district_text)
            if district:
                district = district.group(1)
            #print(district)
            #销售状态
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            #print(sale)
            # 价格
            price= ''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "",price)
            #print(price)
            # 房子详情链接
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            #print(origin_url)

            item = NewHouseItem(name=name, procince = procince, city= city,room= room, sale=sale,price=price,address=address,district=district
                                ,origin_url= origin_url)
            yield item
        # 下一页地址
        next_url = response.xpath("//div[@class='page']//a[@class='next']//@href").get()
        if next_url:
            # 解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
            yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_newhouse,
                              meta={'info':(procince,city)})

    # 获取二手房信息
    def parse_esf(self, response):
        procince, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item = ESFHouseItem(procince=procince,city=city)
            # 小区名字
            name = dl.xpath(".//p[@class='add_shop']/a/text()").get()
            if name:
                item['name'] = name.strip()
            #print(name)
            # 房屋信息
            infors = dl.xpath(".//p[@class='tel_shop']/text()").getall()
            infors = list(map(lambda x:re.sub(r"\s","",x),infors))
            #print(infors)
            for infor in infors:
                if '厅' in infor:
                    item['room'] = infor
                elif '层' in infor:
                    item['floor'] = infor
                elif '向' in infor:
                    item['toward'] = infor
                elif '㎡' in infor:
                    item['area'] = infor
                else:
                    if infor:
                        item['year'] = infor.replace('建','')
            # 地址
            address = dl.xpath(".//p[@class='add_shop']/span/text()").get()
            item['address'] = address
            # 总价
            item['price'] = ''.join(dl.xpath(".//dd[@class='price_right']/span[1]//text()").getall()).replace('\r\n','').replace(' ','')
            #单价
            item['unit'] = ''.join(dl.xpath(".//dd[@class='price_right']/span[2]//text()").getall()).replace('\r\n','').replace(' ','')
            # 房子链接
            detail_url = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
            if detail_url:
                item['origin_url'] = response.urljoin(detail_url)
            #print(item)
            yield item
        # 解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
        next_url = response.xpath("//div[@class='page_al']/p[1]/a/@href").get()
        yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf,
                             meta={'info':(procince,city)})





