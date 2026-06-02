# Hardening behavior changes

This document records compatibility-sensitive behavior changes introduced by the
security and reliability hardening work. They are intentional, but callers that
rely on older implicit behavior should review them before upgrading.

## Checkpoints redact secrets by default

Spider checkpoints are now JSON-based and pickle-free. They also redact known
secret-bearing fields by default, including proxy credentials and authorization
headers stored in request state. This prevents accidental credential disclosure if
a checkpoint directory is copied or logged, but it also means a resumed crawl may
need proxy credentials supplied again from trusted configuration.

Use an explicit trusted checkpoint location and opt in to secret persistence only
when the deployment model requires it.

## Request equality and hashing generate fingerprints lazily

`Request.__eq__` and `Request.__hash__` no longer raise when a fingerprint has
not been generated yet. They compute the fingerprint on demand so set/list
membership and deduplication are safer to use. This changes the old contract that
required callers to generate fingerprints manually before comparing requests.

## Request domains are hostnames, not netlocs

`Request.domain` now returns the lowercase URL hostname and intentionally drops
userinfo and port. This fixes allow-list checks for URLs like
`https://user:pass@example.com:8443/path`, but it also means per-domain throttling
keys no longer distinguish `example.com:8443` from `example.com:443`.

## Checkpoint callback restore is name-based

Checkpoint resume serializes callback names instead of pickling Python callables.
The engine resolves callbacks from the spider object during resume. Avoid using
properties with side effects as crawl callbacks; normal spider methods are the
intended restore target.

## Stealth WebRTC protection is proxy-aware

`block_webrtc` is now tri-state. When a proxy is configured and `block_webrtc` is
left unset, Scrapling enables WebRTC blocking automatically to reduce IP leak
risk. Set `block_webrtc=False` explicitly only when the environment has been
reviewed and that behavior is required.

## Curl proxy normalization is explicit

The interactive shell normalizes `curl -x host:port` to `http://host:port` via a
single helper and preserves explicit proxy schemes such as `socks5://`. This
prevents the old brace-wrapping regression where a proxy could become
`http://host:port` with extra literal braces.
