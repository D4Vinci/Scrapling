---
title: "Response API 참고 문서"
description: "Response의 상태, 헤더, 본문, 메타데이터, Markdown 변환, follow를 확인하세요. Selector에서 상속한 추출 메서드도 사용할 수 있습니다."
---

# Response 클래스 {#response-class}

`Response`는 모든 Fetcher가 반환하는 HTTP 응답을 나타냅니다. 상태, 헤더, 본문, 쿠키를 읽을 수 있고 `Selector`에서 상속한 파싱 기능도 사용할 수 있습니다.

`Response` 클래스는 다음처럼 가져옵니다:

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
