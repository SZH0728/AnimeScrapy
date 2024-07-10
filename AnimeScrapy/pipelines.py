# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from abc import ABC, abstractmethod
from os.path import join, dirname, abspath, normpath
from logging import getLogger

from itemadapter import ItemAdapter
from scrapy import Spider, Item
from scrapy.exceptions import DropItem
from sqlalchemy.orm import scoped_session

from AnimeScrapy.items import DetailItem, ScoreItem, PictureItem
from dbmanager import Session, NameID, Detail, Web, Score

logger = getLogger(__name__)


class DataBasePipeline(ABC):
    def __init__(self):
        self.session: scoped_session[Session] | None = None

    def open_spider(self, spider: Spider):
        """Spider开启时打开数据库会话"""
        self.session = Session()

    def close_spider(self, spider: Spider):
        """Spider关闭时提交事务并关闭会话"""
        self.session.commit()
        self.session.close()

    @abstractmethod
    def process_item(self, item: Item, spider: Spider):
        """处理item的抽象方法"""
        return item


class DetailItemPipeline(DataBasePipeline):
    def process_item(self, item: Item, spider: Spider):
        """处理DetailItem，保存到数据库"""
        if isinstance(item, DetailItem):
            adapter = ItemAdapter(item)

            for i in (adapter.get('name'), adapter.get('translation'), *adapter.get('alias')):
                anime_id = self.session.query(NameID).filter(NameID.name == i).first()
                if anime_id:
                    anime_id = anime_id.id
                    break

            if anime_id:
                detail_object = self.session.query(Detail).filter(Detail.id == anime_id).first()
            else:
                detail_object = Detail()

            detail_object.name = adapter.get('name')
            detail_object.translation = adapter.get('translation')
            detail_object.alias = adapter.get('alias')
            detail_object.season = adapter.get('season')
            detail_object.time = adapter.get('time')
            detail_object.tag = adapter.get('tag')
            detail_object.director = adapter.get('director')
            detail_object.cast = adapter.get('cast')
            detail_object.description = adapter.get('description')
            detail_object.webId = adapter.get('webId')
            detail_object.picture = adapter.get('picture')

            web = adapter.get('web')
            web = self.session.query(Web).filter(Web.host == web).first()
            if web:
                detail_object.web = web.id
            else:
                detail_object.web = None

            if not anime_id:
                try:
                    self.session.add(detail_object)
                    self.session.flush()
                except Exception as e:
                    self.session.rollback()
                    raise DropItem(f'An error occurred when saving {detail_object} to database: {e}')
                anime_id = detail_object.id

            for i in (adapter.get('name'), adapter.get('translation'), *adapter.get('alias')):
                if not i:
                    continue
                if self.session.query(NameID).filter(NameID.name == i).first():
                    continue
                name_object = NameID()
                name_object.id = anime_id
                name_object.name = i
                try:
                    self.session.add(name_object)
                except Exception as e:
                    self.session.rollback()
                    raise DropItem(f'An error occurred when saving {name_object} to database: {e}')

            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                raise DropItem(f'An error occurred when saving data to database: {e}')

        return item


class ScoreItemPipeline(DataBasePipeline):
    def process_item(self, item: Item, spider: Spider):
        """处理ScoreItem，保存到数据库"""
        if isinstance(item, ScoreItem):
            adapter = ItemAdapter(item)
            anime_id = self.session.query(NameID).filter(NameID.name == adapter.get('name')).first()

            if anime_id:
                anime_id = anime_id.id
            else:
                detail_object = Detail()
                detail_object.name = adapter.get('name')
                try:
                    self.session.add(detail_object)
                    self.session.flush()
                except Exception as e:
                    self.session.rollback()
                    raise DropItem(f'An error occurred when saving {detail_object} to database: {e}')
                anime_id = detail_object.id

                name_object = NameID()
                name_object.id = anime_id
                name_object.name = adapter.get('name')
                try:
                    self.session.add(name_object)
                except Exception as e:
                    self.session.rollback()
                    raise DropItem(f'An error occurred when saving {name_object} to database: {e}')

            score_object: Score | None = self.session.query(Score).filter(
                Score.detailId == anime_id,
                Score.date == adapter.get('date')
            ).first()

            if not score_object:
                score_object = Score()
                score_object.detailId = anime_id
                score_object.date = adapter.get('date')
                score_object.detailScore = {}

            web = self.session.query(Web).filter(Web.host == adapter.get('source')).first()
            if web:
                score_object.detailScore[str(web.id)] = {
                    'score': adapter.get('score'),
                    'vote': adapter.get('vote')
                }
            else:
                score_object.detailScore[adapter.get('web')] = {
                    'score': adapter.get('score'),
                    'vote': adapter.get('vote')
                }

            if web:
                if web.name == 'Anikore':
                    score_object.detailScore['2']['score'] *= 2

            score_sum = 0.0
            score_object.vote = 0
            for i in score_object.detailScore:
                score_sum += score_object.detailScore[i]['score'] * score_object.detailScore[i]['vote']
                score_object.vote += score_object.detailScore[i]['vote']
            try:
                score_object.score = round(score_sum / score_object.vote, 1)
            except ZeroDivisionError:
                score_object.score = 0.0
            self.session.add(score_object)

            try:

                self.session.commit()
            except Exception as e:
                self.session.rollback()
                raise DropItem(f'An error occurred when saving data to database: {e}')

        return item


class PictureItemPipeline(DataBasePipeline):
    def __init__(self):
        super().__init__()
        current_dir = dirname(abspath(__file__))
        parent_dir = normpath(join(current_dir, '..'))
        self.save_path = join(parent_dir, 'cover')

    def process_item(self, item: Item, spider: Spider):
        """处理PictureItem，保存图片到本地"""
        if isinstance(item, PictureItem):
            adapter = ItemAdapter(item)
            anime_id = self.session.query(NameID).filter(NameID.name == adapter.get('name')).first().id
            with open(join(self.save_path, f'{anime_id}.jpg'), 'wb') as f:
                f.write(adapter.get('picture'))

        return item
