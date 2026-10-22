<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io/ja/latest/">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling のカバー画像" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>現代のウェブを手軽にスクレイピング</small>
</h1>

<p align="center">
    <a href="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml" alt="テスト">
        <img alt="テスト" src="https://github.com/D4Vinci/Scrapling/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://badge.fury.io/py/Scrapling" alt="PyPI のバージョン">
        <img alt="PyPI のバージョン" src="https://badge.fury.io/py/Scrapling.svg"></a>
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker のダウンロード数" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI パッケージのダウンロード数"></a>
    <a href="https://scrapling.readthedocs.io/ja/latest/ai/agent-skill.html" alt="AI エージェント向け Skill">
        <img alt="Agent Skill のバッジ" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fja%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw 向け Skill">
        <img alt="OpenClaw 向け Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
    <br/>
    <a href="https://discord.gg/EMgGbDceNQ" alt="Discord" target="_blank">
      <img alt="Discord" src="https://img.shields.io/discord/1360786381042880532?style=social&logo=discord&link=https%3A%2F%2Fdiscord.gg%2FEMgGbDceNQ">
    </a>
    <a href="https://x.com/Scrapling_dev" alt="X（旧 Twitter）">
      <img alt="X（旧 Twitter）でフォロー" src="https://img.shields.io/twitter/follow/Scrapling_dev?style=social&logo=x&link=https%3A%2F%2Fx.com%2FScrapling_dev">
    </a>
    <br/>
    <a href="https://pypi.org/project/scrapling/" alt="対応する Python バージョン">
        <img alt="対応する Python バージョン" src="https://img.shields.io/pypi/pyversions/scrapling.svg"></a>
</p>

<p align="center">
    <a href="https://scrapling.readthedocs.io/ja/latest/parsing/selection.html"><strong>選択メソッド</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ja/latest/fetching/choosing.html"><strong>Fetcher の選び方</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ja/latest/spiders/architecture.html"><strong>Spider</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ja/latest/spiders/proxy-blocking.html"><strong>プロキシの切り替え</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ja/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/ja/latest/ai/mcp-server.html"><strong>MCP サーバー</strong></a>
</p>

Scrapling は Python のウェブスクレイピングフレームワークです。高速な HTTP リクエスト、ステルスブラウザ、ページの解析、並行クロールをひとつのライブラリで扱えます。

静的なページの取得、JavaScript の実行、サイトの操作、背後にある API からのデータ抽出ができます。セッションの再利用、プロキシの切り替え、自動再試行、一時停止と再開、データの出力に対応したクローラーを作れます。

Python やターミナルから使うほか、MCP サーバーと Agent Skill を通じて AI エージェントからも使えます。少数の項目を取り出す作業から、サイト全体を整理された Markdown ファイルとして保存する作業まで対応します。

## Scrapling でできること

- **[ページの取得と操作](https://scrapling.readthedocs.io/ja/latest/fetching/choosing.html)**：高速な HTTP リクエスト、ステルスブラウザ、JavaScript の実行、Cloudflare Turnstile と Interstitial への対応、永続セッション、バックグラウンド API レスポンスの記録。
- **[解析とデータ抽出](https://scrapling.readthedocs.io/ja/latest/parsing/selection.html)**：CSS、XPath、テキスト、正規表現による検索、ページ変更後の要素の追跡、類似要素の検索、整理された Markdown の出力。
- **[クロールと出力](https://scrapling.readthedocs.io/ja/latest/spiders/getting-started.html)**：並行クロール、プロキシの切り替え、再試行、AutoThrottle、一時停止と再開、ストリーミング、すぐに使えるテンプレート、JSON・JSONL・CSV・XML への出力。
- **[AI やターミナルからの利用](https://scrapling.readthedocs.io/ja/latest/ai/mcp-server.html)**：AI エージェントがページを操作してデータを抽出するための MCP サーバー、Agent Skill、CLI コマンド、対話型シェル。

まずはひとつのページから始めます。

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

Spider を使えば、より多くのページを取得できます。

```python
from scrapling.spiders import Spider, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

result = QuotesSpider().start()
print(len(result.items))
result.items.to_json("quotes.json")
```

このコードは `10` を表示し、名言と作者を `quotes.json` に保存します。

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# プラチナスポンサー
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingoctober" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingoctober" target="_blank">NodeMaven</a> は、ウェブスクレイピングと自動化向けの最も効率的なプロキシサービスです。市場最高品質の IP を提供します。コード SCRAPLING35 で 35% 割引になります。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling は Cloudflare Turnstile に対応します。企業向けの高度な保護には、<a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a>が<b>Akamai</b>、<b>DataDome</b>、<b>Kasada</b>、<b>Incapsula</b>向けの有効なボット対策用トークンを生成する API を提供します。簡単な API 呼び出しだけで使え、ブラウザの自動操作は不要です。 </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling" target="_blank" title="Evomi is your Swiss Quality Proxy Provider, starting at $0.49/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/evomi.png">
      </a>
    </td>
    <td>
      <a href="https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=d4vinci-scrapling">
        <b>Evomi</b>
      </a>：レジデンシャルプロキシが $0.49/GB から。フィンガープリントを全面的に偽装した Chromium のスクレイピングブラウザを提供します。レジデンシャル IP、CAPTCHA の自動解決、ボット対策の回避に対応します。</br>
      <b>Scraper API で手間なく結果を取得できます。MCP と N8N との連携にも対応します。</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">The Web Scraping Club で Scrapling の詳細レビュー</a>（2025年11月）をお読みください。Web スクレイピング専門の No.1 ニュースレターです。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> は 195 か国以上、8,000 万以上の IP を備え、利用規模に合わせて使えるレジデンシャルプロキシを提供します。高速で信頼性の高い接続、自動のプロキシ切り替え、強力なブロック回避機能が特長です。無料で試せます。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> は、倫理的に調達されたレジデンシャル、モバイル、ISP、データセンタープロキシに加え、スクレイピングと AI 自動化のツールを提供します。コード SCRAPLING10 でレジデンシャルプロキシが 10% オフになります。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>：ブロックと CAPTCHA を 90% 削減します。大規模なウェブスクレイピング向けに、2,800 万の高品質なレジデンシャル IP を提供します。195 か国に対応し、都市・ISP・郵便番号（ZIP）を指定できます。同じ IP を保つセッションと、IP を切り替えるセッションを使えます。有効期限のない通信量を $2/GB から提供します。コード <strong>SCRAPEANDTAKE</strong> で<em>25% オフ</em>になります。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>：GB 単位の課金は不要です。レジデンシャルプロキシの通信量は無制限です。1 億以上の IP、190 か国以上に対応します。料金は帯域幅に応じて決まります。50 Mbps のレジデンシャルプロキシの無料トライアルをお申し込みください。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a> なら $1/GB です。倫理的に調達された自社提供のプロキシで、9,000 万以上の IP、195 か国以上に対応します。レジデンシャル、データセンター、モバイルのプロキシを使えます。従量課金なので、定期契約は不要です。通信量に有効期限はありません。
    </td>
  </tr>
</table>

<i><sub>ここに広告を掲載するには、[こちら](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)をご覧ください。</sub></i>
# スポンサー

<!-- sponsors -->

<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=github&utm_medium=paid_referral&utm_campaign=open_source_sponsorship&utm_content=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>ここに広告を掲載するには、[こちら](https://github.com/sponsors/D4Vinci)からプランを選んでください。</sub></i>

---

## 主な機能

### Spider：本格的なクロールフレームワーク

- 🕷️ **Scrapy に似た Spider API**：`start_urls`、非同期の `parse` コールバック、`Request` と `Response` オブジェクトで Spider を定義します。
- ⚡ **並行クロール**：同時に処理するリクエスト数、ドメインごとの制限、ダウンロードの待ち時間を設定できます。
- 🔄 **複数のセッション**：ひとつの Spider で HTTP リクエストとステルス対応のヘッドレスブラウザを使えます。セッション ID でリクエストの処理先を選びます。
- 💾 **一時停止と再開**：`crawldir` で待機中のリクエストと訪問済み URL を保存します。Ctrl+C で安全に停止し、同じディレクトリで起動すると続きから再開できます。
- 📡 **ストリーミング**：`async for item in spider.stream()` で、抽出したデータをすぐに受け取れます。統計もリアルタイムで確認できます。画面への表示、データ処理、長時間のクロールに適しています。
- 🛡️ **ブロックの検出**：ブロックされたリクエストを自動で検出し、再試行します。処理は変更できます。
- 🚦 **AutoThrottle**：サイトの応答速度に合わせて、ドメインごとの待ち時間を自動調整します。ブロックや頻度制限を受けたら待ち時間を 2 倍にするか、`Retry-After` が指定する時間を待ちます。問題が収まると再び速度を上げます。
- 🤖 **robots.txt の遵守**：`robots_txt_obey` を有効にすると、`Disallow`、`Crawl-delay`、`Request-rate` に従います。ルールはドメインごとにキャッシュします。
- 🧪 **開発モード**：初回のレスポンスをディスクに保存し、次回から再利用します。サーバーに再度アクセスせずに `parse()` を調整できます。
- 🧩 **すぐに使える Spider テンプレート**：`CrawlSpider` はルールに沿ってリンクをたどり、`SitemapSpider` は sitemap や robots.txt を起点にクロールします。`XMLFeedSpider` と `CSVFeedSpider` は XML・RSS・CSV フィードを読み取ります。`ShopifySpider` は公開 Shopify ストアの商品を取得し、バリエーションごとに 1 件のデータを出力します。
- 🔗 **リンク抽出**：`LinkExtractor` はパターンによる許可と除外、ドメインや拡張子の絞り込み、CSS と XPath による範囲指定、URL の正規化に対応します。テンプレート内でも単体でも使えます。
- 📦 **データの出力**：フックと独自の処理を使うか、組み込みの JSON・JSONL・CSV・XML 出力を使えます。`result.items.to_json()`、`to_jsonl()`、`to_csv()`、`to_xml()` を呼び出します。

### セッションを使ったページの取得

- **HTTP リクエスト**：`Fetcher` で高速かつ検出されにくい HTTP リクエストを送れます。ブラウザの TLS フィンガープリントとヘッダーの模倣や、HTTP/3 に対応します。
- **動的なページの読み込み**：`StealthyFetcher` のブラウザ自動化で動的なサイトを取得できます。Playwright の Chromium と Google Chrome に対応します。
- **ボット検出の回避**：`StealthyFetcher` は自動化の痕跡を隠し、フィンガープリントを偽装します。Cloudflare Turnstile や Interstitial の各種検証を自動処理できます。
- **セッション管理**：`FetcherSession` と `StealthySession` は、リクエスト間で Cookie と状態を保持します。
- **プロキシの切り替え**：`ProxyRotator` は、すべてのセッションで順番に、または独自のルールでプロキシを切り替えます。リクエストごとにプロキシを指定することもできます。
- **ドメインと広告のブロック**：指定したドメインとそのサブドメインへのリクエストを止められます。ブラウザ Fetcher には広告ブロック機能もあり、約 3,500 の広告・追跡用ドメインに対応します。
- **DNS リークの防止**：DNS-over-HTTPS を有効にすると、Cloudflare の DoH を通じて DNS を問い合わせます。プロキシ使用時の DNS リークを防ぎます。
- **リモートブラウザ**：CDP と `cdp_url` を使い、すでに動いているブラウザに接続できます。同じパソコン、別のサーバー、ブラウザ提供サービスのいずれでも使えます。`executable_path` で、各ブラウザ Fetcher に独自の Chromium を指定することもできます。
- **バックグラウンド API レスポンスの記録**：ブラウザセッションで `record_requests=True` を有効にし、`session.network.search(limit=None)` で保存済みレスポンスを検索します。リクエストを送り直さずに、複数のページ読み込みで発生した API データや HTTP エラーを確認できます。履歴には上限があり、テキストのレスポンス本文を保存します。
- **非同期対応**：すべての Fetcher で非同期処理を使えます。専用の非同期セッションもあります。

### 解析とデータ抽出

- 🔄 **要素の再検索**：サイトが変わった後も、類似度を使って要素を見つけ直します。
- 🎯 **柔軟な選択**：CSS、XPath、フィルター、テキスト、正規表現などを使えます。
- 🔍 **類似要素の検索**：見つけた要素に似た要素を自動で探します。

### AI 機能

- 🤖 **MCP サーバー**：Claude や Cursor などの AI アシスタントとエージェントが Scrapling を使ってデータを抽出できます。HTTP リクエスト、ブラウザ操作、スクリーンショット、保存済みログイン状態、バックグラウンド API レスポンスに対応します。ステルスブラウザとツールを使い、対応する能力を持つモデルが CAPTCHA を処理できるようにします。Cloudflare 検証の処理機能もあります。モデルへ送る内容を減らし、広告をブロックし、プロンプトインジェクションから保護します。CDP によるリモートブラウザ接続や、認証付きの HTTP 接続にも対応します。（[デモ動画](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）
- 🧠 **Agent Skill**：インストールして使える [Agent Skill](https://scrapling.readthedocs.io/ja/latest/ai/agent-skill.html) が、コーディングエージェントにライブラリの使い方を伝えます。現在の API に合ったコードを書く助けになります。
- 📚 **RAG 向けの Markdown**：1 行のコード（`page.markdown()`）で、ページを整理・クリーニングした LLM 向けの Markdown に変換します。`ContentSpider` テンプレートを使えば、サイト全体を Markdown ファイルに保存できます。この処理に LLM は不要です。（[ドキュメント](https://scrapling.readthedocs.io/ja/latest/ai/building-rag-systems.html)）

### 高速で、実際の作業にも使われています

- 🚀 **高速な処理**：最適化により、多くの Python スクレイピングライブラリを上回る速度を実現しています。
- 🔋 **少ないメモリ使用量**：最適化したデータ構造と、必要なときだけ読み込む仕組みを使っています。
- ⚡ **高速な JSON 出力**：標準ライブラリの 10 倍の速度です。
- 🏗️ **実際の作業で検証済み**：テストカバレッジは 92% で、すべてのコードに型ヒントがあります。この 1 年間、数百人が毎日のデータ抽出に使ってきました。

### 開発とデータ抽出のためのツール

- 🎯 **対話型シェル**：Scrapling と連携した IPython シェルを追加できます。ショートカットやツールでスクリプトの開発を助けます。curl リクエストを Scrapling のリクエストに変換し、結果をブラウザで確認できます。
- 🚀 **ターミナルからの利用**：コードを書かずに URL の内容を取得できます。
- 🛠️ **DOM の移動**：親要素、兄弟要素、子要素をたどれます。
- 🧬 **テキスト処理**：正規表現、テキストのクリーニング、最適化した文字列操作を使えます。
- 📝 **セレクターの生成**：任意の要素に対する CSS と XPath のセレクターを生成します。
- 🔌 **使い慣れた API**：Scrapy や BeautifulSoup に似た API で、Scrapy と Parsel と同じ疑似要素を使えます。
- 🤝 **Scrapy との連携**：コールバックに `scrapling_response` デコレーターを付けると、取得済みのレスポンスを Scrapling のパーサーで解析できます。プログラムを書き直す必要はありません。
- 📘 **すべてのコードに型ヒント**：エディターでの確認とコード補完を助けます。変更のたびに、すべてのコードを **PyRight** と **MyPy** で自動チェックします。
- 🔋 **すぐに使える Docker イメージ**：リリースごとに、すべてのブラウザを含む Docker イメージを自動で作成・公開します。

## はじめに

よく使う機能をいくつか紹介します。

### 基本的な使い方
セッションを使った HTTP リクエスト
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Chrome の TLS fingerprint の最新バージョンを使用
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
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
data = page.css('#padded_content a').getall()
```
完全なブラウザ自動化
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, disable_resources=False, network_idle=True) as session:  # 完了するまでブラウザを開いたままにする
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # お好みであれば XPath セレクタを使用

# または一回限りのリクエストスタイル、このリクエストのためにブラウザを開き、完了後に閉じる
page = StealthyFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
並行リクエスト、複数のセッション、一時停止と再開に対応したクローラーを作れます。
```python
from scrapling.spiders import Spider, Response

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
ひとつの Spider で、複数の種類のセッションを使えます。
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
            # 保護されたページはステルス Session を通してルーティング
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # 明示的な callback
```
進捗を保存すれば、長時間のクロールを一時停止して再開できます。次のように Spider を起動します。
```python
QuotesSpider(crawldir="./crawl_data").start()
```
`crawldir` を設定して Ctrl+C を押すと、保留中のリクエストと訪問済み URL が保存されます。同じ `crawldir` で再起動すると再開できます。抽出データは別途保存してください。

すぐに使えるテンプレートもあります。たとえば、Shopify ストアの商品全体を取得できます。
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # ストア内の全商品を、バリエーションごとに 1 件取得
```
このテンプレートは公開されているコレクション API から商品を読み取り、バリエーションごとに 1 件のデータを出力します。

### さらに詳しい解析と要素の移動
```python
from scrapling.fetchers import Fetcher

# 豊富な要素選択とナビゲーション
page = Fetcher.get('https://quotes.toscrape.com/')

# 複数の選択メソッドで引用を取得
quotes = page.css('.quote')  # CSS セレクタ
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup スタイル
# 以下と同じ
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # など...
# テキスト内容で要素を検索
quotes = page.find_by_text('Albert Einstein', first_match=False)

# 高度なナビゲーション
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_texts = page.css('.quote').css('.text::text').getall()  # チェーンセレクタ
first_quote = page.css('.quote')[0]
author = first_quote.css('.author::text').get()
next_quote = first_quote.next
parent_container = first_quote.parent

# 要素の関連性と類似性
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements
```
ページを取得せずに、パーサーを直接使うこともできます。
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
使い方は同じです。

### 非同期セッションの例
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession

async def main():
    async with FetcherSession(http3=True) as http_session:  # `FetcherSession` はコンテキストに応じて同期・非同期の両方で動作します
        page1 = await http_session.get('https://quotes.toscrape.com/')
        page2 = await http_session.get('https://quotes.toscrape.com/page/2/', impersonate='chrome')
        print(len(page1.css('.quote')), len(page2.css('.quote')))

    async with AsyncStealthySession(max_pages=2) as browser_session:
        urls = ['https://quotes.toscrape.com/js/', 'https://quotes.toscrape.com/js/page/2/']
        pages = await asyncio.gather(*(browser_session.fetch(url, wait_selector='.quote') for url in urls))
        print([len(page.css('.quote')) for page in pages])

asyncio.run(main())
```

## CLI と対話型シェル

ターミナルからも Scrapling を使えます。

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

スクレイピング用の対話型シェルを起動します。
```bash
pip install "scrapling[shell]"
scrapling shell
```
プログラミングなしでページをファイルに抽出できます。`--css-selector` で内容を選ぶか、`--ai-targeted` で `body` の内容を選択・クリーニングします。テキストは `.txt`、Markdown は `.md`、HTML は `.html` を使います。
```bash
scrapling extract get 'https://quotes.toscrape.com/' quotes.md
scrapling extract get 'https://quotes.toscrape.com/' quotes.txt --css-selector '.quote' --impersonate 'chrome'
scrapling extract fetch 'https://quotes.toscrape.com/js/' quotes.md --css-selector '.quote' --wait-selector '.quote' --no-headless
scrapling extract fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> MCP サーバーや対話型シェルなど、ほかの機能は[ドキュメント](https://scrapling.readthedocs.io/ja/latest/)をご覧ください。

## 性能テスト

Scrapling は処理速度も重視しています。以下では、そのパーサーと他のよく使われるライブラリの最新バージョンを比較します。

### テキスト抽出の速度（5,000 個の入れ子の要素）

| # |      ライブラリ      | 時間（ミリ秒） | Scrapling との比較 |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Lxml 単体      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 + Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 + html5lib |  3412.73  |   ~1714.9x   |


### 類似要素とテキストの検索

Scrapling の適応型の要素検索は、他の方法より高速です。

| ライブラリ     | 時間（ミリ秒） | Scrapling との比較 |
|-------------|:---------:|:------------:|
| Scrapling   |    2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x     |


> 各結果は、100 回以上の実行の平均です。測定方法は [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) をご覧ください。

## インストール

Scrapling には Python 3.10 以上が必要です。

```bash
pip install scrapling
```

> [!IMPORTANT]
> このコマンドはパーサーとその依存パッケージだけをインストールします。Fetcher やコマンドラインツールは含まれません。この状態で上の例のように `scrapling.fetchers` や `scrapling.spiders` からインポートすると、`ModuleNotFoundError` が発生します。Fetcher や Spider を使う場合は、先に以下の手順で Fetcher の依存パッケージをインストールしてください。

### 追加の依存パッケージ

1. Fetcher、関連するクラス、以下の追加機能を使う場合は、Fetcher とブラウザに必要なパッケージをインストールします。
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    すべてのブラウザ、必要なシステムパッケージ、フィンガープリントを変更するツールがダウンロードされます。

    コマンドの代わりに、Python のコードからインストールすることもできます。
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 追加機能：
   - MCP サーバーをインストール：
       ```bash
       pip install "scrapling[ai]"
       ```
   - [RAG システムの構築](https://scrapling.readthedocs.io/ja/latest/ai/building-rag-systems.html)に必要なパッケージをインストール：
       ```bash
       pip install "scrapling[rag]"
       ```
   - 対話型シェルと `extract` コマンドをインストール：
       ```bash
       pip install "scrapling[shell]"
       ```
   - すべての機能をインストール：
       ```bash
       pip install "scrapling[all]"
       ```
   ブラウザ Fetcher を使う場合は `scrapling install` を実行してください。HTTP リクエストにはブラウザのインストールは不要です。

### Docker
すべての追加機能とブラウザを含む Docker イメージを DockerHub から取得することもできます。
```bash
docker pull pyd4vinci/scrapling
```
GitHub のレジストリからも取得できます。
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
このイメージはリポジトリのメインブランチを使い、GitHub Actions で自動作成・公開されます。

## 開発への参加

開発への参加を歓迎します。始める前に[参加ガイド](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)をお読みください。

## 免責事項

> [!CAUTION]
> このライブラリは学習と研究のために提供しています。利用する場合は、地域および国際的なデータ取得とプライバシーの法律に従うことに同意したものとします。作者と開発への参加者は、ソフトウェアの悪用に責任を負いません。サイトの利用規約と robots.txt に従ってください。

## 🎓 引用
研究でこのライブラリを使った場合は、次の形式で引用してください。
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {A Python Web Scraping framework for everything from a single request to a full-scale crawl!}
  }
```

## ライセンス

本プロジェクトは BSD-3-Clause ライセンスで公開しています。

## 謝辞

本プロジェクトには、次のプロジェクトをもとにしたコードが含まれます。
- Parsel（BSD ライセンス）：[translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) サブモジュールで使用

---
<div align="center"><small>Karim Shoair が❤️を込めてデザイン・制作しました。</small></div><br>
