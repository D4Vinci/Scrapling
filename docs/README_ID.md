<!-- mcp-name: io.github.D4Vinci/Scrapling -->

<h1 align="center">
    <a href="https://scrapling.readthedocs.io">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_dark.svg?sanitize=true">
          <img alt="Scrapling Poster" src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/cover_light.svg?sanitize=true">
        </picture>
    </a>
    <br>
    <small>Web Scraping Tanpa Repot untuk Web Modern</small>
</h1>

<p align="center">
    <a href="https://trendshift.io/repositories/14244" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14244" alt="D4Vinci%2FScrapling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
    <br/>
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
    <a href="https://scrapling.readthedocs.io/en/latest/parsing/selection.html"><strong>Metode Seleksi</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/fetching/choosing.html"><strong>Fetcher</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/architecture.html"><strong>Spider</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/spiders/proxy-blocking.html"><strong>Rotasi Proxy</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/cli/overview.html"><strong>CLI</strong></a>
    &middot;
    <a href="https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html"><strong>MCP</strong></a>
</p>

Scrapling merupakan framework Web Scraping adaptif yang menangani semuanya, mulai dari satu request hingga crawl skala penuh.

Pengurai (parser) mempelajari perubahan pada website dan secara otomatis menemukan kembali elemen Anda saat halaman diperbarui. Fetcher-nya dapat melewati sistem anti-bot seperti Cloudflare Turnstile tanpa konfigurasi tambahan. Framework spider-nya memungkinkan Anda meningkatkan skala hingga crawl concurrent multi-session dengan pause/resume, rotasi proxy otomatis, serta kecepatan crawl yang menyesuaikan waktu respons setiap website dan melambat saat website mulai memblokir Anda—semuanya hanya dengan beberapa baris Python. Satu library, tanpa kompromi.

Crawl sangat cepat dengan statistik real-time dan streaming. Dibuat oleh Web Scraper untuk Web Scraper dan pengguna umum, Scrapling menawarkan sesuatu untuk semua orang.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
StealthyFetcher.adaptive = True
p = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)  # Fetch website under the radar!
products = p.css('.product', auto_save=True)                                        # Scrape data that survives website design changes!
products = p.css('.product', adaptive=True)                                         # Later, if the website structure changes, pass `adaptive=True` to find them!
```
Atau tingkatkan skalanya menjadi crawl penuh
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

<p align="center">
    <a href="https://dataimpulse.com/?utm_source=scrapling&utm_medium=banner&utm_campaign=scrapling" target="_blank" style="display:flex; justify-content:center; padding:4px 0;">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/DataImpulse.png" alt="At DataImpulse, we specialize in developing custom proxy services for your business. Make requests from anywhere, collect data, and enjoy fast connections with our premium proxies." style="max-height:60px;">
    </a>
</p>

# Sponsor Platinum
<table>
  <tr>
    <td width="200">
      <a href="https://go.nodemaven.com/scraplingaugust" target="_blank" title="Proxies with the Highest IP Scores">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/NodeMaven.jpg" width="240" height="100">
      </a>
    </td>
    <td>
    <a href="https://go.nodemaven.com/scraplingaugust" target="_blank">NodeMaven</a> - Penyedia proxy paling efisien untuk Web Scraping dan Automation dengan IP berkualitas tertinggi di pasar. Gunakan kode SCRAPLING35 untuk diskon 35%.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://proxidize.com/?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=d4vinci" target="_blank" title="Clean Proxies with No Nonsense.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxidize.png">
      </a>
    </td>
    <td> <a href="https://proxidize.com/?utm_source=github&utm_medium=sponsorship&utm_campaign=scrapling&utm_content=d4vinci" target="_blank"><b>Proxidize</b></a> menyediakan mobile dan residential proxy untuk scraping, browser automation, SEO monitoring, AI agents, dan data collection. <i>Gunakan kode <b>scrapling20</b> untuk diskon 20%</i>.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://coldproxy.com/?utm_source=scrapling&utm_medium=github&utm_campaign=coldproxy&utm_content=platinum_sponsor" target="_blank" title="Residential, IPv6 & Datacenter Proxies for Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/coldproxy.png">
      </a>
    </td>
    <td> <a href="https://coldproxy.com/?utm_source=scrapling&utm_medium=github&utm_campaign=coldproxy&utm_content=platinum_sponsor" target="_blank"><b>ColdProxy</b></a> menyediakan residential dan datacenter proxy untuk web scraping yang stabil, pengumpulan data publik, dan pengujian berbasis lokasi di lebih dari 195 negara.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://hypersolutions.co/?utm_source=github&utm_medium=readme&utm_campaign=scrapling" target="_blank" title="Bot Protection Bypass API for Akamai, DataDome, Incapsula & Kasada">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/HyperSolutions.png">
      </a>
    </td>
    <td> Scrapling menangani Cloudflare Turnstile. Untuk perlindungan tingkat enterprise, <a href="https://hypersolutions.co?utm_source=github&utm_medium=readme&utm_campaign=scrapling">
        <b>Hyper Solutions</b>
      </a> menyediakan endpoint API yang menghasilkan token antibot valid untuk <b>Akamai</b>, <b>DataDome</b>, <b>Kasada</b>, dan <b>Incapsula</b>. Cukup dengan panggilan API sederhana, tanpa perlu browser automation. </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://birdproxies.com/t/scrapling" target="_blank" title="At Bird Proxies, we eliminate your pains such as banned IPs, geo restriction, and high costs so you can focus on your work.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/BirdProxies.jpg">
      </a>
    </td>
    <td>Kami membuat <a href="https://birdproxies.com/t/scrapling">
        <b>BirdProxies</b>
      </a> karena proxy seharusnya tidak rumit atau terlalu mahal. Residential dan ISP proxy yang cepat di lebih dari 195 lokasi, harga yang wajar, dan dukungan nyata. <br />
      <b>Coba game FlappyBird kami di landing page untuk mendapatkan data gratis!</b>
    </td>
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
      </a>: residential proxy mulai dari $0.49/GB. Scraping browser dengan Chromium yang sepenuhnya di-spoof, residential IP, pemecahan CAPTCHA otomatis, dan bypass anti-bot. </br>
      <b>Scraper API untuk hasil tanpa repot. Integrasi MCP dan N8N juga tersedia.</b>
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank" title="Unlock the Power of Social Media Data & AI">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TikHub.jpg">
      </a>
    </td>
    <td>
      <a href="https://tikhub.io/?utm_source=github.com/D4Vinci/Scrapling&utm_medium=marketing_social&utm_campaign=retargeting&utm_content=carousel_ad" target="_blank">TikHub.io</a> menyediakan lebih dari 900 API stabil di lebih dari 16 platform termasuk TikTok, X, YouTube & Instagram, dengan lebih dari 40 juta dataset. <br /> Juga menawarkan <a href="https://ai.tikhub.io/?ref=KarimShoair" target="_blank">model AI dengan DISKON</a> - Claude, GPT, GEMINI & lainnya hingga 71% lebih murah.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://petrosky.io/d4vinci" target="_blank" title="PetroSky delivers cutting-edge VPS hosting.">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/petrosky.png">
      </a>
    </td>
    <td>
    Tutup laptop Anda. Scraper Anda tetap berjalan. <br />
    <a href="https://petrosky.io/d4vinci" target="_blank">PetroSky VPS</a> - cloud server yang dibuat untuk automation tanpa henti. Mesin Windows dan Linux dengan kontrol penuh. Mulai €6.99/bulan.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank" title="The #1 newsletter dedicated to Web Scraping">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/TWSC.png">
      </a>
    </td>
    <td>
    Baca ulasan lengkap <a href="https://substack.thewebscraping.club/p/scrapling-hands-on-guide?utm_source=github&utm_medium=repo&utm_campaign=scrapling" target="_blank">Scrapling di The Web Scraping Club</a> (Nov 2025), newsletter #1 yang didedikasikan untuk Web Scraping.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank" title="Scalable Solutions for Web Data Access">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SwiftProxy.png">
      </a>
    </td>
    <td>
    <a href="https://www.swiftproxy.net/?ref=D4Vinci" target="_blank">Swiftproxy</a> menyediakan residential proxy yang scalable dengan lebih dari 80 juta IP di lebih dari 195 negara, menghadirkan koneksi cepat dan andal, rotasi otomatis, serta performa anti-block yang kuat. Tersedia uji coba gratis.
    </td>
  </tr>
  <tr>
    <td width="200">
      <a href="https://niuproxy.com/?utm_source=scrapling&utm_medium=scrapling&ref=scrapling" target="_blank" title="Affordable Residential in 190+ Countries">
        <img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/niuproxy.png">
      </a>
    </td>
    <td>
    <a href="https://niuproxy.com/?utm_source=scrapling&utm_medium=scrapling&ref=scrapling" target="_blank">NiuProxy</a> — Rotating residential proxy mulai dari $0.35/GB. Gunakan kode eksklusif Scrapling PAY2 untuk diskon 10% saat mengisi ulang saldo.
    </td>
  </tr>
</table>

<i><sub>Ingin menampilkan iklan Anda di sini? Klik [di sini](https://github.com/sponsors/D4Vinci/sponsorships?tier_id=586646)</sub></i>
# Sponsor

<!-- sponsors -->

<a href="https://www.novada.com/?d4vinci-scrapling" target="_blank" title="The All-in-One Solution for Every Data Scraping Scenario"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/novada.jpg"></a>
<a href="https://cloro.dev/?utm_source=referral&utm_medium=scrapling" target="_blank" title="The search API for the AI era"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/cloro.jpg"></a>

<br/>

<a href="https://serpapi.com/?utm_source=scrapling" target="_blank" title="Scrape Google and other search engines with SerpApi"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/SerpApi.png"></a>
<a href="https://visit.decodo.com/Dy6W0b" target="_blank" title="Try the Most Efficient Residential Proxies for Free"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/decodo.png"></a>
<a href="https://proxyempire.io/?ref=scrapling&utm_source=scrapling" target="_blank" title="Collect The Data Your Project Needs with the Best Residential Proxies"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/ProxyEmpire.png"></a>
<a href="https://www.webshare.io/?referral_code=48r2m2cd5uz1" target="_blank" title="The Most Reliable Proxy with Unparalleled Performance"><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/webshare.png"></a>
<a href="https://proxiware.com/?ref=scrapling" target="_blank" title="Collect Any Data. At Any Scale."><img src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/images/proxiware.png"></a>


<!-- /sponsors -->

<i><sub>Ingin menampilkan iklan Anda di sini? Klik [di sini](https://github.com/sponsors/D4Vinci) dan pilih tier yang sesuai untuk Anda!</sub></i>

---

## Fitur Utama

### Spider - Framework Crawling Lengkap
- 🕷️ **API Spider mirip Scrapy**: Definisikan spider dengan `start_urls`, callback `parse` async, serta objek `Request`/`Response`.
- ⚡ **Crawling Concurrent**: Batas concurrency yang dapat dikonfigurasi, throttling per domain, dan download delay.
- 🔄 **Dukungan Multi-Session**: Interface terpadu untuk HTTP request dan stealthy headless browser dalam satu spider - arahkan request ke session berbeda berdasarkan ID.
- 💾 **Pause & Resume**: Persistensi crawl berbasis checkpoint. Tekan Ctrl+C untuk shutdown dengan aman; jalankan kembali untuk melanjutkan dari titik terakhir.
- 📡 **Mode Streaming**: Stream item hasil scraping saat tersedia melalui `async for item in spider.stream()` dengan statistik real-time - ideal untuk UI, pipeline, dan crawl jangka panjang.
- 🛡️ **Deteksi Request yang Diblokir**: Deteksi dan retry otomatis untuk request yang diblokir dengan logika yang dapat disesuaikan.
- 🚦 **AutoThrottle**: Tidak perlu lagi menebak delay. Spider menyesuaikan delay tiap domain berdasarkan seberapa cepat website merespons, lalu menggandakannya (atau menunggu sesuai `Retry-After`) ketika website mulai memblokir atau membatasi request Anda, dan mempercepatnya kembali setelah pembatasan berhenti.
- 🤖 **Kepatuhan Robots.txt**: Flag `robots_txt_obey` opsional yang mematuhi directive `Disallow`, `Crawl-delay`, dan `Request-rate` dengan cache per domain.
- 🧪 **Mode Development**: Cache response ke disk pada run pertama dan replay pada run berikutnya - iterasikan logika `parse()` tanpa mengakses ulang target server.
- 🧩 **Template Spider Siap Pakai**: Lewati boilerplate dengan `CrawlSpider` untuk mengikuti link berbasis rule, `SitemapSpider` untuk crawl berbasis sitemap/robots.txt, `XMLFeedSpider`/`CSVFeedSpider` untuk mengiterasi feed XML/RSS dan CSV, serta `ShopifySpider` untuk mengambil seluruh produk dari toko Shopify melalui JSON API-nya, satu item per variant.
- 🔗 **Ekstraksi Link**: Primitive `LinkExtractor` mandiri dengan pola allow/deny, filter domain, scoping CSS/XPath, filter extension, dan canonicalization - gunakan di dalam template atau secara mandiri.
- 📦 **Export Bawaan**: Export hasil melalui hook dan pipeline Anda sendiri atau exporter JSON/JSONL/CSV/XML bawaan dengan `result.items.to_json()`, `to_jsonl()`, `to_csv()`, dan `to_xml()`.

### Fetching Website Tingkat Lanjut dengan Dukungan Session
- **HTTP Request**: HTTP request cepat dan stealthy dengan class `Fetcher`. Dapat meniru TLS fingerprint browser, header, dan menggunakan HTTP/3.
- **Dynamic Loading**: Fetch website dinamis dengan browser automation penuh melalui class `DynamicFetcher` yang mendukung Chromium milik Playwright dan Google Chrome.
- **Bypass Anti-bot**: Kemampuan stealth tingkat lanjut dengan `StealthyFetcher` dan fingerprint spoofing. Dapat dengan mudah melewati berbagai jenis Cloudflare Turnstile/Interstitial melalui automation.
- **Session Management**: Dukungan persistent session dengan class `FetcherSession`, `StealthySession`, dan `DynamicSession` untuk mengelola cookie dan state antar-request.
- **Rotasi Proxy**: `ProxyRotator` bawaan dengan strategi rotasi cyclic atau custom di semua jenis session, termasuk override proxy per request.
- **Pemblokiran Domain & Iklan**: Blokir request ke domain tertentu (beserta subdomain-nya) atau aktifkan ad blocking bawaan (~3.500 domain iklan/tracker yang dikenal) pada fetcher berbasis browser.
- **Pencegahan DNS Leak**: Dukungan DNS-over-HTTPS opsional untuk merutekan query DNS melalui DoH Cloudflare, mencegah DNS leak saat menggunakan proxy.
- **Remote Browser**: Alih-alih menjalankan browser secara lokal, hubungkan ke browser yang sudah berjalan melalui CDP menggunakan `cdp_url`, baik di mesin yang sama, host lain, maupun managed browser provider. Anda juga dapat mengarahkan browser fetcher apa pun ke build Chromium Anda sendiri dengan `executable_path`.
- **Background API Capture**: Berikan pola URL ke `capture_xhr`, lalu semua response XHR/fetch yang cocok dan dibuat halaman saat loading akan dikumpulkan sebagai objek `Response` di `response.captured_xhr` - ambil data API sebuah situs tanpa perlu melakukan reverse-engineering request sendiri.
- **Dukungan Async**: Dukungan async lengkap di seluruh fetcher dan class async session khusus.

### Adaptive Scraping
- 🔄 **Smart Element Tracking**: Temukan kembali elemen setelah perubahan website menggunakan algoritma similarity cerdas.
- 🎯 **Seleksi Fleksibel dan Cerdas**: CSS selector, XPath selector, pencarian berbasis filter, pencarian teks, pencarian regex, dan lainnya.
- 🔍 **Temukan Elemen Serupa**: Secara otomatis menemukan elemen yang mirip dengan elemen yang ditemukan.

### Fitur AI
- 🤖 **MCP Server**: Memungkinkan chatbot dan agent AI (Claude/Cursor/dll.) melakukan scraping melalui Scrapling dengan tool one-shot atau berbasis session yang mencakup HTTP request biasa (method apa pun), browser fetch, dan stealth fetch yang melewati Cloudflare. Halaman dipersempit dengan CSS selector dan dibersihkan dari konten prompt injection sebelum dilihat AI, sehingga agent membaca lebih sedikit, biaya lebih rendah, dan tidak dapat dibajak oleh teks tersembunyi. Screenshot, remote browser melalui CDP, dan transport HTTP yang secure-by-default juga disertakan. ([video demo](https://www.youtube.com/watch?v=qyFk3ZNwOxE))
- 🧠 **Agent Skill**: [Agent Skill](https://scrapling.readthedocs.io/en/latest/ai/agent-skill.html) siap instal yang mengajarkan seluruh library kepada coding agent, sehingga kode Scrapling yang mereka tulis mengikuti API saat ini alih-alih menebak.
- 📚 **Markdown siap RAG**: Ubah halaman apa pun menjadi Markdown yang bersih, tersanitasi, dan siap LLM hanya dengan satu baris (`page.markdown()`), atau crawl seluruh website menjadi korpus Markdown dengan template `SiteToMarkdownSpider`, semuanya tanpa LLM di dalam loop. ([dokumentasi](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html))

### Arsitektur High-Performance & Battle-Tested
- 🚀 **Sangat Cepat**: Performa yang dioptimalkan dan melampaui sebagian besar library scraping Python.
- 🔋 **Hemat Memori**: Struktur data yang dioptimalkan dan lazy loading untuk penggunaan memori minimal.
- ⚡ **Serialisasi JSON Cepat**: 10x lebih cepat dibanding standard library.
- 🏗️ **Battle-Tested**: Scrapling tidak hanya memiliki test coverage 92% dan cakupan type hints penuh, tetapi juga telah digunakan setiap hari oleh ratusan Web Scraper selama setahun terakhir.

### Pengalaman yang Ramah Developer/Web Scraper
- 🎯 **Shell Web Scraping Interaktif**: Shell IPython bawaan opsional dengan integrasi Scrapling, shortcut, dan tool baru untuk mempercepat pengembangan script Web Scraping, seperti mengubah curl request menjadi Scrapling request dan melihat hasil request di browser Anda.
- 🚀 **Gunakan Langsung dari Terminal**: Secara opsional, Anda dapat menggunakan Scrapling untuk melakukan scraping URL tanpa menulis satu baris kode pun!
- 🛠️ **API Navigasi Lengkap**: Traversal DOM tingkat lanjut dengan method navigasi parent, sibling, dan child.
- 🧬 **Pemrosesan Teks yang Ditingkatkan**: Regex bawaan, method cleaning, dan operasi string yang dioptimalkan.
- 📝 **Pembuatan Selector Otomatis**: Buat CSS/XPath selector yang robust untuk elemen apa pun.
- 🔌 **API yang Familiar**: Mirip Scrapy/BeautifulSoup dengan pseudo-element yang sama seperti yang digunakan Scrapy/Parsel.
- 🤝 **Integrasi Scrapy Drop-in**: Sudah banyak berinvestasi di Scrapy? Dekorasi callback apa pun dengan `scrapling_response` untuk parse response yang sudah Anda fetch menggunakan parser Scrapling, tanpa perlu rewrite.
- 📘 **Cakupan Type Lengkap**: Type hint penuh untuk dukungan IDE dan code completion yang sangat baik. Seluruh codebase secara otomatis dipindai dengan **PyRight** dan **MyPy** pada setiap perubahan.
- 🔋 **Docker Image Siap Pakai**: Pada setiap release, Docker image yang berisi semua browser otomatis dibangun dan di-push.

## Memulai

Berikut gambaran singkat tentang apa yang dapat dilakukan Scrapling tanpa membahas terlalu dalam.

### Penggunaan Dasar
HTTP request dengan dukungan session
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:  # Use latest version of Chrome's TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Or use one-off requests
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```
Mode stealth tingkat lanjut
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:  # Keep the browser open until you finish
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```
Browser automation penuh
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:  # Keep the browser open until you finish
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()  # XPath selector if you prefer it

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text').getall()
```

### Spider
Bangun crawler lengkap dengan request concurrent, berbagai jenis session, dan pause/resume:
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
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```
Gunakan beberapa jenis session dalam satu spider:
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
            # Route protected pages through the stealth session
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)  # explicit callback
```
Pause dan lanjutkan crawl panjang menggunakan checkpoint dengan menjalankan spider seperti ini:
```python
QuotesSpider(crawldir="./crawl_data").start()
```
Tekan Ctrl+C untuk pause dengan aman - progress disimpan secara otomatis. Nanti, saat Anda menjalankan spider lagi, gunakan `crawldir` yang sama dan crawl akan dilanjutkan dari titik terakhir.

Atau lewati penulisan logika crawling sepenuhnya dengan template siap pakai, seperti mengambil seluruh katalog toko Shopify:
```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()  # Every product in the store, one item per variant
```

### Parsing & Navigasi Tingkat Lanjut
```python
from scrapling.fetchers import Fetcher

# Rich element selection and navigation
page = Fetcher.get('https://quotes.toscrape.com/')

# Get quotes with multiple selection methods
quotes = page.css('.quote')  # CSS selector
quotes = page.xpath('//div[@class="quote"]')  # XPath
quotes = page.find_all('div', {'class': 'quote'})  # BeautifulSoup-style
# Same as
quotes = page.find_all('div', class_='quote')
quotes = page.find_all(['div'], class_='quote')
quotes = page.find_all(class_='quote')  # and so on...
# Find element by text content
quotes = page.find_by_text('quote', tag='div')

# Advanced navigation
quote_text = page.css('.quote')[0].css('.text::text').get()
quote_text = page.css('.quote').css('.text::text').getall()  # Chained selectors
first_quote = page.css('.quote')[0]
author = first_quote.next_sibling.css('.author::text')
parent_container = first_quote.parent

# Element relationships and similarity
similar_elements = first_quote.find_similar()
below_elements = first_quote.below_elements()
```
Anda dapat langsung menggunakan parser jika tidak ingin melakukan fetch website, seperti berikut:
```python
from scrapling.parser import Selector

page = Selector("<html>...</html>")
```
Dan cara kerjanya tetap sama persis!

### Contoh Async Session Management
```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:  # `FetcherSession` is context-aware and can work in both sync/async patterns
    page1 = session.get('https://quotes.toscrape.com/')
    page2 = session.get('https://quotes.toscrape.com/', impersonate='firefox135')

# Async session usage
async with AsyncStealthySession(max_pages=2) as session:
    tasks = []
    urls = ['https://example.com/page1', 'https://example.com/page2']

    for url in urls:
        task = session.fetch(url)
        tasks.append(task)

    print(session.get_pool_stats())  # Optional - The status of the browser tabs pool (busy/free/error)
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())
```

## CLI & Shell Interaktif

Scrapling menyertakan command-line interface yang powerful:

[![asciicast](https://asciinema.org/a/736339.svg)](https://asciinema.org/a/736339)

Jalankan shell Web Scraping interaktif
```bash
scrapling shell
```
Ekstrak halaman langsung ke file tanpa programming (secara default mengekstrak konten di dalam tag `body`). Jika file output berakhiran `.txt`, konten teks dari target akan diekstrak. Jika berakhiran `.md`, output akan berupa representasi Markdown dari konten HTML; jika berakhiran `.html`, output akan berupa konten HTML itu sendiri.
```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts' --impersonate 'chrome'  # All elements matching the CSS selector '#fromSkipToProducts'
scrapling extract fetch 'https://example.com' content.md --css-selector '#fromSkipToProducts' --no-headless
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --css-selector '#padded_content a' --solve-cloudflare
```

> [!NOTE]
> Masih ada banyak fitur tambahan, tetapi kami ingin menjaga halaman ini tetap ringkas, termasuk MCP server dan Shell Web Scraping interaktif. Lihat dokumentasi lengkapnya [di sini](https://scrapling.readthedocs.io/en/latest/)

## Benchmark Performa

Scrapling bukan hanya powerful — tetapi juga sangat cepat. Benchmark berikut membandingkan parser Scrapling dengan versi terbaru dari library populer lainnya.

### Uji Kecepatan Ekstraksi Teks (5000 elemen bertingkat)

| # |      Library      | Waktu (ms) | vs Scrapling |
|---|:-----------------:|:----------:|:------------:|
| 1 |     Scrapling     |    1.99    |     1.0x     |
| 2 |   Parsel/Scrapy   |    2.06    |    1.035     |
| 3 |     Raw Lxml      |    2.56    |    1.286     |
| 4 |      PyQuery      |   23.98    |     ~12x     |
| 5 |    Selectolax     |   197.02   |     ~99x     |
| 6 |  MechanicalSoup   |  1545.15   |   ~776.5x    |
| 7 |   BS4 with Lxml   |  1562.1   |   ~785.0x    |
| 8 | BS4 with html5lib |  3412.73   |   ~1714.9x   |


### Performa Element Similarity & Pencarian Teks

Kemampuan Scrapling untuk menemukan elemen secara adaptif secara signifikan mengungguli alternatif lainnya:

| Library     | Waktu (ms) | vs Scrapling |
|-------------|:----------:|:------------:|
| Scrapling   |    2.3     |     1.0x     |
| AutoScraper |   12.58    |    5.47x     |


> Semua benchmark merupakan rata-rata dari lebih dari 100 run. Lihat [benchmarks.py](https://github.com/D4Vinci/Scrapling/blob/main/benchmarks.py) untuk metodologinya.

## Instalasi

Scrapling membutuhkan Python 3.10 atau lebih baru:

```bash
pip install scrapling
```

> [!IMPORTANT]
> Instalasi ini hanya menyertakan parser engine dan dependency-nya, tanpa dependency fetcher atau commandline. Karena itu, mengimpor apa pun dari `scrapling.fetchers` atau `scrapling.spiders`, seperti pada contoh di atas, akan menghasilkan `ModuleNotFoundError` jika hanya menggunakan instalasi ini. Jika Anda akan menggunakan fetcher atau spider, instal dependency fetcher terlebih dahulu seperti yang ditunjukkan di bawah.

### Dependency Opsional

1. Jika Anda akan menggunakan fitur tambahan di bawah, fetcher, atau class terkait, Anda perlu menginstal dependency fetcher beserta dependency browser-nya sebagai berikut:
    ```bash
    pip install "scrapling[fetchers]"

    scrapling install           # normal install
    scrapling install  --force  # force reinstall
    ```

    Perintah ini mengunduh semua browser beserta system dependency dan dependency untuk manipulasi fingerprint.

    Atau Anda dapat menginstalnya melalui kode alih-alih menjalankan command seperti ini:
    ```python
    from scrapling.cli import install

    install([], standalone_mode=False)          # normal install
    install(["--force"], standalone_mode=False) # force reinstall
    ```

2. Fitur tambahan:
   - Instal fitur MCP server:
       ```bash
       pip install "scrapling[ai]"
       ```
   - Instal dependency untuk ([membangun sistem RAG](https://scrapling.readthedocs.io/en/latest/ai/building-rag-systems.html)):
       ```bash
       pip install "scrapling[rag]"
       ```
   - Instal fitur shell (shell Web Scraping dan command `extract`):
       ```bash
       pip install "scrapling[shell]"
       ```
   - Instal semuanya:
       ```bash
       pip install "scrapling[all]"
       ```
   Ingat bahwa Anda perlu menginstal dependency browser dengan `scrapling install` setelah memasang salah satu extra ini (jika belum melakukannya).

### Docker
Anda juga dapat menginstal Docker image yang berisi semua extra dan browser dengan command berikut dari DockerHub:
```bash
docker pull pyd4vinci/scrapling
```
Atau unduh dari GitHub registry:
```bash
docker pull ghcr.io/d4vinci/scrapling:latest
```
Image ini dibangun dan di-push secara otomatis menggunakan GitHub Actions dan branch main repository.

## Berkontribusi

Kami menyambut kontribusi! Silakan baca [panduan kontribusi](https://github.com/D4Vinci/Scrapling/blob/main/CONTRIBUTING.md) sebelum memulai.

## Disclaimer

> [!CAUTION]
> Library ini disediakan hanya untuk tujuan pendidikan dan penelitian. Dengan menggunakan library ini, Anda setuju untuk mematuhi hukum lokal dan internasional terkait data scraping dan privasi. Penulis dan kontributor tidak bertanggung jawab atas penyalahgunaan software ini. Selalu hormati terms of service website dan file robots.txt.

## 🎓 Sitasi
Jika Anda menggunakan library kami untuk tujuan penelitian, silakan kutip kami dengan referensi berikut:
```text
  @misc{scrapling,
    author = {Karim Shoair},
    title = {Scrapling},
    year = {2024},
    url = {https://github.com/D4Vinci/Scrapling},
    note = {An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!}
  }
```

## Lisensi

Proyek ini dilisensikan di bawah BSD-3-Clause License.

## Ucapan Terima Kasih

Proyek ini menyertakan kode yang diadaptasi dari:
- Parsel (BSD License)-Digunakan untuk submodule [translator](https://github.com/D4Vinci/Scrapling/blob/main/scrapling/core/translator.py)

---
<div align="center"><small>Dirancang & dibuat dengan ❤️ oleh Karim Shoair.</small></div><br>
