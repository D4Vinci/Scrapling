---
title: "適応型解析の保存先を自分で実装する"
description: "Scrapling の適応型解析用に save と retrieve を実装します。Redis を使う保存先を作り、要素の特徴を保存して取得します。"
---

# 独自の保存の仕組みを作る {#writing-your-retrieval-system}

Scrapling はデフォルトで SQLite を使います。このガイドでは、`adaptive` 機能で使う要素の特徴を保存する仕組みを、自分で実装する方法を説明します。

たとえば Firebase を使い、異なるマシン上の複数の Spider でデータベースを共有できます。このようなオンラインデータベースなら、Spider 同士で適応型解析のデータを共有できます。

保存用のクラスは、次の 3 つの条件を満たす必要があります。

1. 抽象クラス `scrapling.core.storage.StorageSystemMixin` を継承し、文字列引数 `url` を受け取ります。これにより、ライブラリの処理との互換性を保ちます。
2. クラスに `functools.lru_cache` デコレーターを付け、ほかのクラスと同じシングルトンのパターンに従います。
3. 型ヒントに示すように、`save` と `retrieve` を実装します。
    - `save` は何も返さず、ライブラリから 2 つの引数を受け取ります。
        * 1 つ目は要素そのもので、型は `lxml.html.HtmlElement` です。形式をそろえるため、`scrapling.core.utils._StorageTools` の `element_to_dict` で辞書に変換してから、データベースに保存してください。
        * 2 つ目は文字列で、取得時に使う識別子です。この識別子と初期化時の `url` の組み合わせは、各行で一意でなければなりません。重複すると `adaptive` のデータが正しく対応しなくなります。
    - `retrieve` は識別子の文字列を受け取ります。初期化時の `url` と組み合わせ、データベースから要素の辞書を取得して返します。見つからない場合は `None` を返します。

> 手順がわかりにくい場合は、[storage_adaptors](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py) ファイルにある SQLite3 の実装を参考にしてください。

この条件を満たせば、あとは簡単です。マルチスレッドのアプリで使う場合は、クラスが対応していることを確認してください。デフォルトのクラスはスレッドセーフです。

抽象クラスには、必要に応じて使える補助関数もあります。詳しいコメント付きの[コード](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/storage.py)を見ると、理解しやすくなります :)


## 実用例：Redis に保存する {#real-world-example-redis-storage}

次は、AI が作成した Redis を使う実用例です。

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
