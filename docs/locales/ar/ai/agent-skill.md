---
title: "مهارة Scrapling لوكلاء البرمجة: التثبيت والاستخدام"
description: "ثبّت مهارة Scrapling لوكيل البرمجة. وفّر له أمثلة ومراجع حديثة عن جلب الصفحات وتحليلها والزحف إلى المواقع."
---

# مهارة Scrapling لوكلاء البرمجة {#scrapling-agent-skill}

يمنح [خادم MCP](mcp-server.md) مساعد الذكاء الاصطناعي أدوات لاستخراج بيانات المواقع نيابة عنك. أما **مهارة Scrapling لوكلاء البرمجة** فتعلّم الوكيل استخدام المكتبة نفسها، ليكتب كودًا يطابق الـ API الحالي بدلًا من التخمين اعتمادًا على بيانات تدريب قديمة.

تتبع المهارة مواصفات [AgentSkills](https://agentskills.io/specification)، لذلك يستطيع [Claude Code](https://claude.com/product/claude-code) و[OpenClaw](https://github.com/openclaw/openclaw) وغيرهما من أدوات الوكلاء قراءتها. تجمع إرشادات الجلب والتحليل والزحف وMCP وRAG في مراجع Markdown يحمّلها الوكيل عند الحاجة، مع أمثلة جاهزة للتشغيل. وهكذا يستطيع الإجابة عن معظم أسئلة Scrapling وكتابة كود صحيح لاستخراج البيانات دون مغادرة المحرر.

توجد المهارة في مجلد [agent-skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill) داخل المستودع باسم `scrapling-official`، ويتبع إصدارها دائمًا إصدار المكتبة.

## التثبيت {#installation}

### Skills.sh {#skillssh}

ثبّت المهارة من المستودع باستخدام أداة [skills.sh](https://skills.sh) لسطر الأوامر:

```bash
npx skills add D4Vinci/Scrapling --skill scrapling-official
```

تكتشف الأداة الوكلاء المثبّتين لديك وتضيف المهارة إليهم.

### Clawhub {#clawhub}

إذا كنت تستخدم OpenClaw، يمكنك تثبيت المهارة عبر [Clawhub](https://docs.openclaw.ai/tools/clawhub):

```bash
clawhub install scrapling-official
```

أو ثبّتها من [صفحتها على Clawhub](https://clawhub.ai/D4Vinci/scrapling-official).

### التنزيل اليدوي {#manual-download}

نزّل ملف ZIP الخاص بالمهارة [مباشرة من المستودع](https://github.com/D4Vinci/Scrapling/raw/refs/heads/main/agent-skill/Scrapling-Skill.zip)، ثم فكّه داخل مجلد مهارات الوكيل. في Claude Code، هذا المجلد هو `~/.claude/skills/`.

## محتويات المهارة {#whats-inside}

- **`SKILL.md`**: نقطة البداية التي يقرأها الوكيل أولًا. تشرح الإعداد، واختيار أداة الجلب، وقواعد الأمان التي يجب أن يتبعها، مثل تمرير `--ai-targeted` دائمًا إلى أوامر CLI للحماية من حقن التعليمات.
- **`references/`**: نسخ Markdown من صفحات التوثيق، تشمل التحليل والجلب والعناكب وخادم MCP والتكاملات. تُحمّل عند الحاجة فقط، فلا تستهلك مساحة سياق الوكيل قبل أن يحتاج إليها.
- **`examples/`**: سكربتات جاهزة للتشغيل يستطيع الوكيل نسخ الكود منها.

اختبرنا المهارة مع OpenClaw وClaude Code. إذا واجهت مشكلة، افتح [بلاغًا](https://github.com/D4Vinci/Scrapling/issues/new/choose) أو تواصل معنا على [خادم Discord](https://discord.gg/EMgGbDceNQ).
