---
title: "Scrapling CLI: 터미널에서 스크래핑하기"
description: "Scrapling 터미널 도구를 설치하고 추출 명령, 대화형 셸, MCP 서버 중에서 선택하세요. 작업에 맞는 안내를 확인할 수 있습니다."
---

# 명령줄 인터페이스 {#command-line-interface}

Scrapling v0.3부터 다음 세 가지 주요 기능을 갖춘 명령줄 인터페이스를 제공합니다.

1. **대화형 셸**: IPython 기반 웹 스크래핑 셸입니다. 편리한 단축 함수와 도구를 제공합니다.
2. **추출 명령**: 프로그래밍 없이 터미널에서 웹사이트를 스크래핑합니다.
3. **유틸리티 명령**: 설치와 관리를 위한 도구입니다.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## 요구 사항 {#requirements}
이 섹션의 기능을 사용하려면 `shell` 추가 의존성 그룹을 설치하세요.
```bash
pip install "scrapling[shell]"
```
브라우저로 페이지를 가져오려면 브라우저 의존성도 설치하세요.
```bash
scrapling install
```
Chromium과 시스템 의존성을 다운로드하고 TLD 목록을 갱신합니다. HTTP 요청만 사용할 때는 이 단계가 필요하지 않습니다.
