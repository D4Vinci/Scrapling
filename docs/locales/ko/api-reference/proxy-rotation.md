---
title: "ProxyRotator API 참고 문서"
description: "HTTP·브라우저 세션에서 ProxyRotator로 프록시를 선택하고 교체하는 방법을 확인하세요."
---

# 프록시 교체 {#proxy-rotation}

`ProxyRotator`는 모든 Fetcher와 세션에서 프록시를 교체합니다. 여러 스레드에서 안전하게 사용할 수 있습니다.

다음처럼 직접 가져올 수 있습니다:

```python
from scrapling.fetchers import ProxyRotator
```

## ::: scrapling.engines.toolbelt.proxy_rotation.ProxyRotator
    handler: python
    :docstring:
