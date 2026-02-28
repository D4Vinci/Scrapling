<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Effortless Web Scraping for the Modern Web</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="Tests">
        <img alt="Tests" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI version">
        <img alt="PyPI version" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://pepy.tech/project/scrapling" alt="PyPI Downloads">
        <img alt="PyPI Downloads" src="https://static.pepy.tech/personalized-badge/scrapling?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X (formerly Twitter)">
      <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="Supported Python versions">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/"><strong>選択メソッド</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/"><strong>Fetcherの選び方</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>スパイダー</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>プロキシローテーション</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/"><strong>MCPモード</strong></a>
</p>

Scraplingは、単一のリクエストから本格的なクロールまですべてを処理する適応型Web Scrapingフレームワークです。

そのパーサーはウェブサイトの変更から学習し、ページが更新されたときに要素を自動的に再配置します。Fetcherはすぐに使えるCloudflare Turnstileなどのアンチボットシステムを回避します。そしてSpiderフレームワークにより、Pause & Resumeや自動Proxy回転機能を備えた並行マルチSessionクロールへとスケールアップできます — すべてわずか数行のPythonで。1つのライブラリ、妥協なし。

リアルタイム統計とStreamingによる超高速クロール。Web Scraperによって、Web Scraperと一般ユーザーのために構築され、誰にでも何かがあります。

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # レーダーの下でウェブサイトを取得！
products = p.css('.product', auto_save=True)                                        # ウェブサイトのデザイン変更に耐えるデータをスクレイプ！
products = p.css('.product', adaptive=True)                                         # 後でウェブサイトの構造が変わったら、`adaptive=True`を渡して見つける！
```
または本格的なクロールへスケールアップ
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
  name = "demo"
  start_urls = ["https://example.com/"]

  async def parse(self, response: Response):
      for item in response.css('.product'):
          yield {"title": item.css('h2::text').get()}

MySpider().start()
```


# プラチナスポンサー

<i><sub>ここに最初に表示される企業になりませんか？[こちら](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)をクリック</sub></i>
# スポンサー

<!-- sponsors -->

<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>


<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>ここに広告を表示したいですか？[こちら](https://github.com/sponsors/D4Vinci)をクリックして、あなたに合ったティアを選択してください！</sub></i>

---

## 主な機能

### Spider — 本格的なクロールフレームワーク
- 🕷️ **Scrapy風のSpider API**：`start_urls`、async `parse` callback、`Request`/`Response`オブジェクトでSpiderを定義。
- ⚡ **並行クロール**：設定可能な並行数制限、ドメインごとのスロットリング、ダウンロード遅延。
- 🔄 **マルチSessionサポート**：HTTPリクエストとステルスヘッドレスブラウザの統一インターフェース — IDによって異なるSessionにリクエストをルーティング。
- 💾 **Pause & Resume**：Checkpointベースのクロール永続化。Ctrl+Cで正常にシャットダウン；再起動すると中断したところから再開。
- 📡 **Streamingモード**：`async for item in spider.stream()`でリアルタイム統計とともにスクレイプされたアイテムをStreamingで受信 — UI、パイプライン、長時間実行クロールに最適。
- 🛡️ **ブロックされたリクエストの検出**：カスタマイズ可能なロジックによるブロックされたリクエストの自動検出とリトライ。
- 📦 **組み込みエクスポート**：フックや独自のパイプライン、または組み込みのJSON/JSONLで結果をエクスポート。それぞれ`result.items.to_json()` / `result.items.to_jsonl()`を使用。

### Sessionサポート付き高度なウェブサイト取得
- **HTTPリクエスト**：`Fetcher`クラスで高速かつステルスなHTTPリクエスト。ブラウザのTLS fingerprint、ヘッダーを模倣し、HTTP/3を使用可能。
- **動的読み込み**：PlaywrightのChromiumとGoogle Chromeをサポートする`DynamicFetcher`クラスによる完全なブラウザ自動化で動的ウェブサイトを取得。
- **アンチボット回避**：`StealthyFetcher`とfingerprint偽装による高度なステルス機能。自動化でCloudflareのTurnstile/Interstitialのすべてのタイプを簡単に回避。
- **Session管理**：リクエスト間でCookieと状態を管理するための`FetcherSession`、`StealthySession`、`DynamicSession`クラスによる永続的なSessionサポート。
- **Proxy回転**：すべてのSessionタイプに対応したラウンドロビンまたはカスタム戦略の組み込み`ProxyRotator`、さらにリクエストごとのProxyオーバーライド。
- **ドメインブロック**：ブラウザベースのFetcherで特定のドメイン（およびそのサブドメイン）へのリクエストをブロック。
- **asyncサポート**：すべてのFetcherおよび専用asyncSessionクラス全体での完全なasyncサポート。

### 適応型スクレイピングとAI統合
- 🔄 **スマート要素追跡**：インテリジェントな類似性アルゴリズムを使用してウェブサイトの変更後に要素を再配置。
- 🎯 **スマート柔軟選択**：CSSセレクタ、XPathセレクタ、フィルタベース検索、テキスト検索、正規表現検索など。
- 🔍 **類似要素の検出**：見つかった要素に類似した要素を自動的に特定。
- 🤖 **AIと使用するMCPサーバー**：AI支援Web Scrapingとデータ抽出のための組み込みMCPサーバー。MCPサーバーは、AI（Claude/Cursorなど）に渡す前にScraplingを活用してターゲットコンテンツを抽出する強力でカスタムな機能を備えており、操作を高速化し、トークン使用量を最小限に抑えることでコストを削減します。（[デモ動画](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）

### 高性能で実戦テスト済みのアーキテクチャ
- 🚀 **超高速**：ほとんどのPythonスクレイピングライブラリを上回る最適化されたパフォーマンス。
- 🔋 **メモリ効率**：最小のメモリフットプリントのための最適化されたデータ構造と遅延読み込み。
- ⚡ **高速JSONシリアル化**：標準ライブラリの10倍の速度。
- 🏗️ **実戦テスト済み**：Scraplingは92%のテストカバレッジと完全な型ヒントカバレッジを備えているだけでなく、過去1年間に数百人のWeb Scraperによって毎日使用されてきました。

### 開発者/Web Scraperにやさしい体験
- 🎯 **インタラクティブWeb Scraping Shell**：Scrapling統合、ショートカット、curlリクエストをScraplingリクエストに変換したり、ブラウザでリクエスト結果を表示したりするなどの新しいツールを備えたオプションの組み込みIPython Shellで、Web Scrapingスクリプトの開発を加速。
- 🚀 **ターミナルから直接使用**：オプションで、コードを一行も書かずにScraplingを使用してURLをスクレイプできます！
- 🛠️ **豊富なナビゲーションAPI**：親、兄弟、子のナビゲーションメソッドによる高度なDOMトラバーサル。
- 🧬 **強化されたテキスト処理**：組み込みの正規表現、クリーニングメソッド、最適化された文字列操作。
- 📝 **自動セレクタ生成**：任意の要素に対して堅牢なCSS/XPathセレクタを生成。
- 🔌 **馴染みのあるAPI**：Scrapy/Parselで使用されている同じ疑似要素を持つScrapy/BeautifulSoupに似た設計。
- 📘 **完全な型カバレッジ**：優れたIDEサポートとコード補完のための完全な型ヒント。コードベース全体が変更のたびに**PyRight**と**MyPy**で自動的にスキャンされます。
- 🔋 **すぐに使えるDockerイメージ**：各リリースで、すべてのブラウザを含むDockerイメージが自動的にビルドおよびプッシュされます。

## はじめに

深く掘り下げずに、Scraplingにできることの簡単な概要をお見せしましょう。

### 基本的な使い方
Sessionサポート付きHTTPリクエスト
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # ChromeのTLS fingerprintの最新バージョンを使用
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# または一回限りのリクエストを使用
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
高度なステルスモード
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # 完了するまでブラウザを開いたままにする
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# または一回限りのリクエストスタイル、このリクエストのためにブラウザを開き、完了後に閉じる
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
完全なブラウザ自動化
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # 完了するまでブラウザを開いたままにする
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # お好みであればXPathセレクタを使用

# または一回限りのリクエストスタイル、このリクエストのためにブラウザを開き、完了後に閉じる
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
並行リクエスト、複数のSessionタイプ、Pause & Resumeを備えた本格的なクローラーを構築：
```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"{len(result.items)}件の引用をスクレイプしました")
result.items.to_json("quotes.json")
```
単一のSpiderで複数のSessionタイプを使用：
```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            # 保護されたページはステルスSessionを通してルーティング
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 明示的なcallback
```
Checkpointを使用して長時間のクロールをPause & Resume：
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Ctrl+Cを押すと正常に一時停止し、進捗は自動的に保存されます。後でSpiderを再度起動する際に同じ`crawldir`を渡すと、中断したところから再開します。

### 高度なパースとナビゲーション
```python
from scrapling.fetchers import Fetcher

# 豊富な要素選択とナビゲーション
page = Fetcher.get('https://quotes.toscrape.com/')

# 複数の選択メソッドで引用を取得
quotes = page.css('.quote')  # CSSセレクタ
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoupスタイル
# 以下と同じ
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # など...
# テキスト内容で要素を検索
quotes = page.find_by_text('quote', tag='div')

# 高度なナビゲーション
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # チェーンセレクタ
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# 要素の関連性と類似性
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
ウェブサイトを取得せずにパーサーをすぐに使用することもできます：
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
まったく同じ方法で動作します！

### 非同期Session管理の例
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession`はコンテキストアウェアで、同期/非同期両方のパターンで動作可能
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# 非同期Sessionの使用
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # オプション - ブラウザタブプールのステータス（ビジー/フリー/エラー）
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLIとインタラクティブShell

Scraplingには強力なコマンドラインインターフェースが含まれています：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

インタラクティブWeb Scraping Shellを起動
```bash
scrapling shell
```
プログラミングせずに直接ページをファイルに抽出（デフォルトで`body`タグ内のコンテンツを抽出）。出力ファイルが`.txt`で終わる場合、ターゲットのテキストコンテンツが抽出されます。`.md`で終わる場合、HTMLコンテンツのMarkdown表現になります。`.html`で終わる場合、HTMLコンテンツそのものになります。
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # CSSセレクタ'#fromSkipToProducts'に一致するすべての要素
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> MCPサーバーやインタラクティブWeb Scraping Shellなど、他にも多くの追加機能がありますが、このページは簡潔に保ちたいと思います。完全なドキュメントは[こちら](https://scrapling.readthedocs.io/en/latest/)をご覧ください

## パフォーマンスベンチマーク

Scraplingは強力であるだけでなく、超高速です。以下のベンチマークは、Scraplingのパーサーを他の人気ライブラリの最新バージョンと比較しています。

### テキスト抽出速度テスト（5000個のネストされた要素）

| # |      ライブラリ      | 時間(ms) | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   2.02    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.04    |     1.01     |
| 3 |     Raw Lxml      |   2.54    |    1.257     |
| 4 |      PyQuery      |   24.17   |     ~12x     |
| 5 |    Selectolax     |   82.63   |     ~41x     |
| 6 |  MechanicalSoup   |  1549.71  |   ~767.1x    |
| 7 |   BS4 with Lxml   |  1584.31  |   ~784.3x    |
| 8 | BS4 with html5lib |  3391.91  |   ~1679.1x   |


### 要素類似性とテキスト検索のパフォーマンス

Scraplingの適応型要素検索機能は代替手段を大幅に上回ります：

| ライブラリ     | 時間(ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |   2.39    |     1.0x     |
| AutoScraper |   12.45   |    5.209x    |


> すべてのベンチマークは100回以上の実行の平均を表します。方法論については[benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)を参照してください。

## インストール

ScraplingにはPython 3.10以上が必要です：

```bash
pip install scrapling
```

このインストールにはパーサーエンジンとその依存関係のみが含まれており、Fetcherやコマンドライン依存関係は含まれていません。

### オプションの依存関係

1. 以下の追加機能、Fetcher、またはそれらのクラスのいずれかを使用する場合は、Fetcherの依存関係とブラウザの依存関係を次のようにインストールする必要があります：
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    これにより、すべてのブラウザ、およびそれらのシステム依存関係とfingerprint操作依存関係がダウンロードされます。

    または、コマンドを実行する代わりにコードからインストールすることもできます：
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 追加機能：
   - MCPサーバー機能をインストール：
       ```bash
       pip install "scrapling[ai]"
       ```
   - Shell機能（Web Scraping Shellと`extract`コマンド）をインストール：
       ```bash
       pip install "scrapling[shell]"
       ```
   - すべてをインストール：
       ```bash
       pip install "scrapling[all]"
       ```
   これらの追加機能のいずれかの後（まだインストールしていない場合）、`scrapling install`でブラウザの依存関係をインストールする必要があることを忘れないでください

### Docker
DockerHubから次のコマンドですべての追加機能とブラウザを含むDockerイメージをインストールすることもできます：
```bash
docker pull pyd4vinci/scrapling
```
またはGitHubレジストリからダウンロード：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
このイメージは、GitHub Actionsとリポジトリのメインブランチを使用して自動的にビルドおよびプッシュされます。

## 貢献

貢献を歓迎します！始める前に[貢献ガイドライン](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)をお読みください。

## 免責事項

> [!CAUTION]
> このライブラリは教育および研究目的のみで提供されています。このライブラリを使用することにより、地域および国際的なデータスクレイピングおよびプライバシー法に準拠することに同意したものとみなされます。著者および貢献者は、このソフトウェアの誤用について責任を負いません。常にウェブサイトの利用規約とrobots.txtファイルを尊重してください。

## 🎓 引用
研究目的で当ライブラリを使用された場合は、以下の参考文献で引用してください：
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## ライセンス

この作品はBSD-3-Clauseライセンスの下でライセンスされています。

## 謝辞

このプロジェクトには次から適応されたコードが含まれています：
- Parsel（BSDライセンス）— [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)サブモジュールに使用

---
<div align="center"><small>Karim Shoairによって❤️でデザインおよび作成されました。</small></div><br>
