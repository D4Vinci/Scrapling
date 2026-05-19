"""High-value site adapters for the Scrapling MCP.

Each adapter targets a specific site shape and returns structured data
ready for downstream LLM consumption. Adapters pick their own fetcher
(``Fetcher`` for plain HTTP/JSON endpoints, ``StealthyFetcher`` for
JS-heavy or anti-bot pages) and parse the response with ``lxml``.

The public surface lives entirely on :class:`AdaptersMCPTools`. Each
method returns an :class:`AdapterResponse` envelope with ``success``,
``site``, ``data`` and an optional ``error`` / ``fallback_html``.
"""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from lxml import html as lxml_html
from pydantic import BaseModel, Field

from scrapling.fetchers import AsyncFetcher, Fetcher, StealthyFetcher


# ---------------------------------------------------------------------------
# Common envelope
# ---------------------------------------------------------------------------


class AdapterResponse(BaseModel):
    """Unified envelope returned by every adapter."""

    success: bool = Field(description="True when structured data was extracted.")
    site: str = Field(description="Stable identifier of the source site.")
    data: Optional[Any] = Field(default=None, description="Adapter specific payload.")
    error: Optional[str] = Field(default=None, description="Human readable error message.")
    fallback_html: Optional[str] = Field(
        default=None,
        description="Raw HTML excerpt returned when the site blocks structured extraction.",
    )


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class TelegramMessage(BaseModel):
    """A single message rendered on the public ``t.me/s/<channel>`` view."""

    message_id: Optional[int] = Field(default=None, description="Numeric id of the message inside the channel.")
    author: Optional[str] = Field(default=None, description="Display name of the author or channel.")
    text: str = Field(default="", description="Plain text body of the message.")
    date: Optional[str] = Field(default=None, description="ISO date string when the message was posted.")
    edited_date: Optional[str] = Field(default=None, description="ISO date string when the message was last edited.")
    views: Optional[str] = Field(default=None, description="Public view counter, kept as a string (e.g. ``1.2K``).")
    pinned: bool = Field(default=False, description="True when the message is pinned in the channel.")
    reply_to: Optional[str] = Field(default=None, description="URL of the message this one replies to.")
    links: List[str] = Field(default_factory=list, description="Outbound links found in the message body.")
    media_urls: List[str] = Field(default_factory=list, description="Photo, video and document URLs attached to the message.")


class Tweet(BaseModel):
    """A single tweet inside a thread."""

    id: Optional[str] = Field(default=None, description="Numeric tweet id, when extractable.")
    text: str = Field(default="", description="Plain text body of the tweet.")
    author: Optional[str] = Field(default=None, description="Handle of the tweet author including the leading ``@``.")
    date: Optional[str] = Field(default=None, description="ISO datetime when the tweet was posted.")
    likes: Optional[str] = Field(default=None, description="Like counter, as displayed on the page.")
    retweets: Optional[str] = Field(default=None, description="Retweet counter, as displayed on the page.")
    replies_count: Optional[str] = Field(default=None, description="Reply counter, as displayed on the page.")
    media: List[str] = Field(default_factory=list, description="Media URLs (images/videos) attached to the tweet.")


class ThreadResult(BaseModel):
    """Outcome of a Twitter thread extraction."""

    author: Optional[str] = Field(default=None, description="Handle of the thread author.")
    original: Optional[Tweet] = Field(default=None, description="First tweet of the thread.")
    replies: List[Tweet] = Field(default_factory=list, description="Subsequent tweets visible on the page.")


class TranscriptSegment(BaseModel):
    """A single caption cue."""

    start: float = Field(description="Start time of the cue, in seconds.")
    duration: float = Field(description="Duration of the cue, in seconds.")
    text: str = Field(description="Text content of the cue.")


class YouTubeMetadata(BaseModel):
    """Metadata block extracted from the watch page."""

    title: Optional[str] = Field(default=None, description="Video title.")
    channel: Optional[str] = Field(default=None, description="Channel name.")
    duration: Optional[str] = Field(default=None, description="Video duration, in seconds, as a string.")
    views: Optional[str] = Field(default=None, description="View counter as exposed by the player response.")
    published: Optional[str] = Field(default=None, description="Publish or upload date.")
    description: Optional[str] = Field(default=None, description="Long form description.")


class YouTubeResult(BaseModel):
    """Combined transcript + metadata payload."""

    metadata: YouTubeMetadata = Field(description="Top level video metadata.")
    language: Optional[str] = Field(default=None, description="Language code of the resolved caption track.")
    transcript: List[TranscriptSegment] = Field(default_factory=list, description="Ordered caption cues.")
    available_languages: List[str] = Field(default_factory=list, description="Language codes of every caption track exposed by the page.")


class GitHubFile(BaseModel):
    """Lightweight file entry extracted from the git tree."""

    path: str = Field(description="Repository relative path of the file.")
    size: Optional[int] = Field(default=None, description="File size in bytes when reported by the API.")


class GitHubStats(BaseModel):
    """Star / fork / language summary."""

    stars: Optional[int] = Field(default=None, description="Stargazer count.")
    forks: Optional[int] = Field(default=None, description="Fork count.")
    open_issues: Optional[int] = Field(default=None, description="Open issue count (issues + PRs).")
    language: Optional[str] = Field(default=None, description="Primary language reported by GitHub.")


class GitHubRepoResult(BaseModel):
    """Combined repository payload."""

    meta: Dict[str, Any] = Field(description="Subset of the raw repository metadata returned by the GitHub API.")
    readme: Optional[str] = Field(default=None, description="README contents fetched from the default branch.")
    files: List[GitHubFile] = Field(default_factory=list, description="Files discovered in the recursive git tree.")
    stats: GitHubStats = Field(description="Aggregated repository statistics.")


class RedditComment(BaseModel):
    """A flattened reddit comment."""

    author: Optional[str] = Field(default=None, description="Author handle, ``[deleted]`` when removed.")
    body: str = Field(default="", description="Markdown body of the comment.")
    score: Optional[int] = Field(default=None, description="Net score of the comment.")
    replies: List["RedditComment"] = Field(default_factory=list, description="Direct child replies.")


RedditComment.model_rebuild()


class RedditPost(BaseModel):
    """Top level reddit submission."""

    title: Optional[str] = Field(default=None, description="Submission title.")
    author: Optional[str] = Field(default=None, description="Submission author.")
    subreddit: Optional[str] = Field(default=None, description="Subreddit slug without the leading ``r/``.")
    url: Optional[str] = Field(default=None, description="Permalink to the submission.")
    selftext: Optional[str] = Field(default=None, description="Body text for self posts.")
    score: Optional[int] = Field(default=None, description="Net score of the submission.")
    num_comments: Optional[int] = Field(default=None, description="Total number of comments on the submission.")
    created_utc: Optional[float] = Field(default=None, description="Unix timestamp of submission creation.")


class RedditThreadResult(BaseModel):
    """Reddit thread payload."""

    post: RedditPost = Field(description="The submission itself.")
    comments: List[RedditComment] = Field(default_factory=list, description="Top level comments with nested replies.")


class HNItem(BaseModel):
    """A Hacker News item (story or comment)."""

    id: int = Field(description="Numeric Firebase item id.")
    type: Optional[str] = Field(default=None, description="``story``, ``comment``, ``job``, etc.")
    by: Optional[str] = Field(default=None, description="Author username.")
    time: Optional[int] = Field(default=None, description="Unix timestamp of submission.")
    title: Optional[str] = Field(default=None, description="Title for stories.")
    url: Optional[str] = Field(default=None, description="External URL for stories.")
    text: Optional[str] = Field(default=None, description="HTML body for comments and self posts.")
    score: Optional[int] = Field(default=None, description="Item score.")
    descendants: Optional[int] = Field(default=None, description="Total descendant comment count for stories.")
    kids: List["HNItem"] = Field(default_factory=list, description="Resolved child items, recursion limited.")


HNItem.model_rebuild()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _decode_body(body: Any) -> str:
    """Best effort decode of a Scrapling ``Response`` body to ``str``."""

    if body is None:
        return ""
    if isinstance(body, str):
        return body
    if isinstance(body, (bytes, bytearray)):
        try:
            return bytes(body).decode("utf-8", errors="replace")
        except Exception:
            return ""
    return str(body)


def _response_html(response: Any) -> str:
    """Pull the best HTML representation from a Scrapling ``Response``."""

    for attr in ("html_content", "text"):
        candidate = getattr(response, attr, None)
        if candidate:
            return str(candidate)
    return _decode_body(getattr(response, "body", None))


def _balanced_json(source: str, start: int) -> Optional[str]:
    """Return the substring beginning at ``source[start]`` that forms a balanced JSON object.

    Used to peel ``ytInitialPlayerResponse`` out of the watch page HTML where the
    object is followed by ``;`` and additional script content.
    """

    if start < 0 or start >= len(source) or source[start] != "{":
        return None

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    return None


def _strip_tags(value: str) -> str:
    """Cheap HTML tag stripper used on caption XML payloads."""

    return re.sub(r"<[^>]+>", "", value)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class AdaptersMCPTools:
    """Site specific structured-extraction tools exposed via the MCP server."""

    # ------------------------------------------------------------------ Telegram

    @staticmethod
    async def telegram_channel(channel: str, limit: int = 30) -> AdapterResponse:
        """Fetch and parse the public preview of a Telegram channel.

        :param channel: Channel slug (without the leading ``@``).
        :param limit: Maximum number of messages to keep, newest first.
        """

        slug = channel.lstrip("@").strip().strip("/")
        if not slug:
            return AdapterResponse(success=False, site="telegram", error="channel slug is required")

        url = f"https://t.me/s/{slug}"
        try:
            response = await StealthyFetcher.async_fetch(
                url,
                headless=True,
                network_idle=True,
                wait_selector=".tgme_widget_message",
                timeout=30000,
            )
        except Exception as exc:  # pragma: no cover - network/runtime guard
            return AdapterResponse(success=False, site="telegram", error=f"fetch failed: {exc}")

        html_text = _response_html(response)
        if not html_text:
            return AdapterResponse(success=False, site="telegram", error="empty response body")

        try:
            tree = lxml_html.fromstring(html_text)
        except Exception as exc:
            return AdapterResponse(
                success=False,
                site="telegram",
                error=f"html parse failed: {exc}",
                fallback_html=html_text[:5000],
            )

        nodes = tree.cssselect(".tgme_widget_message_wrap")
        messages: List[TelegramMessage] = []
        for wrap in nodes:
            msg_nodes = wrap.cssselect(".tgme_widget_message")
            if not msg_nodes:
                continue
            msg = msg_nodes[0]

            classes = (msg.get("class") or "").split()
            is_pinned = bool(wrap.cssselect(".tgme_widget_message_service_pinned")) or "tgme_widget_message_pinned" in classes

            data_post = msg.get("data-post") or ""
            message_id: Optional[int] = None
            if "/" in data_post:
                tail = data_post.rsplit("/", 1)[-1]
                if tail.isdigit():
                    message_id = int(tail)

            if message_id is None:
                date_links = msg.cssselect("a.tgme_widget_message_date")
                if date_links:
                    href = date_links[0].get("href") or ""
                    tail = href.rstrip("/").rsplit("/", 1)[-1]
                    if tail.isdigit():
                        message_id = int(tail)

            author_nodes = msg.cssselect(".tgme_widget_message_author_name, .tgme_widget_message_owner_name")
            author = author_nodes[0].text_content().strip() if author_nodes else None

            text_nodes = msg.cssselect(".tgme_widget_message_text")
            text_value = ""
            links: List[str] = []
            if text_nodes:
                text_value = text_nodes[0].text_content().strip()
                for anchor in text_nodes[0].cssselect("a"):
                    href = anchor.get("href")
                    if href:
                        links.append(href)

            date_attr = None
            time_nodes = msg.cssselect("a.tgme_widget_message_date time")
            if time_nodes:
                date_attr = time_nodes[0].get("datetime")

            edited_attr = None
            edited_nodes = msg.cssselect(".tgme_widget_message_meta time.time")
            for node in edited_nodes:
                if node.get("datetime") and node.get("datetime") != date_attr:
                    edited_attr = node.get("datetime")
                    break

            views_nodes = msg.cssselect(".tgme_widget_message_views")
            views = views_nodes[0].text_content().strip() if views_nodes else None

            reply_nodes = msg.cssselect("a.tgme_widget_message_reply")
            reply_to = reply_nodes[0].get("href") if reply_nodes else None

            media_urls: List[str] = []
            for photo in msg.cssselect("a.tgme_widget_message_photo_wrap"):
                style = photo.get("style") or ""
                match = re.search(r"background-image:url\(['\"]?([^'\")]+)", style)
                if match:
                    media_urls.append(match.group(1))
            for video in msg.cssselect("video"):
                src = video.get("src")
                if src:
                    media_urls.append(src)
            for doc in msg.cssselect("a.tgme_widget_message_document_wrap"):
                href = doc.get("href")
                if href:
                    media_urls.append(href)

            messages.append(
                TelegramMessage(
                    message_id=message_id,
                    author=author,
                    text=text_value,
                    date=date_attr,
                    edited_date=edited_attr,
                    views=views,
                    pinned=is_pinned,
                    reply_to=reply_to,
                    links=links,
                    media_urls=media_urls,
                )
            )

        if limit and len(messages) > limit:
            messages = messages[-limit:]

        return AdapterResponse(
            success=True,
            site="telegram",
            data={"channel": slug, "url": url, "messages": [m.model_dump() for m in messages]},
        )

    # ------------------------------------------------------------------- Twitter

    @staticmethod
    async def twitter_thread(url: str) -> AdapterResponse:
        """Fetch a Twitter/X status URL and return either structured tweets or an OG fallback."""

        if not url:
            return AdapterResponse(success=False, site="twitter", error="url is required")

        try:
            response = await StealthyFetcher.async_fetch(
                url,
                headless=True,
                network_idle=True,
                wait_selector="article",
                timeout=45000,
            )
        except Exception as exc:
            return AdapterResponse(success=False, site="twitter", error=f"fetch failed: {exc}")

        html_text = _response_html(response)
        if not html_text:
            return AdapterResponse(success=False, site="twitter", error="empty response body")

        try:
            tree = lxml_html.fromstring(html_text)
        except Exception as exc:
            return AdapterResponse(
                success=False,
                site="twitter",
                error=f"html parse failed: {exc}",
                fallback_html=html_text[:5000],
            )

        articles = tree.cssselect("article")
        og_meta: Dict[str, str] = {}
        for meta in tree.cssselect("meta"):
            prop = meta.get("property") or meta.get("name") or ""
            if prop.startswith("og:") or prop.startswith("twitter:"):
                value = meta.get("content")
                if value:
                    og_meta[prop] = value

        if not articles:
            # Twitter is aggressive: when JS gating wins, surface meta + raw HTML.
            return AdapterResponse(
                success=False,
                site="twitter",
                error="no article nodes rendered (likely anti-bot wall)",
                data={"og_meta": og_meta, "url": url},
                fallback_html=html_text[:8000],
            )

        path_match = re.search(r"/status/(\d+)", url)
        thread_id = path_match.group(1) if path_match else None

        def _build_tweet(article: Any) -> Tweet:
            text_chunks = [n.text_content() for n in article.cssselect('div[data-testid="tweetText"]')]
            text_value = "\n".join(chunk.strip() for chunk in text_chunks if chunk).strip()

            author_handle = None
            for anchor in article.cssselect('a[href^="/"]'):
                href = anchor.get("href") or ""
                if re.fullmatch(r"/[A-Za-z0-9_]+", href):
                    author_handle = "@" + href.lstrip("/")
                    break

            time_nodes = article.cssselect("time")
            date_value = time_nodes[0].get("datetime") if time_nodes else None

            tweet_id: Optional[str] = None
            for anchor in article.cssselect('a[href*="/status/"]'):
                href = anchor.get("href") or ""
                m = re.search(r"/status/(\d+)", href)
                if m:
                    tweet_id = m.group(1)
                    break

            def _stat(testid: str) -> Optional[str]:
                # Bug #8: X has rotated DOM repeatedly; old data-testid="like"/"retweet"/"reply"
                # often resolves to the button container with no text. Try several
                # variants and finally fall back to aria-label="N Likes" parsing.
                for sel in (
                    f'div[data-testid="{testid}"]',
                    f'div[data-testid="{testid}-count"]',
                    f'div[data-testid="un{testid}"]',
                    f'button[data-testid="{testid}"]',
                    f'button[aria-label*="{testid}"]',
                    f'a[data-testid="{testid}"]',
                ):
                    nodes = article.cssselect(sel)
                    if not nodes:
                        continue
                    value = (nodes[0].text_content() or "").strip()
                    if value:
                        return value
                    # Pull a number out of aria-label like "1,234 Likes"
                    aria = nodes[0].get("aria-label") or ""
                    m = re.search(r"([\d,.]+\s*[KkMm]?)", aria)
                    if m:
                        return m.group(1).strip()
                return None

            media: List[str] = []
            for img in article.cssselect('div[data-testid="tweetPhoto"] img'):
                src = img.get("src")
                if src:
                    media.append(src)
            for video in article.cssselect("video"):
                src = video.get("src") or video.get("poster")
                if src:
                    media.append(src)

            return Tweet(
                id=tweet_id,
                text=text_value,
                author=author_handle,
                date=date_value,
                likes=_stat("like"),
                retweets=_stat("retweet"),
                replies_count=_stat("reply"),
                media=media,
            )

        tweets = [_build_tweet(article) for article in articles]
        original = next((t for t in tweets if thread_id and t.id == thread_id), tweets[0] if tweets else None)
        replies = [t for t in tweets if t is not original]
        author = original.author if original else None

        result = ThreadResult(author=author, original=original, replies=replies)
        return AdapterResponse(
            success=True,
            site="twitter",
            data={"url": url, "og_meta": og_meta, "thread": result.model_dump()},
        )

    # -------------------------------------------------------------------- YouTube

    @staticmethod
    async def youtube_transcript(url: str, lang: str = "auto") -> AdapterResponse:
        """Fetch a YouTube watch URL, parse player metadata and pull a caption track."""

        if not url:
            return AdapterResponse(success=False, site="youtube", error="url is required")

        try:
            page = await AsyncFetcher.get(url, stealthy_headers=True, timeout=30, retries=2)
        except Exception as exc:
            return AdapterResponse(success=False, site="youtube", error=f"fetch failed: {exc}")

        html_text = _response_html(page)
        if not html_text:
            return AdapterResponse(success=False, site="youtube", error="empty response body")

        marker = "ytInitialPlayerResponse"
        idx = html_text.find(marker)
        if idx < 0:
            return AdapterResponse(
                success=False,
                site="youtube",
                error="ytInitialPlayerResponse marker missing",
                fallback_html=html_text[:5000],
            )

        brace_idx = html_text.find("{", idx)
        json_blob = _balanced_json(html_text, brace_idx)
        if not json_blob:
            return AdapterResponse(
                success=False,
                site="youtube",
                error="failed to isolate ytInitialPlayerResponse",
                fallback_html=html_text[:5000],
            )

        try:
            player = json.loads(json_blob)
        except Exception as exc:
            return AdapterResponse(success=False, site="youtube", error=f"player json decode failed: {exc}")

        video_details = player.get("videoDetails") or {}
        microformat = (player.get("microformat") or {}).get("playerMicroformatRenderer") or {}
        metadata = YouTubeMetadata(
            title=video_details.get("title"),
            channel=video_details.get("author"),
            duration=video_details.get("lengthSeconds"),
            views=video_details.get("viewCount"),
            published=microformat.get("publishDate") or microformat.get("uploadDate"),
            description=video_details.get("shortDescription"),
        )

        captions = (
            (player.get("captions") or {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        available = [track.get("languageCode") for track in captions if track.get("languageCode")]

        track = None
        if captions:
            if lang and lang.lower() != "auto":
                for candidate in captions:
                    if candidate.get("languageCode", "").lower() == lang.lower():
                        track = candidate
                        break
            if track is None:
                track = captions[0]

        transcript_segments: List[TranscriptSegment] = []
        resolved_lang: Optional[str] = None
        caption_failure: Optional[str] = None
        if track and track.get("baseUrl"):
            resolved_lang = track.get("languageCode")
            try:
                caption_response = await AsyncFetcher.get(track["baseUrl"], stealthy_headers=True, timeout=20)
                caption_xml = _response_html(caption_response) or _decode_body(getattr(caption_response, "body", b""))
                # Bug #7: YouTube increasingly returns HTTP 200 with a 13-byte
                # `<html></html>` body for captions when the caller has no
                # consent cookie / signed token. Detect and surface that
                # accurately instead of pretending no captions exist.
                stripped = (caption_xml or "").strip().lower()
                if not stripped or stripped in ("<html></html>", "<html/>", "<?xml version=\"1.0\" encoding=\"utf-8\"?>"):
                    caption_failure = (
                        "caption endpoint returned empty body (likely consent-gated; "
                        "try a stealthy session that carries YouTube cookies)"
                    )
                else:
                    for match in re.finditer(
                        r'<text\s+start="([\d.]+)"(?:\s+dur="([\d.]+)")?[^>]*>(.*?)</text>',
                        caption_xml,
                        flags=re.DOTALL,
                    ):
                        raw = match.group(3) or ""
                        text_value = unescape(_strip_tags(raw)).strip()
                        if not text_value:
                            continue
                        transcript_segments.append(
                            TranscriptSegment(
                                start=float(match.group(1) or 0.0),
                                duration=float(match.group(2) or 0.0),
                                text=text_value,
                            )
                        )
                    if not transcript_segments:
                        caption_failure = "caption body had no <text> segments"
            except Exception as exc:  # pragma: no cover - depend on network
                return AdapterResponse(
                    success=False,
                    site="youtube",
                    error=f"caption fetch failed: {exc}",
                    data={"metadata": metadata.model_dump(), "available_languages": available},
                )

        result = YouTubeResult(
            metadata=metadata,
            language=resolved_lang,
            transcript=transcript_segments,
            available_languages=available,
        )
        # Distinguish "no track listed" from "track listed but body empty".
        if transcript_segments:
            error_text: Optional[str] = None
        elif caption_failure:
            error_text = caption_failure
        elif not captions:
            error_text = "no caption tracks listed in player response"
        else:
            error_text = "caption track exists but no usable baseUrl"
        return AdapterResponse(
            success=bool(transcript_segments) or bool(metadata.title),
            site="youtube",
            data=result.model_dump(),
            error=error_text,
        )

    # --------------------------------------------------------------------- GitHub

    @staticmethod
    async def github_repo(
        url: str,
        include_readme: bool = True,
        include_files: bool = True,
        max_files: int = 100,
    ) -> AdapterResponse:
        """Pull repository metadata, README and a slice of the recursive git tree."""

        owner, repo = _parse_github_repo(url)
        if not owner or not repo:
            return AdapterResponse(success=False, site="github", error="could not parse owner/repo from url")

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "scrapling-mcp"}
        try:
            meta_response = await AsyncFetcher.get(api_url, headers=headers, timeout=20, retries=2)
        except Exception as exc:
            return AdapterResponse(success=False, site="github", error=f"meta fetch failed: {exc}")

        if getattr(meta_response, "status", 0) >= 400:
            return AdapterResponse(
                success=False,
                site="github",
                error=f"github api returned {meta_response.status}",
            )

        try:
            meta_payload = json.loads(_decode_body(getattr(meta_response, "body", b"")) or "{}")
        except Exception as exc:
            return AdapterResponse(success=False, site="github", error=f"meta json decode failed: {exc}")

        default_branch = meta_payload.get("default_branch") or "HEAD"

        meta_subset = {
            key: meta_payload.get(key)
            for key in (
                "full_name",
                "description",
                "html_url",
                "homepage",
                "default_branch",
                "topics",
                "license",
                "created_at",
                "updated_at",
                "pushed_at",
                "archived",
                "disabled",
                "size",
            )
        }
        stats = GitHubStats(
            stars=meta_payload.get("stargazers_count"),
            forks=meta_payload.get("forks_count"),
            open_issues=meta_payload.get("open_issues_count"),
            language=meta_payload.get("language"),
        )

        readme_text: Optional[str] = None
        if include_readme:
            for branch_candidate in (default_branch, "main", "master"):
                for filename in ("README.md", "readme.md", "README.rst", "README"):
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch_candidate}/{filename}"
                    try:
                        readme_response = await AsyncFetcher.get(
                            raw_url,
                            headers={"User-Agent": "scrapling-mcp"},
                            timeout=20,
                            retries=1,
                        )
                    except Exception:
                        continue
                    if getattr(readme_response, "status", 0) == 200:
                        readme_text = _decode_body(getattr(readme_response, "body", b""))
                        break
                if readme_text:
                    break

        files: List[GitHubFile] = []
        if include_files:
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            try:
                tree_response = await AsyncFetcher.get(tree_url, headers=headers, timeout=20, retries=1)
                if getattr(tree_response, "status", 0) < 400:
                    tree_payload = json.loads(_decode_body(getattr(tree_response, "body", b"")) or "{}")
                    for entry in tree_payload.get("tree", []) or []:
                        if entry.get("type") != "blob":
                            continue
                        files.append(GitHubFile(path=entry.get("path", ""), size=entry.get("size")))
                        if max_files and len(files) >= max_files:
                            break
            except Exception:
                files = []

        result = GitHubRepoResult(meta=meta_subset, readme=readme_text, files=files, stats=stats)
        return AdapterResponse(success=True, site="github", data=result.model_dump())

    # ---------------------------------------------------------------------- Reddit

    @staticmethod
    async def reddit_thread(url: str, max_comments: int = 50) -> AdapterResponse:
        """Convert a Reddit thread URL into structured post + comments data."""

        if not url:
            return AdapterResponse(success=False, site="reddit", error="url is required")

        cleaned = url.split("?")[0].rstrip("/")
        json_url = cleaned if cleaned.endswith(".json") else cleaned + ".json"

        headers = {
            "User-Agent": "scrapling-mcp/1.0 (+https://github.com/D4Vinci/Scrapling)",
            "Accept": "application/json",
        }
        # Bug #6: Reddit aggressively 403s anonymous .json access since 2023.
        # Try the legacy old.reddit.com host first (currently still allows anon
        # JSON), then fall back to the modern host. On 403/429 we surface
        # fallback_html so the LLM can see the anti-bot wall instead of an
        # opaque "reddit returned 403".
        candidate_urls: List[str] = []
        m = re.match(r"https?://([^/]+)(/.*)$", json_url)
        if m and m.group(1) not in ("old.reddit.com",):
            candidate_urls.append(f"https://old.reddit.com{m.group(2)}")
        candidate_urls.append(json_url)

        response = None
        last_status = 0
        last_body = ""
        for attempt_url in candidate_urls:
            try:
                response = await AsyncFetcher.get(attempt_url, headers=headers, timeout=20, retries=2)
            except Exception as exc:
                last_status = -1
                last_body = f"fetch failed: {exc}"
                continue
            last_status = getattr(response, "status", 0)
            if last_status < 400:
                break
            last_body = _decode_body(getattr(response, "body", b""))[:5000]
            response = None

        if response is None:
            return AdapterResponse(
                success=False,
                site="reddit",
                error=(
                    f"reddit blocks anonymous .json access (status={last_status}); "
                    "supply OAuth credentials or a registered User-Agent"
                ),
                fallback_html=last_body or None,
            )

        try:
            payload = json.loads(_decode_body(getattr(response, "body", b"")) or "[]")
        except Exception as exc:
            return AdapterResponse(success=False, site="reddit", error=f"json decode failed: {exc}")

        if not isinstance(payload, list) or len(payload) < 2:
            return AdapterResponse(success=False, site="reddit", error="unexpected reddit json shape")

        post_listing = payload[0].get("data", {}).get("children", [])
        if not post_listing:
            return AdapterResponse(success=False, site="reddit", error="post payload missing")
        post_data = post_listing[0].get("data", {})
        post = RedditPost(
            title=post_data.get("title"),
            author=post_data.get("author"),
            subreddit=post_data.get("subreddit"),
            url=("https://www.reddit.com" + post_data["permalink"]) if post_data.get("permalink") else post_data.get("url"),
            selftext=post_data.get("selftext"),
            score=post_data.get("score"),
            num_comments=post_data.get("num_comments"),
            created_utc=post_data.get("created_utc"),
        )

        comment_count = 0

        def _walk(nodes: List[Dict[str, Any]]) -> List[RedditComment]:
            nonlocal comment_count
            collected: List[RedditComment] = []
            for child in nodes:
                if max_comments and comment_count >= max_comments:
                    break
                if child.get("kind") != "t1":
                    continue
                data = child.get("data", {})
                comment_count += 1
                replies_block = data.get("replies")
                child_comments: List[RedditComment] = []
                if isinstance(replies_block, dict):
                    nested = replies_block.get("data", {}).get("children", [])
                    child_comments = _walk(nested)
                collected.append(
                    RedditComment(
                        author=data.get("author"),
                        body=data.get("body", "") or "",
                        score=data.get("score"),
                        replies=child_comments,
                    )
                )
            return collected

        top_comments = _walk(payload[1].get("data", {}).get("children", []))
        result = RedditThreadResult(post=post, comments=top_comments)
        return AdapterResponse(success=True, site="reddit", data=result.model_dump())

    # ------------------------------------------------------------------ HackerNews

    @staticmethod
    async def hackernews_item(item_id_or_url: str) -> AdapterResponse:
        """Fetch a Hacker News item and recurse into kids up to a small budget."""

        item_id = _extract_hn_item_id(item_id_or_url)
        if item_id is None:
            return AdapterResponse(success=False, site="hackernews", error="could not parse item id")

        max_depth = 3
        max_total = 100
        cache: Dict[int, Dict[str, Any]] = {}
        fetched = 0

        async def _fetch_item(iid: int) -> Optional[Dict[str, Any]]:
            nonlocal fetched
            if iid in cache:
                return cache[iid]
            if fetched >= max_total:
                return None
            fetched += 1
            try:
                response = await AsyncFetcher.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{iid}.json",
                    timeout=15,
                    retries=2,
                )
            except Exception:
                return None
            if getattr(response, "status", 0) >= 400:
                return None
            try:
                payload = json.loads(_decode_body(getattr(response, "body", b"")) or "null")
            except Exception:
                return None
            if not isinstance(payload, dict):
                return None
            cache[iid] = payload
            return payload

        async def _build(iid: int, depth: int) -> Optional[HNItem]:
            data = await _fetch_item(iid)
            if not data:
                return None
            kids: List[HNItem] = []
            if depth < max_depth:
                for kid_id in (data.get("kids") or [])[:30]:
                    if fetched >= max_total:
                        break
                    built = await _build(kid_id, depth + 1)
                    if built is not None:
                        kids.append(built)
            return HNItem(
                id=data.get("id", iid),
                type=data.get("type"),
                by=data.get("by"),
                time=data.get("time"),
                title=data.get("title"),
                url=data.get("url"),
                text=data.get("text"),
                score=data.get("score"),
                descendants=data.get("descendants"),
                kids=kids,
            )

        root = await _build(item_id, 0)
        if root is None:
            return AdapterResponse(success=False, site="hackernews", error="item not found")

        return AdapterResponse(
            success=True,
            site="hackernews",
            data={"item": root.model_dump(), "fetched": fetched},
        )


# ---------------------------------------------------------------------------
# URL parsing helpers
# ---------------------------------------------------------------------------


def _parse_github_repo(url: str) -> tuple[Optional[str], Optional[str]]:
    """Return ``(owner, repo)`` from a GitHub URL or ``owner/repo`` shorthand."""

    if not url:
        return None, None
    if "github.com" not in url and "/" in url and not url.startswith("http"):
        parts = url.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1].removesuffix(".git")
        return None, None

    parsed = urlparse(url)
    parts = [segment for segment in parsed.path.split("/") if segment]
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1].removesuffix(".git")


def _extract_hn_item_id(value: str) -> Optional[int]:
    """Pull the numeric Hacker News item id out of a URL or raw string."""

    if value is None:
        return None
    candidate = str(value).strip()
    if candidate.isdigit():
        return int(candidate)

    match = re.search(r"id=(\d+)", candidate)
    if match:
        return int(match.group(1))

    match = re.search(r"/item/(\d+)", candidate)
    if match:
        return int(match.group(1))
    return None


__all__ = [
    "AdapterResponse",
    "AdaptersMCPTools",
    "TelegramMessage",
    "Tweet",
    "ThreadResult",
    "TranscriptSegment",
    "YouTubeMetadata",
    "YouTubeResult",
    "GitHubFile",
    "GitHubStats",
    "GitHubRepoResult",
    "RedditPost",
    "RedditComment",
    "RedditThreadResult",
    "HNItem",
]
