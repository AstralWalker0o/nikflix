#!/usr/bin/env python3
"""Probe a rendered web page for form-related elements.

Usage:
    bin/probe-form <url> [--wait <seconds>]

Loads the URL in a headless Chromium, waits for the SPA to render, and
dumps every <input>, <select>, and <button> with the attributes that
matter for an autofill selector (id, name, type, autocomplete,
formcontrolname, placeholder, role, aria-label).

Output is JSON. Pipe through `jq` for pretty viewing.

The intent is to figure out the right CSS selectors for a Keeper PAM RBI
`autofillConfiguration` rule without guessing. Run on a host that can
reach the URL on its LAN.
"""

import argparse
import json
import sys

from playwright.sync_api import sync_playwright

INTERESTING_ATTRS = (
    "id", "name", "type", "placeholder", "autocomplete",
    "formcontrolname", "data-testid", "role", "aria-label",
    "label", "ng-model", "v-model", "x-model",
)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("url")
    ap.add_argument("--wait", type=float, default=2.0,
                    help="extra seconds to wait after networkidle (default: 2)")
    ap.add_argument("--ignore-ssl", action="store_true",
                    help="ignore SSL cert errors (for self-signed)")
    args = ap.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage",
        ])
        ctx_kwargs = {"ignore_https_errors": args.ignore_ssl}
        ctx = browser.new_context(**ctx_kwargs)
        page = ctx.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=30_000)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
        page.wait_for_timeout(int(args.wait * 1000))

        items = page.evaluate("""
            (attrs) => {
              const result = [];
              const tags = ['input', 'select', 'button'];
              for (const tag of tags) {
                document.querySelectorAll(tag).forEach((el, i) => {
                  const rec = { tag: tag, index_in_tag: i };
                  for (const a of attrs) {
                    const v = el.getAttribute(a);
                    if (v !== null) rec[a] = v;
                  }
                  if (tag === 'input') {
                    rec.value = el.value || null;
                  }
                  if (tag === 'button') {
                    rec.text = (el.innerText || '').trim().slice(0, 80);
                  }
                  // skip elements with no meaningful attrs/text
                  const keys = Object.keys(rec).filter(k =>
                    k !== 'tag' && k !== 'index_in_tag' && k !== 'value');
                  if (keys.length) result.push(rec);
                });
              }
              return {
                title: document.title,
                url: location.href,
                pathname: location.pathname,
                elements: result,
              };
            }
        """, list(INTERESTING_ATTRS))

        print(json.dumps(items, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
