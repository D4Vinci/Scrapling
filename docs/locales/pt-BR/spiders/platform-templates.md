---
title: "Extraia dados de produtos da Shopify com Python"
description: "Extraia o catálogo de uma loja Shopify com ShopifySpider. Defina a URL, colete as variantes dos produtos e consulte os campos de cada item."
---

# Modelos de spiders para plataformas {#platform-spider-templates}

Os modelos genéricos resolvem *padrões* de rastreamento, como seguir links e percorrer mapas do site. Os modelos para plataformas atendem a *plataformas* que oferecem a mesma estrutura de dados em muitos sites independentes. O spider já sabe onde buscar os dados. Você só precisa informar o domínio.

## ShopifySpider {#shopifyspider}

`ShopifySpider` extrai todos os produtos de uma loja Shopify pela API JSON da plataforma, sem usar o HTML do site.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

Defina `target_website` com o domínio da loja. Se estiver vazio, o spider usa o primeiro valor de `start_urls` e, se não houver nenhum, o de `allowed_domains`. Se os três estiverem vazios, lança `ValueError`. URLs completas são convertidas para seu domínio automaticamente.

### Como funciona {#how-it-works}

1. Percorre as páginas de `https://<store>/collections.json`, com 250 coleções por página, que é o limite da plataforma.
2. Para cada coleção que informa ter produtos, percorre as páginas de `/collections/<handle>/products.json`.
3. Entrega um item por variante de produto, sem repetir variantes que aparecem em várias coleções.

### Campos de cada item {#item-fields}

| Campo | Origem |
|-------|--------|
| `name` | Título do produto, mais o título da variante quando ela não é a padrão |
| `price` | Preço da variante como string, exatamente como a Shopify retorna |
| `category` | Identificador da coleção com a inicial de cada palavra em maiúscula (`summer-sale` vira `Summer Sale`) |
| `brand` | Fornecedor do produto |
| `identifier` | ID da variante |
| `sku` | SKU da variante, ou `""` se a loja não definir um |
| `stock` | `None` se a variante estiver disponível, ou `0` se estiver esgotada |
| `image_url` | Primeira imagem do produto, ou `""` |
| `url` | Página do produto dentro da coleção |
| `description` | Conteúdo de `body_html` do produto, sem as tags HTML |
| `old_price` | `compare_at_price` quando é um preço real anterior à promoção; caso contrário, `""` |
| `barcode` | Código de barras da variante, ou `""` (a maioria das lojas não o fornece nesses endpoints) |

Esses campos não são obrigatórios. Redefina `_process_product()` na sua subclasse para mudar a estrutura do item ou extrair outros campos dos dados do produto.

### Notas e limites {#notes-and-limits}

- Os endpoints JSON mostram apenas produtos publicados no canal da loja online. Por isso, `products_count` pode ser maior que a quantidade de produtos que realmente podem ser obtidos. O spider só usa um valor diferente de zero como sinal para consultar a coleção, nunca como um total esperado.
- É provável que este modelo não funcione em lojas com proteções adicionais ou senha. Mesmo quando for possível usá-lo, você terá que redefinir várias partes por conta própria.
- Todos os recursos de `Spider` continuam disponíveis: limites de concorrência, esperas, respeito a robots.txt, checkpoints e hooks do ciclo de vida.

### O que pode ser um modelo para plataformas {#what-qualifies-as-a-platform-template}

São aceitos modelos para plataformas que oferecem uma estrutura uniforme e legível por programas em muitos sites independentes, como a Shopify. Spiders para um único site não fazem parte da biblioteca, por mais popular que o site seja.
