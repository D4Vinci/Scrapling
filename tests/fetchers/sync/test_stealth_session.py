import re
import pytest
import pytest_httpbin

from scrapling.engines.constants import DEFAULT_ARGS, STEALTH_ARGS
from scrapling.engines._browsers._controllers import DynamicSession
from scrapling.engines._browsers._stealth import StealthySession, __CF_PATTERN__


class TestStealthConstants:
    """Test Stealth constants and patterns"""

    def test_cf_pattern_regex(self):
        """Test __CF_PATTERN__ regex compilation"""

        assert isinstance(__CF_PATTERN__, re.Pattern)

        # Test matching URLs
        test_urls = [
            "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/123456",
            "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/orchestrate/jsch/v1",
            "http://challenges.cloudflare.com/cdn-cgi/challenge-platform/scripts/abc"
        ]

        for url in test_urls:
            assert __CF_PATTERN__.search(url) is not None

        # Test non-matching URLs
        non_matching_urls = [
            "https://example.com/challenge",
            "https://cloudflare.com/something",
            "https://challenges.cloudflare.com/other-path"
        ]

        for url in non_matching_urls:
            assert __CF_PATTERN__.search(url) is None


class TestLaunchFlags:
    """The launch flags a StealthySession ends up handing to Chromium.

    No browser is started: `_browser_options` is exactly what
    `chromium.launch(**self._browser_options)` is called with.
    """

    # a flag that is in neither DEFAULT_ARGS nor STEALTH_ARGS, so its presence
    # and the bundle's presence are independent observations
    USER_FLAG = "--window-size=1280,720"

    @staticmethod
    def _args(**kwargs):
        session = StealthySession(headless=True, block_webrtc=True, allow_webgl=False, hide_canvas=True, **kwargs)
        return list(session._browser_options["args"])

    def test_extra_flags_are_added_to_the_stealth_bundle_not_swapped_for_it(self):
        """`extra_flags` used to replace the hardening bundle instead of extending it.

        The bundle reaches __generate_options__ as its `extra_flags` argument, and
        `config.extra_flags or extra_flags` returned whichever came first, so passing
        one flag of your own dropped all 53 STEALTH_ARGS and every conditional flag
        with them.
        """
        without = self._args()
        with_extra = self._args(extra_flags=[self.USER_FLAG])

        assert self.USER_FLAG not in without, "test flag must not already ship"
        assert self.USER_FLAG in with_extra, "the user's own flag was dropped"

        missing = [flag for flag in STEALTH_ARGS if flag not in with_extra]
        assert missing == [], f"extra_flags displaced {len(missing)} stealth flags"
        assert [flag for flag in DEFAULT_ARGS if flag not in with_extra] == []

        # the conditional flags are built in the same place and were lost the same way
        for flag in (
            "--webrtc-ip-handling-policy=disable_non_proxied_udp",
            "--disable-webgl",
            "--fingerprinting-canvas-image-data-noise",
        ):
            assert flag in with_extra, f"{flag} lost to extra_flags"

    def test_flag_order_is_deterministic(self):
        """The flags were collapsed through `set()`, whose order over strings depends on
        the per-process hash seed, so the list differed from run to run. Chrome parses
        `--disable-features` and `--lang` last-wins, so their order is not cosmetic.

        Asserting the declared order survives pins this without needing a subprocess:
        an arbitrary ordering of 11 and 53 flags will not reproduce it by chance.
        """
        args = self._args(extra_flags=[self.USER_FLAG])

        assert [flag for flag in args if flag in set(DEFAULT_ARGS)] == list(DEFAULT_ARGS)
        assert [flag for flag in args if flag in set(STEALTH_ARGS)] == list(STEALTH_ARGS)
        # the user's flags go last, so they win the switches Chrome parses last-wins
        assert args.index(self.USER_FLAG) > max(args.index(flag) for flag in STEALTH_ARGS)

    def test_dynamic_session_keeps_defaults_and_their_order(self):
        """DynamicSession separates the two halves of the bug.

        It passes no bundle, so there was never a second list for `or` to discard and
        it never lost a flag - the membership assertion below held before this fix.
        The order assertion did not: it goes through the same `set()`, so its flags
        were shuffled too. Both halves are covered here so a future change that fixes
        one and reintroduces the other is caught.
        """
        session = DynamicSession(headless=True, extra_flags=[self.USER_FLAG])
        args = list(session._browser_options["args"])

        assert self.USER_FLAG in args
        assert set(DEFAULT_ARGS) <= set(args), "a default flag was dropped"
        assert [flag for flag in args if flag in set(DEFAULT_ARGS)] == list(DEFAULT_ARGS)


@pytest_httpbin.use_class_based_httpbin
class TestStealthySession:

    """All the code is tested in the async version tests, so no need to repeat it here. The async class inherits from this one."""
    @pytest.fixture(autouse=True)
    def setup_urls(self, httpbin):
        """Fixture to set up URLs for testing"""
        self.status_200 = f"{httpbin.url}/status/200"
        self.status_404 = f"{httpbin.url}/status/404"
        self.status_501 = f"{httpbin.url}/status/501"
        self.basic_url = f"{httpbin.url}/get"
        self.html_url = f"{httpbin.url}/html"
        self.delayed_url = f"{httpbin.url}/delay/10"  # 10 Seconds delay response
        self.cookies_url = f"{httpbin.url}/cookies/set/test/value"

    def test_session_creation(self):
        """Test if the session is created correctly"""

        with StealthySession(
            headless=True,
            disable_resources=True,
            solve_cloudflare=True,
            wait=1000,
            timeout=60000,
            cookies=[{"name": "test", "value": "123", "domain": "example.com", "path": "/"}],
        ) as session:

            assert session.max_pages == 1
            assert session._config.headless is True
            assert session._config.disable_resources is True
            assert session._config.solve_cloudflare is True
            assert session._config.wait == 1000
            assert session._config.timeout == 60000
            assert session.context is not None

            # Test Cloudflare detection
            for cloudflare_type in ('managed', 'interactive', 'non-interactive'):
                page_content = f"""
                <html>
                    <script>
                        cType: '{cloudflare_type}'
                    </script>
                </html>
                """
                result = session._detect_cloudflare(page_content)
                assert result == cloudflare_type

            page_content = """
            <html>
                <body>
                    <p>Regular page content</p>
                </body>
            </html>
            """

            result = StealthySession._detect_cloudflare(page_content)
            assert result is None
            assert session.fetch(self.status_200).status == 200
            assert session.page_pool.pages_count == 1
            page = session.page_pool.pages[0].page
            assert session.fetch(self.status_200).status == 200
            assert session.page_pool.pages[0].page is page, "sync sessions reuse their single tab"
            session.close_pages()
            assert session.page_pool.pages_count == 0
