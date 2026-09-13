import pytest

from scrapling.core._types import extraction_types
from scrapling.core.shell import Convertor
from scrapling.engines.toolbelt.custom import Response
from scrapling.parser import Selector
from tests.fetchers.test_shadow_order import extract


HIDDEN_ATTRIBUTES = (
    ('style="display: none"', "style", "display: none"),
    ('style="visibility: hidden"', "style", "visibility: hidden"),
    ('aria-hidden="true"', "aria-hidden", "true"),
    ("hidden", "hidden", ""),
)


def check_clean_output(response: Response, visible: tuple[str, ...], hidden: tuple[str, ...]) -> None:
    kinds: tuple[extraction_types, ...] = ("markdown", "html", "text")
    outputs = [response.markdown()]
    outputs.extend("".join(Convertor._extract_content(response, kind, main_content_only=True)) for kind in kinds)
    for output in outputs:
        positions = [output.index(value) for value in visible]
        assert positions == sorted(positions)
        assert all(value not in output for value in hidden)


@pytest.mark.asyncio
@pytest.mark.parametrize(("attrs", "key", "value"), HIDDEN_ATTRIBUTES)
async def test_hidden_slots_keep_attributes_and_assigned_content(attrs: str, key: str, value: str) -> None:
    response = await extract(
        '<html><body><div id="host"><span id="assigned-element" slot="element">HIDDEN-ELEMENT</span>HIDDEN-TEXT<span id="visible-assigned" slot="visible">VISIBLE-ASSIGNED</span></div></body></html>',
        f"""() => {{
            document.querySelector('#host').attachShadow({{mode: 'open'}}).innerHTML = '<article>BEGIN<slot id="element-slot" name="element" class="kept" data-check="element" aria-label="Label" {attrs}>WRONG-ELEMENT</slot>AFTER-ELEMENT<slot id="text-slot" {attrs}>WRONG-TEXT</slot>AFTER-TEXT<slot id="fallback-slot" name="missing" {attrs}><b>HIDDEN-FALLBACK</b>HIDDEN-FALLBACK-TEXT</slot>AFTER-FALLBACK<slot id="visible-slot" name="visible">WRONG-VISIBLE</slot>END</article>';
        }}""",
    )
    body = response.body.decode()
    for parsed in (response, Selector(response.body)):
        assert len(parsed.css("#host > shadow-root > article > slot")) == 4
        for slot_id in ("element-slot", "text-slot", "fallback-slot"):
            assert parsed.css(f"#{slot_id}")[0].attrib[key] == value
        assert dict(parsed.css("#element-slot")[0].attrib) == {
            "id": "element-slot",
            "name": "element",
            "class": "kept",
            "data-check": "element",
            "aria-label": "Label",
            key: value,
        }
        assert parsed.css("#element-slot > #assigned-element::text").get() == "HIDDEN-ELEMENT"
        assert parsed.css("#text-slot::text").get() == "HIDDEN-TEXT"
        assert parsed.css("#fallback-slot > b::text").get() == "HIDDEN-FALLBACK"
        assert parsed.css("#visible-slot > #visible-assigned::text").get() == "VISIBLE-ASSIGNED"
        assert len(parsed.css("#assigned-element, #visible-assigned")) == 2
        assert parsed.css("article")[0].get_all_text(separator="|", strip=True) == (
            "BEGIN|HIDDEN-ELEMENT|AFTER-ELEMENT|HIDDEN-TEXT|AFTER-TEXT|HIDDEN-FALLBACK|"
            "HIDDEN-FALLBACK-TEXT|AFTER-FALLBACK|VISIBLE-ASSIGNED|END"
        )
    assert body.count("HIDDEN-ELEMENT") == body.count("HIDDEN-TEXT") == body.count("VISIBLE-ASSIGNED") == 1
    assert "WRONG-" not in body
    check_clean_output(
        response,
        ("BEGIN", "AFTER-ELEMENT", "AFTER-TEXT", "AFTER-FALLBACK", "VISIBLE-ASSIGNED", "END"),
        ("HIDDEN-ELEMENT", "HIDDEN-TEXT", "HIDDEN-FALLBACK"),
    )
    assert response.body.decode() == body


@pytest.mark.asyncio
@pytest.mark.parametrize("assigned", [False, True])
@pytest.mark.parametrize(("attrs", "key", "value"), HIDDEN_ATTRIBUTES)
async def test_forwarded_hidden_slots_keep_their_boundary(assigned: bool, attrs: str, key: str, value: str) -> None:
    light = '<b id="assigned" slot="hidden">HIDDEN-ASSIGNED</b>' if assigned else ""
    response = await extract(
        f'<html><body><div id="outer">{light}<b slot="visible">VISIBLE-ASSIGNED</b></div></body></html>',
        f"""() => {{
            const root = document.querySelector('#outer').attachShadow({{mode: 'open'}});
            root.innerHTML = '<div id="inner"><slot id="forward-hidden" name="hidden" slot="hidden" {attrs}>HIDDEN-FALLBACK</slot><slot id="forward-visible" name="visible" slot="visible">WRONG-VISIBLE</slot></div>';
            root.querySelector('#inner').attachShadow({{mode: 'open'}}).innerHTML = '<article>BEGIN<slot id="receiver-hidden" name="hidden">WRONG-HIDDEN</slot>MIDDLE<slot id="receiver-visible" name="visible">WRONG-VISIBLE</slot>END</article>';
        }}""",
    )
    hidden = "HIDDEN-ASSIGNED" if assigned else "HIDDEN-FALLBACK"
    body = response.body.decode()
    for parsed in (response, Selector(response.body)):
        assert parsed.css("#receiver-hidden > slot#forward-hidden[slot=hidden]")[0].attrib[key] == value
        assert (
            parsed.css("#receiver-visible > slot#forward-visible[slot=visible] > b::text").get() == "VISIBLE-ASSIGNED"
        )
        assert (
            parsed.css("article")[0].get_all_text(separator="|", strip=True)
            == f"BEGIN|{hidden}|MIDDLE|VISIBLE-ASSIGNED|END"
        )
        assert len(parsed.css("#outer slot")) == 4
        if assigned:
            assert parsed.css("#forward-hidden > #assigned::text").get() == hidden
        else:
            assert parsed.css("#forward-hidden::text").get() == hidden
    assert body.count(hidden) == body.count("VISIBLE-ASSIGNED") == 1
    assert "WRONG-" not in body
    check_clean_output(response, ("BEGIN", "MIDDLE", "VISIBLE-ASSIGNED", "END"), (hidden,))
    assert response.body.decode() == body


@pytest.mark.parametrize("attrs", ["hidden", 'hidden="false"', 'hidden="until-found"'])
def test_boolean_hidden_filter_is_limited_to_slots(attrs: str) -> None:
    html = f"<html><body><p>BEFORE<slot {attrs}>HIDDEN-SLOT</slot>AFTER<span {attrs}>UNCHANGED-HIDDEN</span></p></body></html>"
    response = Response("https://shadow.test/", html, 200, "OK", {}, {}, {})
    check_clean_output(response, ("BEFORE", "AFTER", "UNCHANGED-HIDDEN"), ("HIDDEN-SLOT",))
    assert response.css("slot::text").get() == "HIDDEN-SLOT"
    assert response.css("span::text").get() == "UNCHANGED-HIDDEN"
    assert response.body.decode() == html
