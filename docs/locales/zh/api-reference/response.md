---
title: "Response API 参考"
description: "查看响应状态、响应头、内容、元数据、Markdown 转换和 follow 方法，并使用从 Selector 继承的方法提取数据。"
---

# Response 类 {#response-class}

`Response` 类表示所有 Fetcher 返回的 HTTP 响应。它提供状态、响应头、内容和 Cookie，也通过继承 `Selector` 提供解析功能。

导入 `Response` 类：

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
