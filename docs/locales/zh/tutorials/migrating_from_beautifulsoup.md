---
title: "从 BeautifulSoup 迁移到 Scrapling"
description: "将 BeautifulSoup 中常用的选择、文本、属性和导航操作对应到 Scrapling，通过实际示例了解 API 差异。"
---

# 从 BeautifulSoup 迁移到 Scrapling {#migrating-from-beautifulsoup-to-scrapling}

如果已经熟悉 BeautifulSoup，使用 Scrapling 会很容易上手。Scrapling 速度更快，提供相同的解析能力，还增加了 BeautifulSoup 没有的解析方法，以及获取和处理现代网页的功能。本指南帮助你将现有 BeautifulSoup 代码快速改为使用 Scrapling。

下表列出了网页抓取中最常见的操作。每一行展示了 BeautifulSoup 的写法和 Scrapling 中对应的方法。

BeautifulSoup 的某些快捷写法在 Scrapling 中不存在，这也是 BeautifulSoup 更慢的原因之一。如果一个功能已经能用简短的一行代码实现，就没必要为了再缩短一点而牺牲性能 :)

| 任务 | BeautifulSoup 代码 | Scrapling 代码 |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 导入 Parser | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| 解析字符串中的 HTML | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| 查找单个元素 | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| 查找多个元素 | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| 查找单个元素（示例 2） | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| 查找单个元素（示例 3） | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| 查找单个元素（示例 4） | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| 查找单个元素（示例 5） | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| 按文本内容查找元素 | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| 用 CSS 选择器查找第一个匹配元素 | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| 用 CSS 选择器查找所有匹配元素 | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| 获取格式化后的页面或元素源码 | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| 获取未格式化的页面或元素源码 | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| 获取元素的标签名 | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| 提取元素的文本内容 | `string = element.string`                                                                                     | `string = element.text`                                                           |
| 提取文档或标签下的全部文本 | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| 访问属性字典 | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| 提取属性 | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| 访问父元素 | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| 获取元素的所有祖先 | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| 在祖先中查找一个元素 | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| 获取所有兄弟元素 | 不支持                                                                                                           | `siblings = element.siblings`                                                     |
| 获取下一个兄弟元素 | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| 在兄弟元素中查找一个元素 | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| 在兄弟元素中查找多个元素 | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| 在后续元素中查找一个元素 | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| 在后续元素中查找多个元素 | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| 在祖先中查找一个元素 | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| 在祖先中查找多个元素 | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| 获取上一个兄弟元素 | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| 访问子元素 | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| 获取所有后代元素 | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| 选择 story 类段落内的链接 | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

直接传给 Scrapling `find()` 或 `find_all()` 的已编译正则表达式，匹配的是元素文本，而不是标签名。要匹配标签名，使用表中的 lambda；要直接匹配文本，可以使用 `page.find_by_regex(r"^b")`。

¹ **注意：** BS4 的 `find_previous`/`find_all_previous` 会按文档顺序搜索所有先前元素，而 Scrapling 的 `path` 只返回祖先，也就是父元素链。它们并非完全等价，但祖先搜索能覆盖最常见的场景。

**一个重要区别**：BeautifulSoup 提供了在解析后修改页面的功能。Scrapling 更专注于快速提取数据，然后交给用户自行处理。两者都能用于网页抓取，但其中一个专门为此设计 :)

### 完整示例 {#putting-it-all-together}

下面分别使用 BeautifulSoup 和 Scrapling，提取页面中的所有链接。

**使用 BeautifulSoup：**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**使用 Scrapling：**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Scrapling 将获取和解析合为一步，让代码更简洁、效率更高。

!!! abstract "**补充说明：**"

    - **不同的 Parser**：BeautifulSoup 允许选择解析引擎，例如 `lxml`。Scrapling 出于性能考虑，默认使用 `lxml` 库。
    - **元素类型**：BeautifulSoup 中的元素是 `Tag` 对象，Scrapling 中的是 `Selector` 对象。它们提供类似的导航和数据提取方法及属性。
    - **错误处理**：找不到元素时，两者都返回 `None`，例如 `soup.find()` 或 `page.find()`。Scrapling 的 `page.css()` 在没有匹配元素时返回空的 `Selectors` 列表。可以用 `page.css('.foo').first` 安全地获取第一个结果或 `None`。访问属性前，先检查结果是否为 `None` 或为空。
    - **文本提取**：Scrapling 通过 `TextHandler` 提供更多文本处理方法，例如 `clean()`，可以帮助移除多余空白、连续空格或不需要的字符。完整列表请查看文档。

文档会更详细地介绍 Scrapling 的功能，并列出各方法支持的全部参数。

希望本指南能让从 BeautifulSoup 到 Scrapling 的迁移更顺利。祝抓取顺利！
