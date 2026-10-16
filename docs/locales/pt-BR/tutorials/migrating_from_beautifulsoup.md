---
title: "Migre do BeautifulSoup para o Scrapling"
description: "Compare as tarefas comuns de seleção, texto, atributos e navegação do BeautifulSoup com as do Scrapling. Veja as diferenças de API com exemplos práticos."
---

# Migrar do BeautifulSoup para o Scrapling {#migrating-from-beautifulsoup-to-scrapling}

Se você já conhece o BeautifulSoup, vai ser fácil começar com o Scrapling. Ele é muito mais rápido, oferece as mesmas funções de análise do BS e acrescenta outras que o BS não tem. Também inclui ferramentas para obter e trabalhar com páginas web modernas. Este guia ajuda você a adaptar seu código do BeautifulSoup para o Scrapling.

A tabela abaixo reúne as tarefas mais comuns na extração de dados web. Cada linha mostra como fazer uma tarefa com BeautifulSoup e como fazer a mesma tarefa com Scrapling.

Você vai notar que alguns atalhos do BeautifulSoup não existem no Scrapling. Esse é um dos motivos pelos quais o BeautifulSoup é mais lento. A ideia é simples: se algo já pode ser feito com uma linha curta, não vale perder desempenho para encurtá-la um pouco mais :)

| Tarefa | Código do BeautifulSoup | Código do Scrapling |
|---|---|---|
| Importar o parser | `from bs4 import BeautifulSoup`                                                                               | `from scrapling.parser import Selector`                                           |
| Analisar HTML de uma string | `soup = BeautifulSoup(html, 'html.parser')`                                                                   | `page = Selector(html)`                                                           |
| Encontrar um elemento | `element = soup.find('div', class_='example')`                                                                | `element = page.find('div', class_='example')`                                    |
| Encontrar vários elementos | `elements = soup.find_all('div', class_='example')`                                                           | `elements = page.find_all('div', class_='example')`                               |
| Encontrar um elemento (exemplo 2) | `element = soup.find('div', attrs={"class": "example"})`                                                      | `element = page.find('div', {"class": "example"})`                                |
| Encontrar um elemento (exemplo 3) | `element = soup.find(re.compile("^b"))`                                                                       | `element = page.find(lambda e: re.search(r"^b", e.tag) is not None)` |
| Encontrar um elemento (exemplo 4) | `element = soup.find(lambda e: len(list(e.children)) > 0)`                                                    | `element = page.find(lambda e: len(e.children) > 0)`                              |
| Encontrar um elemento (exemplo 5) | `element = soup.find(["a", "b"])`                                                                             | `element = page.find(["a", "b"])`                                                 |
| Encontrar um elemento pelo texto | `element = soup.find(text="some text")`                                                                       | `element = page.find_by_text("some text", partial=False)`                         |
| Usar CSS para encontrar a primeira correspondência | `elements = soup.select_one('div.example')`                                                                   | `elements = page.css('div.example').first`                                        |
| Usar CSS para encontrar todas as correspondências | `elements = soup.select('div.example')`                                                                       | `elements = page.css('div.example')`                                              |
| Obter o código da página ou do elemento com formatação legível | `prettified = soup.prettify()`                                                                                | `prettified = page.prettify()`                                                    |
| Obter o código da página ou do elemento sem formatação adicional | `source = str(soup)`                                                                                          | `source = page.html_content`                                                      |
| Obter o nome da tag de um elemento | `name = element.name`                                                                                         | `name = element.tag`                                                              |
| Extrair o texto de um elemento | `string = element.string`                                                                                     | `string = element.text`                                                           |
| Extrair todo o texto de um documento ou de uma tag | `text = soup.get_text(strip=True)`                                                                            | `text = page.get_all_text(strip=True)`                                            |
| Acessar o dicionário de atributos | `attrs = element.attrs`                                                                                       | `attrs = element.attrib`                                                          |
| Extrair atributos | `attr = element['href']`                                                                                      | `attr = element['href']`                                                          |
| Acessar o elemento pai | `parent = element.parent`                                                                                     | `parent = element.parent`                                                         |
| Obter todos os ancestrais de um elemento | `parents = list(element.parents)`                                                                             | `parents = list(element.iterancestors())`                                         |
| Buscar um elemento entre os ancestrais | `target_parent = element.find_parent("a")`                                                                    | `target_parent = element.find_ancestor(lambda p: p.tag == 'a')`                   |
| Obter todos os elementos irmãos | Não disponível                                                                                                           | `siblings = element.siblings`                                                     |
| Obter o próximo elemento irmão | `next_element = element.next_sibling`                                                                         | `next_element = element.next`                                                     |
| Buscar um elemento entre os irmãos | `target_sibling = element.find_next_sibling("a")`<br/>`target_sibling = element.find_previous_sibling("a")`   | `target_sibling = element.siblings.search(lambda s: s.tag == 'a')`                |
| Buscar vários elementos entre os irmãos | `target_sibling = element.find_next_siblings("a")`<br/>`target_sibling = element.find_previous_siblings("a")` | `target_sibling = element.siblings.filter(lambda s: s.tag == 'a')`                |
| Buscar um elemento entre os elementos seguintes | `target_parent = element.find_next("a")`                                                                      | `target_parent = element.below_elements.search(lambda p: p.tag == 'a')`           |
| Buscar vários elementos entre os elementos seguintes | `target_parent = element.find_all_next("a")`                                                                  | `target_parent = element.below_elements.filter(lambda p: p.tag == 'a')`           |
| Buscar um elemento entre os ancestrais | `target_parent = element.find_previous("a")` ¹                                                                | `target_parent = element.path.search(lambda p: p.tag == 'a')`                     |
| Buscar vários elementos entre os ancestrais | `target_parent = element.find_all_previous("a")` ¹                                                            | `target_parent = element.path.filter(lambda p: p.tag == 'a')`                     |
| Obter o elemento irmão anterior | `prev_element = element.previous_sibling`                                                                     | `prev_element = element.previous`                                                 |
| Acessar os elementos filhos | `children = list(element.children)`                                                                           | `children = element.children`                                                     |
| Obter todos os descendentes de um elemento | `children = list(element.descendants)`                                                                        | `children = element.below_elements`                                               |
| Selecionar links dentro de parágrafos com a classe story | `group = soup.select('p.story a')`                                                             | `group = page.css('p.story a')`              |

Uma expressão regular compilada passada diretamente para `find()` ou `find_all()` do Scrapling busca no texto dos elementos, não nos nomes das tags. Use a lambda da tabela para buscar por nome de tag, ou `page.find_by_regex(r"^b")` para buscar diretamente no texto.

¹ **Nota:** `find_previous`/`find_all_previous` do BS4 buscam em todos os elementos anteriores na ordem do documento. Já `path` do Scrapling devolve apenas os ancestrais, ou seja, a sequência de elementos pais. Eles não são equivalentes exatos, mas buscar entre os ancestrais cobre o caso mais comum.

**Um ponto importante**: O BeautifulSoup oferece funções para modificar a página depois da análise. O Scrapling se concentra em extrair os dados com rapidez e deixa você fazer o que precisar com eles depois. As duas ferramentas podem ser usadas na extração de dados web, mas uma delas é especializada nessa tarefa :)

### Um exemplo completo {#putting-it-all-together}

Este exemplo mostra como extrair todos os links de uma página com BeautifulSoup e com Scrapling.

**Com BeautifulSoup:**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
for link in links:
    print(link['href'])
```

**Com Scrapling:**

```python
from scrapling import Fetcher

url = 'https://example.com'
page = Fetcher.get(url)

links = page.css('a::attr(href)').getall()
for link in links:
    print(link)
```

Como você pode ver, o Scrapling combina a obtenção da página e sua análise em uma etapa, deixando o código mais simples e eficiente.

!!! abstract "**Notas adicionais:**"

    - **Parsers diferentes**: O BeautifulSoup permite escolher o mecanismo de análise, e um deles é `lxml`. O Scrapling usa a biblioteca `lxml` por padrão por motivos de desempenho.
    - **Tipos de elemento**: No BeautifulSoup, os elementos são objetos `Tag`; no Scrapling, são objetos `Selector`. Os dois oferecem métodos e propriedades parecidos para navegação e extração de dados.
    - **Tratamento de erros**: As duas bibliotecas devolvem `None` quando não encontram um elemento, por exemplo com `soup.find()` ou `page.find()`. No Scrapling, `page.css()` devolve uma lista `Selectors` vazia quando não há correspondências. Você pode usar `page.css('.foo').first` para obter a primeira correspondência ou `None`. Para evitar erros, confira se recebeu `None` ou um resultado vazio antes de acessar as propriedades.
    - **Extração de texto**: O Scrapling oferece mais métodos para trabalhar com texto por meio de `TextHandler`, como `clean()`. Esse método ajuda a remover espaços extras, espaços seguidos ou caracteres indesejados. Consulte a documentação para ver a lista completa.

A documentação explica as funções do Scrapling com mais detalhes e lista todos os argumentos que você pode passar para cada método.

Esperamos que este guia facilite sua migração do BeautifulSoup para o Scrapling. Boa extração!
