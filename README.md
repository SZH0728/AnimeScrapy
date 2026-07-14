# AnimeScrapy

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)

基于 `asyncio` 异步事件总线的动漫站点结构化数据采集框架。以常驻守护进程方式运行，定时注入采集任务，支持多站点扩展且无需重启进程。

---

## 特性

- **异步事件总线**：所有处理单元通过 `asyncio.Queue` 通信，彼此无直接依赖
- **三种请求策略**：单条（Single）、并发批量（Batch）、节流顺序（Throttled）
- **两段路由**：框架层按域名路由 → 站点层按 URL 路径路由
- **无依赖数据层**：`data/` 模块仅包含 dataclass，不导入任何业务模块，从根本上规避循环导入
- **内置重试**：请求失败自动以 `retry-1` 重入总线，批量请求支持部分失败降级
- **双模式日志**：`debug=true` 输出控制台，`debug=false` 生产文件轮转（INFO/ERROR 分离）

---

## 架构速览

```
Scheduler（独立协程，定时注入种子任务）
    ↓
AsyncQueue（事件总线）
    ↓  type(task) 查 dispatch_registry
Requester  ──→  HttpxSiteRouter  ──→  SiteGateway  ──→  Parser  ──→  Storage
    ↑_____________________返回值投回总线___________________________________|
```

| 层 | 职责 |
|----|------|
| `requester/` | 网络请求；失败重试后重入总线 |
| `router/` | 按响应域名匹配站点，产出 `XxxSiteGatewayData` |
| `gateway/` | 按 URL 路径分发，产出 `XxxParseData` |
| `parser/` | 解析 HTML/JSON，产出新请求或存储数据包 |
| `storage/` | 数据落库；可选产出后续请求（如封面下载） |
| `data/` | 所有 dataclass，零对外依赖 |
| `scheduler/` | 定时触发，向总线注入种子任务 |
| `database/` | SQLAlchemy async ORM，session_factory 单例 |

---

## 环境要求

- Python 3.12+
- PostgreSQL 14+
- 核心依赖：`httpx`、`SQLAlchemy[asyncio]`

---

## 快速上手

### 1. 克隆并安装依赖

```bash
git clone https://github.com/yourname/AnimeScrapy.git
cd AnimeScrapy
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# 或 source .venv/bin/activate  # Linux / macOS
pip install httpx "sqlalchemy[asyncio]" asyncpg
```

### 2. 创建数据库

在 PostgreSQL 中创建数据库，然后执行建表 DDL。

### 3. 配置

编辑 `config.ini`，至少填写以下字段：

```ini
[app]
debug = false                  # 生产模式；true 输出控制台日志

[bangumi]
database_url = postgresql+asyncpg://user:password@localhost:5432/animescrapy
user_agent   = AnimeScrapy/1.0 (https://github.com/yourname/AnimeScrapy)
trigger_hour = 2               # 每天凌晨 2 点触发
trigger_minute = 0
```

### 4. 运行

```bash
python main.py
```

进程常驻，到达触发时刻后自动开始采集。

---

## 配置说明

| 节 | 键 | 说明 |
|----|----|------|
| `[app]` | `debug` | `true` 控制台日志，`false` 文件轮转 |
| `[bus]` | `max_concurrent_tasks` | Bus 信号量上限，控制并发协程数 |
| `[logging]` | `log_dir` | 生产模式日志目录 |
| `[logging]` | `info_backup_count` | info 日志保留天数 |
| `[logging]` | `error_backup_count` | error 日志保留天数（0 = 永不删除） |
| `[bangumi]` | `database_url` | asyncpg 连接串 |
| `[bangumi]` | `user_agent` | HTTP 请求头，建议填写项目地址 |
| `[bangumi]` | `retry` | 单次请求失败最大重试次数 |
| `[bangumi]` | `throttle_interval_seconds` | 节流请求间隔（秒） |
| `[bangumi]` | `trigger_hour` / `trigger_minute` | 每日触发时刻 |

---

## 扩展新站点

不需要修改任何框架代码，四步完成：

1. **新增数据包**（`data/gateway.py`、`data/parse.py`、`data/store.py`）：定义站点专属的 `XxxSiteGatewayData`、`XxxParseData`、`XxxStoreData`。
2. **实现 Gateway**（`gateway/xxx.py`）：继承 `SiteGatewayBase`，在 `_do_handle()` 中按 URL 路径匹配产出 ParseData。
3. **实现 Parser / Storage**（`parser/xxx/`、`storage/xxx/`）：解析响应并落库。
4. **注册**：在 `router/__init__.py` 的 `HTTPX_DOMAIN_REGISTRY` 中添加域名映射，在 `gateway/`、`parser/`、`storage/` 的 `__init__.py` 中注册 `DISPATCH_REGISTRY`。

---

## 项目结构

```
AnimeScrapy/
├── main.py              # 程序入口，装配所有模块
├── config.ini           # 运行时配置
├── base.py              # HandlerBase（总线契约接口）
├── bus.py               # Bus 调度器
├── data/                # 所有 dataclass（零对外依赖）
├── scheduler/           # 定时触发
├── requester/           # HTTP 请求（Single / Batch / Throttled）
├── router/              # 域名路由
├── gateway/             # 路径路由（站点层）
├── parser/              # HTML/JSON 解析
├── storage/             # 数据落库
├── database/            # SQLAlchemy ORM 与 session_factory
└── docs/                # 设计文档
```

---

## License

[GNU General Public License v3.0](LICENSE)
