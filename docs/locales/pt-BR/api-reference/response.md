---
title: "Referência da API de Response"
description: "Veja status, cabeçalhos, conteúdo, metadados, conversão para Markdown e follow. Extraia dados com os métodos herdados de Selector."
---

# Classe Response {#response-class}

A classe `Response` contém as respostas HTTP de todos os fetchers. Ela dá acesso ao status, aos cabeçalhos, ao conteúdo e aos cookies, além de permitir o uso de um `Selector` para analisar a resposta.

Você pode importar a classe `Response` assim:

```python
from scrapling.engines.toolbelt.custom import Response
```

## ::: scrapling.engines.toolbelt.custom.Response
    handler: python
    :docstring:
