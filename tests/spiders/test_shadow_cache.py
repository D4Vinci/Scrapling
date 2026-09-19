from pathlib import Path

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.cache import ResponseCacheManager


@pytest.mark.asyncio
async def test_cache_preserves_shadow_wrappers(tmp_path: Path) -> None:
    content = '<!DOCTYPE html><html><body><p id="host"><shadow-root><!--kept--><section>FIRST<div id="nested"><shadow-root><p>SECOND</p></shadow-root></div>LAST</section></shadow-root></p></body></html>'
    response = Response("https://shadow.test/", content, 200, "OK", {}, {}, {})
    assert response.css("#host > shadow-root > section")
    cache = ResponseCacheManager(tmp_path)
    await cache.put(b"shadow", response)
    restored = await cache.get(b"shadow")
    assert restored is not None
    assert restored.body == response.body == content.encode()
    assert restored.css("#host > shadow-root > section")
    assert restored.css("#nested > shadow-root > p::text").get() == "SECOND"
    assert restored.css("#host")[0].get_all_text(separator="|", strip=True) == "FIRST|SECOND|LAST"
    assert not restored.xpath("//comment()")
    assert "<!--kept-->" in restored.body.decode()
