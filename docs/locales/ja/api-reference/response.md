---
title: "Response の API リファレンス"
description: "ステータス、ヘッダー、本文、メタデータ、Markdown 変換、follow を確認します。Selector から継承したメソッドでデータを抽出できます。"
---

# Response クラス {#response-class}

`Response` は、すべての Fetcher が返す HTTP レスポンスを表すクラスです。ステータス、ヘッダー、本文、Cookie にアクセスでき、`Selector` を継承した解析機能も使えます。

`Response` クラスは次のようにインポートします。

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
