---
title: "为自适应解析编写自定义存储后端"
description: "为 Scrapling 自适应解析实现 save 和 retrieve。编写 Redis 存储后端，保存和读取元素属性。"
---

# 编写自己的存储系统 {#writing-your-retrieval-system}

Scrapling 默认使用 SQLite。本教程介绍如何编写自己的存储系统，为 `adaptive` 功能保存元素属性。

例如，可以使用 Firebase，让不同机器上的多个 Spider 共用一个数据库。使用这样的在线数据库，可以让 Spider 共享自适应数据。

存储类首先需要满足三个要求：

1. 继承抽象类 `scrapling.core.storage.StorageSystemMixin`，并接收字符串参数 `url`，以保持库的处理逻辑一致。
2. 在类上使用 `functools.lru_cache` 装饰器，与其他类一样遵循单例设计模式。
3. 按照类型提示实现 `save` 和 `retrieve` 方法：
    - `save` 方法不返回值，会从库接收两个参数。
        * 第一个参数是元素本身，类型为 `lxml.html.HtmlElement`。必须用子模块 `scrapling.core.utils._StorageTools` 中的 `element_to_dict` 函数将其转成字典，以保持格式一致，然后按需保存到数据库。
        * 第二个参数是字符串，作为后续读取时使用的标识。它与初始化时传入的 `url` 组合后，必须对每行数据都唯一，否则 `adaptive` 数据会对应错误。
    - `retrieve` 方法接收标识字符串，结合初始化时传入的 `url`，从数据库读取并返回元素的字典。如果不存在，则返回 `None`。

> 如果这些步骤还不够清楚，可以查看 [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py) 文件中我的 SQLite3 实现。

只要类满足这些要求，后续就很简单。如果打算在多线程应用中使用本库，请确保自定义类支持多线程。默认使用的类是线程安全的。

抽象类中也提供了一些可选的辅助函数。直接查看[代码](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py)会更容易理解，其中有详细注释 :)


## 实际示例：Redis 存储 {#real-world-example-redis-storage}

下面是一个由 AI 生成的 Redis 实用示例：

```python
import redis
import orjson
from functools import lru_cache
from scrapling.core.storage import StorageSystemMixin
from scrapling.core.utils import _StorageTools

@lru_cache(None)
class RedisStorage(StorageSystemMixin):
    def __init__(self, host='localhost', port=6379, db=0, url=None):
        super().__init__(url)
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False
        )
        
    def save(self, element, identifier: str) -> None:
        # Convert element to dictionary
        element_dict = _StorageTools.element_to_dict(element)
        
        # Create key
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        
        # Store as JSON
        self.redis.set(
            key,
            orjson.dumps(element_dict)
        )
        
    def retrieve(self, identifier: str) -> dict | None:
        # Get data
        key = f"scrapling:{self._get_base_url()}:{identifier}"
        data = self.redis.get(key)
        
        # Parse JSON if exists
        if data:
            return orjson.loads(data)
        return None
```
