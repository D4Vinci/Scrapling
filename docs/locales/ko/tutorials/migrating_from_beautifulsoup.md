---
title: "BeautifulSoup에서 Scrapling으로 옮기기"
description: "BeautifulSoup의 요소 선택, 텍스트, 속성, 탐색 작업을 Scrapling으로 바꿔 보세요. 실제 예제로 API 차이를 확인합니다."
---

# BeautifulSoup에서 Scrapling으로 옮기기 {#migrating-from-beautifulsoup-to-scrapling}

BeautifulSoup에 익숙하다면 Scrapling도 쉽게 시작할 수 있습니다. Scrapling은 더 빠르게 작동하며, BeautifulSoup의 파싱 기능에 더해 새로운 파싱 기능도 제공합니다. 현대적인 웹페이지를 가져오고 처리하는 기능도 있습니다. 이 안내는 기존 BeautifulSoup 코드를 Scrapling으로 빠르게 바꾸는 데 도움을 줍니다.

아래 표에는 웹 스크래핑에서 자주 사용하는 작업을 정리했습니다. 각 행에서 같은 작업을 BeautifulSoup과 Scrapling으로 처리하는 방법을 비교할 수 있습니다.

BeautifulSoup의 일부 단축 표현은 Scrapling에 없습니다. 이것은 Scrapling이 더 빠른 이유 중 하나입니다. 이미 짧은 한 줄로 같은 기능을 쓸 수 있다면, 그 줄을 더 줄이기 위해 성능을 희생할 필요는 없다고 생각합니다 :)


| 작업 | BeautifulSoup 코드 | Scrapling 코드 |
|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 파서 가져오기 | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| 문자열의 HTML 파싱 | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| 요소 하나 찾기 | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| 여러 요소 찾기 | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| 요소 하나 찾기(예제 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| 요소 하나 찾기(예제 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| 요소 하나 찾기(예제 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| 요소 하나 찾기(예제 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| 텍스트 내용으로 요소 찾기 | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| CSS 선택자로 첫 번째 일치 요소 찾기 | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| CSS 선택자로 모든 일치 요소 찾기 | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| 페이지나 요소의 보기 좋게 정리한 소스 가져오기 | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| 페이지나 요소의 정리하지 않은 소스 가져오기 | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| 요소의 태그 이름 가져오기 | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| 요소의 텍스트 추출 | `string = element.string`                                                                                     | `string = element.text`                                                           |
| 문서 전체나 태그 아래의 모든 텍스트 추출 | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| 속성 딕셔너리에 접근 | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| 속성 추출 | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| 부모로 이동 | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| 요소의 모든 조상 가져오기 | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| 조상 중에서 요소 찾기 | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| 모든 형제 요소 가져오기 | 지원 안 함                                                                                                           | `siblings = element.siblings`                                                     |
| 다음 형제 요소 가져오기 | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| 형제 중에서 요소 하나 찾기 | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| 형제 중에서 여러 요소 찾기 | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| 뒤에 나오는 요소 중 하나 찾기 | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| 뒤에 나오는 요소 중 여러 개 찾기 | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| 조상 중에서 요소 하나 찾기 | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| 조상 중에서 여러 요소 찾기 | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| 이전 형제 요소 가져오기 | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| 자식으로 이동 | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| 모든 자손 요소 가져오기 | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| story 클래스가 있는 문단 안의 링크 선택 | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

컴파일한 정규식을 Scrapling의 `find()`나 `find_all()`에 직접 전달하면 태그 이름이 아니라 요소의 텍스트를 검사합니다. 태그 이름에는 위 표의 lambda를 사용하고, 텍스트를 찾을 때는 `page.find_by_regex(r"^b")`를 직접 사용하세요.

¹ **참고:** BS4의 `find_previous`/`find_all_previous`는 문서 순서상 앞에 있는 모든 요소를 검색합니다. 반면 Scrapling의 `path`는 조상, 즉 부모를 따라 올라간 요소만 반환합니다. 완전히 같은 기능은 아니지만, 조상 검색으로 가장 흔한 사용 사례를 처리할 수 있습니다.

**기억할 점**: BeautifulSoup은 파싱 후 페이지를 수정하고 조작하는 기능을 제공합니다. Scrapling은 페이지에서 데이터를 빠르게 수집하는 데 더 집중합니다. 추출한 데이터는 이후에 원하는 대로 처리할 수 있습니다. 두 도구 모두 웹 스크래핑에 사용할 수 있지만 Scrapling은 그 용도에 특화되어 있습니다 :)

### 전체 예제 {#putting-it-all-together}

BeautifulSoup과 Scrapling으로 웹페이지의 모든 링크를 추출하는 간단한 예제입니다.

**BeautifulSoup 사용:**

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

**Scrapling 사용:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Scrapling은 페이지 가져오기와 파싱을 한 단계로 합쳐 코드를 더 간결하고 효율적으로 만듭니다.

!!! abstract "**추가 참고 사항:**"

    - **파서 차이**: BeautifulSoup에서는 파싱 엔진을 선택할 수 있으며 `lxml`도 그중 하나입니다. Scrapling은 엔진을 바꾸지 않고 성능을 위해 기본으로 `lxml`을 사용합니다.
    - **요소 타입**: BeautifulSoup의 요소는 `Tag`, Scrapling의 요소는 `Selector` 객체입니다. 탐색과 데이터 추출에는 비슷한 메서드와 속성을 제공합니다.
    - **오류 처리**: 두 라이브러리 모두 요소를 찾지 못하면 `None`을 반환합니다. 예를 들어 `soup.find()`나 `page.find()`가 그렇습니다. Scrapling의 `page.css()`는 일치하는 요소가 없으면 빈 `Selectors` 리스트를 반환합니다. `page.css('.foo').first`로 첫 번째 일치 요소 또는 `None`을 안전하게 가져올 수 있습니다. 오류를 피하려면 속성에 접근하기 전에 `None`이나 빈 결과인지 확인하세요.
    - **텍스트 추출**: Scrapling은 `TextHandler`로 텍스트 처리 메서드를 더 제공합니다. 예를 들어 `clean()`은 불필요한 공백 문자, 연속된 공백, 원치 않는 문자를 제거하는 데 도움이 됩니다. 전체 목록은 문서를 확인하세요.

문서에는 Scrapling의 기능과 각 메서드에 전달할 수 있는 인수가 자세히 나와 있습니다.

이 안내가 BeautifulSoup에서 Scrapling으로 옮기는 데 도움이 되기를 바랍니다. 즐겁게 스크래핑하세요!
