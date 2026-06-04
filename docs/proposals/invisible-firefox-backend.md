# Stealth patched-Firefox engine option (proposal)

> Status: Draft proposal / interest check
> Tracking discussion: TBD

## Goal

Offer an optional Firefox engine for `StealthyFetcher`, backed by a Firefox 150
binary with fingerprint patches applied at the C++ source level, for targets
where the current Chromium + patchright path still trips Cloudflare, Datadome,
PerimeterX, or Akamai.

## Why this fits Scrapling specifically

Three things already in the repo point at this:

1. **Issue #291** asked for a CloakBrowser-style stealth backend for Cloudflare
   bypass, and the answer was "I will take a look later" rather than a no. This
   is the same slot, on the Firefox side, with an open-source (MPL-2) binary.
2. **`executable_path` already exists** in the fetcher options ("custom browser
   executable to use instead of the bundled Chromium ... custom browser builds").
   So the wiring to point at an alternate binary is already there.
3. **Camoufox was the engine until 0.3.13**, then dropped for patchright over
   memory/stability reasons (per docs/fetching/stealthy.md). So a Firefox stealth
   engine is not a foreign idea here, it was the original one. The proposal is a
   different Firefox build that avoids the camoufox memory/stability pain: patches
   live in the compiled binary, and it is fully pref-driven rather than runtime
   JS injection.

## The detection angle

patchright patches Chromium at the JS layer, which still leaves a surface anti-bot
scripts read: native function `.toString()` enumeration, the CDP attach
signature, and the general "chromium-shaped traffic is higher risk" weighting. A
Firefox build patched at the C++ source level (canvas readback, webgl
getParameter, font metrics, audio, navigator, system colors) has no JS shim and no
CDP attach signature, and presents a non-chrome engine that some anti-bot stacks
score more leniently.

## Proposed change

A Firefox branch in the StealthyFetcher engine: when a firefox engine is selected,
launch `playwright.firefox.launch(executable_path=<patched binary>,
firefox_user_prefs=<prefs>)` instead of the chromium path, reusing the existing
`executable_path` plumbing. The patched binary lives at
https://github.com/feder-cr/invisible_firefox (MPL-2, same license as Firefox
upstream) and auto-downloads on first run via
https://github.com/feder-cr/invisible_playwright. Returned object is a normal
Playwright page, so the rest of Scrapling (parsing, adaptive selectors, response
factory) is unchanged.

## Out of scope

No change to the default Chromium + patchright path. Firefox stays an opt-in
engine choice.

## Honest caveats

- Scrapling is Python and so is the wrapper, so it can drop in; but the minimal
  version is just the firefox launch with executable_path + firefox_user_prefs, no
  hard dependency.
- Helps the fingerprint/engine layer only. It does not solve IP reputation or a
  Press & Hold once it has fired.
- Firefox via Playwright has no CDP, so the `cdp_url` / connect_over_cdp paths
  stay Chromium-only and are unaffected.

If this is in scope I can wire the firefox engine branch and add a docs example
under the stealthy fetcher. If not, happy to close without noise.
