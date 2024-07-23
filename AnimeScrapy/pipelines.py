# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import date
from logging import getLogger
from os.path import join, dirname, abspath, normpath
from typing import Iterable

from itemadapter import ItemAdapter
from scrapy import Spider, Item
from scrapy.exceptions import DropItem
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session

from AnimeScrapy.items import DetailItem, ScoreItem, PictureItem
from dbmanager import Session, NameID, Detail, Web, Score, Cache

logger = getLogger(__name__)


class ScoreItemOperationMixIn(object):
    @staticmethod
    def update_score_and_vote(score: Score):
        """
        更新分数和投票总数，并计算平均分。

        :param score: Score对象，包含detailScore属性，用于存储每个来源的评分和投票数。
        """
        detail_score: dict = score.detailScore

        # 初始化总投票数和总分数
        score_sum = 0.0
        vote_sum = 0

        # 遍历detail_score计算总投票数和总分数
        for i in detail_score.values():
            if float(i['score']) == 0.0:
                continue
            vote_sum += i['vote']
            score_sum += i['vote'] * float(i['score'])

        # 计算平均分，避免除以零错误
        average_score = round(score_sum / vote_sum, 1) if vote_sum else 0.0

        # 更新Score对象的score和vote属性
        score.score = average_score
        score.vote = vote_sum

    def update_detail_score(self, score_object: Score, score: float, vote: int, web: Web):
        """
        更新特定来源的评分详情，并重新计算平均分。

        :param score_object: Score对象，包含detailScore属性。
        :param score: 新的评分值。
        :param vote: 新的投票数。
        :param web: Web对象，包含name和id属性，标识评分来源。
        """
        # 深拷贝detailScore使sqlalchemy识别数据变化并正确更新数据
        detail_score: dict = deepcopy(score_object.detailScore)

        # 如果评分来源为'Anikore'，则将评分值翻倍
        if web.name == 'Anikore':
            score *= 2

        # 更新或添加评分详情
        detail_score[web.id] = {
            'score': float(score),
            'vote': vote,
        }

        # 将更新后的评分详情赋给Score对象
        score_object.detailScore = detail_score

        # 调用静态方法更新平均分和投票总数
        self.update_score_and_vote(score_object)


class DataBasePipeline(ABC):
    def __init__(self, target):
        """
        初始化数据库管道。

        :param target: 数据库操作的目标模型类。
        """
        self.target = target
        self.session: scoped_session[Session] | None = None

    def open_spider(self, spider: Spider):
        """
        当Spider启动时，创建一个新的数据库会话。

        :param spider: 正在运行的Spider实例。
        """
        self.session = Session()

    def close_spider(self, spider: Spider):
        """
        当Spider停止时，提交所有未完成的事务并关闭会话。

        :param spider: 正在运行的Spider实例。
        """
        self.session.commit()
        self.session.close()

    def process_item(self, item: Item, spider: Spider):
        """
        处理特定类型的Item，实现具体的数据处理逻辑。

        :param item: 需要处理的Item实例。
        :param spider: 正在运行的Spider实例。
        :return: 处理后的Item实例。
        """
        if isinstance(item, self.target):
            with self.session.no_autoflush:
                item = self.process(item, spider)

                try:
                    self.session.commit()
                except SQLAlchemyError as e:
                    self.session.rollback()
                    raise DropItem(f'An error occurred while committing the transaction: {e}')

        return item

    @abstractmethod
    def process(self, item: Item, spider: Spider) -> Item:
        """
        处理特定类型的Item，实现具体的数据处理逻辑。

        :param item: 需要处理的Item实例。
        :param spider: 正在运行的Spider实例。
        :return: 处理后的Item实例。
        """
        return item

    def select_web_by_link(self, link: str) -> Web:
        """
        根据链接查询Web实体。

        :param link: 需要查询的Web链接。
        :return: 查询到的Web实体，如果没有找到，则抛出DropItem异常。
        """
        web = self.session.query(Web).filter_by(host=link).first()
        if web:
            # noinspection PyTypeChecker
            return web
        else:
            raise DropItem(f'{link} is not a valid web link')

    def select_web_by_id(self, id_: int) -> Web:
        """
        根据ID查询Web实体。

        :param id_: 需要查询的Web ID。
        :return: 查询到的Web实体，如果没有找到，则抛出DropItem异常。
        """
        web = self.session.query(Web).filter_by(id=id_).first()
        if web:
            return web
        else:
            raise DropItem(f'Web with id {id_} does not exist')


class DetailItemPipeline(DataBasePipeline, ScoreItemOperationMixIn):
    def __init__(self):
        """初始化DetailItemPipeline，设置目标模型为DetailItem。"""
        super().__init__(DetailItem)

    def process(self, item: Item, spider: Spider):
        """
        处理DetailItem，根据名称列表收集信息，创建或更新Detail对象，处理缓存数据。

        :param item: 需要处理的DetailItem实例。
        :param spider: 正在运行的Spider实例。
        :return: 处理后的DetailItem实例。
        """
        # 使用ItemAdapter包装item，便于数据访问
        adapter = ItemAdapter(item)

        # 收集名称列表，去除空值
        name_list = self.collect_name(adapter)
        name_list = [i for i in name_list if i]

        # 根据名称列表查询数据库中的ID
        # noinspection PyTypeChecker
        name_id = self.select_name_id_in_list(name_list)

        # 如果没有找到对应的ID
        if len(name_id) == 0:
            # 创建新的Detail对象并获取其ID
            detail_object = self.create_detail_object(adapter)
            anime_id = detail_object.id

            # 将名称与新创建的Detail ID关联
            self.add_names_to_name_id(name_list, anime_id)

        # 如果只找到一个ID
        elif len(name_id) == 1:
            # 获取唯一ID并查询对应的Detail对象
            anime_id = name_id.pop()
            detail_object = self.select_detail_object_by_id(anime_id)

            # 检查当前网站数据是否比之前的网站优先级高
            cur_web = self.select_web_by_link(adapter.get('web'))
            pre_web = self.select_web_by_id(detail_object.web)
            if cur_web.priority < pre_web.priority:
                self.update_detail_object(detail_object, adapter)

            # 将名称与已存在的Detail ID关联
            self.add_names_to_name_id(name_list, anime_id)

            # 更新别名
            self.update_alias(detail_object, name_list)

        # 如果发现多个ID对应同一组名称，抛出异常
        else:
            raise DropItem(f'The names {name_list} map to more than one ID: {name_id}')

        # 查询所有与名称相关的缓存数据
        cache_list = self.select_all_cache_by_name(name_list)

        # 遍历缓存列表，根据缓存数据创建Score对象并更新数据库
        for i in cache_list:
            self.transform_cache_object(i, anime_id)

        # 清除已处理的缓存数据
        self.clear_cache(cache_list)
        return item

    @staticmethod
    def collect_name(adapter: ItemAdapter) -> tuple[str, ...]:
        """
        收集DetailItem中的名称信息。

        :param adapter: 包含名称信息的ItemAdapter实例。
        :return: 名称元组。
        """
        if adapter.get('alias'):
            return adapter.get('name'), adapter.get('translation'), *adapter.get('alias')
        else:
            return adapter.get('name'), adapter.get('translation')

    def select_name_id_in_list(self, name_list: tuple[str]) -> set[int]:
        """
        根据名称列表查询对应的anime_id集合。

        :param name_list: 需要查询的名称列表。
        :return: 查询到的anime_id集合。
        """
        # noinspection PyUnresolvedReferences
        anime_id_object = self.session.query(NameID).filter(NameID.name.in_(name_list)).all()
        return {i.id for i in anime_id_object}

    def select_detail_object_by_id(self, id_: int) -> Detail:
        """
        根据id查询Detail对象。

        :param id_: 需要查询的id。
        :return: 查询到的Detail对象。
        """
        detail_object = self.session.query(Detail).filter_by(id=id_).first()
        if detail_object:
            # noinspection PyTypeChecker
            return detail_object
        else:
            raise ValueError(f'{id_} is not a valid anime id')

    def select_all_cache_by_name(self, name_list: Iterable[str | NameID]) -> list[Cache]:
        """
        根据名称列表查询所有相关联的Cache对象。

        :param name_list: 需要查询的名称列表。
        :return: 查询到的Cache对象列表。
        """
        name_list = [i if isinstance(i, str) else i.name for i in name_list]
        # noinspection PyUnresolvedReferences,PyTypeChecker
        return self.session.query(Cache).filter(Cache.name.in_(name_list)).all()

    def create_detail_object(self, adapter: ItemAdapter) -> Detail:
        """
        创建Detail对象并保存到数据库。

        :param adapter: 包含Detail信息的ItemAdapter实例。
        :return: 创建的Detail对象。
        """
        detail_object = Detail()
        self.update_detail_object(detail_object, adapter)

        try:
            self.session.add(detail_object)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DropItem(f'An error occurred when saving {detail_object} to database: {e}')

        return detail_object

    def create_score_object_by_cache(self, cache: Cache, id_: int) -> Score:
        """
        根据缓存对象和Detail对象的id创建Score对象，并将其保存至数据库。

        :param cache: Cache对象，包含评分信息。
        :param id_: Detail对象的id，用于关联Score对象。
        :return: 创建的Score对象。
        """
        score_object = Score()

        score_object.detailId = id_
        score_object.date = cache.date

        score_object.detailScore = {
            str(cache.web): {
                'score': float(cache.score),
                'vote': cache.vote,
            }
        }

        self.update_score_and_vote(score_object)
        try:
            self.session.add(score_object)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f'An error occurred when saving {score_object} to database: {e}')
        return score_object

    def add_names_to_name_id(self, name_list: Iterable[str | NameID], id_: int) -> list[NameID]:
        """
        将名称列表与指定id关联并保存到数据库。

        :param name_list: 需要关联的名称列表。
        :param id_: 关联的目标id。
        :return: 成功关联的NameID对象列表。
        """
        name_list = set(name_list)
        name_id_list_object = [NameID(name=i, id=id_) if isinstance(i, str) else i for i in name_list]
        succeed_name_id_list = []

        try:
            self.session.add_all(name_id_list_object)
            self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f'An error occurred when saving {name_id_list_object} to database: {e}')
            self.session.rollback()
            for i in name_id_list_object:
                try:
                    self.session.merge(i)
                    self.session.commit()
                except SQLAlchemyError as e:
                    self.session.rollback()
                    logger.error(f'An error occurred when saving {i} to database: {e}')
                else:
                    succeed_name_id_list.append(i)
        else:
            succeed_name_id_list = name_id_list_object
        finally:
            return succeed_name_id_list

    def update_detail_object(self, detail_object: Detail, adapter: ItemAdapter):
        """
        更新Detail对象的信息。

        :param detail_object: 需要更新的Detail对象。
        :param adapter: 包含更新信息的ItemAdapter实例。
        """
        web = self.select_web_by_link(adapter.get('web'))

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
        detail_object.web = web.id

    @staticmethod
    def update_alias(detail_object: Detail, alias: Iterable[str | NameID]):
        """
        更新Detail对象的别名列表。

        :param detail_object: 需要更新的Detail对象。
        :param alias: 新的别名列表。
        """
        alias = [i if isinstance(i, str) else i.name for i in alias]
        pre_alias = deepcopy(detail_object.alias)
        pre_alias += alias
        detail_object.alias = list(set(pre_alias))

    def transform_cache_object(self, cache_object: Cache, id_: int) -> Score:
        """
        将Cache对象转换为Score对象，或更新已存在的Score对象。

        :param cache_object: 需要转换的Cache对象。
        :param id_: 目标Detail对象的id。
        :return: 转换或更新后的Score对象。
        """
        score_object = self.session.query(Score).filter(and_(
            Score.date == cache_object.date,
            Score.detailId == id_
        )).first()

        if score_object:
            web = self.session.query(Web).filter_by(id=cache_object.web).first()
            # noinspection PyTypeChecker
            self.update_detail_score(score_object, cache_object.score, cache_object.vote, web)
        else:
            score_object = self.create_score_object_by_cache(cache_object, id_)

        return score_object

    def clear_cache(self, cache_list: Iterable[Cache]):
        """
        清除给定的Cache对象列表。

        :param cache_list: 需要清除的Cache对象列表。
        """
        for i in cache_list:
            try:
                self.session.delete(i)
                self.session.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                logger.error(f'An error occurred when deleting {i} from database: {e}')


class ScoreItemPipeline(DataBasePipeline, ScoreItemOperationMixIn):
    def __init__(self):
        """初始化ScoreItemPipeline，设置目标模型为ScoreItem。"""
        super().__init__(ScoreItem)

    def process(self, item: Item, spider: Spider) -> Item:
        """
        处理ScoreItem，根据名称查找anime_id，然后根据anime_id和日期查找或创建Score对象，
        并更新其评分和投票详情。

        :param item: 需要处理的ScoreItem实例。
        :param spider: 正在运行的Spider实例。
        :return: 处理后的ScoreItem实例。
        """
        adapter = ItemAdapter(item)

        anime_id = self.select_id_by_name(adapter.get('name'))
        if anime_id:
            score_object: Score | None = self.select_score(anime_id, adapter.get('date'))

            if score_object:
                web = self.select_web_by_link(adapter.get('source'))
                self.update_detail_score(score_object, adapter.get('score'), adapter.get('vote'), web)

            else:
                self.create_score_object(adapter, anime_id)

        else:
            self.create_cache(adapter)

        return item

    def select_id_by_name(self, name: str) -> int | None:
        """
        根据名称查询NameID表获取id。

        :param name: 需要查询的名称。
        :return: 查询到的id，如果没有找到则返回None。
        """
        name_id_object: NameID | None = self.session.query(NameID).filter_by(name=name).first()
        return name_id_object.id if name_id_object else None

    def select_score(self, id_: int, date_: date) -> Score | None:
        """
        根据anime_id和日期查询Score表。

        :param id_: 需要查询的anime_id。
        :param date_: 需要查询的日期。
        :return: 查询到的Score对象，如果没有找到则返回None。
        """
        return self.session.query(Score).filter(and_(
            Score.detailId == id_,
            Score.date == date_
        )).first()

    def create_cache(self, adapter: ItemAdapter) -> Cache:
        """
        创建Cache对象并保存到数据库。

        :param adapter: 包含信息的ItemAdapter实例。
        :return: 创建的Cache对象。
        """
        cache_object = Cache()

        cache_object.name = adapter.get('name')
        cache_object.score = adapter.get('score')
        cache_object.vote = adapter.get('vote')
        cache_object.date = adapter.get('date')

        web = self.select_web_by_link(adapter.get('source'))
        cache_object.web = web.id

        self.session.add(cache_object)
        return cache_object

    def create_score_object(self, score_item: ItemAdapter, id_: int) -> Score:
        """
        创建Score对象，填充必要的信息，并更新评分和投票详情。

        :param score_item: 包含评分信息的ItemAdapter实例。
        :param id_: 需要关联的anime_id。
        :return: 创建的Score对象。
        """
        score_object = Score()

        score_object.detailId = id_
        score_object.date = score_item.get('date')

        web = self.select_web_by_link(score_item.get('source'))
        score_object.detailScore = {
            str(web.id): {
                'score': score_item.get('score'),
                'vote': score_item.get('vote')
            }
        }

        self.update_score_and_vote(score_object)
        self.session.add(score_object)
        return score_object


class PictureItemPipeline(DataBasePipeline):
    def __init__(self):
        super().__init__(PictureItem)
        current_dir = dirname(abspath(__file__))
        parent_dir = normpath(join(current_dir, '..'))
        self.save_path = join(parent_dir, 'cover')

    def process(self, item: Item, spider: Spider):
        """处理PictureItem，保存图片到本地"""
        adapter = ItemAdapter(item)
        if not adapter.get('name'):
            raise DropItem('No name in PictureItem')

        # noinspection PyTypeChecker
        anime_id = self.select_name_id_in_list(adapter.get('name'))
        if len(anime_id) == 1:
            anime_id = anime_id.pop()
            with open(join(self.save_path, f'{anime_id}.jpg'), 'wb') as f:
                f.write(adapter.get('picture'))
        else:
            logger.error(f'Could not find id for name: {adapter.get("name")}')

        return item

    def select_name_id_in_list(self, name_list: tuple[str]) -> set[int]:
        """
        根据名称列表查询对应的anime_id集合。

        :param name_list: 需要查询的名称列表。
        :return: 查询到的anime_id集合。
        """
        name_list = [i for i in name_list if i]
        # noinspection PyUnresolvedReferences
        anime_id_object = self.session.query(NameID).filter(NameID.name.in_(name_list)).all()
        return {i.id for i in anime_id_object}
