# Anti-bot vendors and captcha solvers

`solve_cloudflare` handles Cloudflare. Many protected sites use other bot-management vendors, and each one has its own challenge pages, cookies and widgets. With `solve_antibot=True`, the `StealthyFetcher` and its session classes recognise seven vendors after every navigation and try to get past them inside the request's `timeout`:

| Vendor | Recognised by | What the handler does |
|---|---|---|
| Cloudflare | `cf-mitigated`, the `cType` challenge page, a Turnstile gate, error pages 1010/1015/1020 | Runs Scrapling's Cloudflare solver within the deadline. A Turnstile gate that a click does not clear can go to a captcha solver. |
| AWS WAF | `x-amzn-waf-action`, `gokuProps`, `<awswaf-captcha>` | Waits for `challenge.js` to store `aws-waf-token`. The image CAPTCHA can go to a captcha solver (image recognition first, then a token). |
| DataDome | The `var dd={...}` verdict, `x-dd-b`, `captcha-delivery.com` frames | Waits out the device check, clicks a shown confirm button once, stops on a ban (`t=bv`). Drags the slide-to-target slider onto its target by itself; the jigsaw slider can go to a captcha solver. |
| Kasada | `x-kpsdk-*` headers, `ips.js` | Waits for the SDK's proof of work and keeps the latest `x-kpsdk-ct`/`st` tokens. |
| HUMAN (PerimeterX) | `#px-captcha`, the block page | Press and hold on the widget with a human-paced pointer, released by the progress bar. |
| Akamai Bot Manager | SEC-CPT and SBSD pages, the edge's "Access Denied" | Lets the interstitial clear under pointer input, with the SEC-CPT proof of work as a local fallback; one same-origin warm-up for edge blocks. |
| Imperva (Incapsula) | The reese84 interstitial, the `___utmvc` page, the incident page | Waits for the sensor to clear the page; on the incident page, clicks the hCaptcha checkbox once and can use a captcha solver token. |

Nothing is solved by a third party unless you pass a `captcha_solver` (see [below](#captcha-solvers)). Without one, everything happens inside your browser.

!!! success "Prerequisites"

    You've read the [StealthyFetcher](stealthy.md) page, since `solve_antibot` is one of its options.

## Basic usage

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://protected-site.com/catalogue', solve_antibot=True)
print(page.status, page.meta['antibot'])
```

It works the same way in the sessions, for the whole session or per request:

```python
from scrapling.fetchers import AsyncStealthySession

async with AsyncStealthySession(solve_antibot=True, max_pages=3) as session:
    page = await session.fetch('https://protected-site.com/catalogue')

# Or switch it on for one request only
async with AsyncStealthySession() as session:
    page = await session.fetch('https://protected-site.com/catalogue', solve_antibot=True)
```

!!! tip

    Prefer turning it on for the whole session (or through `StealthyFetcher`). Only then is the browser itself launched hardened (see [Headless hardening](#headless-hardening)); turning it on for one request hardens that request's page but not the launch. Akamai, for example, blocks a headless browser whose launch switches give it away even when every page is hardened.

The anti-bot pass runs after the page loads (and after the Cloudflare solver, if `solve_cloudflare` is also on) and before your `page_action`. It shares the request's `timeout` and leaves a tenth of it (between 1 and 3 seconds) for your `page_action` and for building the response. It never navigates off the target's origin, except into the vendor's own challenge frames, and it never types into anything but a vendor's widget.

## What the response tells you

Every response fetched with `solve_antibot=True` carries the outcome in `response.meta['antibot']`:

```python
{
    'vendor': 'datadome',        # None when nothing was detected
    'kind': 'device_check',      # device_check, challenge, captcha, block or ban
    'rule': 'dd.frame_device',   # the detection rule that matched
    'solved': True,
    'reason': 'solved',          # 'none' when nothing was detected
    'layers': [...],             # one entry per vendor, in order
    'elapsed_s': 3.1,
    'solver': {...},             # only when a captcha solver was called
}
```

Some sites put two vendors in a row, for example Imperva in front of DataDome. After a vendor is solved, the page is read and checked again, and the next vendor gets its turn, up to three. Until a new document loads, that check keeps the status and headers the page was detected with, so a block page that never changed is never reported as solved. The top-level fields describe the layer that decided the outcome; `solved` is `True` only when every layer was solved. Each entry in `layers` has the same fields plus `cookies` (the names of the clearance cookies the solve earned, never their values), `used_solver`, `solver_kind` and `elapsed_s`. `solver_kind` is set on an unsolved layer that stopped at a captcha a captcha solver can act on (`turnstile`, `hcaptcha`, `awswaf` or `datadome_slider`), and is `None` when no solver would help (a ban, a block, a press-and-hold, an unsupported widget).

The reasons you will see most:

| Reason | Meaning |
|---|---|
| `solved`, `solved:<how>` | The vendor's challenge is gone from the page. |
| `none` | Nothing was detected. |
| `ban` | The vendor has banned this client or IP (DataDome's `t=bv`, for example). Retrying from the same IP makes it worse. |
| `blocked`, `block:<rule>`, `unsolved:root_blocked` | The request was refused, and nothing on this visit changes that. |
| `slider`, `captcha_required...` | An interactive captcha is showing, and no captcha solver that handles it is configured (`solver_kind` says which one would). |
| `no_challenge` | DataDome was detected from its headers alone and the page never moved on (no new cookie, no new document). |

DataDome's slide-to-target slider is dragged onto its target by default. DataDome can answer a drag it does not trust with its hard-block page, which it then shows this IP for a while; to stop at that slider instead (`reason: 'slider'`) and retry later, turn dragging off with `scrapling.engines.antibot.get('datadome').drag_simple_slider = False`.
| `still_detected` | The vendor's handler finished, but its challenge or block is still on the page. |
| `timeout` | The deadline arrived first. |

!!! note

    A `solved` vendor does not guarantee that the content you want is on the page: always check the page itself as you normally would.

## Headless hardening

Bot managers read the browser from inside their own cross-site iframes, and headless Chrome under Playwright leaks there: the iframe sees an 800x600 screen under a page that claims 1920x1080, the window has no toolbar, and the user agent says `HeadlessChrome`. With `solve_antibot=True`, Scrapling makes a headless browser describe one coherent machine:

- **On every page, before it navigates:** one display's size, work area and colour depth, a window with a toolbar, and the browser's own user agent with full client hints, sent through CDP to the page and to every iframe and worker before they run (no init scripts, nothing in the page's JavaScript).
- **At launch, for a session created with `solve_antibot=True` in headless mode:** the launch switches that pin the window to the screen origin, force an sRGB profile and hide scrollbars are replaced by that display's screen, a normal window size and colour profile, and the context drops viewport emulation (`no_viewport`). This is applied when the browser starts, so it also covers launch options you edited yourself.

The display is a common one for the platform (a 14" MacBook Pro screen on macOS, a 1080p screen elsewhere), not your own: the frames only need to agree with each other, and pages should not learn your monitors, their layout or your menu bar and Dock settings. To describe your real displays instead (every monitor, with its real geometry), call this before the session starts:

```python
from scrapling.engines.antibot.headless import set_display_policy

set_display_policy('host')
```

The launch part is skipped for `headless=False`, for `cdp_url`, and when you set `viewport`, `no_viewport`, `screen` or `device_scale_factor` in `additional_args`. Pages read by the handlers are read in a fresh isolated world without a user gesture, so the page's own scripts can't tell that anything was read.

## Captcha solvers

Some challenges need a human or a paid solving service: a DataDome slider, an AWS WAF image grid, a Turnstile gate that a click does not clear, the hCaptcha on an Imperva incident page. Pass a `SolverRouter` as `captcha_solver`, and the handlers will hand those to the providers you configured:

```python
from scrapling.fetchers import StealthySession
from scrapling.engines.antibot.solvers import SolverRouter

router = SolverRouter.from_config({
    'capmonster': 'CAPMONSTER_KEY',   # token kinds first (Turnstile, reCAPTCHA, hCaptcha, GeeTest, AWS WAF)
    'capsolver': 'CAPSOLVER_KEY',     # image and slider recognition first
    '2captcha': '2CAPTCHA_KEY',       # the broadest coverage, used as fallback
    'max_solves_per_fetch': 2,
    'max_cost_usd_per_fetch': 0.01,
})

with StealthySession(solve_antibot=True, captcha_solver=router) as session:
    page = session.fetch('https://protected-site.com/catalogue')
    print(page.meta['antibot'].get('solver'))  # attempts, providers and the estimated cost
```

Any one key is enough. `from_config` returns `None` when no key is set, so you can pass its result straight through.

- **Routing:** each challenge type has an ordered list of providers. If a provider fails, the next one is tried. Auth and balance errors put a provider on a cooldown for 10 minutes, and rate limits for 10 to 300 seconds. Change the order with `routes`, for example `{'turnstile': ['2captcha', 'capmonster']}`.
- **Caps:** `max_solves_per_fetch` (2 by default), `max_attempts_per_solve` (3), `max_cost_usd_per_fetch`, `max_cost_usd_total` and `timeout`. Each request gets a fresh scope of the router, so the per-fetch caps apply to each page. To keep one budget across retries of the same page, pass `router.scope()` instead of the router: a scope is used as it is.
- **Spend is counted when a task is sent**, at the provider's estimated price, and replaced by the provider's own figure when it reports one. A task abandoned at the deadline, cancelled or lost to network errors may still be billed, so it still counts; only failures providers do not bill (a refused task, an unsolvable challenge, no free worker) are refunded. A provider that fails after accepting a task is not followed by another one for the same challenge, and with a USD cap set a provider with no price for a kind is not used for it.
- **What providers see:** for token tasks, the site key and the page's address cut to `scheme://host/path` (never its query string, fragment or credentials); for recognition tasks (sliders, image grids), only the images and the question.
- **No proxy is ever sent to a provider** unless you set `allow_proxy=True`. Tasks run on the provider's own network (the "proxyless" task types).
- **Experimental kinds** (DataDome sliders and Cloudflare challenge-page tokens) stay off unless you set `experimental=True`.
- **Keys and tokens** are never logged, never included in `repr()` and never put in `response.meta`. Provider error messages that echo a key are redacted.

The providers' task types and the full option list are documented in `scrapling/engines/antibot/solvers/`.

## Using the pieces directly

The detectors are plain functions over a `Signal`, so you can run them on any response:

```python
from scrapling.engines.antibot import Signal, detect, get

detection = detect(Signal(url=page.url, status=page.status, headers=dict(page.headers), html=page.html_content))
if detection:
    print(detection.vendor, detection.kind, detection.rule)
```

In your own `page_action`, `get(vendor).solve(page, detection, deadline=..., solver=None, log=...)` runs one vendor's handler on a live async page, and `scrapling.engines.antibot.base.page_signal(page)` builds the `Signal` for you.

## Limits

- **Akamai** often blocks a headless browser at the edge from its fingerprint or the IP's reputation, even with valid sensor cookies. The handler reports those blocks quickly rather than waiting them out.
- **DataDome** answers some IPs with a hard ban (`t=bv`). The handler stops at once, and retrying from the same IP doesn't help.
- **GeeTest** on Imperva incident pages is reported as `captcha_required:geetest`.
- Sites change their protection without notice, so treat the vendor handlers as a best effort and check the content you got.

Parts of the handlers are derived from Averyy/wafer, Crawl4AI, Hyper Solutions' hyper-sdk-py, SeleniumBase and xKiian/awswaf; see the `NOTICE` file for the attributions.
