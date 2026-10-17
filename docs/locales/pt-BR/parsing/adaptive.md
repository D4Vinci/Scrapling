---
title: "Acompanhe e reencontre elementos HTML com a análise adaptativa"
description: "Salve os dados de um elemento e encontre correspondências quando o HTML mudar. Aprenda a ativar a análise adaptativa e a usar save, retrieve e relocate."
---

# Scraping adaptativo {#adaptive-scraping}

!!! success "Antes de começar"

    1. Leia a página [Buscar elementos](../parsing/selection.md) para aprender a buscar e extrair elementos de um objeto [Selector](../parsing/main_classes.md#selector).
    2. Leia a página [Classes principais](../parsing/main_classes.md) para conhecer a classe [Selector](../parsing/main_classes.md#selector).

O scraping adaptativo, antes chamado de automatch, é um dos recursos mais poderosos do Scrapling. Ele permite que seu scraper continue funcionando quando um site muda, pois acompanha e reencontra os elementos.

Imagine que você queira extrair dados de uma página com esta estrutura:
```html
<div class="container">
    <section class="products">
        <article class="product" id="p1">
            <h3>Product 1</h3>
            <p class="description">Description 1</p>
        </article>
        <article class="product" id="p2">
            <h3>Product 2</h3>
            <p class="description">Description 2</p>
        </article>
    </section>
</div>
```
Você quer extrair o primeiro produto, que tem o ID `p1`. Provavelmente usaria um seletor assim:
```python
page.css('#p1')
```
Se os responsáveis pelo site mudarem a estrutura para algo assim:
```html
<div class="new-container">
    <div class="product-wrapper">
        <section class="products">
            <article class="product new-class" data-id="p1">
                <div class="product-info">
                    <h3>Product 1</h3>
                    <p class="new-description">Description 1</p>
                </div>
            </article>
            <article class="product new-class" data-id="p2">
                <div class="product-info">
                    <h3>Product 2</h3>
                    <p class="new-description">Description 2</p>
                </div>
            </article>
        </section>
    </div>
</div>
```
O seletor deixará de funcionar e você precisará ajustar o código. É aí que entra o recurso `adaptive` do Scrapling.

Você pode ativar `adaptive` na primeira vez que selecionar um elemento. Se, na próxima vez, o seletor não o encontrar, o Scrapling usará as propriedades salvas para buscar o elemento mais parecido da página. E tudo isso sem IA :)

```python
from scrapling import Selector, Fetcher
# Before the change
page = Selector(page_source, adaptive=True, url='example.com')
# or
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
# then
element = page.css('#p1', auto_save=True)
if not element:  # One day website changes?
    element = page.css('#p1', adaptive=True)  # Scrapling still finds it!
# the rest of your code...
```
A seguir, você verá um exemplo e depois os detalhes de uso. O recurso funciona com todos os métodos de seleção, não apenas com CSS e XPath.

## Um exemplo real {#real-world-scenario}
Vamos usar um site real e um fetcher para obter seu código. Para testar uma mudança de estrutura, precisaríamos guardar o código antes da atualização e esperar o site mudar. É quase impossível saber quando isso vai acontecer, a menos que eu conheça o dono. Mas aí seria um teste combinado, haha.

Para resolver isso, vou usar o [The Web Archive](https://archive.org/) e sua [Wayback Machine](https://web.archive.org/). Esta é uma cópia do [site do StackOverFlow em 2010](https://web.archive.org/web/20100102003420/http://stackoverflow.com/). Faz tempo, né?</br>Vamos ver se o recurso adaptativo consegue extrair o mesmo botão no layout de 2010 e no atual usando um único seletor :)

Para extrair o botão Questions do layout antigo, posso usar `#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a`. Esse seletor é bem específico porque foi gerado pelo Google Chrome.


Vamos testar o mesmo seletor nas duas versões:
```python
from scrapling import Fetcher
selector = '#hmenus > div:nth-child(1) > ul > li:nth-child(1) > a'
old_url = "https://web.archive.org/web/20100102003420/http://stackoverflow.com/"
new_url = "https://stackoverflow.com/"
Fetcher.configure(adaptive = True, adaptive_domain='stackoverflow.com')
page = Fetcher.get(old_url, timeout=30)
element1 = page.css(selector, auto_save=True)[0]
# Same selector but used in the updated website
page = Fetcher.get(new_url)
element2 = page.css(selector, adaptive=True)[0]

if element1.text == element2.text:
    print('Scrapling found the same element in the old and new designs!')  # Spoiler alert: it does!
```
Aqui aparece um argumento novo: `adaptive_domain`. Para o Scrapling, `archive.org` e `stackoverflow.com` são domínios diferentes, então seus dados de `adaptive` ficam separados. Para indicar que são o mesmo site, passamos o mesmo domínio personalizado ao salvar os dados de `adaptive` dos dois.

Em um caso real, o código seria igual, mas usaria a mesma URL nas duas solicitações. Você não precisaria de `adaptive_domain`. Este é o exemplo mais próximo de um caso real que consigo mostrar. Espero que tenha ficado claro :)

Nos dois exemplos anteriores, usei as classes `Selector` e `Fetcher` para mostrar que a lógica adaptativa é a mesma.

!!! info "Informação"

    O principal motivo para criar `adaptive_domain` foi permitir que um site mude sua URL junto com o layout ou a estrutura. Com esse argumento, você pode continuar usando os dados adaptativos já salvos na nova URL. Sem ele, o Scrapling considera que é outro site e deixa de usar os dados antigos.

## Como funciona o scraping adaptativo {#how-the-adaptive-scraping-feature-works}
O scraping adaptativo tem duas etapas:

1. **Salvar**: armazena as propriedades que distinguem cada elemento.
2. **Buscar correspondências**: encontra depois os elementos com propriedades parecidas.

Imagine que você selecionou um elemento com qualquer método e quer que a biblioteca o encontre na próxima coleta, mesmo que o site mude de estrutura ou layout.

Sem entrar em muitos detalhes técnicos, o processo é este:

  1. Você pede ao Scrapling para salvar as propriedades do elemento por um dos métodos que veremos abaixo.
  2. O Scrapling salva essas propriedades no banco de dados configurado, que por padrão é o SQLite.
  3. Os responsáveis pelo site podem mudar ou remover qualquer dado do elemento. Por isso, nenhum desses dados serve como identificador único no banco. Para resolver isso, o sistema de armazenamento usa dois valores:
     1. O domínio do site atual. Se usar `Selector`, informe o domínio ao criar o objeto. Se usar um fetcher, ele será obtido automaticamente da URL.
     2. Um `identifier` para buscar as propriedades do elemento no banco. Nem sempre você precisa defini-lo, como veremos depois.

     Juntos, esses valores permitem recuperar as propriedades salvas do elemento.

  4. Quando a estrutura do site mudar, ative `adaptive` para buscar o elemento. O Scrapling recupera as propriedades salvas e as compara com as de todos os elementos da página. Cada elemento recebe uma pontuação de semelhança, levando em conta os dados que veremos a seguir.
  5. O elemento ou os elementos com a maior pontuação são retornados.

### As propriedades do elemento {#the-unique-properties}
Você pode estar se perguntando quais propriedades podem ser usadas se todas elas podem mudar ou desaparecer.

O Scrapling usa estes dados:

- Nome da tag, texto, atributos com seus nomes e valores, nomes das tags dos elementos irmãos e nomes das tags no caminho do elemento.
- Nome da tag do elemento pai, seus atributos com nomes e valores e seu texto.

A comparação não exige valores idênticos. Ela mede o quanto eles se parecem. Até a ordem dos valores é considerada, como a ordem em que os nomes das classes aparecem antes e depois da mudança.

## Como usar o recurso adaptativo {#how-to-use-adaptive-feature}
Você pode aplicar o recurso adaptativo a qualquer elemento encontrado. Ele também está disponível por argumentos nos métodos CSS e XPath, como vimos acima. Voltaremos a isso depois.

Primeiro, ative `adaptive` passando `adaptive=True` ao criar um [Selector](main_classes.md#selector), ou ative o recurso no fetcher que estiver usando, como veremos a seguir.

Exemplos:
```python
from scrapling import Selector, Fetcher
page = Selector(html_doc, adaptive=True)
# OR
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```
Se usar a classe [Selector](main_classes.md#selector), passe a URL do site no argumento `url`. Assim, o Scrapling separa as propriedades salvas por domínio.

Se você não passar uma URL, o valor `default` será usado nesse campo ao salvar as propriedades. Isso só causa problema se depois usar o mesmo identificador para outro site sem informar a URL. Cada gravação substitui os dados anteriores, e `adaptive` usa apenas as últimas propriedades salvas.

Os argumentos `storage` e `storage_args` configuram a conexão com o banco de dados. Por padrão, a biblioteca usa sua própria classe SQLite. Você só precisa desses argumentos se quiser criar outro sistema de armazenamento, como veremos em [uma página da seção de desenvolvimento](../development/adaptive_storage_system.md).

Depois de ativar `adaptive` globalmente, você tem duas formas principais de usá-lo.

### Pela seleção CSS ou XPath {#the-cssxpath-selection-way}
Como no exemplo anterior, primeiro use `auto_save` ao selecionar um elemento que existe na página:
```python
element = page.css('#p1', auto_save=True)
```
Se o seletor deixar de encontrá-lo, use o mesmo seletor com `adaptive` para que a biblioteca o procure:
```python
element = page.css('#p1', adaptive=True)
```
Bem simples, né?

Por dentro, várias coisas acontecem. Lembra do identificador que permite recuperar o elemento? Os métodos `css` e `xpath` usam automaticamente o seletor como identificador para facilitar seu trabalho :)

Você também pode passar `identifier` a esses métodos para definir um valor próprio. Isso pode ser útil em alguns casos, inclusive ao salvar propriedades com `auto_save`.

### De forma manual {#the-manual-way}
Você pode salvar e recuperar um elemento manualmente e depois reencontrá-lo com `adaptive`. Assim, consegue usar elementos obtidos por qualquer método de seleção.

Por exemplo, imagine que você encontrou um elemento pelo texto:
```python
element = page.find_by_text('Tipping the Velvet', first_match=True)
```
Salve suas propriedades com `save`. Nesse caso, você precisa definir o identificador. Aqui usei `my_special_element`. No seu código, escolha um nome que descreva o elemento, assim como faz com os nomes das variáveis :)
```python
page.save(element, 'my_special_element')
```
Depois, você pode recuperar os dados e buscar o elemento na página com `adaptive`:
```python
>>> element_dict = page.retrieve('my_special_element')
>>> page.relocate(element_dict, selector_type=True)
[<data='<a href="catalogue/tipping-the-velvet_99...' parent='<h3><a href="catalogue/tipping-the-velve...'>]
>>> page.relocate(element_dict, selector_type=True).css('::text').getall()
['Tipping the Velvet']
```
Para isso, use os métodos `retrieve` e `relocate`.

Para manter o resultado como um objeto `lxml.etree`, não passe `selector_type`:
```python
>>> page.relocate(element_dict)
[<Element a at 0x105a2a7b0>]
```

## Solução de problemas {#troubleshooting}

### Nenhuma correspondência encontrada {#no-matches-found}
```python
# 1. Check if data was saved
element_data = page.retrieve('identifier')
if not element_data:
    print("No data saved for this identifier")

# 2. Try with different identifier
products = page.css('.product', adaptive=True, identifier='old_selector')

# 3. Save again with new identifier
products = page.css('.new-product', auto_save=True, identifier='new_identifier')
```

### Elementos incorretos encontrados {#wrong-elements-matched}
```python
# Use more specific selectors
products = page.css('.product-list .product', auto_save=True)

# Or save with more context
product = page.find_by_text('Product Name').parent
page.save(product, 'specific_product')
```

## Problemas conhecidos {#known-issues}
Ao salvar com `adaptive`, apenas as propriedades do primeiro elemento encontrado são guardadas. Se seu seletor encontra vários elementos em partes diferentes da página, `adaptive` só reencontra o primeiro. Isso não se aplica a seletores CSS combinados, como os separados por vírgulas. Eles são separados e executados um por um.

## Para encerrar {#final-thoughts}
Explicar esse recurso em detalhes sem complicar foi um desafio. Se algo não ficou claro, escreva na [seção de discussões](https://github.com/D4Vinci/Scrapling/discussions) e responderei assim que possível. Você também pode usar o servidor do Discord ou falar comigo em particular :)