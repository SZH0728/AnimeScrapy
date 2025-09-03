# AnimeScrapy - 动画信息爬虫项目

AnimeScrapy 是一个基于 Scrapy 框架的多源动画信息采集系统，可以从多个动画数据库网站收集动画信息，包括番剧名称、评分、演员、导演、标签等详细信息，并将这些信息存储到数据库中。  
### 本项目已停止维护。重构版本将发布于[AnimeScrapyV2](https://github.com/SZH0728/AnimeScrapyV2)

## 项目结构

```
AnimeScrapy/
├── AnimeScrapy/           # Scrapy项目主目录
│   ├── spiders/           # 爬虫模块
│   │   ├── Anikore.py     # Anikore网站爬虫
│   │   ├── Bangumi.py     # Bangumi网站爬虫
│   │   ├── MyAnimeList.py # MyAnimeList网站爬虫
│   │   └── aniDB.py       # aniDB网站爬虫
│   ├── items.py           # 数据模型定义
│   ├── middlewares.py     # 中间件
│   ├── pipelines.py       # 数据处理管道
│   └── settings.py        # 项目设置
├── cover/                 # 封面图片存储目录
├── dbmanager.py           # 数据库管理模块
├── main.py                # 主程序入口
├── scheduler.py           # 任务调度器
├── scrapy.cfg             # Scrapy配置文件
└── README.md              # 项目说明文档
```

## 功能特性

1. **多源数据采集**：支持从以下四个主要动画数据库网站采集数据：
   - [Bangumi 番组计划](https://bangumi.tv/)
   - [Anikore](https://www.anikore.jp/)
   - [aniDB](https://anidb.net/)
   - [MyAnimeList](https://myanimelist.net/)

2. **数据去重与合并**：通过动画名称识别同一部动画在不同网站的数据，并进行智能合并。

3. **自动调度**：使用 schedule 库实现定时任务，每天自动采集最新数据。

4. **数据持久化**：使用 SQLAlchemy ORM 将采集到的数据存储到 MariaDB 数据库中。

5. **图片下载**：自动下载动画封面图片并保存到本地。

## 数据模型

项目定义了三种主要的数据模型：

### DetailItem - 详细信息
- `name`: 动画名称
- `translation`: 译名
- `alias`: 别名列表
- `season`: 季度信息
- `time`: 发布时间
- `tag`: 标签列表
- `director`: 导演
- `cast`: 演员列表
- `description`: 简介
- `web`: 来源网站
- `webId`: 来源网站ID
- `picture`: 封面图片URL

### ScoreItem - 评分信息
- `name`: 动画名称
- `score`: 评分
- `vote`: 投票数
- `source`: 来源网站
- `date`: 采集日期

### PictureItem - 图片信息
- `name`: 动画名称
- `picture`: 图片二进制数据

## 技术架构

### 数据库设计
使用 MariaDB 数据库存储动画信息，主要包含以下表：
- `cache`: 缓存表，用于临时存储未匹配到动画的评分数据
- `detail`: 动画详细信息表
- `nameid`: 动画名称与ID映射表
- `score`: 动画评分表
- `web`: 网站信息表

### 数据处理流程
1. 爬虫从各网站采集原始数据
2. 通过 DetailItemPipeline 处理详细信息，进行数据去重与合并
3. 通过 ScoreItemPipeline 处理评分信息，计算加权平均分
4. 通过 PictureItemPipeline 下载并保存封面图片
5. 所有数据最终存储到数据库中

### 调度机制
- 每天 18:00 自动运行爬虫采集最新数据
- 每天 04:00 更新动画名称列表文件

## 配置说明

### 数据库配置
在 `scrapy.cfg` 文件中配置数据库连接信息：

```ini
[database]
host = localhost
port = 3306
username = your_username
password = your_password
db = your_database
```

### 爬虫配置
在 [settings.py](file:///D:/poject/AnimeScrapy/AnimeScrapy/settings.py#L1-L101) 中可以调整以下参数：
- `DOWNLOAD_DELAY`: 下载延迟（默认10秒）
- `CONCURRENT_REQUESTS_PER_DOMAIN`: 每个域名并发请求数（默认1）
- `DEFAULT_REQUEST_HEADERS`: 默认请求头

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行项目
```bash
python main.py
```

### 单独运行某个爬虫
```bash
scrapy crawl Bangumi
scrapy crawl Anikore
scrapy crawl aniDB
scrapy crawl MyAnimeList
```

## 注意事项

1. 为避免对目标网站造成过大压力，项目设置了较保守的请求频率限制
2. 项目会自动处理同一动画在不同网站的数据合并
3. 评分系统会根据不同网站的评分规则进行标准化处理
4. 图片文件会以动画ID命名保存在 [cover/](file:///D:/poject/AnimeScrapy/cover/) 目录下
