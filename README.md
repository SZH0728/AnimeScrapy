# AnimeScrapyV2

AnimeScrapyV2 是一个用于爬取多个动漫平台数据的爬虫系统，支持从不同来源收集动漫信息并进行统一存储和管理。

<div align="right">
  <a href="./README_en.md">English</a> | 中文
</div>

## 目录

- [功能特性](#功能特性)
- [支持平台](#支持平台)
- [技术架构](#技术架构)
- [技术栈](#技术栈)
- [安装部署](#安装部署)
  - [Docker 部署（推荐）](#docker-部署推荐)
  - [本地运行](#本地运行)
- [项目结构](#项目结构)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [数据库设计](#数据库设计)
- [开发指南](#开发指南)

## 功能特性

- 多平台动漫数据爬取
- 数据统一存储和管理
- 定时任务调度
- 图片下载和保存
- 数据汇总与优先级排序
- 模块化设计，易于扩展
- 支持 Docker 容器化部署

## 支持平台

- [Bangumi 番组计划](https://bangumi.tv/)
- [Anikore](https://www.anikore.jp/)
- [aniDB](https://anidb.net/)
- [MyAnimeList](https://myanimelist.net/)

## 技术架构

AnimeScrapyV2 采用模块化架构设计，主要包含以下模块：

1. **Spider 模块** - 负责从不同平台爬取动漫数据
2. **Database 模块** - 负责数据持久化存储
3. **Frame 模块** - 提供爬虫框架基础功能
4. **Picture 模块** - 处理图片下载和保存
5. **Scheduler 模块** - 定时任务调度
6. **Summarize 模块** - 数据汇总和优先级排序

模块间通过桥接模式进行通信，各模块职责分离，便于维护和扩展。

## 技术栈

- Python 3.13
- httpx 0.28.1 (异步 HTTP 请求)
- lxml 6.0.1 (HTML/XML 解析)
- pytz 2025.2 (时区处理)
- SQLAlchemy 2.0.43 (ORM 数据库操作)
- PyMySQL 1.1.2 (MySQL 数据库连接)
- MariaDB (数据存储)

## 安装部署

部署前请在main.py中启用需要使用的爬虫

### Docker 部署（推荐）

1. 克隆项目代码：
   ```bash
   git clone <repository-url>
   cd AnimeScrapyV2
   ```


2. 根据Dockerfile构建项目


3. 复制并修改 docker-compose 配置：
   ```bash
   cp docker-compose-example.yml docker-compose.yml
   # 修改 docker-compose.yml 中的配置
   ```
   环境变量设置参考 [使用方法](#使用方法)


4. 构建并启动服务：
   ```bash
   docker-compose up -d
   ```

### 本地运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置数据库环境变量

3. 运行主程序：
   ```bash
   python main.py
   ```

## 项目结构

```
AnimeScrapyV2/
├── database/           # 数据库相关文件
│   ├── create.sql      # 数据库初始化脚本
│   ├── data.py         # 数据库操作模块
│   └── model.py        # 数据模型定义
├── frame/              # 爬虫框架基础模块
├── picture/            # 图片处理模块
├── scheduler/          # 任务调度模块
├── spider/             # 各平台爬虫实现
│   ├── AniDB.py
│   ├── Anikore.py
│   ├── Bagumi.py
│   └── MAL.py
├── summarize/          # 数据汇总模块
├── constant.py         # 常量配置
├── main.py             # 程序入口
└── requirements.txt    # 项目依赖
```

## 配置说明

项目通过环境变量进行配置：

- `USERNAME` - 数据库用户名
- `PASSWORD` - 数据库密码
- `HOST` - 数据库主机地址
- `PORT` - 数据库端口
- `LOG_PATH` - 日志文件路径
- `PICTURE_PATH` - 图片保存路径

在 Windows 系统中，默认使用常量值；在 POSIX 系统（Linux/Mac）中，从环境变量获取配置。

## 使用方法

项目默认北京时间每天凌晨2点执行一次爬取任务，可以通过修改 [main.py](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/main.py) 中的调度配置来调整执行频率：

```python
@schedule.repeat(Every().hour(2))
def task():
    # 爬取任务实现
```

## 数据库设计

数据库包含以下主要表结构：

1. `detail` - 存储动漫详细信息
2. `score` - 存储评分信息
3. `web` - 存储网站信息和优先级
4. `cache` - 缓存数据表

具体表结构请查看 [database/create.sql](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/database/create.sql) 文件。

## 开发指南

### 添加新的数据源

1. 在 [spider/](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/spider/) 目录下创建新的爬虫模块
2. 继承框架提供的基础类实现数据爬取逻辑
3. 在 [main.py](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/main.py) 中注册新的爬虫模块
4. 修改数据库Web表，添加相应的网站信息

### 扩展框架功能

框架核心模块位于 [frame/](file:///D:/poject/AnimeScrapyV2/AnimeScrapyV2/frame/) 目录，可根据需要进行扩展。