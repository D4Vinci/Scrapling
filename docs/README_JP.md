<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/v4/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Web Scraping have never been easier!</small>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection/">
        選択メソッド
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing/">
        フェッチャーの選択
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview/">
        CLI
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server/">
        MCPモード
    </a>
    ·
    <a href="https://scrapling.readthedocs.io/en/latest/tutorials/migrating_from_beautifulsoup/">
        Beautifulsoupからの移行
    </a>
</p>

**アンチボットシステムとの戦いをやめましょう。ウェブサイトが更新されるたびにセレクタを書き直すのをやめましょう。**

Scraplingは単なるウェブスクレイピングライブラリではありません。ウェブサイトの変更から学習し、それとともに進化する最初の**適応型**スクレイピングライブラリです。他のライブラリがウェブサイトの構造が更新されると壊れる一方で、Scraplingは自動的に要素を再配置し、スクレイパーを稼働し続けます。

モダンウェブ向けに構築されたScraplingは、**独自の高速パースエンジン**とフェッチャーを備えており、あなたが直面する、または直面するであろうすべてのウェブスクレイピングの課題に対応します。ウェブスクレイパーによってウェブスクレイパーと一般ユーザーのために構築され、誰にでも何かがあります。

```python
>> from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
>> StealthyFetcher.adaptive = True
# レーダーの下でウェブサイトのソースを取得！
>> page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)
>> print(page.status)
200
>> products = page.css('.product', auto_save=True)  # ウェブサイトのデザイン変更に耐えるデータをスクレイプ！
>> # 後でウェブサイトの構造が変わったら、`adaptive=True`を渡す
>> products = page.css('.product', adaptive=True)  # そしてScraplingはまだそれらを見つけます！
```

# スポンサー 

<!-- sponsors -->

<a href="https://www.scrapeless.com/en?utm_source=official&utm_term=scrapling" target="_blank" title="Effortless Web Scraping Toolkit for Business and Developers"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/scrapeless.jpg"></a>
<a href="https://www.thordata.com/?ls=github&lk=github" target="_blank" title="Unblockable proxies and scraping infrastructure, delivering real-time, reliable web data to power AI models and workflows."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/thordata.jpg"></a>
<a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png"></a>
<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png"></a>
<a href="https://hasdata.com/?utm_source=github&utm_medium=banner&utm_campaign=D4Vinci" target="_blank" title="The web scraping service that actually beats anti-bot systems!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/hasdata.png"></a>
<a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png"></a>
<a href="https://www.swiftproxy.net/" target="_blank" title="Unlock Reliable Proxy Services with Swiftproxy!"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/swiftproxy.png"></a>
<a href="https://www.rapidproxy.io/?ref=d4v" target="_blank" title="Affordable Access to the Proxy World – bypass CAPTCHAs blocks, and avoid additional costs."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/rapidproxy.jpg"></a>
<a href="https://browser.cash/?utm_source=D4Vinci&utm_medium=referral" target="_blank" title="Browser Automation & AI Browser Agent Platform"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/browserCash.png"></a>

<!-- /sponsors -->

<i><sub>ここに広告を表示したいですか？[こちら](https://github.com/sponsors/D4Vinci)をクリックして、あなたに合ったティアを選択してください！</sub></i>

---

## 主な機能

### セッションサポート付き高度なウェブサイト取得
- **HTTPリクエスト**：`Fetcher`クラスで高速でステルスなHTTPリクエスト。ブラウザのTLSフィンガープリント、ヘッダーを模倣し、HTTP3を使用できます。
- **動的読み込み**：Playwright's ChromiumとGoogle Chromeをサポートする`DynamicFetcher`クラスを通じた完全なブラウザ自動化で動的ウェブサイトを取得。
- **アンチボット回避**：`StealthyFetcher`とフィンガープリント偽装による高度なステルス機能。自動化でCloudflareのTurnstile/Interstitialのすべてのタイプを簡単に回避できます。
- **セッション管理**：リクエスト間でCookieと状態を管理するための`FetcherSession`、`StealthySession`、`DynamicSession`クラスによる永続的なセッションサポート。
- **非同期サポート**：すべてのフェッチャーと専用非同期セッションクラス全体での完全な非同期サポート。

### 適応型スクレイピングとAI統合
- 🔄 **スマート要素追跡**：インテリジェントな類似性アルゴリズムを使用してウェブサイトの変更後に要素を再配置。
- 🎯 **スマート柔軟選択**：CSSセレクタ、XPathセレクタ、フィルタベース検索、テキスト検索、正規表現検索など。
- 🔍 **類似要素を見つける**：見つかった要素に類似した要素を自動的に特定。
- 🤖 **AIと使用するMCPサーバー**：AI支援ウェブスクレイピングとデータ抽出のための組み込みMCPサーバー。MCPサーバーは、AI（Claude/Cursorなど）に渡す前にScraplingを活用してターゲットコンテンツを抽出する強力でカスタムな機能を備えており、操作を高速化し、トークン使用量を最小限に抑えることでコストを削減します。（[デモビデオ](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）

### 高性能で実戦テスト済みのアーキテクチャ
- 🚀 **高速**：ほとんどのPythonスクレイピングライブラリを上回る最適化されたパフォーマンス。
- 🔋 **メモリ効率**：最小のメモリフットプリントのための最適化されたデータ構造と遅延読み込み。
- ⚡ **高速JSONシリアル化**：標準ライブラリの10倍の速度。
- 🏗️ **実戦テスト済み**：Scraplingは92%のテストカバレッジと完全な型ヒントカバレッジを備えているだけでなく、過去1年間に数百人のウェブスクレイパーによって毎日使用されてきました。

### 開発者/ウェブスクレイパーにやさしい体験
- 🎯 **インタラクティブウェブスクレイピングシェル**：Scraping統合、ショートカット、curlリクエストをScraplingリクエストに変換したり、ブラウザでリクエスト結果を表示したりするなどの新しいツールを備えたオプションの組み込みIPythonシェルで、ウェブスクレイピングスクリプトの開発を加速します。
- 🚀 **ターミナルから直接使用**：オプションで、コードを一行も書かずにScraplingを使用してURLをスクレイプできます！
- 🛠️ **豊富なナビゲーションAPI**：親、兄弟、子のナビゲーションメソッドによる高度なDOMトラバーサル。
- 🧬 **強化されたテキスト処理**：組み込みの正規表現、クリーニングメソッド、最適化された文字列操作。
- 📝 **自動セレクタ生成**：任意の要素に対して堅牢なCSS/XPathセレクタを生成。
- 🔌 **馴染みのあるAPI**：Scrapy/Parselで使用されている同じ疑似要素を持つScrapy/BeautifulSoupに似ています。
- 📘 **完全な型カバレッジ**：優れたIDEサポートとコード補完のための完全な型ヒント。
- 🔋 **すぐに使えるDockerイメージ**：各リリースで、すべてのブラウザを含むDockerイメージが自動的にビルドおよびプッシュされます。

## はじめに

### 基本的な使い方
```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

# セッションサポート付きHTTPリクエスト
with FetcherSession(impersonate='chrome') as session:  # ChromeのTLSフィンガープリントの最新バージョンを使用
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')

# または一回限りのリクエストを使用
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')

# 高度なステルスモード（完了するまでブラウザを開いたままにする）
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')

# または一回限りのリクエストスタイルを使用、このリクエストのためにブラウザを開き、完了後に閉じる
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
    
# 完全なブラウザ自動化（完了するまでブラウザを開いたままにする）
with DynamicSession(headless=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', network_idle=True)
    quotes = page.css('.quote .text::text')

# または一回限りのリクエストスタイルを使用
page = DynamicFetcher.fetch('https://quotes.toscrape.com/', network_idle=True)
quotes = page.css('.quote .text::text')
```

### 要素の選択
```python
# CSSセレクタ
page.css('a::text')                      # テキストを抽出
page.css('a::attr(href)')                # 属性を抽出
page.css('a', recursive=False)           # 直接の要素のみ
page.css('a', auto_save=True)            # 要素の位置を自動保存

# XPath
page.xpath('//a/text()')

# 柔軟な検索
page.find_by_text('Python', first_match=True)  # テキストで検索
page.find_by_regex(r'\d{4}')                   # 正規表現パターンで検索
page.find('div', {'class': 'container'})       # 属性で検索

# ナビゲーション
element.parent                           # 親要素を取得
element.next_sibling                     # 次の兄弟を取得
element.children                         # 子要素を取得

# 類似要素
similar = page.get_similar(element)      # 類似要素を見つける

# 適応型スクレイピング
saved_elements = page.css('.product', auto_save=True)
# 後でウェブサイトが変更されたとき：
page.css('.product', adaptive=True)      # 保存された位置を使用して要素を見つける
```

### セッションの使用
```python
from scrapling.fetchers import FetcherSession, AsyncFetcherSession

# 同期セッション
with FetcherSession() as session:
    # Cookieは自動的に維持されます
    page1 = session.get('https://quotes.toscrape.com/login')
    page2 = session.post('https://quotes.toscrape.com/login', data={'username': 'admin', 'password': 'admin'})
    
    # 必要に応じてブラウザのフィンガープリントを切り替え
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# 非同期セッションの使用
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

## CLIとインタラクティブシェル

Scrapling v0.3には強力なコマンドラインインターフェースが含まれています：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

インタラクティブウェブスクレイピングシェルを起動
```bash
scrapling shell
```
プログラミングせずに直接ページをファイルに抽出（デフォルトで`body`タグ内のコンテンツを抽出）。出力ファイルが`.txt`で終わる場合、ターゲットのテキストコンテンツが抽出されます。`.md`で終わる場合、HTMLコンテンツのMarkdown表現になります；`.html`で終わる場合、HTMLコンテンツそのものになります。
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # CSSセレクタ'#fromSkipToProducts'に一致するすべての要素
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> MCPサーバーやインタラクティブウェブスクレイピングシェルなど、他にも多くの追加機能がありますが、このページは簡潔に保ちたいと思います。完全なドキュメントは[こちら](https://scrapling.readthedocs.io/en/latest/)をご覧ください

## パフォーマンスベンチマーク

Scraplingは強力であるだけでなく、驚くほど高速で、バージョン0.3以降のアップデートはすべての操作で優れたパフォーマンス向上を実現しています。以下のベンチマークは、Scraplingのパーサーを他の人気のあるライブラリと比較しています。

### テキスト抽出速度テスト（5000個のネストされた要素）

| # |       ライブラリ       | 時間(ms)  | vs Scrapling | 
|---|:-----------------:|:-------:|:------------:|
| 1 |     Scrapling     |  1.99   |     1.0x     |
| 2 |   Parsel/Scrapy   |  2.01   |    1.01x     |
| 3 |     Raw Lxml      |   2.5   |    1.256x    |
| 4 |      PyQuery      |  22.93  |    ~11.5x    |
| 5 |    Selectolax     |  80.57  |    ~40.5x    |
| 6 |   BS4 with Lxml   | 1541.37 |   ~774.6x    |
| 7 |  MechanicalSoup   | 1547.35 |   ~777.6x    |
| 8 | BS4 with html5lib | 3410.58 |   ~1713.9x   |


### 要素類似性とテキスト検索のパフォーマンス

Scraplingの適応型要素検索機能は代替手段を大幅に上回ります：

| ライブラリ       | 時間(ms) | vs Scrapling |
|-------------|:------:|:------------:|
| Scrapling   |  2.46  |     1.0x     |
| AutoScraper |  13.3  |    5.407x    |


> すべてのベンチマークは100回以上の実行の平均を表します。方法論については[benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)を参照してください。

## インストール

ScraplingにはPython 3.10以上が必要です：

```bash
pip install scrapling
```

v0.3.2以降、このインストールにはパーサーエンジンとその依存関係のみが含まれており、フェッチャーやコマンドライン依存関係は含まれていません。

### オプションの依存関係

1. 以下の追加機能、フェッチャー、またはそれらのクラスのいずれかを使用する場合は、フェッチャーの依存関係とブラウザの依存関係を次のようにインストールする必要があります：
    ```bash
    pip install "scrapling[fetchers]"
    
    scrapling install
    ```

    これにより、すべてのブラウザ、およびそれらのシステム依存関係とフィンガープリント操作依存関係がダウンロードされます。

2. 追加機能：
   - MCPサーバー機能をインストール：
       ```bash
       pip install "scrapling[ai]"
       ```
   - シェル機能（ウェブスクレイピングシェルと`extract`コマンド）をインストール：
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

## ライセンス

この作品はBSD-3-Clauseライセンスの下でライセンスされています。

## 謝辞

このプロジェクトには次から適応されたコードが含まれています：
- Parsel（BSDライセンス）— [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)サブモジュールに使用

## 感謝と参考文献

- [Daijro](https://github.com/daijro)の[BrowserForge](https://github.com/daijro/browserforge)と[Camoufox](https://github.com/daijro/camoufox)における素晴らしい仕事
- [Vinyzu](https://github.com/Vinyzu)の[Botright](https://github.com/Vinyzu/Botright)と[PatchRight](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)における素晴らしい仕事
- ブラウザ検出回避技術を提供する[brotector](https://github.com/kaliiiiiiiiii/brotector)
- フィンガープリント研究を提供する[fakebrowser](https://github.com/kkoooqq/fakebrowser)と[BotBrowser](https://github.com/botswin/BotBrowser)

---
<div align="center"><small>Karim Shoairによって❤️でデザインおよび作成されました。</small></div><br>