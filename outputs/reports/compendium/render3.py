#!/usr/bin/env python3
"""Render deals3.html -> PDF via Playwright Chromium.

Output: ./Energy_AI_Infra_Deal_Terms_<date>.pdf in this build dir.
"""
import os
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "deals3.html"
DATE = os.environ.get("COMPENDIUM_DATE", datetime.date.today().isoformat())
OUT = HERE / f"Energy_AI_Infra_Deal_Terms_{DATE}.pdf"


def main():
    url = SRC.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(OUT),
            format="Letter",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
