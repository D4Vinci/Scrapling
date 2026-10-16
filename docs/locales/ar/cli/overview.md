---
title: "واجهة Scrapling لسطر الأوامر: استخرج البيانات من الطرفية"
description: "ثبّت أدوات Scrapling للطرفية، واختر بين أوامر extract والبيئة التفاعلية وخادم MCP. اتبع الدليل المناسب لمهمتك."
---

# واجهة سطر الأوامر {#command-line-interface}

منذ الإصدار 0.3، تشمل Scrapling واجهة قوية لسطر الأوامر توفر ثلاث إمكانات رئيسية:

1. **البيئة التفاعلية**: بيئة لاستخراج بيانات الويب مبنية على IPython، وتوفر اختصارات وأدوات مفيدة كثيرة.
2. **أوامر الاستخراج**: استخرج بيانات المواقع من الطرفية دون كتابة كود.
3. **الأوامر المساعدة**: أدوات التثبيت والإدارة.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## المتطلبات {#requirements}

يتطلب هذا القسم تثبيت مجموعة المتطلبات الإضافية `shell` كما يلي:

```bash
pip install "scrapling[shell]"
```

للجلب باستخدام المتصفح، ثبّت متطلبات المتصفح أيضًا:

```bash
scrapling install
```

ينزّل هذا الأمر Chromium ومتطلبات النظام اللازمة له، ويحدّث قائمة TLD. لا تحتاج طلبات HTTP إلى هذه الخطوة.
