---
title: "HTTP 和浏览器 Fetcher API 参考"
description: "查看 Fetcher、AsyncFetcher、StealthyFetcher 和会话的 API，包括请求选项、浏览器设置和返回类型。"
---

# Fetcher 类 {#fetchers-classes}

这里列出了所有 Fetcher 类的参数、属性和方法。

可以直接导入：

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


## 会话类 {#session-classes}

### HTTP 会话 {#http-sessions}

## ::: scrapling.fetchers.FetcherSession
    handler: python
    :docstring:

### 隐身浏览器会话 {#stealth-sessions}

## ::: scrapling.fetchers.StealthySession
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncStealthySession
    handler: python
    :docstring:
