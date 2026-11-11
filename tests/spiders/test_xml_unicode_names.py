from xml.etree import ElementTree  # nosec B405 - reads only files produced by this test

import pytest

from scrapling.spiders.result import ItemList


@pytest.mark.parametrize("key", ["area_m\u00b2", "volume_m\u00b3", "\u00aa", "x\u00ba"])
def test_xml_export_rewrites_non_xml_unicode_name_characters(tmp_path, key):
    path = tmp_path / "items.xml"
    ItemList([{key: "value"}]).to_xml(path)
    root = ElementTree.parse(path).getroot()  # nosec B314 - trusted local output
    child = root[0][0]
    assert child.text == "value"
    assert child.attrib["name"] == key


@pytest.mark.parametrize("key", ["\u9762\u79ef", "caf\u00e9", "normal_key"])
def test_xml_export_preserves_valid_unicode_names(tmp_path, key):
    path = tmp_path / "items.xml"
    ItemList([{key: "value"}]).to_xml(path)
    root = ElementTree.parse(path).getroot()  # nosec B314 - trusted local output
    assert root[0][0].tag == key
    assert root[0][0].text == "value"
    assert "name" not in root[0][0].attrib
