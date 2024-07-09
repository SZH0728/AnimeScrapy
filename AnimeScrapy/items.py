# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class DetailItem(Item):
    name = Field()  # 番剧名称
    translation = Field()  # 译名
    alias = Field()  # 别名
    season = Field()  # 季度
    time = Field()  # 时间
    tag = Field()  # 标签
    director = Field()  # 导演
    cast = Field()  # 演员
    description = Field()  # 简介
    web = Field()  # 来源网站
    webId = Field()  # 来源网站ID
    picture = Field()  # 封面图片网址


class ScoreItem(Item):
    name = Field()
    score = Field()
    vote = Field()
    source = Field()


class PictureItem(Item):
    name = Field()
    picture = Field()
