import pytest

from scrapling.engines.toolbelt.custom import BaseFetcher


class TestBaseFetcher:
    """Test BaseFetcher configuration functionality"""

    def test_default_configuration(self):
        """Test default configuration values"""
        config = BaseFetcher.display_config()

        assert config['huge_tree'] is True
        assert config['adaptive'] is False
        assert config['keep_comments'] is False
        assert config['keep_cdata'] is False

    def test_configure_single_parameter(self):
        """Test configuring single parameter"""
        BaseFetcher.configure(adaptive=True)

        config = BaseFetcher.display_config()
        assert config['adaptive'] is True

        # Reset
        BaseFetcher.configure(adaptive=False)

    def test_configure_multiple_parameters(self):
        """Test configuring multiple parameters"""
        BaseFetcher.configure(
            huge_tree=False,
            keep_comments=True,
            adaptive=True
        )

        config = BaseFetcher.display_config()
        assert config['huge_tree'] is False
        assert config['keep_comments'] is True
        assert config['adaptive'] is True

        # Reset
        BaseFetcher.configure(
            huge_tree=True,
            keep_comments=False,
            adaptive=False
        )

    def test_configure_invalid_parameter(self):
        """Test configuring invalid parameter"""
        with pytest.raises(ValueError):
            BaseFetcher.configure(invalid_param=True)

    def test_configure_no_parameters(self):
        """Test configure with no parameters"""
        with pytest.raises(AttributeError):
            BaseFetcher.configure()

    def test_configure_non_parser_keyword(self):
        """Test configuring non-parser keyword"""
        with pytest.raises(AttributeError):
            # Assuming there's some attribute that's not in parser_keywords
            BaseFetcher.some_other_attr = "test"
            BaseFetcher.configure(some_other_attr="new_value")

    def test_generate_parser_arguments(self):
        """Test parser arguments generation"""
        BaseFetcher.configure(
            huge_tree=False,
            adaptive=True,
            adaptive_domain="example.com"
        )

        args = BaseFetcher._generate_parser_arguments()

        assert args['huge_tree'] is False
        assert args['adaptive'] is True
        assert args['adaptive_domain'] == "example.com"

        # Reset
        BaseFetcher.configure(
            huge_tree=True,
            adaptive=False
        )
        BaseFetcher.adaptive_domain = None
