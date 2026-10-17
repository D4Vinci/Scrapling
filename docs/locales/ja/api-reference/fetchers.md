---
title: "HTTP・ブラウザ Fetcher の API リファレンス"
description: "Fetcher、AsyncFetcher、StealthyFetcher、セッションの API を確認します。リクエストのオプション、ブラウザ設定、戻り値の型を紹介します。"
---

# Fetcher クラス {#fetchers-classes}

すべての Fetcher クラスの引数、属性、メソッドを紹介します。

次のように直接インポートできます。

```python
from scrapling.fetchers import (
    Fetcher, AsyncFetcher, StealthyFetcher,
    FetcherSession, AsyncStealthySession, StealthySession
)
```

## ::: scrapling.fetchers.Fetcher
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncFetcher
    handler: python
    :docstring:

## ::: scrapling.fetchers.StealthyFetcher
    handler: python
    :docstring:


## セッションクラス {#session-classes}

### HTTP セッション {#http-sessions}

## ::: scrapling.fetchers.FetcherSession
    handler: python
    :docstring:

### ステルスセッション {#stealth-sessions}

## ::: scrapling.fetchers.StealthySession
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncStealthySession
    handler: python
    :docstring:
