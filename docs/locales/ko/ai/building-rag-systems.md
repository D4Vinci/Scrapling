---
title: "Scrapling으로 웹사이트를 크롤링해 RAG용 Markdown 만들기"
description: "페이지 응답을 Markdown으로 바꾸거나 ContentSpider로 사이트를 수집하세요. RAG 시스템에서 나누고 인덱싱할 문서 모음을 준비합니다."
---

# Scrapling으로 RAG 시스템 만들기 {#building-rag-systems-with-scrapling}

RAG 파이프라인의 품질은 입력하는 텍스트에 달려 있습니다. 원본 HTML에는 마크업, 탐색 메뉴, 스크립트, 추적 코드 같은 불필요한 내용이 있어 토큰을 낭비합니다. 숨겨진 프롬프트 인젝션 내용이 그대로 LLM에 전달될 수도 있습니다. Scrapling은 LLM 없이 페이지나 사이트 전체를 정리된 Markdown으로 바꿉니다. 따라서 수집이 빠르고 페이지마다 LLM 비용이 들지 않습니다.

## 설치 {#installation}

```bash
pip install "scrapling[rag]"

scrapling install
```

`rag` 추가 의존성 그룹은 Markdown 변환을 지원하는 Fetcher를 설치합니다. `ai`, `shell`, `all`에도 포함되어 있습니다. `scrapling install` 명령은 브라우저 의존성을 다운로드합니다. 이 단계는 브라우저 기반 Fetcher에만 필요합니다.

## 한 페이지를 Markdown으로 바꾸기 {#one-page-to-markdown}

모든 [Response](../fetching/choosing.md#response-object)에는 `markdown()` 메서드가 있습니다.

```python
from scrapling.fetchers import Fetcher

markdown = Fetcher.get("https://example.com").markdown(main_content_only=True)
```

모든 Fetcher에서 작동하므로 Cloudflare로 보호된 페이지도 한 줄로 변환할 수 있습니다.

```python
from scrapling.fetchers import StealthyFetcher

markdown = StealthyFetcher.fetch("https://protected.example.com", solve_cloudflare=True).markdown(main_content_only=True)
```

출력은 두 인수로 조절합니다.

- `main_content_only`: 페이지의 `<body>` 태그 안에 있는 내용만 변환합니다.
- `css_selector`: CSS 선택자와 일치하는 요소만 변환합니다. 일치하는 모든 결과를 합칩니다. 파이프라인에 필요한 부분만 추출해 토큰을 줄일 수 있습니다.

```python
markdown = Fetcher.get("https://example.com/docs/page").markdown(css_selector="article")
```

어떤 인수를 전달하든 변환 전에 스크립트, 스타일, 숨겨진 내용을 항상 제거합니다. [MCP 서버](mcp-server.md)가 AI 에이전트를 프롬프트 인젝션으로부터 보호할 때도 같은 정리 과정을 사용합니다. 인라인 스타일로 숨긴 요소, `aria-hidden="true"` 요소, 숨겨진 슬롯, `<template>` 태그, HTML 주석, 너비가 0인 문자를 변환 전에 제거합니다. MCP 서버는 `main_content_only=True`일 때 이 정리 과정을 사용합니다.

## 사이트 전체를 Markdown 문서 모음으로 만들기 {#a-whole-website-to-a-markdown-corpus}

`ContentSpider` 템플릿은 웹사이트를 크롤링하고 모든 페이지를 변환합니다. [Spider 프레임워크](../spiders/architecture.md)를 사용하므로 동시 처리, AutoThrottle, robots.txt 준수, 일시 정지와 재개 기능도 이용할 수 있습니다.

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"
    max_pages = 200

result = DocsSpider().start()
result.items.to_jsonl("docs.jsonl")
```

수집한 각 페이지는 `url`, `title`, `markdown` 키가 있는 항목이 됩니다. `output_dir`를 설정하면 각 페이지를 URL에 따라 이름을 정한 Markdown 파일로도 저장합니다. 따라서 위 예제는 `.md` 파일이 담긴 폴더와 수집 시스템에 바로 넣을 수 있는 `docs.jsonl`을 함께 만듭니다.

크롤링이 대상 사이트를 벗어나지 않도록 이 템플릿에는 `allowed_domains`가 필요합니다. 사용할 수 있는 옵션은 다음과 같습니다.

- `css_selector` / `main_content_only`: 모든 페이지의 `markdown()`에 전달합니다. `main_content_only`는 기본으로 켜져 있습니다.
- `output_dir`: 설정하면 페이지마다 Markdown 파일 하나를 저장합니다.
- `max_pages`: 변환할 페이지 수의 상한입니다. 상한에 도달했을 때 이미 큐에 들어간 요청은 가져올 수 있지만 변환하지는 않습니다. 기본값인 `0`은 제한을 끕니다.

기본으로 `allowed_domains` 안의 모든 페이지 링크를 따라갑니다. 이 템플릿은 [CrawlSpider](../spiders/generic-templates.md#crawlspider)를 기반으로 하므로, `rules()`를 재정의하고 직접 설정한 [LinkExtractor](../spiders/generic-templates.md#linkextractor-reference)로 크롤링을 조절할 수 있습니다. `allow`로 원하는 URL 패턴만 허용하고, `deny`로 로그인 페이지, 태그 목록, 인쇄용 페이지 같은 불필요한 패턴을 제외합니다.

```python
from scrapling.spiders import CrawlRule, LinkExtractor, ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/"]
    allowed_domains = {"example.com"}

    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/docs/", deny=[r"/docs/changelog/", r"\?print="]))]
```

`deny`가 `allow`보다 우선합니다. 일반 **CrawlSpider**처럼 규칙에 `priority`나 `process_request` 훅을 지정할 수도 있습니다.

## 벡터 저장소에 전달하기 {#feeding-a-vector-store}

JSONL 출력은 어떤 임베딩 파이프라인에도 연결할 수 있습니다. 간단한 예제입니다.

```python
import json

with open("docs.jsonl", encoding="utf-8") as f:
    for line in f:
        page = json.loads(line)
        for chunk in split_into_chunks(page["markdown"]):
            vector_store.add(text=chunk, metadata={"url": page["url"], "title": page["title"]})
```

Spider의 `css_selector`로 텍스트를 나누기 전에 반복되는 공통 부분을 제거하세요. 뒤 단계에서 다시 정리할 필요가 줄어듭니다. 임베딩에 불필요한 내용이 적을수록 검색 품질이 좋아집니다.

## 대화형으로 사용하기 {#interactive-alternatives}

파이프라인 대신 대화로 스크래핑하려면 [MCP 서버](mcp-server.md)를 사용하세요. 같은 Markdown 추출 기능을 AI 챗봇의 도구로 제공합니다. [Agent Skill](agent-skill.md)은 코딩 에이전트가 이런 코드를 직접 작성하도록 돕습니다.
