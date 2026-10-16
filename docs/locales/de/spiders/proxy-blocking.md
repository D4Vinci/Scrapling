---
title: "Proxys wechseln und gesperrte Crawl-Anfragen wiederholen"
description: "Verwenden Sie Proxys und Wechselstrategien in Scrapling-Spidern. Erkennen Sie gesperrte Antworten, wiederholen Sie Anfragen und wechseln Sie von HTTP zu Browser-Sitzungen."
---

# Proxys verwalten und Sperren behandeln {#proxy-management-and-handling-blocks}

## Einführung {#introduction}

!!! success "Voraussetzungen"

    1. Sie haben die Seite [Erste Schritte](getting-started.md) gelesen und wissen, wie Sie einen einfachen Spider erstellen und starten.
    2. Sie haben die Seite [Sitzungen](sessions.md) gelesen und wissen, wie Sie Sitzungen konfigurieren.

Beim Abruf großer Datenmengen müssen Sie oft zwischen mehreren Proxys wechseln, um Anfragelimits und Sperren zu vermeiden. Scraplings `ProxyRotator` macht das einfach. Er arbeitet mit allen Sitzungstypen und mit dem System des Spiders zum Wiederholen gesperrter Anfragen zusammen.

Wenn Sie nicht wissen, was ein Proxy ist oder wie Sie einen guten auswählen, hilft Ihnen [diese Anleitung](https://substack.thewebscraping.club/p/everything-about-proxies).

## ProxyRotator {#proxyrotator}

Die Klasse `ProxyRotator` verwaltet eine Liste von Proxys und wechselt automatisch zwischen ihnen. Übergeben Sie sie mit dem Parameter `proxy_rotator` an einen beliebigen Sitzungstyp:

```python
from scrapling.spiders import Spider, Response
from scrapling.fetchers import FetcherSession, ProxyRotator

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://user:pass@proxy3:8080",
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))

    async def parse(self, response: Response):
        # Check which proxy was used
        print(f"Proxy used: {response.meta.get('proxy')}")
        yield {"title": response.css("title::text").get("")}
```

Jede Anfrage erhält automatisch den nächsten Proxy. Der verwendete Proxy wird in `response.meta["proxy"]` gespeichert. So sehen Sie, welcher Proxy welche Seite abgerufen hat.


Für Browser-Sitzungen sind einige Anpassungen nötig:

```python
from scrapling.fetchers import AsyncStealthySession, ProxyRotator

# String proxies work for all session types
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
])

# Dict proxies (Playwright format) work for browser sessions
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://proxy2:8080"},
])

# Then inside the spider
def configure_sessions(self, manager):
    rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
    manager.add("browser", AsyncStealthySession(proxy_rotator=rotator))
```

!!! info

    1. Sie können `proxy_rotator` in derselben Sitzung nicht zusammen mit den festen Parametern `proxy` oder `proxies` verwenden. Wählen Sie beim Einrichten der Sitzung eine dieser Möglichkeiten. Später können Sie den Proxy für einzelne Anfragen überschreiben, wie unten gezeigt.
    2. Standardmäßig verwenden alle Browser-Sitzungen einen dauerhaften Browser-Kontext mit einem Pool aus Tabs. Browser können jedoch keinen eigenen Proxy pro Tab festlegen. Mit `ProxyRotator` öffnet der Fetcher deshalb automatisch für jeden Proxy einen eigenen Kontext mit einem Tab. Nach Abschluss der Aufgabe werden sowohl der Tab als auch sein Kontext geschlossen.

## Eigene Wechselstrategien {#custom-rotation-strategies}

Standardmäßig verwendet `ProxyRotator` einen zyklischen Wechsel: Er geht die Proxys der Reihe nach durch und beginnt am Ende wieder von vorn.

Sie können eine eigene Strategiefunktion übergeben. Diese muss die folgende Signatur haben:

```python
from scrapling.core._types import ProxyType

def my_strategy(proxies: list, current_index: int) -> tuple[ProxyType, int]:
    ...
```

Sie erhält die Liste der Proxys und den aktuellen Index. Sie muss den ausgewählten Proxy und den nächsten Index zurückgeben.

Hier sind einige Beispiele für eigene Wechselstrategien.

### Zufälliger Wechsel {#random-rotation}

```python
import random
from scrapling.fetchers import ProxyRotator

def random_strategy(proxies, current_index):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(
    ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"],
    strategy=random_strategy,
)
```

### Gewichteter Wechsel {#weighted-rotation}

```python
import random

def weighted_strategy(proxies, current_index):
    # First proxy gets 60% of traffic, others split the rest
    weights = [60] + [40 // (len(proxies) - 1)] * (len(proxies) - 1)
    proxy = random.choices(proxies, weights=weights, k=1)[0]
    return proxy, current_index  # Index doesn't matter for weighted

rotator = ProxyRotator(proxies, strategy=weighted_strategy)
```


## Proxy für einzelne Anfragen festlegen {#per-request-proxy-override}

Mit dem Schlüsselwortargument `proxy=` überschreiben Sie den automatischen Wechsel für einzelne Anfragen:

```python
async def parse(self, response: Response):
    # This request uses the rotator's next proxy
    yield response.follow("/page1", callback=self.parse_page)

    # This request uses a specific proxy, bypassing the rotator
    yield response.follow(
        "/special-page",
        callback=self.parse_page,
        proxy="http://special-proxy:8080",
    )
```

Das ist nützlich, wenn bestimmte Seiten einen bestimmten Proxy brauchen, etwa einen Proxy aus einer bestimmten Region für regionale Inhalte.

## Gesperrte Anfragen behandeln {#blocked-request-handling}

Der Spider erkennt gesperrte Anfragen und wiederholt sie automatisch. Standardmäßig gelten diese HTTP-Statuscodes als Sperre: `401`, `403`, `407`, `429`, `444`, `500`, `502`, `503`, `504`.

Die Wiederholungen laufen so ab:

1. Nach Eingang einer Antwort ruft der Spider `is_blocked(response)` auf.
2. Bei einer Sperre kopiert er die Anfrage und ruft `retry_blocked_request()` auf. So können Sie sie vor dem nächsten Versuch ändern.
3. Die Anfrage kommt mit `dont_filter=True` und niedrigerer Priorität zurück in die Warteschlange. Dadurch wird sie nicht als doppelt verworfen und nicht sofort wiederholt.
4. Das wird bis zu `max_blocked_retries` Mal wiederholt, standardmäßig 3 Mal.

!!! tip

    1. Bei einem neuen Versuch werden die bisherigen Argumente `proxy`/`proxies` automatisch aus der Anfrage entfernt. So weist der Rotator einen neuen Proxy zu.
    2. Das Attribut `max_blocked_retries` ist von den Wiederholungen auf Sitzungsebene getrennt und verwendet einen eigenen Zähler.

### Eigene Erkennung von Sperren {#custom-block-detection}

Überschreiben Sie `is_blocked()`, um Ihre eigene Erkennung hinzuzufügen:

```python
class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]

    async def is_blocked(self, response: Response) -> bool:
        # Check status codes (default behavior)
        if response.status in {403, 429, 503}:
            return True

        # Check response content
        body = response.body.decode("utf-8", errors="ignore")
        if "access denied" in body.lower() or "rate limit" in body.lower():
            return True

        return False

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

### Wiederholungen anpassen {#customizing-retries}

Überschreiben Sie `retry_blocked_request()`, um die Anfrage vor dem nächsten Versuch zu ändern. Das Attribut `max_blocked_retries` bestimmt, wie oft eine gesperrte Anfrage wiederholt wird, standardmäßig 3 Mal:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari']))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```

Im Beispiel bleibt die Erkennung von Sperren unverändert. Der Spider verwendet zunächst HTTP-Anfragen. Erst bei einer Sperre wechselt er zum Stealth-Browser.


Alles zusammen:

```python
from scrapling.spiders import Spider, SessionManager, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession, ProxyRotator


cheap_proxies = ProxyRotator([ "http://proxy1:8080", "http://proxy2:8080"])

# A format acceptable by the browser
expensive_proxies = ProxyRotator([
    {"server": "http://residential_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://residential_proxy2:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy1:8080", "username": "user", "password": "pass"},
    {"server": "http://mobile_proxy2:8080", "username": "user", "password": "pass"},
])


class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    max_blocked_retries = 5

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add('requests', FetcherSession(impersonate=['chrome', 'firefox', 'safari'], proxy_rotator=cheap_proxies))
        manager.add('stealth', AsyncStealthySession(block_webrtc=True, proxy_rotator=expensive_proxies), lazy=True)

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        request.sid = "stealth"
        self.logger.info(f"Retrying blocked request: {request.url}")
        return request

    async def parse(self, response: Response):
        yield {"title": response.css("title::text").get("")}
```
Die Logik im Beispiel: Anfragen verwenden günstige Proxys, etwa aus Rechenzentren, bis sie gesperrt werden. Danach werden sie mit höherwertigen Proxys wiederholt, etwa Residential- oder Mobilfunk-Proxys.
