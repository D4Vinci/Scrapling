
If you have issues with the browser installation, such as resource management, we recommend you try the Cloud Browser from [Scrapeless](https://www.scrapeless.com/en/product/scraping-browser) for free!

The usage is straightforward: create an account and [get your API key](https://docs.scrapeless.com/en/scraping-browser/quickstart/getting-started/), then pass it to the `DynamicSession` like this:

```python
from urllib.parse import urlencode

from scrapling.fetchers import DynamicSession

# Configure your browser session
config = {
    "token": "YOUR_API_KEY",
    "sessionName": "scrapling-session",
    "sessionTTL": "300",  # 5 minutes
    "proxyCountry": "ANY",
    "sessionRecording": "false",
}

# Build WebSocket URL
ws_endpoint = f"wss://browser.scrapeless.com/api/v2/browser?{urlencode(config)}"
print('Connecting to Scrapeless...')

with DynamicSession(cdp_url=ws_endpoint, disable_resources=True) as s:
    print("Connected!")
    page = s.fetch("https://httpbin.org/headers", network_idle=True)
    print(f"Page loaded, content length: {len(page.body)}")
    print(page.json())
```
The `DynamicSession` class instance will work as usual, so no further explanation is needed.

However, the Scrapeless Cloud Browser can be configured with proxy options, like the proxy country in the config above, [custom fingerprint](https://docs.scrapeless.com/en/scraping-browser/features/advanced-privacy-anti-detection/custom-fingerprint/) configuration, [captcha solving](https://docs.scrapeless.com/en/scraping-browser/features/advanced-privacy-anti-detection/supported-captchas/), and more.

Check out the [Scrapeless's browser documentation](https://docs.scrapeless.com/en/scraping-browser/quickstart/introduction/) for more details.