# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 定义要获取的信息名称对象
# 新房
class NewHouseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 省份
    procince = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 几居
    room = scrapy.Field()
    # 面积
    area = scrapy.Field()
    #地区
    district = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 销售状态
    sale = scrapy.Field()
    # 价格
    price = scrapy.Field()
    # 房子详情链接
    origin_url = scrapy.Field()
    # 小区的名字
    name = scrapy.Field()


# 二手房
class ESFHouseItem(scrapy.Item):

    # 省份
    procince = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 几室几厅
    room = scrapy.Field()
    # 建筑面积
    area = scrapy.Field()
    # 层
    floor = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 单价
    unit = scrapy.Field()
    # 总价
    price = scrapy.Field()
    # 年代
    year = scrapy.Field()
    # 小区的名字
    name = scrapy.Field()
    # 朝向
    toward = scrapy.Field()
    # 房子详情链接
    origin_url = scrapy.Field()