---
title: "Modelos de spiders para links, mapas do site, feeds e Markdown"
description: "Escolha entre CrawlSpider, SitemapSpider, XMLFeedSpider, CSVFeedSpider e ContentSpider. Defina regras para coletar páginas, linhas de feeds ou documentos Markdown."
---

# Modelos genéricos de spiders {#generic-spider-templates}

A maioria dos rastreamentos segue um destes dois padrões: seguir links que correspondam a uma regra ou percorrer todas as URLs de um mapa do site. O Scrapling inclui modelos para os dois, para que você não precise repetir a mesma lógica de `parse()` toda vez.

`CrawlSpider` e `SitemapSpider` usam `LinkExtractor`, que extrai URLs de um `Response` ou filtra uma URL com `matches()`. `SitemapSpider` também analisa o conteúdo de sitemap.xml e sitemap_index.xml, com ou sem compressão gzip.

Você pode usar `LinkExtractor` diretamente em qualquer `Spider.parse()`. Os modelos apenas poupam o trabalho de conectar essas partes.

## CrawlSpider {#crawlspider}

`CrawlSpider` segue links automaticamente conforme as regras que você definir.

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class QuotesSpider(CrawlSpider):
    name = "blog"
    start_urls = ["https://quotes.toscrape.com/"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination, no callback
        ]

    async def parse_author(self, response):
        yield {
            '.author-title': response.css('.author-title::text').get(),
            "birthday": response.css('.author-born-date::text').get(),
            "url": response.url,
        }

result = QuotesSpider().start()
```

Um `CrawlRule` combina um `LinkExtractor` com três opções: `callback`, um método do spider; `priority`, para mudar a prioridade do `Request` gerado; e `process_request`, um método que modifica cada `Request` antes de entregá-lo. O `parse()` padrão aplica todas as regras a cada resposta e produz um `Request` para cada URL correspondente.

Se uma regra não tiver callback, as URLs correspondentes passam para o `parse()` padrão do spider. Isso é útil para paginação: você pode extrair os links das próximas páginas sem criar outro método para processá-los.

### Ordem do rastreamento {#crawl-order}

Defina `crawl_strategy` em `CrawlSpider` ou em suas subclasses, incluindo `ContentSpider`, para escolher a próxima solicitação pendente:

| `crawl_strategy` | Ordem entre solicitações com o mesmo `Request.priority` |
|------------------|---------------------------------------------------------|
| `"bfs"` (padrão) | Primeiro a solicitação mais antiga na fila |
| `"dfs"` | Primeiro a última solicitação adicionada à fila |

O Scheduler sempre escolhe primeiro as solicitações com maior `Request.priority`. A estratégia só ordena as que têm a mesma prioridade.

Use `concurrent_requests = 1` para processar uma solicitação por vez na ordem escolhida. URLs duplicadas continuam sendo filtradas: encontrar uma URL de novo não muda a posição da solicitação na fila. Com solicitações paralelas, as páginas podem terminar em outra ordem, e os níveis ou ramos do rastreamento podem se sobrepor.

Mantenha o mesmo `crawl_strategy` ao retomar de um checkpoint.

### Combinar regras com sua própria lógica {#combining-rules-with-custom-logic}

Redefina `parse()` e chame `super().parse(response)` para manter as regras e adicionar seus próprios resultados:

```python
class MySpider(CrawlSpider):
    def rules(self):
        return [CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post)]

    async def parse(self, response):
        yield {"page_url": response.url}
        async for req in super().parse(response):
            yield req
```

### Modificar solicitações com `process_request` {#mutating-requests-with-process_request}

```python
def add_priority(self, request, response):
    request.priority = 10
    return request

def rules(self):
    return [CrawlRule(
        LinkExtractor(allow=r"/posts/"),
        callback=self.parse_post,
        process_request=self.add_priority,
    )]
```

## SitemapSpider {#sitemapspider}

`SitemapSpider` inicia o rastreamento com as URLs de sitemap.xml. Usa a mesma API `rules()` de `CrawlSpider`, então a forma de configurar é parecida.

```python
from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/products/"), callback=self.parse_product),
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}

    async def parse_product(self, response):
        yield {"sku": response.css(".sku::text").get()}

result = MySitemap().start()
```

### Como cada URL é encaminhada {#how-urls-are-dispatched}

Para cada URL do mapa do site, `SitemapSpider` verifica `LinkExtractor.matches(url)` de cada regra em ordem. A primeira regra correspondente é usada, e um `Request` é produzido com seu callback. Se nenhuma regra corresponder e `rules()` contiver regras, a URL será descartada. Se `rules()` retornar uma lista vazia, todas as URLs passarão para `parse()` do spider. Você precisa redefinir esse método, pois ele lança `NotImplementedError` por padrão.

### Índices de mapas do site {#sitemap-indexes}

Quando `SitemapSpider` encontra um `<sitemapindex>`, um mapa de outros mapas do site, ele percorre cada mapa filho automaticamente. Para escolher quais seguir, atribua um `LinkExtractor` a `sitemap_follow`:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/sitemap.xml"]
    sitemap_follow = LinkExtractor(allow=r"/posts-sitemap-\d+\.xml")  # only post sitemaps
```

### Suporte a robots.txt {#robotstxt-support}

Adicione uma URL de `robots.txt` diretamente em `sitemap_urls`. `SitemapSpider` vai detectá-la, extrair todos os mapas do site indicados e seguir cada um:

```python
class MySitemap(SitemapSpider):
    name = "sm"
    sitemap_urls = ["https://example.com/robots.txt"]
```

### URLs em outros idiomas {#alternate-language-urls}

Defina `sitemap_alternate_links = True` para que as URLs de `<xhtml:link rel="alternate" hreflang="...">` também passem pelas suas regras.

## XMLFeedSpider {#xmlfeedspider}

`XMLFeedSpider` percorre os nós de um feed XML, como RSS, Atom ou feeds de produtos. Defina `itertag` com o nome do nó que você quer ler, que é `"item"` por padrão, e redefina `parse_node()`. Esse método é chamado uma vez para cada nó correspondente:

```python
from scrapling.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = "rss"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "item"

    async def parse_node(self, response, node):
        yield {
            "title": node.findtext("title"),
            "link": node.findtext("link"),
            "date": node.findtext("pubDate"),
        }

result = RSSSpider().start()
```

Assim como os outros callbacks, `parse_node()` também pode produzir objetos `Request`. Por exemplo, use `response.follow(node.findtext("link"), callback=self.parse_post)` para percorrer as páginas indicadas pelo feed.

### Como os nós são encontrados e analisados {#how-nodes-are-matched-and-parsed}

Cada nó recebido por `parse_node()` é um elemento de `lxml` com todos os namespaces removidos. Assim, você pode usar `node.findtext("title")`, `node.find("thumbnail").get("url")` e `node.xpath(...)`, que diferencia maiúsculas e minúsculas, sem definir mapas de namespaces. Um `itertag` simples como `"entry"` busca nós pelo nome, independentemente do namespace. Isso funciona para Atom e para a maioria dos feeds com namespaces. Para buscar em um namespace específico, use um `itertag` com prefixo e defina esse prefixo em `namespaces`:

```python
class ThumbnailSpider(XMLFeedSpider):
    name = "thumbs"
    start_urls = ["https://example.com/feed.xml"]
    itertag = "media:thumbnail"
    namespaces = (("media", "http://search.yahoo.com/mrss/"),)

    async def parse_node(self, response, node):
        yield {"thumbnail": node.get("url")}
```

Feeds comprimidos com gzip, seja com extensão `.xml.gz` ou com content-type de gzip, são descomprimidos automaticamente com as mesmas proteções do spider de mapas do site. Se o XML estiver malformado, um aviso será registrado em vez de interromper o rastreamento.

## CSVFeedSpider {#csvfeedspider}

`CSVFeedSpider` percorre as linhas de um feed CSV. Redefina `parse_row()`, que recebe cada linha como um dicionário cujas chaves são os nomes das colunas:

```python
from scrapling.spiders import CSVFeedSpider

class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]

    async def parse_row(self, response, row):
        yield {"product": row["title"], "price": float(row["price"])}

result = PriceSpider().start()
```

Por padrão, a primeira linha contém os nomes das colunas. Se o feed não tiver essa linha, informe os nomes em `headers`. Use `delimiter`/`quotechar` para arquivos que não seguem o formato comum com vírgulas:

```python
class PriceSpider(CSVFeedSpider):
    name = "prices"
    start_urls = ["https://example.com/products.csv"]
    headers = ["title", "price", "url"]
    delimiter = ";"
```

Feeds com gzip também são descomprimidos automaticamente, como em **XMLFeedSpider**.

<a id="sitetomarkdownspider"></a>

## ContentSpider {#contentspider}

`ContentSpider` usa **CrawlSpider** para percorrer um site e converter cada página em Markdown limpo, pronto para usar com um LLM. Produz um item por página e, se você quiser, salva cada página em seu próprio arquivo Markdown:

```python
from scrapling.spiders import ContentSpider

class DocsSpider(ContentSpider):
    name = "docs"
    start_urls = ["https://example.com/docs/"]
    allowed_domains = {"example.com"}
    output_dir = "docs_markdown"

result = DocsSpider().start()
```

Você precisa definir `allowed_domains` para limitar o rastreamento ao site escolhido. A página [Criar sistemas RAG](../ai/building-rag-systems.md) explica todas as opções e como usar os resultados em um fluxo RAG.

## Usar `LinkExtractor` diretamente {#using-linkextractor-directly}

Você não precisa usar os modelos. `LinkExtractor` funciona dentro de qualquer `Spider`:

```python
from scrapling.spiders import Spider, LinkExtractor

class CustomSpider(Spider):
    name = "custom"
    start_urls = ["https://example.com"]

    def __init__(self):
        super().__init__()
        self._links = LinkExtractor(allow=r"/posts/", deny_domains="ads.example.com")

    async def parse(self, response):
        for url in self._links.extract(response):
            yield response.follow(url, callback=self.parse_post)

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

## Referência de LinkExtractor {#linkextractor-reference}

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `allow` | `()` | Padrões de URL permitidos. Vazio significa permitir todas. Aceita uma string, um `Pattern` compilado ou um iterável de qualquer um dos dois |
| `deny` | `()` | Padrões de URL descartados. Sempre têm prioridade sobre `allow` |
| `allow_domains` | `()` | Nomes de host permitidos. Inclui subdomínios automaticamente: `example.com` inclui `api.example.com` |
| `deny_domains` | `()` | Nomes de host descartados |
| `restrict_css` | `()` | Seletores CSS que limitam a extração a uma área do DOM |
| `restrict_xpath` | `()` | Seletores XPath que limitam a extração a uma área do DOM |
| `tags` | `("a", "area")` | Tags dos elementos em que os links são buscados |
| `attrs` | `("href",)` | Atributos dessas tags de onde as URLs são lidas |
| `canonicalize` | `True` | Ordena os parâmetros de consulta e normaliza o caminho |
| `strip` | `True` | Remove espaços em branco das pontas das URLs extraídas |
| `keep_fragment` | `False` | Mantém `#fragment` ao normalizar a URL |
| `deny_extensions` | `IGNORED_EXTENSIONS` | Extensões descartadas, como pdf, zip, imagens e vídeos |
| `process` | `None` | Função opcional aplicada a cada URL extraída antes dos filtros. Retorne um valor que seja avaliado como falso para descartá-la |

`LinkExtractor.extract(response)` retorna uma `list[str]` de URLs absolutas, filtradas e sem duplicatas.

`LinkExtractor.matches(url)` retorna um `bool`. Aplica a uma URL os filtros de padrões permitidos e excluídos, domínios e extensões. `SitemapSpider` usa esse método para escolher URLs sem precisar de um `Response`.
