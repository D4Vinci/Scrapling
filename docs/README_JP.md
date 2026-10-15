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
    <a href="https://hub.docker.com/r/pyd4vinci/scrapling" target="_blank">
        <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/pyd4vinci/scrapling?labelColor=%20%23FDB062&logo=Docker&labelColor=%20%23528bff"></a>
    <a href="https://clickpy.clickhouse.com/dashboard/scrapling" rel="nofollow"><img src="https://img.shields.io/pypi/dm/scrapling" alt="PyPI package downloads"></a>
    <a href="https://scrapling.readthedocs.io/en/latest/ai/agent-skill.html" alt="AI Agent Skill">
        <img alt="Static Badge" src="https://img.shields.io/badge/Skill-black?style=flat&label=Agent&link=https%3A%2F%2Fscrapling.readthedocs.io%2Fen%2Flatest%2Fai%2Fagent-skill.html"></a>
    <a href="https://clawhub.ai/D4Vinci/scrapling-official" alt="OpenClaw Skill">
        <img alt="OpenClaw Skill" src="https://img.shields.io/badge/Clawhub-darkred?style=flat&label=OpenClaw&link=https%3A%2F%2Fclawhub.ai%2FD4Vinci%2Fscrapling-official"></a>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection.html"><strong>選択メソッド</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing.html"><strong>Fetcher の選び方</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>スパイダー</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>プロキシローテーション</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html"><strong>MCP モード</strong></a>
</p>

Scrapling は、高速な HTTP リクエスト、ステルスブラウザ、強力なパース機能、並行クロールを 1 つのライブラリにまとめた Python Web スクレイピングフレームワークです。

静的ページのスクレイピング、JavaScript のレンダリング、ウェブサイトの操作、ページの裏で呼ばれる API からのデータ抽出に対応します。再利用可能なセッション、プロキシローテーション、自動リトライ、一時停止/再開、組み込みのデータエクスポート機能を備えたクローラーを構築できます。

Python やターミナルから、または MCP サーバーと Agent Skill を通じて AI エージェントから利用できます。いくつかのフィールドの抽出から、ウェブサイト全体を読みやすい Markdown として収集する作業まで、Scrapling がスクレイピングの全工程をカバーします。

## Scrapling でできること

- **[取得と操作](https://scrapling.readthedocs.io/en/latest/fetching/choosing.html)**：高速な HTTP リクエスト、ステルスブラウザ、JavaScript のレンダリング、Cloudflare Turnstile/Interstitial への対応、セッションの維持、バックグラウンドの API 通信の記録。
- **[パースと抽出](https://scrapling.readthedocs.io/en/latest/parsing/selection.html)**：CSS、XPath、テキストと正規表現による検索、適応型の要素追跡、類似要素のマッチング、読みやすい Markdown 出力。
- **[クロールとエクスポート](https://scrapling.readthedocs.io/en/latest/spiders/getting-started.html)**：並行クロール、プロキシローテーション、リトライ、AutoThrottle、一時停止/再開、ストリーミング、すぐに使える Spider テンプレート、JSON/JSONL/CSV/XML エクスポート。
- **[AI やターミナルからスクレイピング](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html)**：AI エージェントがウェブを閲覧してデータを抽出するための MCP サーバー、Agent Skill、CLI コマンド、インタラクティブ Shell。

まずは 1 ページから：

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
print(quotes)
```

または Spider でスケールアップ：

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

`10` が表示され、引用と著者が `quotes.json` に保存されます。

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# プラチナスポンサー
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingseptember" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingseptember" target="_blank">NodeMaven</a> - Webスクレイピングと自動化のための最も効率的なプロキシプロバイダーで、市場最高品質のIPを提供します。コード SCRAPLING35 で35%割引になります。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling は Cloudflare Turnstile に対応。エンタープライズレベルの保護には、<a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a>が<b>Akamai</b>、<b>DataDome</b>、<b>Kasada</b>、<b>Incapsula</b>向けの有効な antibot トークンを生成する API エンドポイントを提供。シンプルな API 呼び出しで、ブラウザ自動化不要。 </td>
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
      </a>：レジデンシャルプロキシが $0.49/GB から。完全に偽装された Chromium によるスクレイピングブラウザ、レジデンシャル IP、自動 CAPTCHA 解決、アンチボットバイパス。</br>
      <b>Scraper API で手間なく結果を取得。MCP と N8N の統合に対応。</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank">TikHub.io</a> は TikTok、X、YouTube、Instagram を含む 16 以上のプラットフォームで 900 以上の安定した API を提供し、4,000 万以上のデータセットを保有。<br /> さらに <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">割引 AI モデル</a>も提供 - Claude、GPT、GEMINI など最大 71% オフ。
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
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> は195カ国以上、8,000万以上のIPを備えたスケーラブルな住宅用プロキシを提供し、高速で信頼性の高い接続、自動ローテーション、強力なブロック回避性能を実現します。無料トライアルあり。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank" title="Ethically sourced residential proxy infrastructure powering web scraping and AI agents">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/byteful.png">
      </a>
    </td>
    <td>
    <a href="https://byteful.com/?utm_source=github&utm_medium=github-sponsor&utm_campaign=scrapling_github_sponsor" target="_blank">Byteful</a> は、倫理的に調達されたレジデンシャル、モバイル、ISP、データセンタープロキシに加え、スクレイピングとAI自動化のツールを提供します。コード SCRAPLING10 でレジデンシャルプロキシが10%オフになります。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank" title="28M+ clean residential IPs for browser automation. No Blocks. No CAPTCHAs. Pay-as-you-Go.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxylane.png">
      </a>
    </td>
    <td>
    <a href="https://proxylane.dev/?utm_source=scrapling&utm_medium=partnership&utm_campaign=scrapling_platinum_202609&utm_content=github_readme" target="_blank">ProxyLane</a>：ブロックとCAPTCHAを90%削減。大規模なWebスクレイピング向けに、2,800万の高品質なレジデンシャルIPを提供。195か国に対応。都市・ISP・郵便番号（ZIP）の指定が可能。固定・ローテーションセッション。有効期限のない通信量を $2/GB から提供。コード <strong>SCRAPEANDTAKE</strong> で<em>25%オフ</em>。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.lundproxy.com/unlimited-residential-bandwidth.html?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=banner" target="_blank" title="Unlimited residential traffic, sized only by bandwidth.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/lundproxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.lundproxy.com?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=text" target="_blank">LundProxy</a>：GB単位の課金はもう不要。レジデンシャルプロキシの通信量は無制限。1億以上のIP、190か国以上に対応。帯域幅に応じた料金。50 Mbps のレジデンシャルプロキシの無料トライアルをお申し込みください。
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank" title="Buy Pay-as-you-go proxies from $1/GB">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse_Platinum.png">
      </a>
    </td>
    <td>
    <a href="https://dataimpulse.com/?utm_source=website&utm_medium=github_readme&utm_campaign=scrapling_platinum" target="_blank">DataImpulse</a> なら $1/GB。倫理的に調達された自社提供のプロキシ。9,000万以上のIP、195か国以上に対応。レジデンシャル、データセンター、モバイル。従量課金 = サブスクリプション不要。通信量に有効期限はありません。
    </td>
  </tr>
</table>

<i><sub>ここに広告を表示したいですか？[こちら](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)をクリック</sub></i>
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

<i><sub>ここに広告を表示したいですか？[こちら](https://github.com/sponsors/D4Vinci)をクリックして、あなたに合ったティアを選択してください！</sub></i>

---

## 主な機能

### Spider - 本格的なクロールフレームワーク
- 🕷️ **Scrapy 風の Spider API**：`start_urls`、async `parse` callback、`Request`/`Response` オブジェクトで Spider を定義。
- ⚡ **並行クロール**：設定可能な並行数制限、ドメインごとのスロットリング、ダウンロード遅延。
- 🔄 **マルチ Session サポート**：HTTP リクエストとステルスヘッドレスブラウザの統一インターフェース - ID によって異なる Session にリクエストをルーティング。
- 💾 **一時停止と再開**：`crawldir` で保留中のリクエストと訪問済み URL を保存します。Ctrl+C で正常終了し、同じディレクトリで再起動します。
- 📡 **Streaming モード**：`async for item in spider.stream()` でリアルタイム統計とともにスクレイプされたアイテムを Streaming で受信 - UI、パイプライン、長時間実行クロールに最適。
- 🛡️ **ブロックされたリクエストの検出**：カスタマイズ可能なロジックによるブロックされたリクエストの自動検出とリトライ。
- 🚦 **AutoThrottle**：待ち時間を勘で決める必要はありません。Spider がサイトの応答速度からドメインごとの待ち時間を自動調整し、ブロックやレート制限が始まると待ち時間を 2 倍に（または `Retry-After` が求める時間だけ待機）して、収まればまた加速します。
- 🤖 **robots.txt 準拠**：オプションの `robots_txt_obey` フラグで `Disallow`、`Crawl-delay`、`Request-rate` ディレクティブをドメインごとのキャッシュで遵守。
- 🧪 **開発モード**：初回実行時にレスポンスをディスクにキャッシュし、以降の実行ではそれを再生 - ターゲットサーバーに再リクエストすることなく `parse()` ロジックを反復開発できます。
- 🧩 **すぐに使える Spider テンプレート**：定型コードは不要です。ルールベースのリンク追跡には `CrawlSpider`、sitemap/robots.txt を起点としたクロールには `SitemapSpider`、XML/RSS や CSV フィードの走査には `XMLFeedSpider`/`CSVFeedSpider`、そして `ShopifySpider` で公開されている Shopify ストアの商品を取得できます（バリエーションごとに 1 件）。
- 🔗 **リンク抽出**：allow/deny パターン、ドメインフィルタ、CSS/XPath による範囲指定、拡張子フィルタ、正規化に対応した独立した `LinkExtractor` を提供。テンプレート内でも単体でも使用できます。
- 📦 **組み込みエクスポート**：フックや独自のパイプライン、または組み込みの JSON/JSONL/CSV/XML で結果をエクスポート。`result.items.to_json()`、`to_jsonl()`、`to_csv()`、`to_xml()` が使えます。

### Session サポート付き高度なウェブサイト取得
- **HTTP リクエスト**：`Fetcher` クラスで高速かつステルスな HTTP リクエスト。ブラウザの TLS fingerprint、ヘッダーを模倣し、HTTP/3 を使用可能。
- **動的読み込み**：Playwright の Chromium と Google Chrome をサポートする `StealthyFetcher` クラスによる完全なブラウザ自動化で動的ウェブサイトを取得。
- **アンチボット回避**：`StealthyFetcher` の高度なステルス機能とフィンガープリント偽装。あらゆる種類の Cloudflare Turnstile/Interstitial を自動で簡単に回避できます。
- **Session 管理**：リクエスト間で Cookie と状態を管理するための `FetcherSession`、`StealthySession` クラスによる永続的な Session サポート。
- **Proxy 回転**：すべての Session タイプに対応したラウンドロビンまたはカスタム戦略の組み込み `ProxyRotator`、さらにリクエストごとの Proxy オーバーライド。
- **ドメイン＆広告ブロック**：ブラウザベースの Fetcher で特定のドメイン（およびそのサブドメイン）へのリクエストをブロック、または内蔵広告ブロック（約3,500の既知の広告/トラッカードメイン）を有効化。
- **DNS リーク防止**：Proxy 使用時の DNS リークを防ぐため、Cloudflare の DoH 経由で DNS クエリをルーティングするオプションの DNS-over-HTTPS サポート。
- **リモートブラウザ**：ローカルでブラウザを起動する代わりに、`cdp_url` を使って CDP 経由で既に起動しているブラウザに接続できます。同じマシン上でも、別のホストでも、マネージドブラウザサービスでも構いません。`executable_path` を使えば、任意のブラウザ Fetcher を独自ビルドの Chromium に向けることもできます。
- **バックグラウンド API キャプチャ**：ブラウザーセッションで `record_requests=True` を有効にし、`session.network.search(limit=None)` で保存済みのレスポンスを検索できます。リクエストを再送信せずに、複数のページ読み込みで発生した API データや HTTP エラーを確認できます。履歴には保存上限があり、テキストのレスポンス本文を保存します。
- **async サポート**：すべての Fetcher および専用 async Session クラス全体での完全な async サポート。

### パースとデータ抽出
- 🔄 **スマート要素追跡**：インテリジェントな類似性アルゴリズムを使用してウェブサイトの変更後に要素を再配置。
- 🎯 **スマート柔軟選択**：CSS セレクタ、XPath セレクタ、フィルタベース検索、テキスト検索、正規表現検索など。
- 🔍 **類似要素の検出**：見つかった要素に類似した要素を自動的に特定。

### AI 機能
- 🤖 **MCP サーバー**：AI チャットボットやエージェント（Claude/Cursor など）が Scrapling を通じてスクレイピングできるようにします。HTTP リクエスト、ブラウザ操作、スクリーンショット、保存済みログイン状態、バックグラウンド API レスポンスを利用できます。独自のステルスブラウザと適切なツールで、十分な能力を持つ AI モデルが作業中に遭遇するどんな CAPTCHA でも回避できるようにします（もちろん、独自の Cloudflare ソルバーもあります）。モデルに送る内容の削減、広告のブロック、プロンプトインジェクションからの保護にさまざまな手法を使います。CDP 経由のリモートブラウザと認証オプション付き HTTP トランスポートにも対応します。（[デモ動画](https://www.youtube.com/watch?v=qyFk3ZNwOxE)）
- 🧠 **Agent Skill**：ライブラリ全体をコーディングエージェントに教える、インストールするだけの [Agent Skill](https://scrapling.readthedocs.io/en/latest/ai/agent-skill.html)。エージェントが Scrapling で書くコードが、推測ではなく現在の API に沿ったものになります。
- 📚 **RAG 対応の Markdown**：1 行（`page.markdown()`）で任意のページをクリーンでサニタイズ済みの LLM 向け Markdown に変換したり、`ContentSpider` テンプレートでサイト全体を Markdown コーパスとしてクロールしたりできます。処理に LLM は一切使いません。（[ドキュメント](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html)）

### 高性能で実戦テスト済みのアーキテクチャ
- 🚀 **超高速**：ほとんどの Python スクレイピングライブラリを上回る最適化されたパフォーマンス。
- 🔋 **メモリ効率**：最小のメモリフットプリントのための最適化されたデータ構造と遅延読み込み。
- ⚡ **高速 JSON シリアル化**：標準ライブラリの 10 倍の速度。
- 🏗️ **実戦テスト済み**：Scrapling は 92% のテストカバレッジと完全な型ヒントカバレッジを備えているだけでなく、過去1年間に数百人の Web Scraper によって毎日使用されてきました。

### 開発者/Web Scraper にやさしい体験
- 🎯 **インタラクティブ Web Scraping Shell**：Scrapling 統合、ショートカット、curl リクエストを Scrapling リクエストに変換したり、ブラウザでリクエスト結果を表示したりするなどの新しいツールを備えたオプションの組み込み IPython Shell で、Web Scraping スクリプトの開発を加速。
- 🚀 **ターミナルから直接使用**：オプションで、コードを一行も書かずに Scrapling を使用して URL をスクレイプできます！
- 🛠️ **豊富なナビゲーション API**：親、兄弟、子のナビゲーションメソッドによる高度な DOM トラバーサル。
- 🧬 **強化されたテキスト処理**：組み込みの正規表現、クリーニングメソッド、最適化された文字列操作。
- 📝 **自動セレクタ生成**：任意の要素に対して堅牢な CSS/XPath セレクタを生成。
- 🔌 **馴染みのある API**：Scrapy/Parsel で使用されている同じ疑似要素を持つ Scrapy/BeautifulSoup に似た設計。
- 🤝 **Scrapy とのシームレスな統合**：すでに Scrapy を使っていますか？任意のコールバックを `scrapling_response` でデコレートするだけで、既に取得しているレスポンスを Scrapling のパーサーで解析できます。書き直しは不要です。
- 📘 **完全な型カバレッジ**：優れた IDE サポートとコード補完のための完全な型ヒント。コードベース全体が変更のたびに**PyRight**と**MyPy**で自動的にスキャンされます。
- 🔋 **すぐに使える Docker イメージ**：各リリースで、すべてのブラウザを含む Docker イメージが自動的にビルドおよびプッシュされます。

## はじめに

深く掘り下げずに、Scrapling にできることの簡単な概要をお見せしましょう。

### 基本的な使い方
Session サポート付き HTTP リクエスト
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
並行リクエスト、複数の Session タイプ、Pause & Resume を備えた本格的なクローラーを構築：
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
単一の Spider で複数の Session タイプを使用：
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
Checkpoint を使用して長時間のクロールをPause & Resume：
```python
QuotesSpider(crawldir="./crawl_data").start()
```
`crawldir` を設定して Ctrl+C を押すと、保留中のリクエストと訪問済み URL が保存されます。同じ `crawldir` で再起動すると再開できます。抽出データは別途保存してください。

あるいは、すぐに使えるテンプレートでクロールのロジックを書くこと自体を省略できます。たとえば Shopify ストアのカタログを丸ごと取得する場合：
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # ストア内の全商品を、バリエーションごとに 1 件取得
```
テンプレートは公開コレクション API が提供する商品を、バリエーションごとに 1 件取得します。

### 高度なパースとナビゲーション
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
ウェブサイトを取得せずにパーサーをすぐに使用することもできます：
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
まったく同じ方法で動作します！

### 非同期 Session 管理の例
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

## CLI とインタラクティブ Shell

Scrapling には強力なコマンドラインインターフェースが含まれています：

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

インタラクティブ Web Scraping Shell を起動
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
> MCP サーバーやインタラクティブ Web Scraping Shell など、他にも多くの追加機能がありますが、このページは簡潔に保ちたいと思います。完全なドキュメントは[こちら](https://scrapling.readthedocs.io/en/latest/)をご覧ください

## パフォーマンスベンチマーク

Scrapling は強力であるだけでなく、超高速です。以下のベンチマークは、Scrapling のパーサーを他の人気ライブラリの最新バージョンと比較しています。

### テキスト抽出速度テスト（5000 個のネストされた要素）

| # |      ライブラリ      | 時間 (ms) | vs Scrapling |
|---|:-----------------:|:---------:|:------------:|
| 1 |     Scrapling     |   1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |   2.06    |    1.035     |
| 3 |     Raw Lxml      |   2.56    |    1.286     |
| 4 |      PyQuery      |   23.98   |     ~12x     |
| 5 |    Selectolax     |  197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15  |   ~776.5x    |
| 7 |   BS4 with Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 with html5lib |  3412.73  |   ~1714.9x   |


### 要素類似性とテキスト検索のパフォーマンス

Scrapling の適応型要素検索機能は代替手段を大幅に上回ります：

| ライブラリ     | 時間 (ms) | vs Scrapling |
|-------------|:---------:|:------------:|
| Scrapling   |    2.3    |     1.0x     |
| AutoScraper |   12.58   |    5.47x     |


> すべてのベンチマークは 100 回以上の実行の平均を表します。方法論については[benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py)を参照してください。

## インストール

Scrapling には Python 3.10 以上が必要です：

```bash
pip install scrapling
```

> [!IMPORTANT]
> このインストールにはパーサーエンジンとその依存関係のみが含まれており、Fetcher やコマンドライン依存関係は含まれていません。 そのため、このインストールのみでは、上記の例のように `scrapling.fetchers` や `scrapling.spiders` から何かをインポートすると `ModuleNotFoundError` が発生します。Fetcher や Spider を使用する場合は、以下のように、まず Fetcher の依存関係をインストールしてください。

### オプションの依存関係

1. 以下の追加機能、Fetcher、またはそれらのクラスのいずれかを使用する場合は、Fetcher の依存関係とブラウザの依存関係を次のようにインストールする必要があります：
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    これにより、すべてのブラウザ、およびそれらのシステム依存関係とfingerprint 操作依存関係がダウンロードされます。

    または、コマンドを実行する代わりにコードからインストールすることもできます：
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. 追加機能：
   - MCP サーバー機能をインストール：
       ```bash
       pip install "scrapling[ai]"
       ```
   - （[RAG システムの構築](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html)）用の依存関係をインストール：
       ```bash
       pip install "scrapling[rag]"
       ```
   - Shell 機能（Web Scraping Shell と`extract`コマンド）をインストール：
       ```bash
       pip install "scrapling[shell]"
       ```
   - すべてをインストール：
       ```bash
       pip install "scrapling[all]"
       ```
   ブラウザ fetcher を使う場合は `scrapling install` を実行してください。HTTP リクエストにはブラウザのインストールは不要です。

### Docker
DockerHub から次のコマンドですべての追加機能とブラウザを含む Docker イメージをインストールすることもできます：
```bash
docker pull pyd4vinci/scrapling
```
または GitHub レジストリからダウンロード：
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
このイメージは、GitHub Actions とリポジトリのメインブランチを使用して自動的にビルドおよびプッシュされます。

## 貢献

貢献を歓迎します！始める前に[貢献ガイドライン](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md)をお読みください。

## 免責事項

> [!CAUTION]
> このライブラリは教育および研究目的のみで提供されています。このライブラリを使用することにより、地域および国際的なデータスクレイピングおよびプライバシー法に準拠することに同意したものとみなされます。著者および貢献者は、このソフトウェアの誤用について責任を負いません。常にウェブサイトの利用規約とrobots.txt ファイルを尊重してください。

## 🎓 引用
研究目的で当ライブラリを使用された場合は、以下の参考文献で引用してください：
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

この作品は BSD-3-Clause ライセンスの下でライセンスされています。

## 謝辞

このプロジェクトには次から適応されたコードが含まれています：
- Parsel（BSD ライセンス）- [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py) サブモジュールに使用

---
<div align="center"><small>Karim Shoair によって❤️でデザインおよび作成されました。</small></div><br>
