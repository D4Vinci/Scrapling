---
title: "적응형 파싱을 위한 저장소 만들기"
description: "Scrapling의 적응형 파싱을 위한 save와 retrieve를 구현하세요. Redis 저장소를 만들어 요소 속성을 저장하고 가져옵니다."
---

# 저장과 검색 시스템 만들기 {#writing-your-retrieval-system}

Scrapling은 기본적으로 SQLite를 사용합니다. 이 안내에서는 `adaptive` 기능에 필요한 요소 속성을 직접 만든 저장소에 저장하는 방법을 설명합니다.

예를 들어 Firebase를 사용해 여러 컴퓨터에서 실행하는 스파이더가 데이터베이스를 공유하도록 만들 수 있습니다. 이런 온라인 데이터베이스를 쓰면 스파이더 사이에서 적응형 데이터를 공유할 수 있습니다.

저장소 클래스는 다음 세 가지 조건을 만족해야 합니다.

1. 추상 클래스 `scrapling.core.storage.StorageSystemMixin`을 상속하고 문자열 인수를 받습니다. 라이브러리의 동작을 유지하기 위한 `url` 인수입니다.
2. 클래스 위에 `functools.lru_cache` 데코레이터를 사용해 다른 클래스처럼 Singleton 패턴을 따릅니다.
3. 타입 힌트에 맞게 `save`와 `retrieve`를 구현합니다.
    - `save`는 아무것도 반환하지 않으며 라이브러리에서 인수 두 개를 받습니다.
        * 첫 번째는 요소 자체인 `lxml.html.HtmlElement`입니다. 같은 형식을 유지하려면 `scrapling.core.utils._StorageTools` 하위 모듈의 `element_to_dict`로 딕셔너리로 바꾼 뒤 원하는 방식으로 데이터베이스에 저장하세요.
        * 두 번째는 검색에 사용할 문자열 식별자입니다. 초기화할 때 받은 `url`과 이 식별자를 조합한 값은 각 행마다 고유해야 합니다. 그렇지 않으면 `adaptive` 데이터가 섞입니다.
    - `retrieve`는 문자열 식별자를 받습니다. 초기화할 때 받은 `url`과 함께 사용해 데이터베이스에서 요소의 딕셔너리를 찾고 반환합니다. 없으면 `None`을 반환합니다.

> 더 자세한 예가 필요하면 [storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py) 파일의 SQLite3 구현을 살펴보세요.

이 조건을 만족하면 나머지는 간단합니다. 여러 스레드를 사용하는 앱이라면 클래스가 안전하게 동작하는지 확인하세요. 기본 저장소 클래스는 스레드 안전성을 제공합니다.

추상 클래스에는 사용할 수 있는 보조 함수도 있습니다. 설명이 자세히 있는 [코드](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py)를 살펴보세요 :)


## 실제 예: Redis 저장소 {#real-world-example-redis-storage}

다음은 AI로 만든 Redis 저장소 예입니다.

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
