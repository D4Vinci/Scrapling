---
title: "Web scraping por HTTP en Python con Fetcher y FetcherSession"
description: "Envía solicitudes HTTP síncronas o asíncronas con imitación de navegador, cookies, proxies y sesiones reutilizables. Extrae datos de la respuesta con Scrapling."
---

# Solicitudes HTTP {#http-requests}

`Fetcher` envía solicitudes HTTP rápidas y ligeras mediante `curl_cffi`, una biblioteca de alto rendimiento con muchas opciones para evitar la detección.

!!! success "Antes de empezar"

    1. Lee [Conceptos básicos de las herramientas de descarga](../fetching/choosing.md) para saber qué es [Response](../fetching/choosing.md#response-object) y qué herramienta elegir.
    2. Lee [Buscar elementos](../parsing/selection.md) para saber cómo buscar y extraer elementos de [Selector](../parsing/main_classes.md#selector)/[Response](../fetching/choosing.md#response-object).
    3. Lee [Clases principales](../parsing/main_classes.md) para conocer las propiedades y métodos que [Response](../fetching/choosing.md#response-object) hereda de [Selector](../parsing/main_classes.md#selector).

## Uso básico {#basic-usage}
La forma principal de importar esta herramienta es la misma que para las demás:

```python
from scrapling.fetchers import Fetcher
```
Consulta cómo configurar el analizador [aquí](choosing.md#parser-configuration-in-all-fetchers).

### Argumentos compartidos {#shared-arguments}
Todos los métodos de solicitud comparten estos argumentos:

- **url**: URL de destino.
- **stealthy_headers**: genera y añade cabeceras de un navegador real, incluido un referer de Google. Está activado por defecto.
- **follow_redirects**: controla las redirecciones. **Por defecto es `"safe"`**: las sigue, pero rechaza las que apuntan a IP internas o privadas para proteger contra SSRF. Usa `True` para seguirlas sin restricciones, o `False` para desactivarlas.
- **timeout**: segundos de espera máxima para completar cada solicitud. **Por defecto, 30 segundos**.
- **retries**: número máximo de intentos si una solicitud falla, incluido el primero. **Por defecto, 3**.
- **retry_delay**: segundos de espera entre intentos. **Por defecto, 1 segundo**.
- **impersonate**: imita la huella TLS de un navegador. Acepta una cadena o una lista, como `"chrome110"`, `"firefox102"` o `"safari15_5"` para versiones concretas. Usa `"chrome"`, `"firefox"`, `"safari"` o `"edge"` para elegir la última versión disponible. Así las solicitudes parecen venir de un navegador real a nivel TLS. Si pasas una lista, elige una opción al azar en cada solicitud. **Por defecto, usa la última versión disponible de Chrome.**
- **http3**: usa HTTP/3. **Por defecto es False**. Puede causar problemas si se combina con `impersonate`.
- **cookies**: cookies de la solicitud. Acepta un diccionario de `name→value` o una lista de diccionarios.
- **proxy**: proxy que dirige todo el tráfico HTTP y HTTPS de esta solicitud. El formato es `http://username:password@localhost:8030`.
- **proxy_auth**: autenticación HTTP básica del proxy, como una tupla de (usuario, contraseña).
- **proxies**: diccionario de proxies con el formato `{"http": proxy_url, "https": proxy_url}`.
- **proxy_rotator**: objeto `ProxyRotator` para cambiar de proxy automáticamente. No se puede combinar con `proxy` ni `proxies`.
- **headers**: cabeceras de la solicitud. Pueden reemplazar las que genera `stealthy_headers`.
- **max_redirects**: número máximo de redirecciones. **Por defecto, 30**. Usa -1 para no poner límite.
- **verify**: indica si se comprueban los certificados HTTPS. **Por defecto es True**.
- **cert**: tupla de nombres de archivo (certificado, clave) para el certificado del cliente.
- **selector_config**: diccionario de ajustes del analizador al crear el objeto `Selector`/`Response` final.

!!! note "Notas"

    1. Los navegadores disponibles para imitar son (`"edge"`, `"chrome"`, `"chrome_android"`, `"safari"`, `"safari_beta"`, `"safari_ios"`, `"safari_ios_beta"`, `"firefox"`, `"tor"`).<br/>
    2. Los navegadores y sus versiones aparecen en el autocompletado del argumento y se renuevan con cada actualización de `curl_cffi`.<br/>
    3. Si activas `impersonate` o `stealthy_headers`, las herramientas generan cabeceras reales que coinciden con la versión del navegador usada.

Para ajustar más opciones, puedes pasar a cualquier método otros argumentos que admita `curl_cffi` y que el método no gestione ya.

### Codificación del texto {#text-encoding}

Si una página que no usa UTF-8 muestra caracteres incorrectos, pasa `default_encoding="shift_jis"`, o su codificación real, con la solicitud. Se usa cuando la cabecera `Content-Type` no indica un juego de caracteres. No reemplaza la codificación enviada por el servidor.

Si el servidor indica una codificación incorrecta, puedes forzar la correcta con `selector_config={"encoding": "shift_jis"}`.

### Métodos HTTP {#http-methods}
Cada método admite argumentos propios, como `params` para GET y `data`/`json` para POST, PUT y DELETE.

Veamos algunos ejemplos:

> Los métodos `OPTIONS` y `HEAD` no están disponibles.
#### GET {#get}
```python
from scrapling.fetchers import Fetcher
# Basic GET
page = Fetcher.get('https://example.com')
page = Fetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = Fetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = Fetcher.get('https://example.com/search', params={'q': 'query'})

# With headers
page = Fetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = Fetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = Fetcher.get('https://example.com', impersonate='chrome')
# HTTP/3 support
page = Fetcher.get('https://example.com', http3=True)
```
Para solicitudes asíncronas, solo cambia un poco:
```python
from scrapling.fetchers import AsyncFetcher
# Basic GET
page = await AsyncFetcher.get('https://example.com')
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', stealthy_headers=True)
page = await AsyncFetcher.get('https://scrapling.requestcatcher.com/get', proxy='http://username:password@localhost:8030')
# With parameters
page = await AsyncFetcher.get('https://example.com/search', params={'q': 'query'})
# With headers
page = await AsyncFetcher.get('https://example.com', headers={'User-Agent': 'Custom/1.0'})
# Basic HTTP authentication
page = await AsyncFetcher.get("https://example.com", auth=("my_user", "password123"))
# Browser impersonation
page = await AsyncFetcher.get('https://example.com', impersonate='chrome110')
# HTTP/3 support
page = await AsyncFetcher.get('https://example.com', http3=True)
```
En todos los casos, `page` es un [Response](choosing.md#response-object), que también es un [Selector](../parsing/main_classes.md#selector). Puedes usarlo directamente:
```python
page.css('.something.something')

page = Fetcher.get('https://api.github.com/events')
>>> page.json()
[{'id': '<redacted>',
  'type': 'PushEvent',
  'actor': {'id': '<redacted>',
   'login': '<redacted>',
   'display_login': '<redacted>',
   'gravatar_id': '',
   'url': 'https://api.github.com/users/<redacted>',
   'avatar_url': 'https://avatars.githubusercontent.com/u/<redacted>'},
  'repo': {'id': '<redacted>',
...
```
#### POST {#post}
```python
from scrapling.fetchers import Fetcher
# Basic POST
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, params={'q': 'query'})
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = Fetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = Fetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = Fetcher.post('https://example.com/api', json={'key': 'value'})
```
Para solicitudes asíncronas, solo cambia un poco:
```python
from scrapling.fetchers import AsyncFetcher
# Basic POST
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, stealthy_headers=True)
page = await AsyncFetcher.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'}, proxy='http://username:password@localhost:8030', impersonate="chrome")
# Another example of form-encoded data
page = await AsyncFetcher.post('https://example.com/submit', data={'username': 'user', 'password': 'pass'}, http3=True)
# JSON data
page = await AsyncFetcher.post('https://example.com/api', json={'key': 'value'})
```
#### PUT {#put}
```python
from scrapling.fetchers import Fetcher
# Basic PUT
page = Fetcher.put('https://example.com/update', data={'status': 'updated'})
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = Fetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = Fetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```
Para solicitudes asíncronas, solo cambia un poco:
```python
from scrapling.fetchers import AsyncFetcher
# Basic PUT
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'})
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.put('https://example.com/update', data={'status': 'updated'}, proxy='http://username:password@localhost:8030')
# Another example of form-encoded data
page = await AsyncFetcher.put("https://scrapling.requestcatcher.com/put", data={'key': ['value1', 'value2']})
```

#### DELETE {#delete}
```python
from scrapling.fetchers import Fetcher
page = Fetcher.delete('https://example.com/resource/123')
page = Fetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = Fetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```
Para solicitudes asíncronas, solo cambia un poco:
```python
from scrapling.fetchers import AsyncFetcher
page = await AsyncFetcher.delete('https://example.com/resource/123')
page = await AsyncFetcher.delete('https://example.com/resource/123', stealthy_headers=True, impersonate="chrome")
page = await AsyncFetcher.delete('https://example.com/resource/123', proxy='http://username:password@localhost:8030')
```

## Gestión de sesiones {#session-management}

Usa `FetcherSession` para enviar varias solicitudes con la misma configuración. Sirve tanto en código síncrono como asíncrono: detecta el tipo de uso y ajusta la sesión sin que tengas que importar otra clase.

`FetcherSession` acepta casi todos los argumentos de los métodos de solicitud. Puedes definir los ajustes para toda la sesión y cambiarlos en una solicitud concreta, como muestran los siguientes ejemplos.

```python
from scrapling.fetchers import FetcherSession

# Create a session with default configuration
with FetcherSession(
    impersonate='chrome',
    http3=True,
    stealthy_headers=True,
    timeout=30,
    retries=3
) as session:
    # Make multiple requests with the same settings and the same cookies
    page1 = session.get('https://scrapling.requestcatcher.com/get')
    page2 = session.post('https://scrapling.requestcatcher.com/post', data={'key': 'value'})
    page3 = session.get('https://api.github.com/events')

    # All requests share the same session and connection pool
```

También puedes usar `ProxyRotator` con `FetcherSession` para cambiar de proxy automáticamente entre solicitudes:

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
])

with FetcherSession(proxy_rotator=rotator, impersonate='chrome') as session:
    # Each request automatically uses the next proxy in rotation
    page1 = session.get('https://example.com/page1')
    page2 = session.get('https://example.com/page2')

    # You can check which proxy was used via the response metadata
    print(page1.meta['proxy'])
```

Para una solicitud concreta, puedes reemplazar el proxy o rotador de la sesión pasando `proxy=` al método:

```python
with FetcherSession(proxy='http://default-proxy:8080') as session:
    # Uses the session proxy
    page1 = session.get('https://example.com/page1')

    # Override the proxy for this specific request
    page2 = session.get('https://example.com/page2', proxy='http://special-proxy:9090')
```

Un ejemplo asíncrono:

```python
async with FetcherSession(impersonate='firefox', http3=True) as session:
    # All standard HTTP methods available
    response = await session.get('https://example.com')
    response = await session.post('https://scrapling.requestcatcher.com/post', json={'data': 'value'})
    response = await session.put('https://scrapling.requestcatcher.com/put', data={'update': 'info'})
    response = await session.delete('https://scrapling.requestcatcher.com/delete')
```
O, mejor aún:
```python
import asyncio
from scrapling.fetchers import FetcherSession

# Async session usage
async with FetcherSession(impersonate="safari") as session:
    urls = ['https://example.com/page1', 'https://example.com/page2']

    tasks = [
        session.get(url) for url in urls
    ]

    pages = await asyncio.gather(*tasks)
```

`Fetcher` usa `FetcherSession` para crear una sesión temporal en cada solicitud.

### Ventajas de las sesiones {#session-benefits}

- **Más velocidad**: 10 veces más rápido que crear una sesión por solicitud.
- **Cookies persistentes**: gestión automática de cookies entre solicitudes.
- **Menor consumo**: mejor uso de memoria y CPU al enviar varias solicitudes.
- **Configuración centralizada**: un solo lugar para gestionar los ajustes.

## Ejemplos {#examples}
Ejemplos completos para quienes empiezan con web scraping.

### Solicitud HTTP básica {#basic-http-request}

```python
from scrapling.fetchers import Fetcher

# Make a request
page = Fetcher.get('https://example.com')

# Check the status
if page.status == 200:
    # Extract title
    title = page.css('title::text').get()
    print(f"Page title: {title}")

    # Extract all links
    links = page.css('a::attr(href)').getall()
    print(f"Found {len(links)} links")
```

### Extraer productos {#product-scraping}

```python
from scrapling.fetchers import Fetcher

def scrape_products():
    page = Fetcher.get('https://example.com/products')
    
    # Find all product elements
    products = page.css('.product')
    
    results = []
    for product in products:
        results.append({
            'title': product.css('.title::text').get(),
            'price': product.css('.price::text').re_first(r'\d+\.\d{2}'),
            'description': product.css('.description::text').get(),
            'in_stock': product.has_class('in-stock')
        })
    
    return results
```

### Descargar archivos {#downloading-files}

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/main_cover.png')
with open(file='main_cover.png', mode='wb') as f:
   f.write(page.body)
```

### Recorrer páginas de resultados {#pagination-handling}

```python
from scrapling.fetchers import Fetcher

def scrape_all_pages():
    base_url = 'https://example.com/products?page={}'
    page_num = 1
    all_products = []
    
    while True:
        # Get current page
        page = Fetcher.get(base_url.format(page_num))
        
        # Find products
        products = page.css('.product')
        if not products:
            break
            
        # Process products
        for product in products:
            all_products.append({
                'name': product.css('.name::text').get(),
                'price': product.css('.price::text').get()
            })
            
        # Next page
        page_num += 1
        
    return all_products
```

### Enviar formularios {#form-submission}

```python
from scrapling.fetchers import Fetcher

# Submit login form
response = Fetcher.post(
    'https://example.com/login',
    data={
        'username': 'user@example.com',
        'password': 'password123'
    }
)

# Check login success
if response.status == 200:
    # Extract user info
    user_name = response.css('.user-name::text').get()
    print(f"Logged in as: {user_name}")
```

### Extraer tablas {#table-extraction}

```python
from scrapling.fetchers import Fetcher

def extract_table():
    page = Fetcher.get('https://example.com/data')
    
    # Find table
    table = page.css('table')[0]
    
    # Extract headers
    headers = [
        th.text for th in table.css('thead th')
    ]
    
    # Extract rows
    rows = []
    for row in table.css('tbody tr'):
        cells = [td.text for td in row.css('td')]
        rows.append(dict(zip(headers, cells)))
        
    return rows
```

### Menú de navegación {#navigation-menu}

```python
from scrapling.fetchers import Fetcher

def extract_menu():
    page = Fetcher.get('https://example.com')
    
    # Find navigation
    nav = page.css('nav')[0]
    
    menu = {}
    for item in nav.css('li'):
        links = item.css('a')
        if links:
            link = links[0]
            menu[link.text] = {
                'url': link['href'],
                'has_submenu': bool(item.css('.submenu'))
            }
            
    return menu
```

## Cuándo usar cada opción {#when-to-use}

Usa `Fetcher` cuando:

- Necesites solicitudes HTTP rápidas.
- Quieras reducir el consumo de recursos.
- No necesites ejecutar JavaScript porque los datos se pueden obtener con solicitudes HTTP.
- Necesites evitar cierta detección, por ejemplo, si el sitio tiene protección pero no usa pruebas de JavaScript.

Usa `FetcherSession` cuando:

- Envíes varias solicitudes al mismo sitio o a sitios distintos.
- Necesites conservar cookies o autenticación entre solicitudes.
- Quieras reutilizar conexiones para mejorar el rendimiento.
- Necesites mantener los mismos ajustes entre solicitudes.
- Trabajes con API que requieran estado de sesión.

Usa otras herramientas de descarga cuando:

- Necesites automatizar un navegador.
- Necesites opciones avanzadas para evitar la detección de bots.
- Necesites ejecutar JavaScript o interactuar con contenido dinámico.
