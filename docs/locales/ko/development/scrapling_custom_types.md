---
title: "코드에서 Scrapling 텍스트와 속성 타입 사용하기"
description: "파서 밖에서도 TextHandler, TextHandlers, AttributesHandler를 사용하세요. 기본 Python 타입, JSON 도구, 읽기 전용 속성을 알아봅니다."
---

# Scrapling의 사용자 정의 타입 사용하기 {#using-scraplings-custom-types}

> Scrapling용으로 만든 타입을 라이브러리 밖에서도 사용할 수 있습니다. 코드를 복사하는 것보다 편리합니다 :)

### 모든 타입을 개별적으로 가져올 수 있습니다 {#all-current-types-can-be-imported-alone-like-below}
```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler`는 Python의 `str`을 상속하므로 표준 문자열 연산과 메서드를 모두 사용할 수 있습니다.
`parsed`는 문자열 `'{}'`가 아니라 딕셔너리 `{}`입니다. 인스턴스를 확인하려면 `isinstance(somestring, TextHandler)`를, 클래스를 확인하려면 `issubclass(TextHandler, str)`을 사용하세요.

`AttributesHandler`는 `collections.abc.Mapping`을 상속하며, 변경할 수 없는 읽기 전용 매핑입니다. 연산은 기반 클래스에서 상속합니다. 전달한 데이터는 `_data`로 접근할 수 있지만, 이것도 읽기 전용인 `types.MappingProxyType`입니다. `collections.abc.Mapping`보다 조금 더 빠릅니다.

Python을 처음 사용한다면 이렇게 이해하면 됩니다. `AttributesHandler`에서는 실제 데이터를 바꾸는 연산을 제외하고 표준 `dict`의 연산과 메서드를 사용할 수 있습니다.

`AttributesHandler`의 데이터를 바꾸려면 먼저 `dict` 같은 함수로 일반 딕셔너리로 변환한 뒤 그 딕셔너리를 수정하세요.
