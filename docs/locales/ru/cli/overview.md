---
title: "Scrapling CLI: сбор данных из терминала"
description: "Установите инструменты Scrapling для терминала и выберите команды извлечения, интерактивную оболочку или MCP-сервер. Откройте руководство для своей задачи."
---

# Интерфейс командной строки {#command-line-interface}

Начиная с v0.3, в Scrapling есть интерфейс командной строки с тремя основными возможностями:

1. **Интерактивная оболочка**: среда на основе IPython для сбора данных с сайтов, с удобными сокращениями и инструментами.
2. **Команды извлечения**: сбор данных с сайтов из терминала без программирования.
3. **Служебные команды**: инструменты установки и управления.

```bash
# Launch interactive shell
scrapling shell

# Convert the content of a page to markdown and save it to a file
scrapling extract get "https://example.com" content.md

# Get help for any command
scrapling --help
scrapling extract --help
```

## Требования {#requirements}
Для этого раздела установите дополнительную группу зависимостей `shell`:
```bash
pip install "scrapling[shell]"
```
Для загрузки страниц через браузер также установите его зависимости:
```bash
scrapling install
```
Команда скачивает Chromium и его системные зависимости, а также обновляет список TLD. Для HTTP-запросов этот шаг не нужен.
