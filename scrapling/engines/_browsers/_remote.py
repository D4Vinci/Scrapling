from scrapling.core._types import Any, Dict, Tuple, Unpack
from scrapling.engines._browsers._base import StealthySessionMixin
from scrapling.engines._browsers._stealth import StealthySession, AsyncStealthySession
from scrapling.engines._browsers._types import RemoteSessionParams
from scrapling.engines._browsers._validators import RemoteConfig


class _RemoteSessionMixin(StealthySessionMixin):
    _config: RemoteConfig
    _config_class = RemoteConfig

    def __generate_options__(self, extra_flags: Tuple | None = None) -> None:
        self._browser_options = {}
        if self._config.new_context:
            if self._config.locale:
                self._context_options["locale"] = self._config.locale
            self.__generate_context_options__()
        else:
            self._context_options = {}


class RemoteSession(_RemoteSessionMixin, StealthySession):
    """A CDP browser session that creates its own context or borrows the default context."""

    _config: RemoteConfig

    def __init__(self, cdp_url: str, *, new_context: bool = True, **kwargs: Unpack[RemoteSessionParams]):
        """Connect to a remote browser when the session starts.

        :param cdp_url: HTTP or WebSocket CDP endpoint of an existing Chromium browser.
        :param new_context: Create and close a separate context. If False, keep the existing default context open
            and ignore useragent, locale, timezone_id, proxy, proxy_rotator and additional_args.
        :param kwargs: Shared session and page options. Browser launch options do not apply.
            Cookies and init scripts affect the shared context when new_context is False.
        """
        params: Dict[str, Any] = dict(kwargs, cdp_url=cdp_url, new_context=new_context)
        super().__init__(**params)
        self._owns_context = self._config.new_context

    def _create_context(self) -> None:
        self.browser = self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url, no_defaults=True)
        if self._config.new_context:
            if not self._config.proxy_rotator:
                self.context = self.browser.new_context(**self._context_options)
        elif self.browser.contexts:
            self.context = self.browser.contexts[0]
        else:
            raise RuntimeError("The remote browser has no existing context; use new_context=True.")


class AsyncRemoteSession(_RemoteSessionMixin, AsyncStealthySession):
    """An async CDP session that creates its own context or borrows the default context."""

    _config: RemoteConfig

    def __init__(self, cdp_url: str, *, new_context: bool = True, **kwargs: Unpack[RemoteSessionParams]):
        """Connect to a remote browser when the session starts.

        :param cdp_url: HTTP or WebSocket CDP endpoint of an existing Chromium browser.
        :param new_context: Create and close a separate context. If False, keep the existing default context open
            and ignore useragent, locale, timezone_id, proxy, proxy_rotator and additional_args.
        :param kwargs: Shared session and page options. Browser launch options do not apply.
            Cookies and init scripts affect the shared context when new_context is False.
        """
        params: Dict[str, Any] = dict(kwargs, cdp_url=cdp_url, new_context=new_context)
        super().__init__(**params)
        self._owns_context = self._config.new_context

    async def _create_context(self) -> None:
        self.browser = await self.playwright.chromium.connect_over_cdp(
            endpoint_url=self._config.cdp_url, no_defaults=True
        )
        if self._config.new_context:
            if not self._config.proxy_rotator:
                self.context = await self.browser.new_context(**self._context_options)
        elif self.browser.contexts:
            self.context = self.browser.contexts[0]
        else:
            raise RuntimeError("The remote browser has no existing context; use new_context=True.")
