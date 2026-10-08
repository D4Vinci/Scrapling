"""Detection on what a browser holds after a navigation: the serialised DOM, the main document's status and headers,
the site's cookie jar and the child frame URLs.

The cases mirror pages seen from a residential connection in October 2026 (statuses, vendor headers, cookie names,
frame hosts, titles and page sizes as measured; page text and identifiers are made up). The negative cases are real
content pages from protected sites: they load the vendor's sensor, carry its cookies and sometimes its headers, and
must not be detected.
"""

import pytest

from scrapling.engines.antibot import Signal, detect, detect_all

# About 4,700 characters of visible text: a content page, not a gate.
CONTENT = "<main>" + "<p>Listing 42: a three bedroom flat near the park, with prices, photos and a long description.</p>" * 50 + "</main>"


def html(title: str, body: str, head: str = "") -> str:
    return f"<!DOCTYPE html><html><head><title>{title}</title>{head}</head><body>{body}</body></html>"


def dd_page(site: str, rt: str, t: str = "fe") -> str:
    """DataDome's block page as the browser serialises it before the iframe is attached."""
    return html(
        site,
        '<p id="cmsg">Please enable JS and disable any ad blocker</p>'
        f"<script data-cfasync=\"false\">var dd={{'rt':'{rt}','cid':'AHrlqAAAAAMA0x','hsh':'0B4B2B','t':'{t}','s':48291,"
        "'e':'0f1e2d','host':'geo.captcha-delivery.com','cookie':'abc'}</script>"
        f'<script data-cfasync="false" src="https://ct.captcha-delivery.com/{rt}.js"></script>',
    )


DD_CAPTCHA_FRAME = "https://geo.captcha-delivery.com/captcha/?initialCid=AHrl&hash=0B4B2B&cid=x&t=fe&referer=https%3A%2F%2Fwww.example.com%2F&s=48291&e=0f1e2d&dm=cd"
DD_DEVICE_FRAME = "https://geo.captcha-delivery.com/interstitial/?initialCid=AHrl&hash=0B4B2B&cid=x&s=48291&e=0f1e2d&b=1"

AKAMAI_ACCESS_DENIED = html(
    "Access Denied",
    '<h1>Access Denied</h1>You don\'t have permission to access "http&#58;&#47;&#47;www&#46;example&#46;com&#47;search" '
    "on this server.<p>Reference&#32;#18&#46;5d3a1c17&#46;1791428512&#46;1b2c3d4e</p>"
    "<p>https&#58;&#47;&#47;errors&#46;edgesuite&#46;net&#47;18&#46;5d3a1c17&#46;1791428512&#46;1b2c3d4e</p>",
)
AKAMAI_SEC_CPT = (
    '<html><head></head><body><script type="text/javascript" src="/aBc1/dEf2/gHi3?v=4f2a8c1e-1d2b-4c3d-9e8f-0a1b2c3d4e5f'
    '&amp;t=130700734"></script><div id="sec-if-cpt-container" role="main" style="display: none"><div class="behavioral-content">'
    '<div id="sec-bc-text-container"></div><div id="sec-bc-tile-parent"><div id="sec-bc-tile-container"></div></div>'
    '<p class="scf-akamai-protected-by">Powered and protected by</p></div></div></body></html>'
)
KASADA_BOOT = (
    "<html><head></head><body><script>window.KPSDK={};KPSDK.now=typeof performance!=='undefined'&&performance.now?"
    "performance.now.bind(performance):Date.now.bind(Date);KPSDK.start=KPSDK.now();</script>"
    '<script src="/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/@SCRIPT@?x-kpsdk-v=j-1.2.3&amp;r=1">'
    "</script></body></html>"
)
AWS_CHALLENGE = html(
    "",
    '<div id="challenge-container"></div><script>window.awsWafCookieDomainList = [];'
    'window.gokuProps = {"key":"AQIDAHjcYu/GjX+QlghicBgQ/7bFaQZ+m5FKCMDnO+vTbNg96AE=","iv":"CgAHbCe2GgAAAAAA",'
    '"context":"rFz0cN2s3k8u1Q=="};</script>'
    '<script src="https://3f38f7f4f368.83dd1d2e.us-east-1.token.awswaf.com/3f38f7f4f368/e1fcfc58118e/challenge.js"></script>',
)
AWS_CAPTCHA = html(
    "Ich bin kein Roboter - Example",
    '<h1>Ich bin kein Roboter</h1><p>Bitte lösen Sie das Rätsel, um fortzufahren.</p><div id="captcha-container"></div>'
    '<script src="https://ab12cd34ef56.edge.captcha-sdk.awswaf.com/ab12cd34ef56/jsapi.js"></script>'
    '<script src="https://ab12cd34ef56.eu-central-1.captcha-sdk.awswaf.com/ab12cd34ef56/captcha.js"></script>'
    '<script>AwsWafCaptcha.renderCaptcha(document.getElementById("captcha-container"), '
    '{apiKey: "LkSYJz6ApiKeyExample0123456789==", onSuccess: captchaExampleSuccessFunction});</script>',
)
IMPERVA_INCIDENT = (
    '<html style="height:100%"><head><meta name="ROBOTS" content="NOINDEX, NOFOLLOW"></head><body style="margin:0px;height:100%">'
    '<iframe id="main-iframe" src="/_Incapsula_Resource?SWUDNSAI=31&amp;xinfo=10-12345678-0%200NNN&amp;incident_id=605000'
    '123-456&amp;edet=12&amp;cinfo=04000000&amp;rpinfo=0&amp;mth=GET" frameborder="0" width="100%" height="100%">'
    "Request unsuccessful. Incapsula incident ID: 605000123-456</iframe></body></html>"
)
IMPERVA_PARDON = html(
    "Pardon Our Interruption",
    "<h1>Pardon Our Interruption</h1><p>As you were browsing something about your browser made us think you were a bot."
    '</p><div id="interstitial-inprogress"></div><script>window.reeseSkipExpirationCheck = true;</script>'
    '<script src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3&amp;ns=2"></script>',
)
PX_HOLD = html(
    "Robot or human?",
    '<h1>Robot or human?</h1><p>Activate and hold the button to confirm that you\'re human. Thank You!</p>'
    '<div id="px-captcha"></div><script>window._pxAppId = "PXu6b0qd2S";window._pxJsClientSrc = "/px/PXu6b0qd2S/init.js";'
    '</script><script src="https://captcha.px-cdn.net/PXu6b0qd2S/captcha.js?a=c&amp;m=0"></script>',
)

CASES = [
    # ---------------------------------------------------------------- DataDome
    pytest.param(
        dict(
            url="https://www.example-news.com/world/",
            status=401,
            headers={"Server": "CloudFront", "X-DataDome": "protected", "X-DD-B": "3", "X-DataDome-CID": "AHrl"},
            cookies={"datadome": "AHrlqAAAAAMA"},
            html=dd_page("example-news.com", "i"),
            frame_urls=[DD_CAPTCHA_FRAME],
        ),
        ("datadome", "captcha", "dd.frame_captcha"),
        id="datadome-device-check-escalated-to-captcha",
    ),
    pytest.param(
        dict(
            url="https://www.example-reviews.com/categories/crm",
            status=403,
            headers={"server": "cloudflare", "cf-ray": "a46f6ae20b04236d-SJC", "x-datadome": "protected", "x-dd-b": "259"},
            cookies={"__cf_bm": "x", "cf_clearance": "x", "datadome": "x"},
            html=dd_page("example-reviews.com", "i").replace(
                "</head>", '<script src="/cdn-cgi/challenge-platform/scripts/jsd/main.js"></script></head>'
            ),
            frame_urls=[DD_DEVICE_FRAME],
        ),
        ("datadome", "device_check", "dd.frame_device"),
        id="datadome-device-check-behind-cloudflare-edge",
    ),
    pytest.param(
        dict(
            url="https://www.example-homes.com/venta/madrid/",
            status=403,
            headers={"server": "DataDome", "x-datadome": "protected", "x-dd-b": "1"},
            cookies={"datadome": "x"},
            html=dd_page("example-homes.com", "c"),
            frame_urls=[],
        ),
        ("datadome", "captcha", "dd.captcha"),
        id="datadome-captcha-page-before-frame",
    ),
    pytest.param(
        dict(
            url="https://www.example-toys.com/category/plush",
            status=403,
            headers={"x-iinfo": "10-123-0 0NNN", "x-cdn": "Imperva", "x-datadome": "protected", "x-dd-b": "3"},
            cookies={"datadome": "x", "incap_ses_605_2682446": "x", "visid_incap_2682446": "x", "reese84": "x"},
            html=dd_page("example-toys.com", "i"),
            frame_urls=[DD_CAPTCHA_FRAME],
        ),
        ("datadome", "captcha", "dd.frame_captcha"),
        id="datadome-behind-imperva-edge",
    ),
    pytest.param(
        dict(
            url="https://www.example.com/",
            status=403,
            headers={"x-datadome": "protected"},
            cookies={"datadome": "x"},
            html=dd_page("example.com", "c", t="bv"),
            frame_urls=[DD_CAPTCHA_FRAME.replace("t=fe", "t=bv")],
        ),
        ("datadome", "ban", "dd.hard"),
        id="datadome-banned-visitor",
    ),
    pytest.param(
        dict(
            url="https://www.example.com/listing/1",
            status=200,
            headers={"x-datadome": "protected"},
            cookies={"datadome": "x"},
            html=html("Listing", CONTENT, '<script src="https://js.datadome.co/tags.js"></script>'),
            frame_urls=[DD_CAPTCHA_FRAME],
        ),
        ("datadome", "captcha", "dd.frame_captcha"),
        id="datadome-captcha-over-a-served-page",
    ),
    pytest.param(
        dict(
            url="https://api.example.com/v1/search",
            status=403,
            headers={"x-datadome": "protected", "content-type": "application/json"},
            cookies={"datadome": "x"},
            html='<html><head></head><body><pre>{"url":"https:\\/\\/geo.captcha-delivery.com\\/interstitial\\/?initialCid=AHrl'
            '&hash=0B&cid=x&s=1&e=00"}</pre></body></html>',
            frame_urls=[],
        ),
        ("datadome", "device_check", "dd.json"),
        id="datadome-json-answer-to-an-api-call",
    ),
    # ---------------------------------------------------------------- Cloudflare
    pytest.param(
        dict(
            url="https://www.example.com/",
            status=403,
            headers={"server": "cloudflare", "cf-mitigated": "challenge"},
            cookies={"__cf_bm": "x"},
            html=html("Example Access Info", "<p>Checking</p><script>window._cf_chl_opt = {cType: 'managed'};</script>"),
            frame_urls=["https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2/av0/rcv/abc/"],
        ),
        ("cloudflare", "challenge", "cf.challenge"),
        id="cloudflare-managed-challenge",
    ),
    pytest.param(
        dict(
            url="https://www.example.fr/",
            status=403,
            headers={"server": "cloudflare"},
            cookies={},
            html="<html><head><title>Un instant…</title></head><body><script>cType: 'interactive'</script></body></html>",
            frame_urls=[],
        ),
        ("cloudflare", "challenge", "cf.interstitial"),
        id="cloudflare-localized-interstitial-without-header",
    ),
    pytest.param(
        dict(
            url="https://www.example.com/login",
            status=200,
            headers={"server": "cloudflare"},
            cookies={},
            html=html(
                "Verify",
                '<h1>One more step</h1><form><div class="cf-turnstile" data-sitekey="0x4AAAAAAAExampleKey" data-action="login" '
                'data-callback="onVerified"></div></form>',
                '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>',
            ),
            frame_urls=[],
        ),
        ("cloudflare", "captcha", "cf.turnstile"),
        id="cloudflare-turnstile-gate",
    ),
    pytest.param(
        dict(
            url="https://www.example-travel.com/",
            status=429,
            headers={"server": "cloudflare", "x-kpsdk-ct": "0abc", "x-kpsdk-r": "1-AAAA"},
            cookies={"KP_UIDz": "x"},
            html=KASADA_BOOT.replace("@SCRIPT@", "ips.js"),
            frame_urls=[],
        ),
        ("kasada", "challenge", "kasada.header"),
        id="kasada-429-behind-cloudflare-is-not-a-rate-limit",
    ),
    # ---------------------------------------------------------------- Akamai
    pytest.param(
        dict(
            url="https://www.example-diy.com/search?q=drill",
            status=403,
            headers={"akamai-grn": "0.1c3a5d17.1791428512.1b2c3d4e"},
            cookies={"_abck": "ABC~-1~YAAQ~-1~-1~-1", "bm_sz": "x", "ak_bmsc": "x"},
            html=AKAMAI_ACCESS_DENIED,
            frame_urls=[],
        ),
        ("akamai", "block", "akamai.block"),
        id="akamai-access-denied",
    ),
    pytest.param(
        dict(
            url="https://www.example-diy.com/s/drill",
            status=403,
            headers={"server": "AkamaiGHost", "akamai-grn": "0.1"},
            cookies={"_abck": "ABC~-1~YAAQ~-1~-1~-1", "bm_sz": "x", "bm_s": "x", "bm_so": "x", "AKA_A2": "A"},
            html=html(
                "Error Page",
                '<div class="hdr">Home Improvement</div><main class="err"><div class="msg">Oops!! Something went wrong. '
                'Please refresh page</div><button id="refreshBtn">Refresh</button></main>',
            ),
            frame_urls=[],
        ),
        ("akamai", "block", "akamai.edge_block"),
        id="akamai-error-page-after-sensor",
    ),
    pytest.param(
        dict(
            url="https://www.example-store.com/shop/jeans",
            status=200,
            headers={"akamai-grn": "0.1", "x-akamai-transformed": "9 828 0 pmb=mtoe,1mrum,1"},
            cookies={"_abck": "ABC~-1~YAAQ~-1~-1~-1", "bm_sz": "x", "ak_bmsc": "x", "bm_sv": "x"},
            html=AKAMAI_SEC_CPT,
            frame_urls=[],
        ),
        ("akamai", "challenge", "akamai.sec_cpt_html"),
        id="akamai-sec-cpt-served-with-200",
    ),
    pytest.param(
        dict(
            url="https://www.example-air.com/",
            status=200,
            headers={},
            cookies={"bm_so": "x", "bm_sz": "x"},
            html='<html><head><title>Challenge Page</title><script src="/.well-known/sbsd/Ab3d?v=4f2a8c1e-1d2b-4c3d-9e8f-0a1b2c3d4e5f'
            '&amp;t=1791428512"></script></head><body></body></html>',
            frame_urls=[],
        ),
        ("akamai", "challenge", "akamai.sbsd_html"),
        id="akamai-sbsd-active-page",
    ),
    # ---------------------------------------------------------------- Kasada
    pytest.param(
        dict(
            url="https://www.example-realty.com.au/buy/list-1",
            status=429,
            headers={"x-kpsdk-ct": "0abc", "x-kpsdk-r": "1-AAAA"},
            cookies={"KP_UIDz": "x", "KP_UIDz-ssn": "x"},
            html=KASADA_BOOT.replace("@SCRIPT@", "ips.js"),
            frame_urls=[],
        ),
        ("kasada", "challenge", "kasada.header"),
        id="kasada-429",
    ),
    pytest.param(
        dict(
            url="https://www.example-realty.com.au/buy/list-1",
            status=None,
            headers={},
            cookies={"KP_UIDz": "x"},
            html=KASADA_BOOT.replace("@SCRIPT@", "p.js"),
            frame_urls=[],
        ),
        ("kasada", "challenge", "kasada.page"),
        id="kasada-recheck-without-status",
    ),
    # ---------------------------------------------------------------- HUMAN / PerimeterX
    pytest.param(
        dict(
            url="https://www.example-mart.com/search?q=headphones",
            status=200,
            headers={"x-akamai-transformed": "0 - 0 -"},
            cookies={"bm_mi": "x", "bm_sv": "x", "_pxhd": "x"},
            html=PX_HOLD,
            frame_urls=[],
        ),
        ("perimeterx", "captcha", "px.hold"),
        id="perimeterx-press-and-hold-served-with-200-on-akamai-edge",
    ),
    pytest.param(
        dict(
            url="https://www.example-mart.com/search?q=headphones",
            status=403,
            headers={"akamai-grn": "0.1"},
            cookies={"_abck": "x", "bm_sz": "x", "_pxhd": "x"},
            html=PX_HOLD.replace("Robot or human?", "Access to this page has been denied"),
            frame_urls=[],
        ),
        ("perimeterx", "captcha", "px.hold"),
        id="perimeterx-403-on-akamai-site-belongs-to-perimeterx",
    ),
    # ---------------------------------------------------------------- Imperva
    pytest.param(
        dict(
            url="https://www.example-toys.co.uk/toys/c/1",
            status=200,
            headers={"x-iinfo": "10-1-0 0NNN"},
            cookies={"incap_ses_605_2483049": "x", "visid_incap_2483049": "x", "reese84": "x"},
            html=IMPERVA_INCIDENT,
            frame_urls=["https://www.example-toys.co.uk/_Incapsula_Resource?SWUDNSAI=31&xinfo=10-1-0&incident_id=605000123-456&edet=12"],
        ),
        ("imperva", "captcha", "imperva.incident"),
        id="imperva-incident-frame",
    ),
    pytest.param(
        dict(
            url="https://www.example-toys.co.uk/toys/c/1",
            status=200,
            headers={"x-iinfo": "10-1-0 0NNN"},
            cookies={"incap_ses_605_2483049": "x", "visid_incap_2483049": "x"},
            html=IMPERVA_PARDON,
            frame_urls=[],
        ),
        ("imperva", "challenge", "imperva.interstitial"),
        id="imperva-reese84-interstitial",
    ),
    # ---------------------------------------------------------------- AWS WAF
    pytest.param(
        dict(
            url="https://www.example-films.com/find/?q=matrix",
            status=202,
            headers={"x-amzn-waf-action": "challenge", "server": "Server"},
            cookies={},
            html=AWS_CHALLENGE,
            frame_urls=[],
        ),
        ("aws_waf", "challenge", "aws.challenge"),
        id="aws-waf-202-challenge",
    ),
    pytest.param(
        dict(url="https://www.example-films.com/", status=202, headers={}, cookies={}, html=AWS_CHALLENGE, frame_urls=[]),
        ("aws_waf", "challenge", "aws.challenge_page"),
        id="aws-waf-challenge-page-without-header",
    ),
    pytest.param(
        dict(url="https://www.example-immo.de/Suche/", status=401, headers={"server": "CloudFront"}, cookies={}, html=AWS_CAPTCHA, frame_urls=[]),
        ("aws_waf", "captcha", "aws.captcha_page"),
        id="aws-waf-captcha-page-with-site-status",
    ),
]

CONTENT_PAGES = [
    pytest.param(
        dict(
            url="https://www.example-homes.com/austin-tx/",
            status=200,
            headers={"server": "CloudFront"},
            cookies={"_px3": "x", "_pxvid": "x", "zguid": "x"},
            html=html(
                "Austin TX Homes For Sale",
                CONTENT,
                '<script>window._pxAppId = "PXHYx10rg3";</script><script src="//client.px-cloud.net/PXHYx10rg3/main.min.js"></script>',
            ),
            frame_urls=["https://www.google.com/recaptcha/api2/aframe"],
        ),
        id="perimeterx-sensor-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-mart.com/search?q=headphones",
            status=200,
            headers={"x-akamai-transformed": "0 - 0 -"},
            cookies={"_px3": "x", "_pxhd": "x", "ak_bmsc": "x", "bm_sv": "x", "TS012768cf": "x"},
            html=html(
                "headphones - Example Mart",
                CONTENT,
                '<script src="/akam/13/7c6f8d2e" defer></script><script>window._pxAppId="PXu6b0qd2S";</script>'
                '<link rel="preconnect" href="https://captcha.px-cdn.net">',
            ),
            frame_urls=[],
        ),
        id="akamai-and-perimeterx-sensors-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-films.com/find/?q=matrix",
            status=200,
            headers={"server": "Server"},
            cookies={"aws-waf-token": "x"},
            html=html(
                "Find - Example Films",
                CONTENT,
                '<script src="https://0a1b2c3d4e5f.edge.sdk.awswaf.com/0a1b2c3d4e5f/9f8e7d6c5b4a/jsapi.js"></script>'
                "<script>AwsWafIntegration.fetch('/api');</script>",
            ),
            frame_urls=[],
        ),
        id="aws-waf-sdk-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-films.com/app",
            status=None,
            headers={},
            cookies={"aws-waf-token": "x"},
            html=html(
                "Example App",
                '<div id="root"></div>',
                '<script src="https://0a1b2c3d4e5f.edge.sdk.awswaf.com/0a1b2c3d4e5f/9f8e7d6c5b4a/jsapi.js"></script>'
                "<script>AwsWafIntegration.getToken();</script>",
            ),
            frame_urls=[],
        ),
        id="aws-waf-sdk-on-a-near-empty-app-shell-recheck",
    ),
    pytest.param(
        dict(
            url="https://www.example-realty.com.au/buy/list-1",
            status=200,
            headers={"x-kpsdk-ct": "0abc", "x-kpsdk-r": "1-AAAA"},
            cookies={"KP_UIDz": "x", "KP_UIDz-ssn": "x"},
            html=html(
                "Real Estate for Sale",
                CONTENT,
                '<script src="/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js"></script>'
                "<script>KPSDK.configure([{protocol:'https:',method:'POST',domain:'example',path:'/graphql'}]);</script>",
            ),
            frame_urls=[],
        ),
        id="kasada-sdk-and-headers-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-security.com/",
            status=200,
            headers={"x-iinfo": "10-1-0 NNNN", "x-cdn": "Imperva"},
            cookies={"incap_ses_363_2439": "x", "visid_incap_2439": "x", "nlbi_2439": "x", "reese84": "x"},
            html=html(
                "Cyber Security Leader",
                CONTENT,
                '<script src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3&amp;ns=1"></script>',
            ),
            frame_urls=[],
        ),
        id="imperva-loader-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-defence.com/en/markets",
            status=404,
            headers={"x-iinfo": "10-1-0 NNNN", "x-cdn": "Imperva", "server": "nginx"},
            cookies={"incap_ses_605_3201330": "x"},
            html=html("404 | Example Group", CONTENT, '<script src="/_Incapsula_Resource?SWJIYLWA=719d34d3&amp;ns=3"></script>'),
            frame_urls=[],
        ),
        id="imperva-site-404",
    ),
    pytest.param(
        dict(
            url="https://www.example-electronics.com/site/searchpage.jsp?st=laptop",
            status=200,
            headers={"akamai-grn": "0.1", "x-akamai-transformed": "0 - 0 -"},
            cookies={"_abck": "ABC~0~YAAQ~-1~-1~-1", "bm_sz": "x", "ak_bmsc": "x", "bm_s": "x"},
            html=html("laptop - Example Electronics", CONTENT, '<script src="/akam/13/3d5a9c1e" defer></script>'),
            frame_urls=[],
        ),
        id="akamai-sensor-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-paper.com/section/technology",
            status=200,
            headers={"server": "envoy", "x-datadome": "protected"},
            cookies={"nyt-b-sid": "x"},
            html=html("Technology - The Example Times", CONTENT),
            frame_urls=[],
        ),
        id="datadome-header-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example-home.com/keyword.php?keyword=sofa",
            status=200,
            headers={"server": "cloudflare", "cf-ray": "a46f6ae20b04236d-SJC"},
            cookies={"datadome": "x", "_px3": "x", "_pxhd": "x", "__cf_bm": "x"},
            html=html(
                "Sofas & Couches",
                CONTENT,
                '<script src="https://js.datadome.co/tags.js" async></script><script>window._pxAppId="PXabcdef12";</script>'
                '<script src="/cdn-cgi/challenge-platform/scripts/jsd/main.js"></script>',
            ),
            frame_urls=[],
        ),
        id="datadome-perimeterx-cloudflare-on-content",
    ),
    pytest.param(
        dict(
            url="https://www.example.com/cloudflare-challenge",
            status=200,
            headers={"server": "cloudflare", "cf-mitigated": "challenge"},
            cookies={"cf_clearance": "x"},
            html=html(
                "Cloudflare Challenge - Example",
                "<h2>You bypassed the Cloudflare challenge! :D</h2>",
                '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>',
            ),
            frame_urls=[],
        ),
        id="cloudflare-solved-page-with-stale-challenge-header",
    ),
    pytest.param(
        dict(
            url="https://www.example.com/account/login",
            status=200,
            headers={"server": "cloudflare"},
            cookies={},
            html=html(
                "Sign in",
                CONTENT + '<form><div class="cf-turnstile" data-sitekey="0x4AAAAAAAExampleKey"></div></form>',
                '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>',
            ),
            frame_urls=["https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2/av0/rcv/abc/"],
        ),
        id="cloudflare-turnstile-on-a-content-form",
    ),
    pytest.param(
        dict(
            url="https://www.example-outdoor.com/us/en/shop/men/",
            status=404,
            headers={"server": "cloudflare", "cf-ray": "a46f6ae20b04236d-SJC"},
            cookies={"__cf_bm": "x"},
            html=html("404 Not Found | Example", CONTENT),
            frame_urls=[],
        ),
        id="cloudflare-site-404",
    ),
]


@pytest.mark.parametrize("signal, expected", CASES)
def test_browser_page_detection(signal, expected):
    found = detect(Signal(**signal))
    assert found is not None
    assert (found.vendor, found.kind, found.rule) == expected


@pytest.mark.parametrize("signal", CONTENT_PAGES)
def test_content_pages_are_not_detected(signal):
    assert detect_all(Signal(**signal)) == []


def test_layered_vendors_report_only_the_live_challenge():
    """Imperva's edge in front of a DataDome check: the DataDome page is the challenge, Imperva steps aside."""
    signal = Signal(**CASES[3].values[0])
    assert [d.vendor for d in detect_all(signal)] == ["datadome"]


def test_details_carry_what_the_solvers_need():
    dd = detect(Signal(**CASES[0].values[0]))
    assert dd.details["dd"]["rt"] == "i" and dd.details["dd"]["cid"] == "AHrlqAAAAAMA0x"
    assert dd.details["frame_url"] == DD_CAPTCHA_FRAME
    assert dd.details["action"] == 3 and dd.details["invisible"] is False

    turnstile = detect(Signal(**CASES[9].values[0]))
    assert turnstile.details["sitekey"] == "0x4AAAAAAAExampleKey"
    assert turnstile.details["action"] == "login" and turnstile.details["callback"] == "onVerified"

    akamai = detect(Signal(**CASES[11].values[0]))
    assert akamai.details["reference"] == "18.5d3a1c17.1791428512.1b2c3d4e"
    assert akamai.details["abck"] == "invalid"

    kasada = detect(Signal(**CASES[15].values[0]))
    assert kasada.details["flow"] == "ips"
    assert kasada.details["script_url"].startswith("/149e9513-01fa-4fb0-aad4-566afd725d1b/")
    assert "&amp;" not in kasada.details["script_url"]

    aws = detect(Signal(**CASES[21].values[0]))
    assert aws.details["aws_iv"] == "CgAHbCe2GgAAAAAA"
    assert aws.details["aws_challenge_script"].endswith("/challenge.js")

    captcha = detect(Signal(**CASES[23].values[0]))
    assert captcha.details["aws_api_key"] == "LkSYJz6ApiKeyExample0123456789=="
    assert captcha.details["aws_captcha_script"].endswith("/captcha.js")
