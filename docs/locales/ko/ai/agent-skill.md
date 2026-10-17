---
title: "Scrapling Agent Skill 설치와 사용법"
description: "코딩 에이전트에 Scrapling 스킬을 설치하세요. 페이지 가져오기, 파싱, 크롤링에 필요한 최신 API 예제와 참고 자료를 제공합니다."
---

# Scrapling Agent Skill {#scrapling-agent-skill}

[MCP 서버](mcp-server.md)는 AI 챗봇에 웹사이트를 스크래핑하는 도구를 제공합니다. **Scrapling Agent Skill**은 코딩 에이전트에 라이브러리 자체의 사용법을 알려 줍니다. 따라서 에이전트가 오래된 학습 데이터로 추측하는 대신, 현재 API에 맞는 Scrapling 코드를 작성할 수 있습니다.

이 스킬은 [AgentSkills](https://agentskills.io/specification) 사양을 따르므로 [Claude Code](https://claude.com/product/claude-code), [OpenClaw](https://github.com/openclaw/openclaw) 등 여러 에이전트 도구에서 읽을 수 있습니다. 페이지 가져오기, 파싱, 크롤링, MCP, RAG 안내를 필요할 때 읽는 Markdown 참고 자료로 묶어 제공합니다. 바로 실행할 수 있는 예제도 포함되어 있어, 편집기를 벗어나지 않고 대부분의 Scrapling 질문에 답하거나 올바른 스크래핑 코드를 작성할 수 있습니다.

스킬은 저장소의 [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) 디렉터리에 `scrapling-official`이라는 이름으로 있습니다. 스킬 버전은 항상 라이브러리 버전에 맞춰집니다.

## 설치 {#installation}

### Skills.sh {#skillssh}

[skills.sh](https://skills.sh) CLI로 저장소에서 스킬을 설치하세요.
```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```
CLI가 설치된 에이전트를 찾아 스킬을 추가합니다.

### Clawhub {#clawhub}

OpenClaw를 사용한다면 [Clawhub](https://docs.openclaw.ai/tools/clawhub)로 설치할 수 있습니다.
```bash
clawhub install scrapling-official
```
[Clawhub 페이지](https://clawhub.ai/D4Vinci/scrapling-official)에서 설치할 수도 있습니다.

### 직접 다운로드 {#manual-download}

스킬의 ZIP 파일을 [저장소에서 직접 다운로드](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip)한 뒤 에이전트의 스킬 디렉터리에 압축을 푸세요. Claude Code에서는 `~/.claude/skills/`입니다.

## 포함된 내용 {#whats-inside}

- **`SKILL.md`**: 에이전트가 가장 먼저 읽는 파일입니다. 설정 방법, Fetcher 선택, 지켜야 할 안전 규칙을 설명합니다. 예를 들어 프롬프트 인젝션을 막기 위해 CLI 명령에 항상 `--ai-targeted`를 전달하도록 안내합니다.
- **`references/`**: 파싱, 페이지 가져오기, Spider, MCP 서버, 통합 기능을 설명하는 문서의 Markdown 사본입니다. 필요할 때만 읽으므로 그전에는 에이전트의 컨텍스트를 차지하지 않습니다.
- **`examples/`**: 에이전트가 복사해 사용할 수 있는 실행 가능한 스크립트입니다.

이 스킬은 OpenClaw와 Claude Code에서 테스트했습니다. 문제가 생기면 [이슈](https://github.com/D4Vinci/Scrapling/issues/new/choose)를 등록하거나 [Discord 서버](https://discord.gg/EMgGbDceNQ)에 알려 주세요.
