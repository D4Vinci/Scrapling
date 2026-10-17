---
title: "HTTP·브라우저 Fetcher API 참고 문서"
description: "Fetcher, AsyncFetcher, StealthyFetcher와 세션의 API를 확인하세요. 요청 옵션, 브라우저 설정, 반환 자료형을 설명합니다."
---

# Fetcher 클래스 {#fetchers-classes}

모든 Fetcher 클래스의 인수, 속성, 메서드를 설명합니다.

다음처럼 직접 가져올 수 있습니다:

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


## 세션 클래스 {#session-classes}

### HTTP 세션 {#http-sessions}

## ::: scrapling.fetchers.FetcherSession
    handler: python
    :docstring:

### 스텔스 세션 {#stealth-sessions}

## ::: scrapling.fetchers.StealthySession
    handler: python
    :docstring:

## ::: scrapling.fetchers.AsyncStealthySession
    handler: python
    :docstring:
