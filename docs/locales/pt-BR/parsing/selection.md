---
title: "Extraia dados HTML com CSS, XPath, texto e regex"
description: "Selecione elementos HTML com CSS, XPath, texto e regex. Encontre elementos parecidos e extraia dados com exemplos do Scrapling."
---

# Buscar elementos {#querying-elements}
A classe `Selector` analisa HTML. Essa escolha foi feita porque o recurso adaptativo não funciona com XML. Para feeds XML, RSS ou Atom, use [XMLFeedSpider](../spiders/generic-templates.md#xmlfeedspider), que usa um analisador XML e entrega cada nó do feed diretamente.

O Scrapling oferece cinco formas principais de buscar elementos:

1. Seletores CSS3.
2. Seletores XPath.
3. Filtros ou condições.
4. Um texto específico dentro do conteúdo.
5. Uma expressão regular que corresponda ao conteúdo.

Há outras formas indiretas de encontrar elementos, mas aqui veremos as principais. Também veremos um recurso importante: encontrar elementos parecidos com um que você já tem. Você pode ir direto para [essa seção](#finding-similar-elements).

Se você está começando com web scraping, tem pouca experiência com seletores e quer avançar rápido, recomendo começar pelos métodos `find`/`find_all` [aqui](#filters-based-searching).

## Seletores CSS e XPath {#cssxpath-selectors}

### O que são seletores CSS? {#what-are-css-selectors}
[CSS](https://en.wikipedia.org/wiki/CSS) é uma linguagem que aplica estilos a documentos HTML. Seus seletores indicam quais elementos recebem cada estilo.

O Scrapling oferece seletores CSS3 conforme a [especificação do W3C](http://www.w3.org/TR/2011/REC-css3-selectors-20110929/). Para isso, usa `cssselect`. Consulte os [seletores aceitos pelo cssselect](https://cssselect.readthedocs.io/en/latest/#supported-selectors), incluindo suas pseudofunções e pseudoelementos.

O Scrapling também inclui alguns pseudoelementos que não fazem parte do padrão:

* Para selecionar nós de texto, use ``::text``.
* Para selecionar valores de atributos, use ``::attr(name)``, em que name é o nome do atributo.

Se você já usa Scrapy ou Parsel, encontrará a mesma lógica. Assim, não precisa aprender outra forma de usar seletores :)

Para selecionar com CSS, use `css`, que retorna `Selectors`. Use `[0]` para obter o primeiro elemento, ou `.get()` / `.getall()` para extrair os valores dos pseudoseletores de texto e atributos.

### O que são seletores XPath? {#what-are-xpath-selectors}
[XPath](https://en.wikipedia.org/wiki/XPath) é uma linguagem para selecionar nós em documentos XML e também funciona com HTML. Este [guia rápido](https://devhints.io/xpath) ajuda a aprender [XPath](https://en.wikipedia.org/wiki/XPath). O Scrapling oferece XPath diretamente por meio do [lxml](https://lxml.de/).

Assim como no CSS, quem usa Scrapy ou Parsel encontrará a mesma lógica. Porém, o Scrapling não inclui a função XPath `has-class`. No lugar dela, oferece o método `has_class` para verificar as classes dos elementos encontrados.

Para selecionar com XPath, use `xpath`. Ele segue a mesma lógica do método CSS acima.

> Os métodos `css` e `xpath` têm outros argumentos relacionados ao recurso adaptativo. Vamos explicá-los na página dedicada a esse recurso.

### Exemplos de seletores {#selectors-examples}
Veja alguns exemplos equivalentes com CSS e XPath.

Selecione todos os elementos da classe `product`:
```python
products = page.css('.product')
products = page.xpath('//*[@class="product"]')
```
!!! info "Nota"

    O XPath não será preciso se o elemento tiver outra classe. **É melhor usar CSS para selecionar por classe.**

Selecione o primeiro elemento da classe `product`:
```python
product = page.css('.product')[0]
product = page.xpath('//*[@class="product"]')[0]
```
Obtenha o texto do primeiro elemento com a tag `h1`:
```python
title = page.css('h1::text').get()
title = page.xpath('//h1//text()').get()
```
Isso equivale a fazer:
```python
title = page.css('h1')[0].text
title = page.xpath('//h1')[0].text
```
Obtenha o atributo `href` do primeiro elemento com a tag `a`:
```python
link = page.css('a::attr(href)').get()
link = page.xpath('//a/@href').get()
```
Selecione o texto do primeiro `h1` que contenha `Phone` e esteja dentro de um elemento da classe `product`:
```python
title = page.css('.product h1:contains("Phone")::text').get()
title = page.xpath('//*[@class="product"]//h1[contains(text(),"Phone")]/text()').get()
```
Você pode aninhar e encadear seletores, desde que retornem resultados:
```python
page.css('.product')[0].css('h1:contains("Phone")::text').get()
page.xpath('//*[@class="product"]')[0].xpath('.//h1[contains(text(),"Phone")]/text()').get()
page.xpath('//*[@class="product"]')[0].css('h1:contains("Phone")::text').get()
```
Use `.//` para que o XPath busque a partir do elemento atual. Se começar com `//`, ele busca no documento inteiro, mesmo depois de selecionar um produto.

Outro exemplo:

Todos os links que contêm 'image' no atributo 'href':
```python
links = page.css('a[href*="image"]')
links = page.xpath('//a[contains(@href, "image")]')
for index, link in enumerate(links):
    link_value = link.attrib['href']  # Cleaner than link.css('::attr(href)').get()
    link_text = link.text
    print(f'Link number {index} points to this url {link_value} with text content as "{link_text}"')
```

## Seleção pelo conteúdo de texto {#text-content-selection}
O Scrapling permite buscar pelo texto direto de cada elemento de duas formas:

1. Com `find_by_text`, busque elementos cujo texto direto contenha o texto informado. O método oferece várias opções.
2. Com `find_by_regex`, busque elementos cujo texto direto corresponda a uma expressão regular. Ele também oferece várias opções.

Se você sabe usar expressões regulares, pode fazer com `find_by_regex` o mesmo que com `find_by_text`. Oferecemos os dois métodos para facilitar o uso por todas as pessoas.

O primeiro argumento de `find_by_text` é o texto que você procura. Em `find_by_regex`, é a expressão regular. Os dois compartilham estes argumentos:

* **first_match**: se for `True`, o valor padrão, retorna apenas o primeiro resultado.
* **case_sensitive**: se for `True`, diferencia maiúsculas de minúsculas.
* **clean_match**: se for `True`, substitui os caracteres de espaço em branco e os espaços seguidos por um único espaço antes de comparar.

Por padrão, `find_by_text` busca uma correspondência exata. O texto do elemento deve conter SOMENTE o texto informado. Para mudar isso, existe outro argumento:

* **partial**: quando ativado, faz `find_by_text` retornar elementos que contenham o texto informado, mesmo que tenham mais texto.

!!! abstract "Nota"

    `find_by_regex` aceita uma string comum ou uma expressão regular compilada como primeiro argumento. Veremos isso nos exemplos.

### Buscar elementos parecidos {#finding-similar-elements}
Um dos recursos mais úteis do Scrapling é buscar elementos parecidos com um que você já encontrou. A ideia veio do AutoScraper, mas aqui funciona com elementos obtidos por qualquer método. É comum usá-lo depois de uma busca por texto, como no AutoScraper, por isso vamos explicá-lo aqui.

Como ele funciona?

Imagine que você encontrou um produto pelo título e quer extrair os outros produtos da mesma tabela ou contêiner. Chame `.find_similar()` nesse elemento, e o Scrapling fará o seguinte:

1. Busca todos os elementos na mesma profundidade da árvore DOM.
2. Descarta os que não têm o mesmo nome de tag, de tag do pai e de tag do avô.
3. É muito provável que os elementos restantes sejam os que você procura. Como última verificação, compara seus atributos e descarta os que não são parecidos o suficiente. Você pode ajustar a porcentagem de semelhança, mas recomendo manter o padrão, a menos que ele não encontre os elementos desejados.

São vários passos, mas eles ajudam a entender o método. Veremos exemplos na próxima seção. Estes são os argumentos:

* **similarity_threshold**: controla a comparação de atributos do passo 3. O valor padrão é 0,2, ou seja, os atributos precisam ser pelo menos 20% parecidos. Use 0 para desativar essa verificação. Antes disso, recomendo conhecer os outros argumentos.
* **ignore_attributes**: nomes de atributos ignorados na última comparação. O padrão é `('href', 'src',)`, pois as URLs podem variar muito entre elementos e não são uma referência confiável.
* **match_text**: se for `True`, também compara o texto do elemento no passo 3. Não costuma ser necessário, mas depende do caso.

Vamos aos exemplos.

### Exemplos {#examples}
Veja exemplos de busca por texto e expressões regulares.

Vou usar a classe `Fetcher`, que será explicada em detalhes depois.
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://books.toscrape.com/index.html')
```
Busque o primeiro elemento cujo texto corresponda exatamente ao texto informado:
```python
>>> page.find_by_text('Tipping the Velvet')
<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>
```
Combine com `page.urljoin` para transformar o `href` relativo em uma URL completa:
```python
>>> page.find_by_text('Tipping the Velvet').attrib['href']
'catalogue/tipping-the-velvet_999/index.html'
>>> page.urljoin(page.find_by_text('Tipping the Velvet').attrib['href'])
'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'
```
Obtenha todas as correspondências, se houver mais de uma. Observe que o retorno é uma lista:
```python
>>> page.find_by_text('Tipping the Velvet', first_match=False)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
```
Obtenha todos os elementos que contenham a palavra `the`, usando uma correspondência parcial:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Requiem Red',
 'The Dirty Little Secrets ...',
 'The Coming Woman: A ...',
 'The Boys in the ...',
 'The Black Maria',
 'Mesaerion: The Best Science ...',
 "It's Only the Himalayas"]
```
A busca não diferencia maiúsculas de minúsculas. Por isso, inclui `The` além de `the`. Vamos limitar os resultados a `the`:
```python
>>> results = page.find_by_text('the', partial=True, first_match=False, case_sensitive=True)
>>> [i.text for i in results]
['A Light in the ...',
 'Tipping the Velvet',
 'The Boys in the ...',
 "It's Only the Himalayas"]
```
Obtenha o primeiro elemento cujo texto corresponda a esta expressão regular de preços:
```python
>>> page.find_by_regex(r'£[\d\.]+')
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(r'£[\d\.]+').text
'£51.77'
```
Você também pode passar uma expressão regular compilada. O Scrapling detecta o tipo de entrada e a usa:
```python
>>> import re
>>> regex = re.compile(r'£[\d\.]+')
>>> page.find_by_regex(regex)
<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>
>>> page.find_by_regex(regex).text
'£51.77'
```
Obtenha todos os elementos que correspondam à expressão regular:
```python
>>> page.find_by_regex(r'£[\d\.]+', first_match=False)
[<data='<p class="price_color">£51.77</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£53.74</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£50.10</p>' parent='<div class="product_price"> <p class="pr...'>,
 <data='<p class="price_color">£47.82</p>' parent='<div class="product_price"> <p class="pr...'>,
 ...]
```
E assim por diante...

Busque todos os elementos parecidos com o atual em posição e atributos. Neste caso, ignore o atributo 'title' na comparação:
```python
>>> element = page.find_by_text('Tipping the Velvet')
>>> element.find_similar(ignore_attributes=['title'])
[<data='<a href="catalogue/a-light-in-the-attic_...' parent='<h3><a href="catalogue/a-light-in-the-at...'>,
 <data='<a href="catalogue/soumission_998/index....' parent='<h3><a href="catalogue/soumission_998/in...'>,
 <data='<a href="catalogue/sharp-objects_997/ind...' parent='<h3><a href="catalogue/sharp-objects_997...'>,
...]
```
Há 19 elementos, não 20, porque o elemento atual não entra nos resultados.
```python
>>> len(element.find_similar(ignore_attributes=['title']))
19
```
Obtenha o atributo `href` de todos os elementos parecidos:
```python
>>> [
    element.attrib['href']
    for element in element.find_similar(ignore_attributes=['title'])
]
['catalogue/a-light-in-the-attic_1000/index.html',
 'catalogue/soumission_998/index.html',
 'catalogue/sharp-objects_997/index.html',
 ...]
```
Agora um exemplo um pouco mais completo: obter todos os dados dos livros usando esse elemento como ponto de partida.
```python
>>> first_product = element.parent.parent
>>> for product in [first_product, *first_product.find_similar()]:
        print({
            "name": product.css('h3 a::text').get(),
            "price": product.css('.price_color')[0].re_first(r'[\d\.]+'),
            "stock": product.css('.availability::text').getall()[-1].clean()
        })
{'name': 'Tipping the Velvet', 'price': '53.74', 'stock': 'In stock'}
{'name': 'A Light in the ...', 'price': '51.77', 'stock': 'In stock'}
{'name': 'Soumission', 'price': '50.10', 'stock': 'In stock'}
{'name': 'Sharp Objects', 'price': '47.82', 'stock': 'In stock'}
...
```
### Exemplos avançados {#advanced-examples}
Veja casos mais completos de uso de `find_similar`.

Extrair produtos de uma loja:
```python
def extract_product_grid(page):
    # Find the first product card
    first_product = page.find_by_text('Add to Cart').find_ancestor(
        lambda e: e.has_class('product-card')
    )

    # Find similar product cards
    products = [first_product, *first_product.find_similar()]

    return [
        {
            'name': p.css('h3::text').get(),
            'price': p.css('.price::text').re_first(r'\d+\.\d{2}'),
            'stock': 'In stock' in p.get_all_text(),
            'rating': p.css('.rating')[0].attrib.get('data-rating')
        }
        for p in products
    ]
```
Extrair linhas de uma tabela:
```python
def extract_table_data(page):
    # Find the first data row
    first_row = page.css('table tbody tr')[0]

    # Find similar rows
    rows = [first_row, *first_row.find_similar()]

    return [
        {
            'column1': row.css('td:nth-child(1)::text').get(),
            'column2': row.css('td:nth-child(2)::text').get(),
            'column3': row.css('td:nth-child(3)::text').get()
        }
        for row in rows
    ]
```
Extrair campos de um formulário:
```python
def extract_form_fields(page):
    # Find first form field container
    first_field = page.css('input')[0].find_ancestor(
        lambda e: e.has_class('form-field')
    )

    # Find similar field containers
    fields = [first_field, *first_field.find_similar()]

    return [
        {
            'label': f.css('label::text').get(),
            'type': f.css('input')[0].attrib.get('type'),
            'required': 'required' in f.css('input')[0].attrib
        }
        for f in fields
    ]
```
Extrair avaliações de um site:
```python
def extract_reviews(page):
    # Find first review
    first_review = page.find_by_text('Great product!')
    review_container = first_review.find_ancestor(
        lambda e: e.has_class('review')
    )
    
    # Find similar reviews
    all_reviews = [review_container, *review_container.find_similar()]
    
    return [
        {
            'text': r.css('.review-text::text').get(),
            'rating': r.attrib.get('data-rating'),
            'author': r.css('.reviewer::text').get()
        }
        for r in all_reviews
    ]
```
## Busca por filtros {#filters-based-searching}
Esse método é uma das melhores formas de buscar elementos no Scrapling. Ele é poderoso e costuma ser mais fácil de aprender do que seletores para quem começa com web scraping.

Inspirados em `find_all` do BeautifulSoup, os métodos `find_all` e `find` aceitam vários filtros e buscam elementos que atendam a todas as condições.

Cada tipo de argumento é interpretado assim:

* Uma string é um nome de tag.
* Um iterável, como List, Tuple ou Set, contém nomes de tags.
* Um dicionário associa nomes de atributos HTML a seus valores.
* Uma expressão regular filtra pelo conteúdo, como `find_by_regex`.
* Uma função filtra os elementos.
* Um argumento nomeado representa um atributo HTML e seu valor.

O método reúne todos os argumentos e aplica os filtros em sequência. Cada filtro recebe os resultados do anterior.

Os filtros se aplicam aos elementos da página ou do elemento atual nesta ordem:

1. Reúne os elementos com os nomes de tag informados.
2. Busca os que atendam a todos os atributos informados. Se já houver um filtro, verifica apenas os resultados dele.
3. Busca os que correspondam a todas as expressões regulares. Se já houver filtros, verifica apenas os resultados deles.
4. Busca os que atendam a todas as funções. Se já houver filtros, verifica apenas os resultados deles.

!!! note "Notas"

    1. O processo começa pelo primeiro filtro disponível na ordem acima. Se você não passar nomes de tags, mas passar atributos, ele começa no passo 2.
    2. A ordem em que você passa os argumentos não importa. Só vale a ordem explicada acima.

Os exemplos ajudam a entender melhor :)

### Exemplos {#examples_1}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://quotes.toscrape.com/')
```
Busque todos os elementos com a tag `div`:
```python
>>> page.find_all('div')
[<data='<div class="container"> <div class="row...' parent='<body> <div class="container"> <div clas...'>,
 <data='<div class="row header-box"> <div class=...' parent='<div class="container"> <div class="row...'>,
...]
```
Busque todos os div cuja classe seja `quote`:
```python
>>> page.find_all('div', class_='quote')
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
O mesmo que antes:
```python
>>> page.find_all('div', {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Busque todos os elementos cuja classe seja `quote`:
```python
>>> page.find_all({'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Busque todos os div cuja classe seja `quote` e que contenham um elemento `.text` com a palavra 'world':
```python
>>> page.find_all('div', {'class': 'quote'}, lambda e: "world" in e.css('.text::text').get())
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>]
```
Busque todos os elementos que tenham filhos:
```python
>>> page.find_all(lambda element: len(element.children) > 0)
[<data='<html lang="en"><head><meta charset="UTF...'>,
 <data='<head><meta charset="UTF-8"><title>Quote...' parent='<html lang="en"><head><meta charset="UTF...'>,
 <data='<body> <div class="container"> <div clas...' parent='<html lang="en"><head><meta charset="UTF...'>,
...]
```
Busque todos os elementos que contenham a palavra 'world' no texto:
```python
>>> page.find_all(lambda element: "world" in element.text)
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>,
 <data='<a class="tag" href="/tag/world/page/1/"...' parent='<div class="tags"> Tags: <meta class="ke...'>]
```
Busque todos os span que correspondam à expressão regular:
```python
>>> page.find_all('span', re.compile(r'world'))
[<data='<span class="text" itemprop="text">“The...' parent='<div class="quote" itemscope itemtype="h...'>]
```
Busque os div e span da classe 'quote'. Não há span assim, então só são retornados div:
```python
>>> page.find_all(['div', 'span'], {'class': 'quote'})
[<data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
 <data='<div class="quote" itemscope itemtype="h...' parent='<div class="col-md-8"> <div class="quote...'>,
...]
```
Combine vários filtros:
```python
>>> page.find_all({'itemtype':"http://schema.org/CreativeWork"}, 'div').css('.author::text').getall()
['Albert Einstein',
 'J.K. Rowling',
...]
```
Mais uma dica: busque elementos cujo atributo `href` termine com 'Einstein':
```python
>>> page.find_all({'href$': 'Einstein'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>]
```
Outra dica: busque elementos cujo atributo `href` contenha '/author/':
```python
>>> page.find_all({'href*': '/author/'})
[<data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/J-K-Rowling">(about)</a...' parent='<span>by <small class="author" itemprop=...'>,
 <data='<a href="/author/Albert-Einstein">(about...' parent='<span>by <small class="author" itemprop=...'>,
...]
```
E assim por diante...

## Gerar seletores {#generating-selectors}
Você pode gerar seletores CSS e XPath para qualquer elemento e reutilizá-los aqui ou em outro lugar. Não importa qual método usou para encontrar o elemento.

Gere um seletor CSS curto para `url_element`. Se não for possível, gere um completo:
```python
>>> url_element = page.find({'href*': '/author/'})
>>> url_element.generate_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Gere um seletor CSS completo para `url_element`, desde o início da página:
```python
>>> url_element.generate_full_css_selector
'body > div > div:nth-of-type(2) > div > div > span:nth-of-type(2) > a'
```
Gere um seletor XPath curto para `url_element`. Se não for possível, gere um completo:
```python
>>> url_element.generate_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
Gere um seletor XPath completo para `url_element`, desde o início da página:
```python
>>> url_element.generate_full_xpath_selector
'//body/div/div[2]/div/div/span[2]/a'
```
!!! abstract "Nota"

    Para criar um seletor curto, o Scrapling procura um elemento único que sirva de ponto de partida, como um elemento com atributo `id`. Neste caso, não há nenhum. Por isso, o seletor curto e o completo são iguais.

## Usar seletores com expressões regulares {#using-selectors-with-regular-expressions}
Como em `parsel`/`scrapy`, você pode usar `re` e `re_first` para extrair dados com expressões regulares. No Scrapling, eles estão disponíveis em quase todas as classes, como `Selector`/`Selectors`/`TextHandler` e `TextHandlers`. Assim, você pode usá-los diretamente em um elemento sem selecionar um nó de texto antes.

Veremos isso em detalhes ao explicar [TextHandler](main_classes.md#texthandler). Por enquanto, estes exemplos mostram como funciona:
```python
>>> page.css('.price_color')[0].re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re_first(r'[\d\.]+')
'51.77'

>>> page.css('.price_color').re(r'[\d\.]+')
['51.77',
 '53.74',
 '50.10',
 '47.82',
 '54.23',
...]

>>> page.css('.product_pod h3 a::attr(href)').re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000',
 'tipping-the-velvet_999',
 'soumission_998',
 'sharp-objects_997',
...]

>>> filtering_function = lambda e: e.parent.tag == 'h3' and e.parent.parent.has_class('product_pod')  # As above selector
>>> page.find('a', filtering_function).attrib['href'].re(r'catalogue/(.*)/index.html')
['a-light-in-the-attic_1000']

>>> page.find_by_text('Tipping the Velvet').attrib['href'].re(r'catalogue/(.*)/index.html')
['tipping-the-velvet_999']
```
E assim por diante. Vamos explicar melhor na próxima página, junto com a classe [TextHandler](main_classes.md#texthandler).