# Changelog

All notable changes to Scrapling, taken from the [GitHub releases](https://github.com/D4Vinci/Scrapling/releases).

## [v0.4.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.14) - 2026-08-10

**A quick maintenance release to fix installation with `uv` 🔧**

### 🐛 Bug Fixes

- **Fixed `uv` refusing to install v0.4.13 by default and silently falling back to an older version**. The previous release required a prerelease version of `curl_cffi`, which `uv` doesn't allow unless explicitly enabled.
All dependencies now resolve to stable releases. (Fixes [#407](https://github.com/D4Vinci/Scrapling/issues/407))

## [v0.4.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.13) - 2026-08-09

**A new update bringing feed spiders and a smarter MCP server 🎉**

### 🚀 New Stuff and quality of life changes

- **New feed spider templates**. `XMLFeedSpider` iterates over the nodes of any XML feed (RSS, Atom, product feeds, etc.), and `CSVFeedSpider` iterates over CSV rows as dictionaries. Both decompress gzipped feeds automatically. (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/generic-templates.html))
  ```python
  from scrapling.spiders import XMLFeedSpider

  class RSSSpider(XMLFeedSpider):
      name = "rss"
      start_urls = ["https://example.com/feed.xml"]

      async def parse_node(self, response, node):
          yield {"title": node.findtext("title"), "link": node.findtext("link")}

  result = RSSSpider().start()
  ```
- **Upgraded the MCP server to MCP SDK v2 and made it smarter**. The server now ships instructions that teach your AI agent how to use the tools efficiently; every tool declares annotations so clients like Claude Code can auto-approve the read-only ones; tool descriptions are leaner to save tokens; and the server advertises its version and logo to MCP clients. (Check the [docs](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html))
- **Added a `scrapling-mcp` command** that maps directly to `scrapling mcp`, so registering Scrapling with MCP clients and registries that expect a single command is now a one-liner.
- **Unpinned Playwright/Patchright and browser versions**. The generated browser User-Agent now always matches the exact Chromium version your installed Playwright/Patchright drives, so Scrapling no longer pins their versions and you can upgrade them freely. Run `scrapling install --force` after updating to refresh the browsers.

### 🐛 Bug Fixes

- **Fixed importing Scrapling crashing with a `browserforge` ValueError** when the fingerprints data package lags behind the browser versions. (Fixes [#394](https://github.com/D4Vinci/Scrapling/issues/394), [#396](https://github.com/D4Vinci/Scrapling/issues/396), and [#400](https://github.com/D4Vinci/Scrapling/issues/400))
- **Fixed the MCP bulk browser tools mis-sizing their page pools**, which made `bulk_fetch` fail on batches of more than 50 URLs and `bulk_stealthy_fetch` fetch all URLs through a single tab, by @Yigtwxx in [#393](https://github.com/D4Vinci/Scrapling/pull/393).

### Project

- **New [AI Contribution Policy](https://github.com/D4Vinci/Scrapling/blob/main/AI_POLICY.md)**: AI-assisted contributions are welcome but must be disclosed in the PR or issue; submissions that look like undisclosed AI output get labeled and closed.

## [v0.4.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.12) - 2026-07-26

**A release focused on making your spiders smarter about the websites they crawl**

### 🚀 New Stuff and quality of life changes

- **Spiders can now tune their own speed with AutoThrottle.** Instead of guessing a `download_delay` that's either too slow or gets you banned, the spider measures how fast each website answers and adjusts the delay of every domain on its own. When a website starts blocking or rate-limiting you, it doubles the delay (or waits exactly what the `Retry-After` header asks for) until that stops, then speeds back up. Your `download_delay` and any robots.txt `Crawl-delay` are still respected as the minimum. (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/advanced.html#autothrottle))
    ```python
    class MySpider(Spider):
        name = "adaptive"
        start_urls = ["https://example.com"]
        autothrottle_enabled = True
        autothrottle_start_delay = 2.0
        autothrottle_max_delay = 30.0
        autothrottle_block_backoff = True
    ```

- **Export your results to CSV and XML**, next to the JSON/JSONL exporters you already had. Items that don't all share the same keys are still exported without losing anything, and nested values are written as JSON. (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/getting-started.html))
    ```python
    result = MySpider().start()
    result.items.to_csv("products.csv")
    result.items.to_xml("products.xml")
    ```

- **The MCP server can now require authentication**, so you can safely expose it instead of keeping it on your own machine. Any request without the token is rejected, and you can also restrict which hostnames the server answers to. (Check the [docs](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html))
    ```bash
    scrapling mcp --http --auth-token "$(openssl rand -hex 32)"
    ```

- **Browsers now accept CDP URLs over HTTP**, not just WebSocket ones. So next to the `wss://` endpoints managed browser providers hand out, you can now point any browser fetcher or MCP session at a Chrome you started yourself with `--remote-debugging-port=9222`.

- **Published Docker images are now tagged with their release version** instead of only `latest`, so you can pin the exact version you want, by @JanRK in [#384](https://github.com/D4Vinci/Scrapling/pull/384).

### 🐛 Bug Fixes

- **Fixed cached responses losing all their cookies** when the response came from a browser engine, which silently broke any session or auth logic relying on them while using the spiders' development mode, by @amitvijapur in [#379](https://github.com/D4Vinci/Scrapling/pull/379). (Fixes [#376](https://github.com/D4Vinci/Scrapling/issues/376))

- **Fixed `StealthyFetcher` forcing the `en-US` locale** on every browser instead of following your system's, which made websites see a mismatch between your locale and your IP address and treat you as suspicious, like Google answering with 429s. (Fixes [#381](https://github.com/D4Vinci/Scrapling/issues/381))

- **Fixed a misleading error message in the storage system** and removed a dead call left after inserts, by @fix2015 in [#377](https://github.com/D4Vinci/Scrapling/pull/377).

### Performance

- **`get_all_text()` is now O(nodes)** instead of walking up the ancestors of every single text node, which makes it around 5-6x faster on deeply nested pages, by @yetval in [#378](https://github.com/D4Vinci/Scrapling/pull/378).

## [v0.4.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.11) - 2026-07-12

**A solid update bringing the first platform spider template, a faster parser, and important fixes 🎉**

### 🚀 New Stuff and quality of life changes

- **Added `ShopifySpider`, the first platform spider template!** Extract every product from any Shopify-powered store through its JSON API without touching the website's HTML. Subclass it, set the store's domain, and you are done (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/platform-templates/))
  ```python
  from scrapling.spiders import ShopifySpider

  class MyStore(ShopifySpider):
      target_website = "example.com"

  result = MyStore().start()
  ```
- **Added `--executable-path` to the CLI browser commands**. Both `scrapling extract fetch` and `scrapling extract stealthy-fetch` now accept a custom Chromium-compatible browser executable, and fall back to the `SCRAPLING_EXECUTABLE_PATH` environment variable when the option isn't passed, bringing full parity with the MCP server (Solves [#371](https://github.com/D4Vinci/Scrapling/issues/371))
  ```bash
  scrapling extract fetch "https://example.com" page.html --executable-path "/path/to/chromium"
  ```
### 🤖 Quality of life changes
- **Made `find_by_text` and `find_by_regex` up to ~2x faster** when `first_match` is enabled (the default) by wrapping elements lazily so the search stops at the first match, by @yetval in [#370](https://github.com/D4Vinci/Scrapling/pull/370)
- **Updated the benchmarks with the new numbers against the latest versions of all libraries.**
- **Updated contribution rules**

### 🐛 Bug Fixes

- **Fixed the MCP server's fetch tools crashing on pages containing control characters** with the error `All strings must be XML compatible`, by @yetval in [#368](https://github.com/D4Vinci/Scrapling/pull/368) (Fixes [#366](https://github.com/D4Vinci/Scrapling/issues/366))

## [v0.4.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.10) - 2026-07-04

**A new update with a brand-new Scrapy integration and a batch of community fixes 🎉**

### 🚀 New Stuff and quality of life changes

- **Added a Scrapy integration** so you can use Scrapling's parsing API inside your existing Scrapy projects without rewriting them. Put the `scrapling_response` decorator on any spider callback, and the response it receives becomes a Scrapling `Response` while Scrapy keeps handling the crawling (Check the [docs](https://scrapling.readthedocs.io/en/latest/integrations/scrapy/)):

    ```python
    import scrapy
    from scrapling.integrations.scrapy import scrapling_response

    class QuotesSpider(scrapy.Spider):
        name = "quotes"
        start_urls = ["https://quotes.toscrape.com"]

        @scrapling_response
        def parse(self, response):  # `response` is now a Scrapling Response
            first_quote = response.find_by_text("The world as we have created it", partial=True)
            for quote in [first_quote, *first_quote.find_similar()]:
                yield {"text": quote.get_all_text(strip=True)}
    ```

- **The MCP server can now use a custom Chromium-compatible browser** for all browser-based tools. Set it once with `scrapling mcp --executable-path "/path/to/chromium"` or the `SCRAPLING_EXECUTABLE_PATH` environment variable, or per request with the `executable_path` argument, by @samrusani in [#360](https://github.com/D4Vinci/Scrapling/pull/360) (Solves [#347](https://github.com/D4Vinci/Scrapling/issues/347))
- **Updated all browsers and fingerprints**. Run `scrapling install --force` after updating to refresh them.

### 🐛 Bug Fixes

- **Fixed garbled text (mojibake) from browser fetchers on non-UTF-8 websites** by @yehudalevy-collab in [#365](https://github.com/D4Vinci/Scrapling/pull/365) (Fixes [#364](https://github.com/D4Vinci/Scrapling/issues/364)).
- **Fixed `LinkExtractor` not filtering compound file extensions like `.tar.gz`** by @renbkna in [#359](https://github.com/D4Vinci/Scrapling/pull/359) (Fixes [#349](https://github.com/D4Vinci/Scrapling/issues/349)).
- **Fixed paused crawls losing their in-flight requests from checkpoints, so resuming no longer skips them** by @yetval in [#358](https://github.com/D4Vinci/Scrapling/pull/358).
- **Fixed spiders calculating wrong crawl delays from robots.txt `Request-rate` directives** through the Protego upgrade, with tests aligned by @Disaster-Terminator in [#355](https://github.com/D4Vinci/Scrapling/pull/355).

### Docs

- **Clarified how `init_script` interacts with Patchright's isolated execution context in stealth mode** by @mturac in [#353](https://github.com/D4Vinci/Scrapling/pull/353) (Solves [#350](https://github.com/D4Vinci/Scrapling/issues/350)).
- **Added the [skills.sh](https://skills.sh/D4Vinci/Scrapling) install method for the agent skill** by @ob-aion in [#363](https://github.com/D4Vinci/Scrapling/pull/363).

## [v0.4.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.9) - 2026-06-07

**A maintenance update packed with community-reported fixes 🛠️**

### 🚀 New Stuff and quality of life changes

- **Updated all browsers and fingerprints**. Run `scrapling install --force` after updating to refresh them.
- **Added a `--version` flag to the CLI** by @ETM-Code in [#303](https://github.com/D4Vinci/Scrapling/pull/303) (Solves [#299](https://github.com/D4Vinci/Scrapling/issues/299))

### 🐛 Bug Fixes

- **Fixed the session-level `proxy` argument being silently ignored in HTTP sessions**, which could leak your real IP (Solves [#295](https://github.com/D4Vinci/Scrapling/issues/295)). Note that mixing a session-level `proxy` with a per-request `proxies` argument (or vice versa) now raises an error instead of one being silently dropped.
- **Fixed browser navigations failing when combining `init_script` with `user_data_dir`** (Solves [#294](https://github.com/D4Vinci/Scrapling/issues/294)).
- **Fixed encoding detection when websites quote the charset value in the `Content-Type` header** by @Bortlesboat in [#323](https://github.com/D4Vinci/Scrapling/pull/323).
- **Fixed an `IndexError` in adaptive element relocation when `auto_save` is enabled** by @Mubashirrrr in [#340](https://github.com/D4Vinci/Scrapling/pull/340).
- **Fixed spiders' checkpoint and cache saving crashing on Windows** by @MrStarkEG in [#344](https://github.com/D4Vinci/Scrapling/pull/344).
- **Fixed incorrect similarity scoring in `find_similar` for elements with mismatched attribute counts** (Solves [#322](https://github.com/D4Vinci/Scrapling/issues/322)).

### Docs

- **Clarified that the default installation includes the parser engine only**, and the fetchers/spiders need the extras (Solves [#343](https://github.com/D4Vinci/Scrapling/issues/343)).
- **Fixed the Docker image name in the remaining examples** by @evanclan in [#315](https://github.com/D4Vinci/Scrapling/pull/315).
- **Fixed a broken link in the contribution guide** by @Bortlesboat in [#320](https://github.com/D4Vinci/Scrapling/pull/320).

## [v0.4.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.8) - 2026-05-11

**A big spider update that takes the crawling framework to the next level 🕷️**

### 🚀 New Stuff and quality of life changes

- **Added a `LinkExtractor` primitive** in `scrapling.spiders.LinkExtractor` to pull URLs out of a `Response`. There are a lot of controls (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/generic-templates.html))

    ```python
    from scrapling.spiders import LinkExtractor

    extractor = LinkExtractor(allow=r"/posts/", deny_domains=["ads.example.com"])
    ```

- **Added `CrawlSpider` and `CrawlRule`** generic spider templates so you no longer have to hand-write the same "follow links matching this pattern" boilerplate. Override `rules()` to return a list of `CrawlRule` objects, each pairing a `LinkExtractor`. (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/generic-templates.html))

    ```python
    from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

    class QuotesSpider(CrawlSpider):
        name = "blog"
        start_urls = ["https://quotes.toscrape.com/"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/author/"), callback=self.parse_author),
                CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # pagination, no callback
            ]

        async def parse_author(self, response):
            yield {
                "name": response.css(".author-title::text").get(),
                "birthday": response.css(".author-born-date::text").get(),
                "url": response.url,
            }
    ```

- **Added a `SitemapSpider` template** that seeds a crawl directly from a sitemap, or `robots.txt` URLs. Handles gzip-compressed sitemaps, and a lot of controls and options. URLs are dispatched via the crawl rules as shown above for **CrawlSpider**. (Check the [docs](https://scrapling.readthedocs.io/en/latest/spiders/generic-templates.html))

    ```python
    from scrapling.spiders import SitemapSpider, CrawlRule, LinkExtractor

    class NewsSitemap(SitemapSpider):
        name = "news"
        sitemap_urls = ["https://example.com/robots.txt"]

        def rules(self):
            return [
                CrawlRule(LinkExtractor(allow=r"/articles/"), callback=self.parse_article),
            ]

        async def parse_article(self, response):
            yield {"url": response.url, "title": response.css("h1::text").get()}
    ```

- **Adaptive relocation now defaults to a 40% similarity threshold** instead of `0` across all methods. This will make the adaptive feature work better. When nothing crosses the threshold, a warning now tells you the top score it did see, so you can lower `percentage` deliberately if needed.

- **Updated all browsers and fingerprints**. Run a new `scrapling install  --force` after updating to refresh the browsers and fingerprints.

### 🐛 Bug Fixes

- **Fixed `Fetcher.configure(...)` not applying to per-request calls**. Same fix applied to `AsyncFetcher`.
- **Fixed incorrect request fingerprinting that caused duplicate requests in spiders** by @yetval in [#255](https://github.com/D4Vinci/Scrapling/pull/255).
- **Fixed the Adaptive scraping engine staying silent on weak matches.** Combined with the threshold change above, you now get a warning instead of a misleading "best guess" element when relocation fails.

### Docs

- **Refreshed older code examples** across the documentation to match the current version.
- **Improved the code copy-paste experience** on the docs site and trimmed the agent skill so it uses fewer tokens per invocation.

## [v0.4.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.7) - 2026-04-17

**A focused update bringing eyes to your AI agents 📸**

### 🚀 New Stuff and quality of life changes

- **Added a `screenshot` MCP tool** that captures a page and returns it as a real MCP `ImageContent` block so the model can actually see it. The tool requires an open browser session, so you call `open_session` first (either `dynamic` or `stealthy`) and pass the `session_id` here. Supports PNG and JPEG, full-page captures, JPEG quality, and the usual readiness controls (`wait`, `wait_selector`, `network_idle`, `timeout`). (implements [#244](https://github.com/D4Vinci/Scrapling/issues/244))
- **Added a custom `session_id` parameter to `open_session`** so you can name sessions meaningfully (`"search"`, `"checkout"`) instead of the random 12-character hex default. By @hauntedhost in [#243](https://github.com/D4Vinci/Scrapling/pull/243)

### 🐛 Bug Fixes

- **Fixed `FetcherSession` state corruption and a lazy session close crash**. By @yetval in [#245](https://github.com/D4Vinci/Scrapling/pull/245)
- **Fixed `TypeError: Session.request() got an unexpected keyword argument 'block_ads'`** when using the CLI's `--ai-targeted` flag with HTTP commands. By @voidborne-d in [#249](https://github.com/D4Vinci/Scrapling/pull/249) (Fixes [#247](https://github.com/D4Vinci/Scrapling/issues/247))

### Translations

- **Added a Brazilian Portuguese README translation** By @rgomids in [#250](https://github.com/D4Vinci/Scrapling/pull/250)

## [v0.4.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.6) - 2026-04-13

**A focused update on browser stealth, privacy, and developer experience 🔒**

### 🚀 New Stuff and quality of life changes

- **Added built-in ad blocking** for browser fetchers. Pass `block_ads=True` to block requests to ~3,500 known ad and tracker domains at the route interception level -- no DNS, no TCP, instant abort. Can be combined with `blocked_domains` for custom lists. The MCP server and CLI `--ai-targeted` mode enable this automatically to save tokens and speed up page loads.
    ```python
    page = StealthyFetcher.fetch('https://example.com', block_ads=True)
    ```
- **Added DNS-over-HTTPS support** to prevent DNS leaks when using proxies. Pass `dns_over_https=True` to route DNS queries through Cloudflare's DoH, so your real location isn't exposed through DNS resolution even when your HTTP traffic goes through a proxy.
    ```python
    page = StealthyFetcher.fetch('https://example.com', proxy='http://proxy:8080', dns_over_https=True)
    ```
- **Added `page_setup` callback** for browser fetchers. A function that runs before `page.goto()`, letting you register event listeners, routes, or scripts that must be set up before the page navigates. Pairs with `page_action` (which runs after navigation). (Solves [#237](https://github.com/D4Vinci/Scrapling/issues/237))
    ```python
    def capture_websockets(page):
        page.on("websocket", lambda ws: print(f"WS: {ws.url}"))

    page = DynamicFetcher.fetch('https://example.com', page_setup=capture_websockets)
    ```
- **Added `--block-ads` and `--dns-over-https` CLI options** to both `fetch` and `stealthy-fetch` commands.

### 🐛 Bug Fixes

- **Fixed `Seconds` type alias** rejecting float values. Passing `wait=1.5` or `timeout=500.0` to browser fetchers would fail with a type error because the type alias incorrectly treated `float` as metadata instead of a type. by @kuishou68 in [#240](https://github.com/D4Vinci/Scrapling/pull/240)
- **Fixed duplicate ID segments in full-path selector generation**. Elements with `id` attributes had their selector appended twice when generating full CSS/XPath paths, producing selectors like `body > #main > #main > #target > #target`. Also fixed full-path XPath emitting bare `[@id='x']` predicates (invalid XPath) instead of `*[@id='x']`. by @sjhddh in [#241](https://github.com/D4Vinci/Scrapling/pull/241)
- **Fixed missing shell signature parameters**. The interactive shell was missing `blocked_domains`, `block_ads`, `retries`, `retry_delay`, `capture_xhr`, `executable_path`, and `dns_over_https` from its function signatures.

## [v0.4.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.5) - 2026-04-07

**A focused update with one big quality-of-life feature for spider developers and a couple of important fixes 🎉**

### 🚀 New Stuff and quality of life changes

- **Spider Development Mode**: Iterating on a spider's `parse()` logic used to mean re-hitting the target servers on every run, which is slow, noisy, and a great way to get rate-limited while you're still figuring out your selectors. The new development mode caches every response to disk on the first run and replays them from disk on every subsequent run, so you can tweak your callbacks and re-run as many times as you want without making a single network request. Enable it with one class attribute:

    ```python
    class MySpider(Spider):
        name = "my_spider"
        start_urls = ["https://example.com"]
        development_mode = True

        async def parse(self, response):
            yield {"title": response.css("title::text").get("")}
    ```

    The cache lives in `.scrapling_cache/{spider.name}/` by default and can be redirected anywhere with `development_cache_dir`. Two new stat counters, `cache_hits` and `cache_misses`, let you see how the cache performed. Cache replay bypasses `download_delay`, rate limiting, and the blocked-request retry path so iteration is as fast as the disk allows. Don't ship a spider with `development_mode = True` -- it's a development tool, not a production cache. See the [docs](https://scrapling.readthedocs.io/en/latest/spiders/advanced.html#development-mode) for the full story.

- **Safer redirects by default**: `follow_redirects` now defaults to `"safe"` across all HTTP fetchers, the MCP server, and the shell. Redirects are still followed, but ones targeting internal/private IPs (loopback, private networks, link-local) are rejected. This protects you from SSRF when scraping user-supplied URLs. Pass `follow_redirects="all"` to get the old behavior, or `False` to disable redirects entirely.

### 🐛 Bug Fixes

- **Force-stop no longer loses your checkpoint**: Pressing Ctrl+C twice (force-stop) on a spider with `crawldir` enabled used to race against the checkpoint write -- the cancel scope would tear down the task before the pickle finished, leaving `paused=False` and triggering the cleanup path that *deletes* the previous checkpoint. The result was that force-stopping a long crawl could lose all the progress you were trying to save. The engine now writes the checkpoint **before** calling `cancel_scope.cancel()`, so a force-stop always preserves the latest pending state. By @voidborne-d in [#230](https://github.com/D4Vinci/Scrapling/pull/230).

## [v0.4.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.4) - 2026-04-05

**A new update with important spider improvements and bug fixes 🎉**

### 🚀 New Stuff and quality of life changes
- **Added robots.txt compliance to the Spider framework** with a new `robots_txt_obey` option. When enabled, the spider will automatically fetch and respect robots.txt rules before crawling, including `Disallow`, `Crawl-delay`, and `Request-rate` directives. Robots.txt files are fetched concurrently and cached per domain for the entire crawl. By @AbdullahY36 in [#226](https://github.com/D4Vinci/Scrapling/pull/226)
- **Added robots.txt cache pre-warming** so all start_urls domains have their robots.txt fetched and parsed before the crawl loop begins, avoiding delays on the first request to each domain.
- **Added a new `robots_disallowed_count` stat** to `CrawlStats` to track how many requests were blocked by robots.txt rules during a crawl.

Check it out on the website from [here](https://scrapling.readthedocs.io/en/latest/spiders/getting-started.html#robotstxt-compliance)

### 🐛 Bug Fixes
- **Fixed a critical MRO issue with `ProxyRotator`** where the `_build_context_with_proxy` stub was shadowing the real implementation from child classes, causing proxy rotation to always raise `NotImplementedError` (Fixes [#215](https://github.com/D4Vinci/Scrapling/issues/215)). Thanks @yetval
- **Fixed a page pool leak** when using per-request proxy rotation with browser sessions. Pages created inside temporary contexts were not removed from the pool on cleanup, leading to stale references accumulating over time. By @yetval in [#223](https://github.com/D4Vinci/Scrapling/pull/223)
- **Fixed a missing type assertion** in the static fetcher where `curl_cffi` could return `None` from `session.request()`, causing downstream errors.

### Other
- Updated dependencies, so expect the latest fingerprints and other stuff.
- Added `protego` as a new dependency under the `fetchers` optional group for robots.txt parsing.

## [v0.4.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.3) - 2026-03-30

**A new update with many important changes 🎉**

### 🚀 New Stuff and quality of life changes
- **Added a new MCP tool** to open a persistent normal/stealthy browser to keep using it with the rest of the tools, and another new tool to close it. ([Examples](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html?h=Using+Persistent+Sessions#examples))
- **Added a new MCP tool** to list all existing browser sessions. Aimed to be used with the new tools.
- **Added a new option to browser sessions** to automatically collect all background requests that happen during a request (Solves [#159](https://github.com/D4Vinci/Scrapling/pull/159)) [[Examples](https://scrapling.readthedocs.io/en/latest/fetching/dynamic.html#capturing-xhrfetch-requests)].
- **Added a new sanitizer** to protect the MCP server from common Prompt Injection attacks by removing hidden/invisible content.
- **Added a new commandline option** called `--ai-targeted` to the Web Scraping commands to make content targeted to AI and safe against common Prompt Injection attacks like the MCP server.
- **Added a new option to browser sessions** called `executable_path` to allow setting a custom browser path (Solves [#202](https://github.com/D4Vinci/Scrapling/pull/202))
- **Refactored** the MCP server code to be easily maintained and unified all tools to be async.
- **Refactored** the CLI commands code to be easily maintained and shorter by 210 lines.

### 🐛 Bug Fixes
- A fix to preserve HTTP method across retries in spider session by @karesansui-u in [#201](https://github.com/D4Vinci/Scrapling/pull/201)
- Added a max retry limit to getting page content to prevent infinite loop by @haosenwang1018 & @D4Vinci in [#197](https://github.com/D4Vinci/Scrapling/pull/197)
- Replace bare `raise` with `return False` in `_restore_from_checkpoint` by @haosenwang1018 in [#196](https://github.com/D4Vinci/Scrapling/pull/196)
- Replaced `get_all` with `getall` in `Texthandler` to match the Selector class.

### Coverage/tests improvement
- Added `_normalize_credentials` edge case coverage tests by @Bortlesboat in [#192](https://github.com/D4Vinci/Scrapling/pull/192)
- Added save/retrieve round-trip and core storage coverage tests by @haosenwang1018 in [#193](https://github.com/D4Vinci/Scrapling/pull/193)
- Added coverage for `TextHandler` regex paths and `TextHandlers.re()` by @haosenwang1018 in [#194](https://github.com/D4Vinci/Scrapling/pull/194)
- Added edge case tests for `filter`, `iterancestors`, and `find_similar` by @awanawana in [#200](https://github.com/D4Vinci/Scrapling/pull/200)

### Agent Skill improvement
- Fixed broken markdown links in skill references by @yetval in [#204](https://github.com/D4Vinci/Scrapling/pull/204)
- Improved the skill structure to be more acceptable by [Clawhub](https://clawhub.ai/d4vinci/scrapling-official) validation.
- Forced the skill to use the `--ai-targeted` commandline option when scraping through commandline commands.

### Docs improvement
- Added Korean README translation by @greatsk55 in [#187](https://github.com/D4Vinci/Scrapling/pull/187)
- CJK Latin spacing fixes for the Chinese and Japanese READMEs.
- Fixed broken links from the old website design.

## [v0.4.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.2) - 2026-03-08

**A new maintenance update with important changes**

#### Bug fixes
- The function `get_all_text()` now captures tail text nodes. This will make the MCP server and commands see text that was missed before ([#168](https://github.com/D4Vinci/Scrapling/pull/168)). Thanks @mhillebrand
- Referer now returns a bare Google url instead of a Google search URL. The previous logic was incorrect and may have produced a fingerprinting signal ([#179](https://github.com/D4Vinci/Scrapling/pull/179)). Thanks @Bortlesboat
- Fixed an issue with extra flags concatenation in all browsers. Thanks @rostchri
- Fixed a type hints issue with Python versions below 3.12 that caused it to crash. (Solves [#163](https://github.com/D4Vinci/Scrapling/issues/163))

#### Other
- Added an Agent Skill for Claude Code / OpenClaw and other AI agentic tools.
- Added the Agent Skill to Clawhub.
- Updates all browsers and Playwright versions to the latest.
- Added a French translation to the main README file.

## [v0.4.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4.1) - 2026-02-27

**A new update with many important changes**

### 🚀 New Stuff and quality of life changes
- **Improved regex precision** for Cloudflare challenge detection (Thanks to @Rinz27 [#133](https://github.com/D4Vinci/Scrapling/pull/133))
- **Improved the speed and efficiency** of the Cloudflare solver. Now it is nearly twice as fast.
- **Improved the Cloudflare solver** to handle the case where websites sometimes show the Cloudflare page twice before redirecting to the main website.
- **Improved the stealthy browser**'s stealth mode and speed by removing the injected JS files.
- **Improved the MCP schema** to be acceptable by OpenCode (Thanks to @robin-ede [#137](https://github.com/D4Vinci/Scrapling/pull/137))
- **Made the MCP schema even more MCP-friendly** to be accepted by VS Code Copilot and other strict tools. (Solves #150 )
- **Improved the MCP server tokens consumption** by a large margin through stripping useless HTML tags while the `main_content_only` option is activated.
- Fixed the PyPI page and added the files to register the MCP server to the MCP servers registry.
- Added a new code snippet to show how to install the browsers deps through code instead of using the commandline to allow easier automation.
- Improved all workflows by using the latest actions versions (Thanks to @salmanmkc [#143](https://github.com/D4Vinci/Scrapling/pull/143)/[#144](https://github.com/D4Vinci/Scrapling/pull/144))

## [v0.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.4) - 2026-02-15

**The biggest release of Scrapling yet — introducing the Spider framework, proxy rotation, and major parser improvements**

This release brings a fully async spider/crawling framework, intelligent proxy management, and significant API changes that make Scrapling more powerful and consistent. Please review the breaking changes section carefully before upgrading.

🕷️ Spider Framework
============

A new async crawling framework built on top of `anyio` for structured, large-scale scraping:

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
-  **Scrapy-like Spider API**: Define spiders with `start_urls`, async `parse` callbacks, `Request`/`Response` objects, and priority queue.
- **Concurrent Crawling**: Configurable concurrency limits, per-domain throttling, and download delays.
- **Multi-Session Support**: Unified interface for HTTP requests, and stealthy headless browsers in a single spider - route requests to different sessions by ID. Supports lazy session initialization.
- **Pause & Resume**: Checkpoint-based crawl persistence. Press Ctrl+C to gracefully shut down; then restart to resume from where you left off.
- **Streaming Mode**: Stream scraped items as they arrive via `async for item in spider.stream()` with real-time stats - ideal for UI, pipelines, and long-running crawls.
- **Blocked Request Detection**: Automatic detection and retry of blocked requests with customizable logic.
- **Built-in Export**: Export results through hooks and your own pipeline or the built-in JSON/JSONL with `result.items.to_json()` / `result.items.to_jsonl()` respectively.
- **Lifecycle hooks**: `on_start()`, `on_close()`, `on_error()`, `on_scraped_item()`, and more hooks for full control over the crawl lifecycle.
- **Detailed crawl stats**: track requests, responses, bytes, status codes, proxies, per-domain/session breakdowns, log level counts, and more.
- **uvloop support**: Pass `use_uvloop=True` to `spider.start()` for faster async execution when available.

A new section has been added to the website with the Full details. Click [here](https://scrapling.readthedocs.io/en/latest/spiders/architecture.html)

🔄 Proxy Rotation
============

* New `ProxyRotator` class with thread-safe rotation. Works with all fetchers and sessions:
  ```python
  from scrapling import ProxyRotator
  rotator = ProxyRotator(["http://proxy1:8080", "http://proxy2:8080"])
  Fetcher.get(url, proxy_rotator=rotator)
  ```
* **Custom rotation strategies**: Make your own proxy rotation logic
* **Per-request proxy override**: Pass `proxy=` to any individual `get()`/`post()`/`fetch()` call to override the session proxy for that request.

🌐 Browser Fetcher Improvements
============

* **Domain blocking**: New `blocked_domains` parameter on `DynamicFetcher`/`StealthyFetcher` to block requests to specific domains (subdomains matched automatically).
* **Automatic retries**: Browser fetchers now retry on failure with `retries` (default: 3) and `retry_delay` (default: 1s) parameters. Includes proxy-aware error detection.
* **Response metadata**: `Response.meta` dict automatically stores the proxy used, and merges request metadata.
* **Response.follow()**: Create follow-up `Request` objects with automatic referer flow, designed for the spider system.
* **No autoplay**: Browser sessions are now blocking autoplay content, which caused issues before.
* **Speed**: Improved stealth and speed by adjusting browser flags.

🔧 Bug Fixes & Improvements
============
- **Parser optimization**: Optimized the parser for repeated operations, improving performance.
- **Errored pages**: Fixed a bug that caused the browser to not close when pages gave errors.
- **Empty body**: Handle responses with empty body.
- **Playwright loop**: Solving an issue with leaving the Playwright loop open when CDP connection fails
- **Type safety**: Fixed all mypy errors and added type hints across untyped function bodies. Added mypy and pyright to the CI workflow.

⚠️ Breaking Changes
============

* **`css_first`/`xpath_first` removed**: Use `css('.selector').first`, `css('.selector')[0]`, or `css('.selector').get()` instead.
* **All selection now returns `Selectors`**: `css('::text')`, `xpath('//text()')`, `css('::attr(href)')`, and `xpath('//@href')` now return `Selectors` (wrapping text nodes in `Selector` objects with `tag="#text"`) instead of `TextHandlers`. This makes the API consistent across all selection methods and the type hints.
* **`Response.body` is always `bytes`**: Previously could be `str` or `bytes`, now always returns `bytes`.
* **`get()`/`getall()` behavior**: On `Selector`: `get()` returns `TextHandler` (serialized HTML or text value), `getall()` returns `TextHandlers`. Aliases: `extract_first = get`, `extract = getall`. Old `get_all()` on `Selectors` is removed.
* **`Selectors.first`/`.last`**: Safe accessors that return `Selector | None` instead of raising `IndexError`.
* **Internal constants renamed**: `DEFAULT_FLAGS` → `DEFAULT_ARGS`, `DEFAULT_STEALTH_FLAGS` → `STEALTH_ARGS`, `HARMFUL_DEFAULT_ARGS` → `HARMFUL_ARGS`, `DEFAULT_DISABLED_RESOURCES` → `EXTRA_RESOURCES`.

🔨 Other Changes
============

* **Dependency changes**: Replaced `tldextract` with `tld`, removed internal `_html_utils.py` in favor of `w3lib.html.replace_entities`, added `typing_extensions` as a hard requirement.
* **Docs overhaul**: Full switch from MkDocs to Zensical, new spider documentation section, updated all existing pages, and added new API references.

## [v0.3.14](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.14) - 2026-01-03

**A minor maintenance update to fix issues that happened with some devices in v0.3.13**

- Disabled the incognito mode in `StealthyFetcher` and its session classes since it made cookies not persistent across pages on Windows devices. It didn't happen on MacOS and Linux (Fixes [#123](https://github.com/D4Vinci/Scrapling/issues/123), thanks to @frugality4121 for bringing it up and to @gembleman for pointing out the solution).
- Pinned down the last version of browserforge to solve the issue with old header models for users with an already old browserforge version.

## [v0.3.13](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.13) - 2026-01-01

**This is a big update with many improvements across many places, but also many breaking changes for good reasons. Please read the below before updating**

* For many reasons, we decided that from now on, we will stop using Camoufox entirely, and we might switch back to it in the future if its development continues. If you prefer to continue using Camoufox as before this release, there are instructions for that in this [section](https://scrapling.readthedocs.io/en/latest/fetching/stealthy/#using-camoufox-as-an-engine).

* Previously, we were using patchright in the stealth mode inside `DynamicFetcher` and its session classes. Now we removed the stealth mode from them and started using patchright inside `StealthyFetcher` and its session classes, with A LOT of improvements, as you will see, improving the stealth overall on top of patchright.

**This makes `StealthyFetcher` and its session classes 101% faster than before, use less memory and space, and have ~400 lines of code shorter, but, most importantly, are more stable than when we used Camoufox before.**

This will also shorten the installation time of the `scrapling install` command, reduce the size of the Docker image, improve test smoothness in GitHub's CI, and make scrapling less confusing for new users.

### Breaking changes
1. The `stealth` argument was removed from the `DynamicFetcher` class and its session class, while the `hide_canvas` argument was moved to the `StealthyFetcher` and its session classes.
2.  The `disable_webgl` argument has been moved from `DynamicFetcher` to the `StealthyFetcher` class and renamed as `allow_webgl`. All session classes as well.
3. The `StealthyFetcher` class is now basically the new stealthy version of `DynamicFetcher`, so the following arguments are removed: `block_images`, `humanize`, `addons`, `os_randomize`, `disable_ads`, and `geoip`. I tried to replicate them in Chromium, but each had its own problem. This might change with upcoming releases before v0.4.

Now to the good news, we have improved and fixed a lot of stuff :)

### Improvements
- You already know that the `StealthyFetcher` class and its session classes are now 101% faster than before, but now also the `DynamicFetcher` class and its session class are 20% faster.
- Cloudflare's solver algorithm has been improved over before now to finish faster and handle more cases. Also, thanks to the new refactor, expect the solver to solve the captcha twice as fast!
- All fetchers now use less memory.
- The MCP server now uses fewer tokens to save more money!
- The Docker image is now 60% smaller.
- The whole documentation website has been updated with the new stuff. At the same time, it was made more explicit, many sections were shortened, more examples were added, missing arguments were included, the API reference section was updated with graphs, and many other improvements were made. The Website now loads 130% faster, uses less data, and is better for SEO.

### Fixes
- Added the arguments that were missing before in the Web Scraping shell shortcuts and made them more accurate.
- Fixed the issue where the `google_search` argument was creating a Google referrer even if the URL is a localhost/IP.

## [v0.3.12](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.12) - 2025-12-18

### What's Changed
- Added a new argument to `DynamicSession`/`AsyncDynamicSession` classes called `timezone_id`, which allows you to set the timezone of the browser so that it matches the timezone of the Proxy/VPN you are using. That way, the websites can't detect that you are using a proxy through the timezone mismatch technique.
- Improved the automated conversion of response to JSON.
- Renamed the internal function `__create__` to `start` inside fetchers' session classes to make it easier to use them outside the `with` context.
- Updated `curl_cffi` and other deps to the latest versions.

## [v0.3.11](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.11) - 2025-12-03

### What's Changed
- Added a better logic for handling timeout errors when the `network_idle` argument is used on an unstable website (websites with media playing, etc.)
- Fixed the autocompletion for the `stealthy_fetch` shortcut in the Web Scraping Shell

## [v0.3.10](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.10) - 2025-11-26

**A maintenance update with many significant changes and possible breaking changes**

- **Solved** all encoding issues by using a better approach which will handle web pages where encoding is not correctly declared (Thanks to @Kemsty2's efforts for pointing that out in [#110](https://github.com/D4Vinci/Scrapling/issues/110) [#111](https://github.com/D4Vinci/Scrapling/pull/111) )
- **Solved** a logical issue with overriding session-level parameters with request-level parameters in all browser-based fetchers that was present since v0.3
- **Fixed** the signatures of the shortcuts in the interactive web scraping shell, which made a perfect autocompletion experience for the shortcuts in the shell. This issue has been present since v0.3 as well.
- **Pumped up** the version for the Maxmind database, which will improve the `geoip` argument for `StealthyFetcher` and its session classes.
- **Updated** all used browser versions to the latest available ones.
- **BREAKING** - all fetchers had gone through a big refactor, which resulted in some interesting things that might break your code:
  1. Scrapling codebase is now smaller by ~750 lines and many changes which would make maintenance very much easier in the future and use a bit less resources.
  2. The validation for all fetchers and their session classes became much faster, which will reflect on their overall speed.
  3. To achieve this, now all fetchers can't accept standard arguments other than the `url` argument; the rest of the arguments must be keyword-arguments so your code must be like `Fetcher.get('https://google.com', stealthy_headers=True)` not `Fetcher.get('https://google.com', True)` if you were doing that for some reason!
  4. An annoying difference between browser-based fetchers and their session classes since v0.3 was that the argument used to pass custom parser settings per request was called `custom_config`, while it was named `selector_config` in the session classes. This refactor allowed us to unify the naming to `selector_config` without breaking your code, so the main one is now `selector_config` with backward compatibility for the `custom_config` argument. The autocompletion support will be available only for the `selector_config` argument.
  5. Also, to achieve all of this, we had to make the type hints of the fetchers' functions dynamically generated, so if you don't get a proper autocompletion in your IDE, make sure you are using a modern version of it. We have tested almost all known IDEs/editors.

> We have also updated all benchmark tables with the current numbers against the latest versions of all alternative libraries.

## [v0.3.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.9) - 2025-11-17

**A new update with many important changes**

### 🚀 New Stuff and quality of life changes
- Now the `impersonate` argument in `Fetcher` and `FetcherSession` can accept a list of browsers that the library will choose a random browser from them with each request.
```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate=['chrome', 'firefox', 'safari']) as s:
  s.get('https://github.com/D4Vinci/Scrapling')
```
- A new argument to the `clean` method in `TextHandler` to remove html entities from the current text easily.
- Huge improvements to the documentation with more precise explanations of many parts and automatic translations of the main `README.md` file.

### 🐛 Bug Fixes
- Fixed a big issue with retrieving responses from browser-based fetchers. Now, there is intelligent content type detection that ensures `response.body` contains the rendered browser content only if the content is HTML; otherwise, it contains the raw content of the last request made. This allows you to download binary files and text-based files without having to find them wrapped in HTML tags, while being able to retrieve the rendered content you want from the website when fetching it.

### 🔨 Misc
- Updated the contributing guide to make it clearer and easier.
- Add a new workflow to enforce code quality tools (Same ones used as pre-commit hooks).

## [v0.3.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.8) - 2025-10-27

**A new update with many important changes**

### 🚀 New Stuff and quality of life changes
- For all browser-based fetchers: websites that never finish loading their requests won't crash the code now if you used `network_idle` with them.
- The logic for collecting/checking for page content in browser-based fetchers has been changed to make browsers more stable on Windows systems now, as Linux/MacOS (All this difference in behaviour is because of Playwright's different implementation on Windows systems).
- Refactored all the validation logic, which made all requests done from all browser-based fetchers faster by 8-15%
- A New option called `extra_flags` has been added to `DynamicFetcher` and its session to allow users to add custom Chrome flags to the existing ones while launching the browser.
- Reverted the route logic for catching responses (changed in the last version) to use the old routing version when `page_action` is used. This was added to collect the latest version of a page's content in case `page_action` changes it without making a request. (Thanks for @gembleman to pointing it in [#100](https://github.com/D4Vinci/Scrapling/issues/100) and [#102](https://github.com/D4Vinci/Scrapling/pull/102) )

### 🐛 Bug Fixes
- Fixed a typo in `load_dom` in DynamicSession's async_fetch
- Fixed an issue with Cloudflare solver that made the solver wait forever for embedded captchas that don't disappear after solving. Now it will wait for the captcha to disappear for 30 seconds, then assume it's the type that doesn't disappear (Fixes #100 )

### 🔨 Misc
- Now the Docker image is automatically pushed to Dockerhub and GitHub's container registry for user convenience.
- Added a [new documentation page](https://scrapling.readthedocs.io/en/latest/tutorials/external/) to show how to use Scrapeless browser with Scrapling.

## [v0.3.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.7) - 2025-10-12

**A new update with many important changes**

### 🚀 New Stuff and quality of life changes
- Reworked `solve_cloudflare` argument in `StealthyFetcher` to make it able to solve all kinds of custom implementations of Turnstile.
- Refactored the entire codebase to be acceptable by Pyright, so expect a flawless IDE experience now with all software and many bugs solved.
- Refactored the requests logic to be cleaner and faster (Also solves #97 )
- Added a new option `user_data_dir` to all browser-based session classes to allow the user to reuse the browser session data (cookies/storage/etc...) from previous sessions. Leaving it will cause Playwright to use a random directory on each run, as was happening before.
- Added a new customization option `additional_args` to `Dynamic fetcher` and its session class to enable the user to pass extra arguments to Playwright's context, as we had with `StealthyFetcher` before.
- The route logic for collecting the last navigation response for all browsers has been improved, which allows the raw responses to be passed to the parser before being processed by the browsers as before. This will be very helpful with text/JSON responses.

### 🐛 Bug Fixes
- The rework of the route logic solved an issue with retrieving the content of unstable websites on some Windows devices.
- All the refactors that happened in this version solved a lot of bugs along the way that were hard to spot before, and weird autocompletion issues with some IDEs.
- Many fixes to the documentation website

## [v0.3.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.6) - 2025-10-01

### 🚀 New Stuff
- Improved the `solve_cloudflare` argument in `StealthyFetcher` and its session classes to be able to solve all types of both Turnstile and interstitial Cloudflare challenges 🎉 
- Now the MCP server has the option to use `Streamable HTTP`, so you can easily expose the server.
- Added Docker support, so now an image is built and pushed to Docker Hub automatically with each release (contains all browsers)

### 🐛 Bug Fixes
- Fixed an encoding issue with the parser that happened in some cases (the famous `invalid start byte` error)
- Restructured multiple parts of the library to fix some memory leaks, so now enjoy noticably lower memory usage based on your config (Also solves #92 )
- Improved type annotation in many parts of the code so you can have a better IDE experience (Also solves #93 )

## [v0.3.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.5) - 2025-09-20

**Necessary release that fixes multiple issues**

### 🚀 New Stuff
- All browser-based fetchers (`DynamicFetcher`/`StealthyFetcher`/...) and their session classes are now fetching websites 15-20%:
  1. Page management is now much faster due to the logic improvement by @AbdullahY36 in #87
  2. Optimized the validation logic overall and improved page creation for sync fetches, which together introduced a lot of speed improvements

- Big improvements to the stealth mode in `DynamicFetcher` and its session classes by replacing `rebrowser-playwright` with `PatchRight`:
  1. Before this update, `rebrowser-playwright` was turned off when you enabled `stealth` and `real_chrome` because they weren't doing well together, but now we don't have this issue with `PatchRight`
  2. You can now interact with Closed-Shadow Roots since `PatchRight` can handle them automatically.

### 🐛 Bug Fixes
- Fixed a bug that happens while using the `re` method from the `Selectors` class.
- Fixed a bug with `uncurl` and `curl2fetcher` commands in the Web Scraping Shell that made curl's `--data-raw` flag parse incorrectly.
- Fixed a bug with the `view` command in the Web Scraping Shell that depended on the website's encoding to happen.
- Fixed a bug with content converting that affected the `mcp` mode and `extract` commands.

### New Contributors
- @AbdullahY36 made their first contribution in #87

## [v0.3.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.4) - 2025-09-16

**Necessary release that fixes multiple issues**

### 🚀 New Stuff
- Added all the fetchers session classes to the interactive shell to be available right away without import.

### 🐛 Bug Fixes
- Added a workaround for a bug with the Playwright API on Windows that happened while retrieving content while solving Cloudflare.
- Fixed an encoding issue with the `view` command in the interactive shell
- Fixed a bug with the `max_pages` argument in `AsyncStealthySession` that was crashing the code.
- Fixed an issue that happened with the last updates that made the `html_content` and `prettify` properties in the `Selector` class return bytes, depending on the encoding. Both are returning strings as they were.

## [v0.3.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.3) - 2025-09-15

- Removed the logic that is removing the default browser tab on browser-based fetchers since it caused a crashing error (Not happening on Mac, only managed to produce on Windows and Linux)

## [v0.3.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.2) - 2025-09-15

Release Notes for v0.3.2

### 🚀 New Stuff

- **Optional fetcher dependencies**: All fetchers are now part of optional dependency groups, reducing core package size. So the base `scrapling` module is now the parser only, and to use the fetchers or the commandline options, you have to do: `pip install "scrapling[fetchers]"`. Check out the detailed installation instructions from [here](https://scrapling.readthedocs.io/en/latest/#installation)
- **Per-page configuration in sessions**: Session classes for browser fetchers now support individual configuration per page in sessions. All fetch-level parameters are now validated like session-level ones. More details on the documentation website [here](https://scrapling.readthedocs.io/en/latest/fetching/dynamic/#full-list-of-arguments)
    <br>Example:
    ```python
    with StealthySession(headless=True, solve_cloudflare=True) as session:
        page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    ```
- **Improved browser-based fetchers**
  - A new option to control whether to wait for JavaScript execution to finish in pages or not (it's enabled by default now, as it was before)
    ```python
    with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
       page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    ```
  - The Stealth mode is now more reliable in `DynamicFetcher` and its session classes.
  - Both `DynamicFetcher` and `StealthyFetcher` are now using fewer resources (Automatically finding and closing the default tab opened by Persistent contexts in Playwright API)
  - Fixed a vital logic bug in browser-based fetchers' pages rotation - previous pages are now replaced with fresh ones. (Tabs that get reused in rotation are possibly contaminated from previous settings used on them)
  - `StealthyFetcher` and its session classes are now slightly faster (5%)

- **Enhanced `.body` property**: Now returns the passed content as-is without processing, enabling file downloads and handling non-HTML requests. Below is an example of downloading a photo:
    ```python
    from scrapling.fetchers import Fetcher

   page = Fetcher.get('https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/poster.png')
   with open(file='poster.png', mode='wb') as f:
       f.write(page.body)
    ```

### 🐛 Bug Fixes

- **Encoding issues resolved**: Fixed multiple encoding problems that happened with some websites in parser, mcp mode, and extract commands (Also solves #80 and #81)
- **Faster parsing**: Due to many changes here and there, the library is now faster, and it's reflected in the updated benchmarks

### 🔨 Misc

- **Updated benchmarks**: Refreshed performance benchmarks to compare the current speed improvements to the latest versions of similar libraries
- **Refactored a lot of the code and replaced dead code with better implementations**: Fewer code, cleaner code, easier maintenance
- **Added YouTube video**: Included video content for MCP documentation.
- **A new issues template**: Easy new template for users who can't use the current templates.
- **CI workflow optimization**: Tests workflow now skips runs when only documentation or non-code files are changed.
- **Updated dependencies**: Bumped up various dependencies to the latest versions.
- **Code style improvements**: Applied new ruff rules across all files.
- **Pre-commit hooks**: Updated pre-commit configuration.

### 🎯 Breaking Changes

- Removed `max_pages` parameter from sync `StealthySession` to match `DynamicSession` (it's meaningless to have in the sync version)

## [v0.3.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3.1) - 2025-09-02

1. Fixed an issue with scrapling installation when you install it without the `shell` extra (#76 )
2. Added a new argument to all browser-based fetchers and their session classes to add a JS file to be executed on page creation (#56) :
```python
from scrapling.fetchers import StealthyFetcher

StealthyFetcher.fetch('https://example.com', init_script="/absolute/path/to/js/script.js")
```

## [v0.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.3) - 2025-09-01

🎉 **Major Release — Complete Architecture Overhaul**

Scrapling v0.3 represents the most significant update in the project's history, featuring a complete architectural rewrite, considerable performance improvements, and powerful new features, including AI integration and interactive Web Scraping shell capabilities.

This release includes multiple breaking changes; please review the release notes carefully.

### 🚀 Major New Features

#### Session-Based Architecture
- **New Session Classes**: Complete rewrite introducing persistent session support
  - `FetcherSession` - HTTP requests with persistent state management that works with both sync and async code
  - `DynamicSession`/`AsyncDynamicSession` - Browser automation while keeping the browser open till you finish
  - `StealthySession`/`AsyncStealthySession` - Stealth browsing while keeping the browser open till you finish
- **Async Browser Tabs Management**: A new pool of tabs feature through the `max_pages` argument that rotates browser tabs for concurrent browser fetches
- **Concurrent Sessions**: Run multiple isolated sessions simultaneously

Refer to the `Fetching` section on the website for more details.

#### A lot of new stealth/anti-bot Capabilities
- **🤖 Cloudflare Solver**: Automatic [Cloudflare Turnstile challenge solving](https://scrapling.readthedocs.io/en/latest/fetching/stealthy/#cloudflare-protection-bypass) in `StealthyFetcher` and its session classes
- **Browser fingerprint impersonation**: Mimic real browsers' TLS fingerprints, version-matching browser headers, HTTP/3 support, and more with the all-new [Fetcher](https://scrapling.readthedocs.io/en/latest/fetching/static/) class
- **Improved stealth mode**: The stealth mode for `DynamicFetcher` and its session classes is now more robust and reliable (AKA `PlayWrightFetcher`)

#### AI Integration & MCP Server
- **Built-in MCP Server**: Model Context Protocol server for AI-assisted web scraping
- **6 Powerful Tools**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`
- **Smart Content Extraction**: Convert web pages/elements to Markdown, HTML, or extract a clean version of the text content
- **CSS Selector Support**: Use the Scrapling engine to target specific elements with precision before handing the content to the AI
- **Anti-Bot Bypass**: Handle Cloudflare Turnstile and other protections
- **Proxy Support**: Use proxies for anonymity and geo-targeting
- **Browser Impersonation**: Mimic real browsers with TLS fingerprinting, real browser headers matching that version, and more
- **Parallel Processing**: Scrape multiple URLs concurrently for efficiency
- [and more...](https://scrapling.readthedocs.io/en/latest/ai/mcp-server/)

#### New Interactive Web Scraping Shell
- **A New Shell**: Custom IPython shell with many smart Built-in Shortcuts like `get`, `post`, `put`, `delete`, `fetch`, and `stealthy_fetch`
- **Smart Page Management**: New commands `page` and `pages` to automatically store the current page and history for all requests done through the shell
- **Curl Integration**: Convert browser DevTools curl commands with `uncurl` and `curl2fetcher` functions to `Fetcher` requests 
- [and more...](https://scrapling.readthedocs.io/en/latest/cli/interactive-shell/)

#### Scrape from the terminal without programming
- **New Extract Commands**: Terminal-based scraping without programming
  - `scrapling extract get/post/put/delete` - Simple HTTP requests
  - `scrapling extract fetch` - Dynamic content scraping
  - `scrapling extract stealthy-fetch` - Anti-bot bypass
- **Downloads web pages** and saves their content to files.
- **Converts HTML to readable formats** like Markdown, keeps it as HTML, or just extracts the text content of the page.
- **Supports custom CSS selectors** to extract specific parts of the page.
- **Handles HTTP requests and fetching through browsers.**
- **Highly customizable** with custom headers, cookies, proxies, and the rest of the options. Almost all the options available through the code are also accessible through the terminal.
- [and more...](https://scrapling.readthedocs.io/en/latest/cli/extract-commands/)

### 🔧 Technical Improvements

#### Performance Enhancements
- **Fetcher is now 4 times faster** - Yes you have read it right!
- **DynamicFetcher is now ~60% faster** - A much faster version depending on your config (especially stealth mode)
- **StealthyFetcher is now 20–30% faster** - Using the new structure, and starting to use our implementation instead of `Camoufox` Python interface
- **50%+ combined speed gains** across core selection methods (`find_by_text`, `find_similar`, `find_by_regex`, `relocate`, etc.) 🚀
- **~10% CSS/XPath first methods speed increase** - `css_first` and `xpath_first` are now faster than `css` and `xpath`
- **40% faster `get_all_text()` method** for content extraction
- **20% speed improvement** in adaptive element relocation 
- **Navigation properties optimization** — Properties like `next`, `previous`, `below_elements`, and more are now noticeably faster
- **5x faster text cleaning** operations
- **Memory efficiency improvements** with optimized imports and reduced overhead
- **⚡ Lightning-fast imports**: Reduced startup time with optimized module loading
- **Better benchmarks**: All the speed improvements Scrapling got made it much faster than before, compared to other libraries (1775x faster than BeautifulSoup and 5.1x faster than AutoScraper, check [benchmarks](https://scrapling.readthedocs.io/en/latest/benchmarks/))

#### Architecture/Code Quality, and Quality of life
- **Persistent Context**: All browser-based fetchers now use persistent context by default. (Solves #64 too)
- **Using msgspec to validate all browser-based fetchers very fast** before running the requests, so now it's easier to debug errors.
- **All cookies** returned from fetchers are now matching the format accepted by the same fetcher. So you can retrieve cookies and pass them again to all fetchers and their session classes.
- **Faster linting and formatting** due to migrating to `ruff`
- **Modern Build System**: Migrated from setup.py to pyproject.toml 📦
- **Better GitHub actions and workflows** for smoother development and testing
- **🎨 Enhanced Type Hints**: Complete type coverage with modern Python standards for better IDE support and reliability
- **Cleaner Codebase**: Removed dead code and optimized core functions 🧹
- **🚀 Backward Compatibility**: Added shortcuts to maintain compatibility with older code

### Breaking Changes

#### Minimum Python Version
- **Python 3.10+ Required**: Dropped support for Python 3.9 and below

#### Class and Method Naming
These renamings are intended to improve clarity and consistency, particularly for new users.

- **`Adaptor` → `Selector`**: Core parsing class renamed (But still can be imported as `Adaptor` for backward compatibility)
- **`Adaptors` → `Selectors`**: Collection class renamed (But still can be imported as `Adaptors` for backward compatibility)
- **`auto_match` → `adaptive`**: Parameter renamed across all methods
- **`adaptor_arguments` → `selector_config`**: Configuration parameter renamed
- **`automatch_domain` → `adaptive_domain`**: Domain parameter renamed
- **`additional_arguments` → `additional_args`**: Shortened parameter name
- **⚠️ `text/body` → `content`**: Selector constructor parameter is now accepting both `str` and `bytes` format
- **`PlayWrightFetcher` → `DynamicFetcher`**: Browser automation class renamed (But still can be imported as `PlayWrightFetcher` for backward compatibility)
- **DynamicFetcher doesn't have the NSTBrowser logic/arguments anymore** since it's pointless to leave this logic now anyway.
- **StealthyFetcher's headless argument can't accept 'virtual' as an argument anymore** since we are not using Camoufox's library right now in anything other than getting the browser installation path and the rest of the launch options 

### 🐛 Bug Fixes

- Fixed nested children counting in ignored tags for `get_all_text` (#61)
- Fixed the issue with installation due to spaces in Python's executable path (#57)
- Resolved threading issues in storage with recursion handling while the adaptive feature is enabled
- Fixed argument precedence issues using the Sentinel pattern in `FetcherSession`
- Resolved proxy type handling in `StealthyFetcher`
- Fixed `referer` and `google_search` argument conflicts
- Fixed async stealth script injection problems

## [v0.2.99](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.99) - 2025-04-08

**This is an essential update for everyone to fully enjoy Scrapling as it's intended.**

### What's changed
#### New full documentation website
- Yup, finally 😄 Check it out from [here](https://scrapling.readthedocs.io/en/latest/)
#### Unified import logic for fetchers
- Now you can import all fetchers with `from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`, then use them directly like `page = Fetcher.get(...)` without initialization.<br/> This replaces this old import `from scrapling.defaults import Fetcher, AsyncFetcher, StealthyFetcher, PlayWrightFetcher`.
#### Breaking change: automatch is now turned off by default
- Now there's new logic to enable automatch from fetchers or other parsing options. Check out the [documentation page](https://scrapling.readthedocs.io/en/latest/fetching/choosing/#parser-configuration-in-all-fetchers) for details.
>  Old imports and logic are left usable with a warning for backward compatibility.
#### New options added to fetchers
- Now, both `StealthyFetcher` and `PlayWrightFetcher` have a new argument while fetching called `wait`. This makes the fetcher wait/sleep for a specific period (milliseconds) before closing the page and returning the response to you.
- Now `StealthyFetcher` methods `fetch` and `async_fetch` have the argument `additional_arguments` to be passed to Camoufox as additional settings, which takes higher priority than Scrapling's settings (#54 )
#### Bugs squashed
- Fixed a bug in `async_fetch` in both `StealthyFetcher` and `PlayWrightFetcher` classes, with catching redirections.

**_Thanks for all your support and donations!_**

## [v0.2.98](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.98) - 2025-03-17

**This is an essential update for everyone to enjoy Scrapling as it's intended fully**

### What's changed
#### Various memory usage and speed optimizations
- All selection methods' memory usage is ~40% of previous memory usage and the speed slightly increased.
- Implemented Lazy loading for all submodules of the library so now what you use is what you load, for example:
Before the update this import `from scrapling import Adaptor` was using `30-40mb` of RAM because it loaded all fetchers and stuff with it too, now it uses `~1.2mb`.
- The last update made the library use ~32% memory it used before with a large requests pool, now we adjusted the caching further to use even less than that.
- Overall speed increase in the parser by a slight 2-5%

**_Thanks for all your support and donations!_**

## [v0.2.97](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.97) - 2025-03-15

**This is an essential update for everyone to fully enjoy Scrapling as it's intended**

### What's changed
#### Lower memory usage and small speed increase across all Fetchers.
- With new limitations across the library over caching size you will notice significantly lower memory usage than before while doing large numbers of requests/operations.
- Refactored big parts of the fetchers to easier maintainability and small speed increase.

#### Bugs fixed
- Fixed a bug in `TextHandler` where importing it alone and passing a non-string value converts it to an empty string. Now anything passed to `TextHandler` is automatically converted to a string before being converted to `TextHandler`, this is forced on any value passed -- `TextHandler` as the name implies is intended to work with strings only after all! (#45 )
- Fixed a bug where the `retries` arguments weren't taken into account in most AsyncFetcher methods.

#### Miscellaneous
- Update type hints for most arguments in all fetchers to be clearer and more accurate.

**_Thanks for all your support and donations!_**

## [v0.2.96](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.96) - 2025-03-05

**This is an essential update for everyone to fully enjoy Scrapling as it's intended**

### What's changed
1. Added the `-f` option to `scrapling install` to force reinstall browser dependencies. I recommend you do `scrapling install -f` now to enjoy the big speed performance `StealthyFetcher` just got with the new Camoufox browser version :)
2. Fixed a bug in `TextHandler` where slicing returned `TextHandlers` instead of `TextHandler` and fixed the type hint there (#41 )
3. Fixed an issue where `scrapling install` might in some instances drop the user into a Python shell!

## [v0.2.95](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.95) - 2025-02-25

**This is an essential update for everyone to fully enjoy Scrapling as it's intended**

### What's changed
1. Fixed a bug in `Fetcher` that made headers generated by the `stealthy_headers` argument overwrite some of the headers provided by the user like `Accept` (#39 )
2. Improved the headers generation logic a bit so it should give a slight speed boost.

## [v0.2.94](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.94) - 2025-02-22

**This is an essential update for everyone to fully enjoy Scrapling as it's intended**

### What's changed
1. Added the `history` property to all fetchers to show redirections (#32 )
2. Fixed the logic of the `case_sensitive` argument logic for all `re`/`re_first`. This may make your code return different results if you were using it (but you probably deserve it because you noticed it wasn't working as intended and didn't open an issue LOL)
3. Updated dependencies and enabled `coop` back again in the Camoufox engine (StealthyFetcher).

## [v0.2.93](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.93) - 2025-01-31

**This is an essential update for everyone to fully enjoy Scrapling as it's intended**

### What's changed
1. The return type is now consistent across all the parser engine so you will always get a return type as one of these `Adaptor`, `Adaptors`, `TextHandler`, `TextHandlers`, `None`, and a list in case you have mixed results like combined CSS selector. This allows a better coding experience with minimum manual type checking, makes the library more stable, and makes chaining methods always possible.
2. Most of the parser engine especially the `Adaptor` class got refactored to a cleaner version and most importantly a faster version. So now almost all the methods/properties, especially the searching methods, got a speed increase between 5-40%. Some methods got bigger speed boosts like `find_by_regex` got a ~60% speed boost! The automatch feature got a small ~5% speed boost.
3. Fixed logic bugs with the `find_all`/`find` methods that made the passed filters used in OR fashion and other times as an AND. So now all elements returned need to fulfill all filters you pass.
4. Now all regex-related methods return `TextHandler`/`TextHandlers` for easier methods chaining.
5. **Added a new** `below_elements` property that returns an `Adaptors` object of all elements under the current element in the DOM tree.
6. Now all methods/properties that were returning HTML source as string are now returning it as `TextHandler` so you can do regex easily on it etc...
7. StealthyFetcher is now a bit faster and more stealthy. Also, now it's possible to click Captchas in iframes like **Cloudflare Turnstile**.
8. The auto-completion and type hints improved a lot in nearly half the library. Especially `Adaptor`, `TextHandler`, and `TextHandlers`.
9. Now slicing `TextHandler`, accessing by index, or using the `split` method returns another `TextHandler` instead of the standard Python string. Now almost all standard string operations/methods return other `Texthandler` instead of standard string to make chaining methods/functions always possible.
10. Fixed some small bugs and typos. For example, the Fetcher async_put was doing post request instead of put request 😶‍🌫️ 
11. Improved the README a bit till I finish the documentation website.

This was supposed to be a small update till version 0.3 but thought to make it better.

## [v0.2.92](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.92) - 2024-12-26

### What's changed
- Now response returned by browser-based fetchers uses more reliable data sources in cases where the page loaded uses many Iframes.
- **Now installing `Scrapling` is made even easier, you install it with pip then run `scrapling install` in the terminal and you are ready!**
- Fixed an inaccurate type hint in the parser.

## [v0.2.91](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.91) - 2024-12-19

### What's changed
- Fixed a bug where the logging fetch logging sentence was showing in the first request only.
- The default behavior for Playwright API while browsing a page is returning the first response that fulfills the load state given to the `goto` method `["load", "domcontentloaded", "networkidle"]` so if a website has a wait page like Cloudflare's one that redirects you to the real website afterward, Playwright will return the first status code which in this case would be something like 403. This update solves this issue for both `PlaywrightFetcher` and `StealthyFetcher` as both are using Playwright API so the result depends on Playwright's default behavior no more.
- Added support for proxies that use SOCKS proxies in the `Fetcher` class.
- Fixed the type hint for the `wait_selector_state` argument so now it will show the accurate values you should use while auto-completing.

## [v0.2.9](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.9) - 2024-12-16

### What's changed
##### New features
1. Introducing the **long-awaited** async support for Scrapling! Now you have the `AsyncFetcher` class version of `Fetcher`, and both `StealthyFetcher` and `PlayWrightFetcher` have a new method called `async_fetch` with the same options.
```python
>> from scrapling import StealthyFetcher
>> page = await StealthyFetcher().async_fetch('https://www.browserscan.net/bot-detection')  # the async version of fetch
>> page.status == 200
True
```
2. Now the `StealthyFetcher` class has the `geoip` argument in its fetch methods which when enabled makes the class automatically use IP's longitude, latitude, timezone, country, and locale, then spoof the WebRTC IP address. It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
3. Added the `retries` argument to `Fetcher`/`AsyncFetcher` classes so now you can set the number of retries of each request done by `httpx`.
4. Added the `url_join` method to `Adaptor` and Fetchers which takes a relative URL and joins it with the current URL to generate an absolute full URL!
5. Added the `keep_cdata` method to `Adaptor` and Fetchers to stop the parser from removing cdata when needed.
6. Now `Adaptor`/`Response` `body` method returns the raw HTML response when possible (without processing it in the library).
7. Adding logging for the `Response` class so now when you use the Fetchers you will get a log that gives info about the response you got.
Example:

   ```python
   >> from scrapling.defaults import Fetcher
   >> Fetcher.get('https://books.toscrape.com/index.html')
   [2024-12-16 13:33:36] INFO: Fetched (200) <GET https://books.toscrape.com/index.html> (referer: https://www.google.com/search?q=toscrape)
   >> 
   ```
8. Now using all standard string methods on a `TextHandler` like `.replace()` will result in another `TextHandler`. It was returning the standard string before.
9. Big improvements to speed across the library and improvements to stealth in Fetchers classes overall.
10. Added dummy functions like `extract_first`\`extract` which returns the same result as the parent. These functions are added only to make it easy to copy code from Scrapy/Parsel to Scrapling when needed as these functions are used there!
11. Due to refactoring a lot of the code and using caching at the right positions, now doing requests in bulk will have a big speed increase.

##### Breaking changes
- Now the support for Python 3.8 has been dropped. (Mainly because Playwright stopped supporting it but it was a problematic version anyway)
- The `debug` argument has been removed from all the library, now if you want to set the library to debugging, do this after importing the library:

   ```python
   >>> import logging
   >>> logging.getLogger("scrapling").setLevel(logging.DEBUG)
   ```

##### Bugs Squashed
1. Now WebGL is enabled by default as a lot of protections are checking if it's enabled now.
2. Some mistakes and typos in the docs/README.

##### Quality of life changes
1. All logging is now unified under the logger name `scrapling` for easier and cleaner control. We were using the root logger before.
2. Restructured the tests folder into a cleaner structure and added tests for the new features. All the tests were rewritten to a cleaner version and more tests were added for higher coverage.
3. Refactored a big part of the code to be cleaner and easier to maintain.

> All these changes were part of the changes I decided before to add with 0.3 but decided to add them here because it will be some time till the next version. Now the next step is to finish the detailed documentation website and then work on version 0.3

## [v0.2.8](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.8) - 2024-11-30

### What's changed
- This is a small update that includes some must-have quality-of-life changes to the code and fixed a typo in the main README file (#20)

## [v0.2.7](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.7) - 2024-11-26

### What's changed
##### New features
- Now if you used the `wait_selector` argument with `StealthyFetcher` and `PlayWrightFetcher` classes, Scrapling will wait again for the JS to fully load and execute like normal. If you used the `network_idle` argument, Scrapling will wait for it again too after waiting for all of that. If the states are all fulfilled then no waiting happens, of course.
- Now you can enable and disable ads on `StealthyFetcher` with the `disable_ads` argument. This is enabled by default and it installs the `ublock origin` addon.
- Now you can set the locale used by `PlayWrightFetcher` with the `locale` argument. The default value is still `en-US`.
- Now the basic requests done through `Fetcher` can accept proxies in this format `http://username:password@localhost:8030`.
- The stealth mode improved a bit for `PlayWrightFetcher`.

##### Bugs Squashed/Improvements
1. Now enabling proxies on the `PlayWrightFetcher` class is not tied to the `stealth` mode being on or off (Thanks to [@AbdullahY36](https://github.com/AbdullahY36) for pointing that out)
2. Now the `ResponseEncoding` tests if the encoding returned from the response can be used with the page or not. If the returned encoding triggered an error, Scrapling defaults to `utf-8`

## [v0.2.6](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.6) - 2024-11-24

### What's changed
##### New features
- Now the `PlayWrightFetcher` can use the real browser directly with the `real_chrome` argument passed to the `PlayWrightFetcher.fetch` function but this requires you to have Chrome browser installed. Scrapling will launch an instance of your Chrome browser and you can use most of the options as normal. (Before you only had the `cdp_url` argument to do so)
- Pumped up the version of headers generated for real browsers.

##### Bugs Squashed
1. Turns out the format of the browser headers generated by `BrowserForge` was outdated which made Scrapling detected by some protections so now `BrowserForge` is only used to generate real useragent.
2. Now the `hide_canvas` argument is turned off by default as it's being detected by Google's ReCaptcha.

## [v0.2.5](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.5) - 2024-11-23

### What's changed

##### Bugs Squashed
- Handled an error that happens with the 'wait_selector' argument if it resolved to more than 1 element. This affects the `StealthyFetcher` and the `PlayWrightFetcher` classes.
- Fixed the encoding type in cases where the `content_type` header gets value with parameters like `charset` (Thanks to @andyfcx for [#12](https://github.com/D4Vinci/Scrapling/issues/12) )

##### Quality of life
- Added more tests to cover new parts of the code and made tests run in threads.
- I updated the docs strings to be readable correctly on Sphinx's apidoc or similar tools.

##### New Contributors
- @andyfcx made their first contribution at [#13 ](https://github.com/D4Vinci/Scrapling/pull/13)

## [v0.2.4](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.4) - 2024-11-20

### What's changed

##### Bugs Squashed
- Fixed a bug when retrieving response bytes after using the `network_idle` argument in both the `StealthyFetcher` and `PlayWrightFetcher` classes. <br/> That was causing the following error message:
 ```
Response.body: Protocol error (Network.getResponseBody): No resource with given identifier found
```
- The PlayWright API sometimes returns empty status text with responses, so now `Scrapling` will calculate it manually if that happens. This affects both the `StealthyFetcher` and `PlayWrightFetcher` classes.

## [v0.2.3](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.3) - 2024-11-19

### What's changed

##### Bugs Squashed
- Fixed a bug with pip installation that prevented the stealth mode on PlayWright Fetcher from working entirely.

## [v0.2.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.2) - 2024-11-16

### What's changed
##### New features
- Now if you don't want to pass arguments to the generated `Adaptor` object and want to use the default values, you can use this import instead for cleaner code
    ```python
    >> from scrapling.default import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher.get('https://example.com', stealthy_headers=True)
    ```
   Otherwise
    ```python
    >> from scrapling import Fetcher, StealthyFetcher, PlayWrightFetcher
    >> page = Fetcher(auto_match=False).get('https://example.com', stealthy_headers=True)
    ```

##### Bugs Squashed
1. Fixed a bug with the `Response` object introduced with patch v0.2.1 yesterday that happened with some cases of nested selecting/parsing.

## [v0.2.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2.1) - 2024-11-15

### What's changed
##### New features
1. Now the `Response` object returned from all fetchers is the same as the `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`. All `cookies`, `headers`, and `request_headers` are always of type `dictionary`. <br/>So your code can now become like:
    ```python
    >> from scrapling import Fetcher
    >> page = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(page.status)
    200
    >> products = page.css('.product')
    ```
   Instead of before
    ```python
    >> from scrapling import Fetcher
    >> fetcher = Fetcher().get('https://example.com', stealthy_headers=True)
    >> print(fetcher.status)
    200
    >> page = fetcher.adaptor
    >> products = page.css('.product')
    ```
   But I have left the `.adaptor` property working for backward compatibility.
2. Now both the `StealthyFetcher` and `PlayWrightFetcher` classes can take a `proxy` argument with the fetch method which accepts a string or a dictionary.
3. Now the `StealthyFetcher` class has the `os_randomize` argument with the `fetch` method. If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.

##### Bugs Squashed
1. Fixed a bug that happens while passing headers with the `Fetcher` class.
2. Fixed a bug with parsing JSON responses passed from the fetcher-type classes.

##### Quality of life changes
1. The text functionality behavior was to try to remove HTML comments before returning the text but that induced errors in some cases and made the code more complicated than needed. Now it has reverted to the default lxml behavior, **you will notice a slight speed increase to all operations that counts on elements' text like selectors**. Now if you want Scrapling to remove HTML comments from elements before returning the text to avoid the weird text-splitting behavior that's in lxml/parsel/scrapy, just keep the `keep_comments` argument set to True as it is by default.

## [v0.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.2) - 2024-11-11

### What's changed
##### New features
1. Introducing the `Fetchers` feature with 3 new main types to make Scrapling fetch pages for you with a LOT of options!
   - The `Fetcher` class for basic HTTP requests
   - The `StealthyFetcher` class is a completely stealthy fetcher that uses a [stealthy modified version of Firefox](https://github.com/daijro/camoufox).
   - The `PlayWrightFetcher` class that allows doing browser-based requests with Vanilla PlayWright, PlayWright with stealth mode made by me, Real browsers through CDP, and [NSTBrowser](https://app.nstbrowser.io/r/1vO5e5)'s [docker browserless](https://hub.docker.com/r/nstbrowser/browserless)!
2. Added the completely new `find_all`/`find` methods to find elements easily on the page with dark magic!
3. Added the methods `filter` and `search` to the `Adaptors` class for easier bulk operations on `Adaptor` object groups.
4. Added methods `css_first` and `xpath_first` methods for easier usage.
5. Added the new class type `TextHandlers` which is used for bulk operations on `TextHandler` objects like the `Adaptors` class.
6. Added `generate_full_css_selector` and `generate_full_xpath_selector` methods.

##### Bugs Squashed
1. Now the `Adaptors` class version of `re_first` returns the first result that matches in all `Adaptor` objects inside instead of the faulty logic of returning the results of `re_first` of all `Adaptor` objects.
2. Now if the user selects a text-type content to be returned from selected elements (like css `::text` function) with any method like `.css` or `.xpath`. The `Adaptor` object will return the `TextHandlers` class instead of returning a list of strings like before. So now you can do `page.css('something::text').re_first(r'regex_pattern').json()` instead of `page.css('something::text')[0].re_first(r'regex_pattern').json()`
3. Now `Adaptor`/`Adaptors` re/re_first arguments are consistent with the `TextHandler` ones. So now you have `clean_match` and `case_sensitive` arguments. 
4. Now the `auto_match` argument is enabled by default in the initialization of `Adaptor` but still you have to enable it while selecting elements if you want to enable it. (Not a bug but a design decision)
5. A lot of type-annotations corrections here and there for better auto-completion experience while you are coding with Scrapling.

##### Quality of life changes
1. Renamed both `css_selector` and `xpath_selector` methods to `generate_css_selector` and `generate_xpath_selector` for clarity and to not interrupt the auto-completion while coding.
2. Restructured most of the old code into a `core` subpackage and other design decisions for cleaner and easier maintenance in the future.
3. Restructured the tests folder into a cleaner structure and added tests for the new features. Also now tox environments are cached on GitHub for faster automated tests with each commit.

## [v0.1.2](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.2) - 2024-10-16

**Changelog**:
- Fixed a bug where the `keep_comments` argument is not working as intended.
- Adjusted the text function to automatically remove HTML comments from elements before extracting its text to prevent Lxml different behavior, for example:
  ```python
  >>> page = Adaptor('<span>CONDITION: <!-- -->Excellent</span>', keep_comments=True)
  >>> page.css('span::text')
  ['CONDITION: ', 'Excellent']
  ```
  previously would result in this because of Lxml default behavior but now it would return the full text 'CONDITION: Excellent'
  This behavior is known with parsel\scrapy as well so wanted to handle it here.
- Fixed a bug where the SQLite db file created by the library is not deleted when doing `pip uninstall scrapling` or similar.

## [v0.1.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1.1) - 2024-10-14

Minor fixes

## [v0.1](https://github.com/D4Vinci/Scrapling/releases/tag/v0.1) - 2024-10-13

**Full Changelog**: https://github.com/D4Vinci/Scrapling/commits/v0.1

