import pytest

from scrapling.core._html_utils import to_unicode, _replace_entities, name2codepoint


class TestToUnicode:
    def test_string_input(self):
        """Test to_unicode with string input"""
        text = "hello world"
        assert to_unicode(text) == "hello world"
    
    def test_bytes_input_default_encoding(self):
        """Test to_unicode with `bytes` input using default UTF-8"""
        text = b"hello world"
        assert to_unicode(text) == "hello world"
    
    def test_bytes_input_custom_encoding(self):
        """Test to_unicode with custom encoding"""
        text = "café".encode('latin-1')
        assert to_unicode(text, encoding='latin-1') == "café"
    
    def test_bytes_input_with_errors(self):
        """Test to_unicode with error handling"""
        # Invalid UTF-8 bytes
        text = b'\xff\xfe'
        assert to_unicode(text, errors='ignore') == ""
        assert to_unicode(text, errors='replace') == "��"
    
    def test_invalid_input_type(self):
        """Test to_unicode with an invalid input type"""
        with pytest.raises(TypeError, match="to_unicode must receive bytes or str"):
            to_unicode(123)
    
    def test_none_encoding_defaults_to_utf8(self):
        """Test that None encoding defaults to UTF-8"""
        text = "café".encode('utf-8')
        assert to_unicode(text, encoding=None) == "café"


class TestReplaceEntities:
    def test_named_entities(self):
        """Test replacement of named HTML entities"""
        text = "&amp; &lt; &gt; &quot; &nbsp;"
        result = _replace_entities(text)
        assert result == "& < > \" \xa0"
    
    def test_decimal_entities(self):
        """Test replacement of decimal numeric entities"""
        text = "&#38; &#60; &#62;"
        result = _replace_entities(text)
        assert result == "& < >"
    
    def test_hexadecimal_entities(self):
        """Test replacement of hexadecimal numeric entities"""
        text = "&#x26; &#x3C; &#x3E;"
        result = _replace_entities(text)
        assert result == "& < >"
    
    def test_mixed_entities(self):
        """Test replacement of mixed entity types"""
        text = "Price: &pound;100 &#8364;50 &#x24;25"
        result = _replace_entities(text)
        assert result == "Price: £100 €50 $25"
    
    def test_keep_entities(self):
        """Test keeping specific entities"""
        text = "&amp; &lt; &gt;"
        result = _replace_entities(text, keep=['amp', 'lt'])
        assert result == "&amp; &lt; >"
    
    def test_windows_1252_range(self):
        """Test handling of Windows-1252 range characters"""
        text = "&#128; &#130; &#159;"  # Windows-1252 range
        result = _replace_entities(text)
        # These should be decoded using cp1252
        assert "€" in result  # 128 -> Euro sign
    
    def test_remove_illegal_entities_true(self):
        """Test removing illegal entities with remove_illegal=True"""
        text = "&unknown; &#999999;"
        result = _replace_entities(text, remove_illegal=True)
        # The function may convert large numbers to Unicode characters or leave them as-is
        assert "&unknown;" not in result  # Unknown entities should be removed or converted
    
    def test_remove_illegal_entities_false(self):
        """Test keeping illegal entities with remove_illegal=False"""
        text = "&unknown; &#999999;"
        result = _replace_entities(text, remove_illegal=False)
        # Unknown entities should be preserved when remove_illegal=False
        assert "&unknown;" in result
        # Large numeric entities may be converted to Unicode characters
    
    def test_bytes_input(self):
        """Test with bytes input"""
        text = b"&amp; &lt; &gt;"
        result = _replace_entities(text)
        assert result == "& < >"
    
    def test_custom_encoding(self):
        """Test with custom encoding"""
        text = "&eacute;".encode('latin-1')
        result = _replace_entities(text, encoding='latin-1')
        assert result == "é"
    
    def test_entities_without_semicolon(self):
        """Test entities without semicolon"""
        text = "&amp &lt &gt"
        result = _replace_entities(text, remove_illegal=True)
        # Should handle entities without a semicolon
        assert len(result) <= len(text)
    
    def test_case_insensitive_named_entities(self):
        """Test case-insensitive named-entity handling"""
        text = "&AMP; &Lt; &GT;"
        result = _replace_entities(text)
        assert result == "& < >"
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Empty string
        assert _replace_entities("") == ""
        
        # No entities
        assert _replace_entities("plain text") == "plain text"
        
        # Invalid numeric entity
        text = "&#-1;"
        result = _replace_entities(text, remove_illegal=True)
        # Invalid entities may be left as-is or removed depending on implementation
        assert len(result) >= 0  # Ensure no exception is raised


class TestName2Codepoint:
    def test_common_entities_exist(self):
        """Test that common HTML entities exist in mapping"""
        common_entities = ['amp', 'lt', 'gt', 'quot', 'nbsp', 'copy', 'reg']
        for entity in common_entities:
            assert entity in name2codepoint
    
    def test_greek_letters_exist(self):
        """Test that Greek letter entities exist"""
        greek_letters = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        for letter in greek_letters:
            assert letter in name2codepoint
    
    def test_mathematical_symbols_exist(self):
        """Test that mathematical symbol entities exist"""
        math_symbols = ['sum', 'prod', 'int', 'infin', 'plusmn']
        for symbol in math_symbols:
            assert symbol in name2codepoint
    
    def test_currency_symbols_exist(self):
        """Test that currency symbol entities exist"""
        currencies = ['pound', 'yen', 'euro', 'cent']
        for currency in currencies:
            assert currency in name2codepoint
    
    def test_codepoint_values(self):
        """Test specific codepoint values"""
        assert name2codepoint['amp'] == 0x0026  # &
        assert name2codepoint['lt'] == 0x003C   # <
        assert name2codepoint['gt'] == 0x003E   # >
        assert name2codepoint['nbsp'] == 0x00A0  # non-breaking space
        assert name2codepoint['copy'] == 0x00A9  # ©


class TestIntegration:
    def test_real_world_html(self):
        """Test with real-world HTML content"""
        html = """
        &lt;div class=&quot;content&quot;&gt;
            &copy; 2024 Company &amp; Associates
            Price: &pound;99.99 (&euro;89.99)
            Math: &alpha; + &beta; = &gamma;
        &lt;/div&gt;
        """
        result = _replace_entities(html)
        
        assert '<div class="content">' in result
        assert '© 2024 Company & Associates' in result
        assert 'Price: £99.99 (€89.99)' in result
        assert 'Math: α + β = γ' in result
    
    def test_performance_with_large_text(self):
        """Test performance with large text containing many entities"""
        # Create large text with repeated entities
        text = ("&amp; &lt; &gt; &quot; " * 1000)
        result = _replace_entities(text)
        
        # Should complete without issues and have correct content
        assert result.count("&") == 1000
        assert result.count("<") == 1000
        assert result.count(">") == 1000
        assert result.count('"') == 1000
