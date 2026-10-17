---
title: "Selector e Selectors do Scrapling: dados e navegação"
description: "Entenda como Selector e Selectors guardam HTML, texto e atributos. Extraia valores, resolva URLs e percorra elementos pais, filhos e irmãos."
---

# Classes principais do analisador {#parsing-main-classes}

!!! success "Antes de começar"

    - Leia [Buscar elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de um objeto [Selector](../parsing/main_classes.md#selector).

Depois de ver as formas de selecionar elementos e seus recursos, vamos conhecer melhor a classe [Selector](#selector) e os outros objetos. Assim, você entende melhor como o analisador funciona.

A classe [Selector](#selector) é a base do analisador do Scrapling. Ela analisa HTML e permite selecionar elementos. Você pode importá-la de qualquer uma destas formas:
```python
from scrapling import Selector
from scrapling.parser import Selector
```
Depois, use-a diretamente, como vimos na [visão geral](../overview.md):
```python
page = Selector(
    '<html>...</html>',
    url='https://example.com'
)

# Then select elements as you like
elements = page.css('.product')
```
Ao passar código HTML ou obter um site, o principal objeto com que você trabalha é um [Selector](#selector). Operações de seleção ou navegação que retornam elementos da página entregam um [Selector](#selector) ou um [Selectors](#selectors). Isso não se aplica às operações que retornam texto ou outros valores.

A página é um [Selector](#selector), e cada elemento dentro dela também é um [Selector](#selector). O texto dos elementos e dos atributos usa [TextHandler](#texthandler). Os atributos de cada elemento ficam em [AttributesHandler](#attributeshandler). Veremos os dois depois. Primeiro, vamos focar em [Selector](#selector).

## Selector {#selector}
### Argumentos {#arguments-explained}
O mais importante é `content`, que recebe o HTML que você quer analisar como `str` ou `bytes`.

`url` define a URL da página, usada para resolver links relativos e separar os dados adaptativos salvos por domínio. Os argumentos `adaptive`, `storage` e `storage_args` configuram o recurso [adaptativo](adaptive.md). Eles não fazem diferença se você não usar esse recurso.

Estes argumentos controlam como o HTML é processado:

- **encoding**: codificação usada para analisar o HTML. O padrão é `UTF-8`.
- **keep_comments**: define se os comentários HTML serão mantidos ao analisar a página. Fica desativado por padrão, pois os comentários podem causar problemas na extração.

Vamos deixar `huge_tree` e `root` para depois para não complicar esta página.
São recursos avançados que você não precisa conhecer para começar. A seção de desenvolvimento cobre esses detalhes se você quiser se aprofundar.

A maioria das propriedades da página e de seus elementos só é carregada quando você a usa, como o conteúdo de texto. Esse carregamento sob demanda é um dos motivos da velocidade do Scrapling :)

### Propriedades {#properties}
Já vimos parte disso na [visão geral](../overview.md), mas aqui vamos explicar com mais detalhes e exemplos mais completos. As propriedades para percorrer a página ficam na seção de [navegação](#traversal).

Para os exemplos, vamos analisar esta página HTML:
```html
<html>
  <head>
    <title>Some page</title>
  </head>
  <body>
    <div class="product-list">
      <article class="product" data-id="1">
        <h3>Product 1</h3>
        <p class="description">This is product 1</p>
        <span class="price">$10.99</span>
        <div class="hidden stock">In stock: 5</div>
      </article>
    
      <article class="product" data-id="2">
        <h3>Product 2</h3>
        <p class="description">This is product 2</p>
        <span class="price">$20.99</span>
        <div class="hidden stock">In stock: 3</div>
      </article>
    
      <article class="product" data-id="3">
        <h3>Product 3</h3>
        <p class="description">This is product 3</p>
        <span class="price">$15.99</span>
        <div class="hidden stock">Out of stock</div>
      </article>
    </div>

    <script id="page-data" type="application/json">
      {
        "lastUpdated": "2024-09-22T10:30:00Z",
        "totalProducts": 3
      }
    </script>
  </body>
</html>
```
Carregue a página como antes:
```python
from scrapling import Selector
page = Selector(html_doc)
```
Obtenha todo o texto da página, incluindo os elementos internos:
```python
>>> page.get_all_text()
'Some page\n\n    \n\n      \nProduct 1\nThis is product 1\n$10.99\nIn stock: 5\nProduct 2\nThis is product 2\n$20.99\nIn stock: 3\nProduct 3\nThis is product 3\n$15.99\nOut of stock'
```
Obtenha o primeiro artigo, que usaremos como exemplo:
```python
article = page.find('article')
```
Da mesma forma, obtenha todo o texto do elemento e de seus elementos internos:
```python
>>> article.get_all_text()
'Product 1\nThis is product 1\n$10.99\nIn stock: 5'
```
Se você tentar ler apenas o texto direto, o resultado será vazio. No HTML acima, esse elemento não tem texto fora dos filhos:
```python
>>> article.text
''
```
O método `get_all_text` aceita estes argumentos opcionais:

1. **separator**: separador usado para unir os textos encontrados. O padrão é '\n'.
2. **strip**: remove os espaços das extremidades de cada texto antes de uni-los. Fica desativado por padrão.
3. **ignore_tags**: tupla de nomes de tags que serão ignoradas junto com todo o conteúdo dentro delas. O padrão é `('script', 'style',)`.
4. **valid_values**: coleta apenas textos com conteúdo. Ignora textos vazios ou só com espaços. Fica ativado por padrão.

O texto retornado é um [TextHandler](#texthandler), não uma string comum. Veremos isso depois. Se ele contiver JSON válido, você pode usar `.json()`:
```python
>>> script = page.find('script')
>>> script.json()
{'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
```
Obtenha a tag do elemento:
```python
>>> article.tag
'article'
```
Se fizer isso diretamente na página, estará trabalhando com o elemento raiz `html`:
```python
>>> page.tag
'html'
```
A mesma ideia vale para `page` e `element`, então não vamos repeti-la.

Obtenha os atributos do elemento:
```python
>>> print(article.attrib)
{'class': 'product', 'data-id': '1'}
```
Acesse um atributo específico de qualquer uma destas formas:
```python
article.attrib['class']
article.attrib.get('class')
article['class']  # new in v0.3
```
Verifique se um atributo existe com um destes métodos:
```python
'class' in article.attrib
'class' in article  # new in v0.3
```
Obtenha o HTML do elemento:
```python
>>> article.html_content
'<article class="product" data-id="1"><h3>Product 1</h3>\n        <p class="description">This is product 1</p>\n        <span class="price">$10.99</span>\n        <div class="hidden stock">In stock: 5</div>\n      </article>'
```
Obtenha uma versão do HTML com formatação mais fácil de ler:
```python
print(article.prettify())
```
```html
<article class="product" data-id="1"><h3>Product 1</h3>
    <p class="description">This is product 1</p>
    <span class="price">$10.99</span>
    <div class="hidden stock">In stock: 5</div>
</article>
```
Use `.body` para obter o conteúdo original da página. Desde a v0.4, nos objetos `Response` dos fetchers, `.body` sempre retorna `bytes`.
```python
>>> page.body
'<html>\n  <head>\n    <title>Some page</title>\n  </head>\n  ...'
```
Obtenha todos os ancestrais do elemento na árvore DOM:
```python
>>> article.path
[<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>,
 <data='<body> <div class="product-list"> <artic...' parent='<html><head><title>Some page</title></he...'>,
 <data='<html><head><title>Some page</title></he...'>]
```
Gere um seletor CSS curto, se possível. Caso contrário, gere um completo:
```python
>>> article.generate_css_selector
'body > div > article'
>>> article.generate_full_css_selector
'body > div > article'
```
O mesmo com XPath:
```python
>>> article.generate_xpath_selector
"//body/div/article"
>>> article.generate_full_xpath_selector
"//body/div/article"
```

### Navegação {#traversal}
Com os elementos anteriores, vamos ver as propriedades e os métodos para percorrer a página.

Se você não conhece a árvore DOM ou estruturas de árvore, esta parte pode ser um pouco confusa. Recomendo ler sobre esses conceitos para entendê-los melhor.

Aqui vai uma explicação rápida para começar.<br/>
O elemento `html` é a raiz da árvore da página, já que toda página começa com um elemento `html`.<br/>
Logo abaixo ficam elementos como `head` e `body`. Eles são filhos de `html`, e esse elemento `html` é o pai deles. Por sua vez, `head` e `body` são irmãos porque têm o mesmo pai.

Acesse o pai de um elemento:
```python
>>> article.parent
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
>>> article.parent.tag
'div'
```
Você pode encadear essa propriedade. O mesmo vale para as propriedades e os métodos parecidos que veremos.
```python
>>> article.parent.parent.tag
'body'
```
Obtenha os filhos de um elemento:
```python
>>> article.children
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Obtenha todos os elementos abaixo dele, incluindo os níveis mais profundos. Funciona como `children`, mas percorre todos os níveis:
```python
>>> article.below_elements
[<data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>]
```
Neste caso, o resultado é igual ao de `children`, pois os filhos não têm outros filhos.

Este exemplo com o elemento da classe `product-list` mostra melhor a diferença entre `children` e `below_elements`:
```python
>>> products_list = page.css('.product-list')[0]
>>> products_list.children
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]

>>> products_list.below_elements
[<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<h3>Product 1</h3>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<p class="description">This is product 1...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<span class="price">$10.99</span>' parent='<article class="product" data-id="1"><h3...'>,
 <data='<div class="hidden stock">In stock: 5</d...' parent='<article class="product" data-id="1"><h3...'>,
 <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
...]
```
Obtenha os irmãos de um elemento:
```python
>>> article.siblings
[<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
 <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
```
Obtenha o próximo elemento:
```python
>>> article.next
<data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>
```
A mesma lógica vale para `previous`:
```python
>>> article.previous  # It's the first child, so it doesn't have a previous element
>>> second_article = page.css('.product[data-id="2"]')[0]
>>> second_article.previous
<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>
```
Verifique rapidamente se um elemento tem uma classe específica:
```python
>>> article.has_class('product')
True
```
Se precisar ir além do pai, você pode percorrer todos os ancestrais de um elemento:
```python
for ancestor in article.iterancestors():
    # do something with it...
```
Você também pode buscar um ancestral que atenda a uma condição. Passe uma função que receba um [Selector](#selector) e retorne `True` se a condição for atendida ou `False` caso contrário:
```python
>>> article.find_ancestor(lambda ancestor: ancestor.has_class('product-list'))
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>

>>> article.find_ancestor(lambda ancestor: ancestor.css('.product-list'))  # Same result, different approach
<data='<div class="product-list"> <article clas...' parent='<body> <div class="product-list"> <artic...'>
```
## Selectors {#selectors}
`Selectors` é a versão em lista de [Selector](#selector). Ela herda do tipo `List` do Python, mantendo suas propriedades e métodos de `List`. Também adiciona métodos para trabalhar com os objetos [Selector](#selector) que contém.

Em [Selector](#selector), os métodos e as propriedades que retornam vários elementos entregam um objeto [Selectors](#selectors).

Desde a v0.4, todos os métodos de seleção retornam objetos [Selector](#selector)/[Selectors](#selectors), inclusive ao selecionar texto ou atributos. Nós de texto obtidos com `::text`, `/text()`, `::attr()` ou `/@attr` são envolvidos em objetos [Selector](#selector). Seu `tag` é `"#text"`, e sua propriedade `text` retorna o valor do texto. As outras propriedades retornam valores vazios ou padrão sem causar erros.

```python
page.css('a::text')              # -> Selectors (of text node Selectors)
page.xpath('//a/text()')         # -> Selectors
page.css('a::text').get()        # -> TextHandler (the first text value)
page.css('a::text').getall()     # -> TextHandlers (all text values)
page.css('a::attr(href)')        # -> Selectors
page.xpath('//a/@href')          # -> Selectors
page.css('.price_color')         # -> Selectors
```

### Métodos de extração de dados {#data-extraction-methods}
Desde a v0.4, [Selector](#selector) e [Selectors](#selectors) oferecem `get()`, `getall()` e seus aliases `extract_first` e `extract`, seguindo as convenções do Scrapy. O método antigo `get_all()` foi removido.

**Em um objeto [Selector](#selector):**

- `get()` retorna um `TextHandler`: o valor do texto, se for um nó de texto, ou o HTML externo completo como string, se for um elemento HTML.
- `getall()` retorna uma lista `TextHandlers` com essa única string.
- `extract_first` é um alias de `get()`, e `extract` é um alias de `getall()`.

```python
>>> page.css('h3')[0].get()        # Outer HTML of the element
'<h3>Product 1</h3>'

>>> page.css('h3::text')[0].get()  # Text value of the text node
'Product 1'
```

**Em um objeto [Selectors](#selectors):**

- `get(default=None)` retorna a string do **primeiro** elemento, ou `default` se a lista estiver vazia.
- `getall()` converte **todos** os elementos em strings e retorna uma lista `TextHandlers`.
- `extract_first` é um alias de `get()`, e `extract` é um alias de `getall()`.

```python
>>> page.css('.price::text').get()      # First price text
'$10.99'

>>> page.css('.price::text').getall()   # All price texts
['$10.99', '$20.99', '$15.99']

>>> page.css('.price::text').get('')    # With default value
'$10.99'
```

Esses métodos funcionam com todos os tipos de seleção, como CSS, XPath e `find`. São a forma recomendada de extrair texto e atributos com um estilo compatível com Scrapy.

Agora, vamos ver o que mais [Selectors](#selectors) oferece.
### Propriedades {#properties_1}
Além das operações normais das listas do Python, como percorrer os itens e obter uma fatia, você pode fazer o seguinte:

Executar seletores CSS e XPath diretamente nos objetos [Selector](#selector) da lista. Os tipos retornados são os mesmos de `css` e `xpath` em [Selector](#selector). Os argumentos também são parecidos, mas `adaptive` não está disponível aqui. Isso facilita encadear os métodos.
```pycon
>>> page.css('.product h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
>>> page.css('.product').css('h3::text').getall()
['Product 1', 'Product 2', 'Product 3']
```
Executar `re` e `re_first` diretamente, com os mesmos argumentos de [Selector](#selector). Vamos explicá-los na seção de [TextHandler](#texthandler).

Aqui, `re_first` funciona de outra forma: executa `re` em cada [Selector](#selector) e retorna o primeiro que tiver um resultado. `re` retorna um [TextHandlers](#texthandlers) que reúne todos os objetos [TextHandler](#texthandler) em um único [TextHandlers](#texthandlers).
```pycon
>>> page.css('.price::text').re(r'[\d.]+')
['10.99', '20.99', '15.99']
>>> page.css('.product h3::text').re(r'Product (\d+)')
['1', '2', '3']
```
Com `search`, você pode buscar entre os objetos [Selector](#selector) da lista. Passe uma função que receba um [Selector](#selector) como primeiro argumento e retorne True ou False. O método retorna o primeiro [Selector](#selector) que atenda à condição, ou `None` se não houver nenhum.

```pycon
>>> product = page.css('.product').search(lambda p: p.css('.price::text').get() == '$20.99')
>>> product.css('h3::text').get()
'Product 2'
```
Você também pode usar `filter`. Ele recebe uma função como `search`, mas retorna um `Selectors` com todos os objetos [Selector](#selector) que atendam à condição.

```pycon
>>> products = page.css('.product').filter(lambda p: float(p.css('.price::text').re_first(r'[\d.]+')) > 15)
>>> products.css('h3::text').getall()
['Product 2', 'Product 3']
```
Você pode acessar o primeiro ou o último elemento sem se preocupar com erros de índice:
```python
>>> page.css('.product').first   # First Selector or None
<data='<article class="product" data-id="1"><h3...'>
>>> page.css('.product').last    # Last Selector or None
<data='<article class="product" data-id="3"><h3...'>
>>> page.css('.nonexistent').first  # Returns None instead of raising IndexError
```

Para saber quantos objetos [Selector](#selector) existem em um [Selectors](#selectors), faça isto:
```python
page.css('.product').length
```
Isso equivale a:
```python
len(page.css('.product'))
```
Sim, como no JavaScript :)

## TextHandler {#texthandler}
Esta classe é importante: os métodos e as propriedades que retornam uma string usam `TextHandler`. Os que retornam uma lista de strings usam [TextHandlers](#texthandlers).

TextHandler herda da string padrão do Python, então aceita todas as suas operações. Por que usar outro nome, então?

Porque ela adiciona métodos e propriedades que as strings comuns não têm. Como é usada para textos em toda a biblioteca, você pode combinar esses recursos para escrever código mais curto e claro. Também pode importá-la e usá-la com qualquer string, como veremos [depois](../development/scrapling_custom_types.md).
### Uso {#usage}
Operações como obter uma fatia, acessar por índice ou chamar `split`, `replace` e `strip` retornam outro `TextHandler`. Assim, você pode encadeá-las. Se encontrar uma operação que retorne uma string comum em vez de `TextHandler`, abra uma issue para que também possamos adaptá-la.

Vamos começar com `re` e `re_first`. São os mesmos métodos de [Selector](#selector), [Selectors](#selectors) e [TextHandlers](#texthandlers), com os mesmos argumentos.

- `re` recebe uma expressão regular como string ou já compilada no primeiro argumento. Ele busca todas as correspondências e as retorna em um [TextHandlers](#texthandlers). `re_first` aceita os mesmos argumentos, mas retorna apenas a primeira correspondência como `TextHandler`.
    
    Também aceita estes argumentos:
    
    - **replace_entities**: substitui referências a entidades pelos caracteres correspondentes. Fica ativado por padrão.
    - **clean_match**: ignora espaços em branco, incluindo espaços seguidos, na comparação. Fica desativado por padrão.
    - **case_sensitive**: diferencia maiúsculas de minúsculas. Fica ativado por padrão. Se você desativá-lo, a expressão regular será compilada sem essa distinção.
  
    Já vimos estes exemplos. Eles retornam [TextHandlers](#texthandlers) porque usam `re`:
    ```pycon
    >>> page.css('.price::text').re(r'[\d.]+')
    ['10.99', '20.99', '15.99']
    >>> page.css('.product h3::text').re(r'Product (\d+)')
    ['1', '2', '3']
    ```
    Para mostrar os outros argumentos, vamos usar uma string diferente em cada exemplo:
    ```python
    >>> from scrapling import TextHandler
    >>> test_string = TextHandler('hi  there')  # Hence the two spaces
    >>> test_string.re('hi there')
    >>> test_string.re('hi there', clean_match=True)  # Using `clean_match` will clean the string before matching the regex
    ['hi there']
    
    >>> test_string2 = TextHandler('Oh, Hi Mark')
    >>> test_string2.re_first('oh, hi Mark')
    >>> test_string2.re_first('oh, hi Mark', case_sensitive=False)  # Hence disabling `case_sensitive`
    'Oh, Hi Mark'
    
    # Mixing arguments
    >>> test_string.re('hi there', clean_match=True, case_sensitive=False)
    ['hi there']
    ```
    Usar `TextHandler` em toda a biblioteca tem outra vantagem: como `html_content` retorna `TextHandler`, você pode aplicar expressões regulares diretamente ao HTML:
    ```python
    >>> page.html_content.re('div class=".*">(.*)</div')
    ['In stock: 5', 'In stock: 3', 'Out of stock']
    ```

- `.json()` tenta converter o conteúdo em um objeto JSON rapidamente. Se não for possível, gera um erro:
  ```python
  >>> page.css('#page-data::text').get()
    '\n      {\n        "lastUpdated": "2024-09-22T10:30:00Z",\n        "totalProducts": 3\n      }\n    '
  >>> page.css('#page-data::text').get().json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Se você não indicar um nó de texto ou atributo ao selecionar um elemento, seu conteúdo de texto será usado automaticamente:
  ```python
  >>> page.css('#page-data')[0].json()
  {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  A classe [Selector](#selector) acrescenta outro detalhe. Imagine que estamos trabalhando com esta página:
  ```html
  <html>
      <body>
          <div>
            <script id="page-data" type="application/json">
              {
                "lastUpdated": "2024-09-22T10:30:00Z",
                "totalProducts": 3
              }
            </script>
          </div>
      </body>
  </html>
  ```
  [Selector](#selector) tem o método `get_all_text`, que retorna um `TextHandler`.<br/><br/>
  Se você fizer isto:
  ```python
  >>> page.css('div::text').get().json()
  ```
  Receberá um erro porque o `div` não tem texto direto que possa ser convertido em JSON. Na verdade, ele não tem texto direto nenhum.<br/><br/>
  Nesse caso, você pode usar `get_all_text`:
  ```python
  >>> page.css('div')[0].get_all_text(ignore_tags=[]).json()
    {'lastUpdated': '2024-09-22T10:30:00Z', 'totalProducts': 3}
  ```
  Usei `ignore_tags` porque seu valor padrão é `('script', 'style',)`.<br/><br/>
  Há outro caso relacionado ao usar um fetcher. Imagine que você receba uma resposta JSON assim:
  ```python
  >>> page = Selector("""{"some_key": "some_value"}""")
  ```
  Como [Selector](#selector) foi feito para páginas HTML, ele trata esse conteúdo como HTML incompleto e o corrige. Se usar `html_content`, você recebe isto:
  ```python
  >>> page.html_content
  '<html><body><p>{"some_key": "some_value"}</p></body></html>'
  ```
  Aqui, você pode usar `json` diretamente:
  ```python
  >>> page.json()
  {'some_key': 'some_value'}
  ```
  Você pode estar se perguntando como isso funciona, já que `html` não tem texto direto.<br/>
  Para respostas como JSON, [Selector](#selector) mantém uma cópia do conteúdo original. Ao chamar `.json()`, ele tenta converter essa cópia primeiro. Se ela não existir, como nos elementos internos, usa o texto direto do elemento. Se também não houver texto direto, chama `get_all_text`.<br/>

- `.clean()` remove espaços em branco e espaços seguidos e retorna um novo `TextHandler`:
```python
>>> TextHandler('\n wonderful  idea, \reh?').clean()
'wonderful idea, eh?'
```
Você também pode passar `remove_entities` para que `clean` substitua entidades HTML pelos caracteres correspondentes.

- `.sort()` ordena os caracteres de uma string, de forma parecida com a ordenação de listas:
```python
>>> TextHandler('acb').sort()
'abc'
```
Ou na ordem inversa:
```python
>>> TextHandler('acb').sort(reverse=True)
'cba'
```

Outros métodos e propriedades serão adicionados com o tempo. Lembre-se de que essa classe substitui as strings comuns em quase toda a biblioteca.

## TextHandlers {#texthandlers}
Esta classe segue uma ideia parecida com [Selectors](#selectors) e [Selector](#selector). Ela herda as operações das listas comuns e adiciona `re` e `re_first`.

Aqui, `re_first` executa `re` em cada [TextHandler](#texthandler) e retorna o primeiro resultado, ou `None`. O restante funciona como já vimos. Mais métodos serão adicionados com o tempo.

## AttributesHandler {#attributeshandler}
É uma versão somente para leitura do dicionário `dict` do Python. Ela guarda os atributos de cada elemento ou objeto [Selector](#selector).
```python
>>> print(page.find('script').attrib)
{'id': 'page-data', 'type': 'application/json'}
>>> type(page.find('script').attrib).__name__
'AttributesHandler'
```
Por ser somente para leitura, usa menos recursos do que um dicionário comum. Mantém os mesmos métodos e propriedades, exceto os que permitem modificar os dados.

Ela acrescenta dois recursos simples:

- O método `search_values`:

    Em um dicionário, você pode usar `dict.get("key_name")` para buscar uma chave. Buscar pelos valores exige mais código. Este método faz isso por você: busca nos valores dos atributos e retorna um dicionário para cada correspondência.
    
    Um exemplo simples:
    ```python
    >>> for i in page.find('script').attrib.search_values('page-data'):
            print(i)
    {'id': 'page-data'}
    ```
    Ele também aceita `partial` para buscar por parte do valor:
    ```python
    >>> for i in page.find('script').attrib.search_values('page', partial=True):
            print(i)
    {'id': 'page-data'}
    ```
    Um uso mais comum seria combiná-lo com `find_all` para buscar elementos que tenham um valor específico nos atributos:
    ```python
    >>> page.find_all(lambda element: list(element.attrib.search_values('product')))
    [<data='<article class="product" data-id="1"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="2"><h3...' parent='<div class="product-list"> <article clas...'>,
     <data='<article class="product" data-id="3"><h3...' parent='<div class="product-list"> <article clas...'>]
    ```
    Todos esses elementos têm 'product' como valor de `class`.
    
    Usei `list` porque `search_values` retorna um gerador. Sem convertê-lo em lista, a condição seria `True` para todos os elementos.

- A propriedade `json_string`:

    Converte os atributos em uma string JSON. Se não for possível convertê-los, gera um erro.
  
    ```python
    >>>page.find('script').attrib.json_string
    b'{"id":"page-data","type":"application/json"}'
    ```