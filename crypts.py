"""
CRYPTS: Crypto TUI Tracker
==================

A simple terminal user interface (TUI) built with PyTermGUI to display
cryptocurrency market data from CoinMarketCap in real time.

Features:
- Fetches live data from CoinMarketCap
- Configurable refresh interval
- Row limit
- Filters by coin name and price ranges
- Color-coded price indicators with up/down carets
- Screenshot capture
- Quit confirmation

Author: Hosni Zaaraoui
"""

import os
import sys
import time
from typing import Any
from bs4 import BeautifulSoup
import pytermgui as ptg
import requests

# -------------------------
# Application State
# -------------------------
STATE = {
    "refresh": False,  # Auto-refresh toggle
    "delay": 5,  # Delay between refreshes (seconds)
    "rows": 10,  # Number of rows to display
    "filter_name": None,  # Filter by coin name
    "filter_gtprice": 0,  # Show coins with price greater than this
    "filter_ltprice": 0  # Show coins with price less than this
}


# -------------------------
# UI Styling Helpers
# -------------------------
def _create_aliases() -> None:
    """Define custom color aliases for the theme."""
    ptg.tim.alias(name="griin", value="#66FF00")
    ptg.tim.alias(name="rid", value="#FF0055")


def _configure_widgets() -> None:
    """Configure global styles for windows and borders."""
    ptg.Window.styles.border = "!gradient(212)"
    ptg.Window.styles.border_focused = "!gradient(212)"
    ptg.Window.styles.corner = "!gradient(212)"
    ptg.Window.styles.corner_focused = "!gradient(212)"


# -------------------------
# Utility Modals
# -------------------------
def _confirm_quit(manager: ptg.WindowManager) -> None:
    """Show a confirmation modal before quitting the application."""
    yes_btn = ptg.Button("Yes", lambda *_: manager.stop())
    yes_btn.styles.highlight = "red"

    modal = ptg.Window(
        "[rid]Are you sure you want to quit?",
        "",
        ptg.Container(
            ptg.Splitter(
                yes_btn,
                ptg.Button("No", lambda *_: modal.close()),
            ), ),
    ).center()

    modal.select(1)
    manager.add(modal)


def screenshot(manager: ptg.WindowManager) -> None:
    """Take a screenshot of the current UI and save it as an SVG."""
    tempname = ".screenshot_temp.svg"

    def _finish(*_: Any) -> None:
        """Finalize screenshot save process."""
        manager.remove(modal)
        filename = field.value or "screenshot"

        if not filename.endswith(".svg"):
            filename += ".svg"

        os.rename(tempname, filename)
        manager.toast("[griin]Screenshot saved!", "", f"{filename}")

    title = sys.argv[0]
    field = ptg.InputField(prompt="Save as: ")

    manager.screenshot(title=title, filename=tempname)
    modal = manager.alert("[griin]Screenshot taken!", "", ptg.Container(field),
                          "", ["Save!", _finish])


# -------------------------
# Layout
# -------------------------
def _define_layout(id: int):
    """Define application layout slots."""
    layout = ptg.Layout()
    if id == 0:
        layout.add_slot(name="BANNER", height=5)
        layout.add_break()
        layout.add_slot(name="HEADER", height=3)
        layout.add_slot(name="FILTER", height=3)
        layout.add_break()
        layout.add_slot(name="BODY")
        layout.add_break()
        layout.add_slot(name="FOOTER", height=3)
    return layout


# -------------------------
# UI Sections
# -------------------------
def _define_banner():
    """Top banner with ASCII art title."""
    label = ptg.Label("""░█▀▀░█▀▄░█░█░█▀█░▀█▀░█▀▀
░█░░░█▀▄░░█░░█▀▀░░█░░▀▀█
░▀▀▀░▀░▀░░▀░░▀░░░░▀░░▀▀▀
""",
                      style="bold !gradient(212)")
    return ptg.Window("", label, box="EMPTY")


def _define_header():
    """Refresh controls: toggle, delay, and row count."""
    refresh = ptg.Checkbox(
        checked=False, on_toggle=lambda val: STATE.update({"refresh": val}))
    delay = ptg.InputField(prompt="Delay (s): ",
                           default=STATE["delay"],
                           on_change=lambda val: STATE.update({"delay": val}))
    rows = ptg.InputField(prompt="Rows : ",
                          default=STATE["rows"],
                          on_change=lambda val: STATE.update({"rows": val}))
    return ptg.Window(ptg.Splitter(refresh, delay, rows),
                      box="SINGLE_HORIZONTAL").set_title("REFRESH")


def _define_filters():
    """Filters for coin name and price range."""
    name = ptg.InputField(
        prompt="Name: ",
        default=STATE["filter_name"],
        on_change=lambda val: STATE.update({"filter_name": val or None}))
    price_gt = ptg.InputField(
        prompt="> Price: ",
        default=STATE["filter_gtprice"],
        on_change=lambda val: STATE.update({"filter_gtprice": val}))
    price_lt = ptg.InputField(
        prompt="< Price: ",
        default=STATE["filter_ltprice"],
        on_change=lambda val: STATE.update({"filter_ltprice": val}))
    return ptg.Window(ptg.Splitter(name, price_gt, price_lt),
                      box="SINGLE_HORIZONTAL").set_title("FILTERS")


def _define_body():
    """Main content area: displays cryptocurrency table."""
    url = "https://coinmarketcap.com/"
    html = requests.get(url=url).text
    soup = BeautifulSoup(html, "html.parser")
    coins_raw = soup.table.tbody.find_all(name="tr")

    # Apply row limit
    if STATE["rows"] > 0:
        coins_raw = coins_raw[:STATE["rows"]]

    # Apply name filter
    if STATE["filter_name"]:
        coins_raw = [
            coin for coin in coins_raw if STATE["filter_name"].lower() in
            coin.contents[2].p.string.lower()
        ]

    # Apply price filters
    if STATE["filter_gtprice"]:
        coins_raw = [
            coin for coin in coins_raw
            if STATE["filter_gtprice"] < float(coin.contents[3].text)
        ]
    if STATE["filter_ltprice"]:
        coins_raw = [
            coin for coin in coins_raw
            if STATE["filter_ltprice"] > float(coin.contents[3].text)
        ]

    # Create scrollable table
    win = ptg.Window(box="SINGLE_VERTICAL",
                     overflow=ptg.Overflow.SCROLL,
                     vertical_align=ptg.VerticalAlignment.TOP)
    win.lazy_add(
        ptg.Splitter("[bold !gradient(212)]NAME", "[bold !gradient(212)]PRICE",
                     "[bold !gradient(212)]1h%", "[bold !gradient(212)]24%",
                     "[bold !gradient(212)]MARKET CAP"))
    win.lazy_add("")

    # Populate rows with colored carets
    for coin in coins_raw:
        name = ptg.Label(f"[bold !gradient(212)]{coin.contents[2].text}",
                         parent_align=0)
        price = ptg.Label(f"[rid]▽ {coin.contents[3].text}",
                          parent_align=0) if coin.contents[3].find(
                              class_="icon-Caret-down") else ptg.Label(
                                  f"[griin]△ {coin.contents[3].text}",
                                  parent_align=0)
        last_hour = ptg.Label(f"[rid]▽ {coin.contents[4].text}",
                              parent_align=0) if coin.contents[4].find(
                                  class_="icon-Caret-down") else ptg.Label(
                                      f"[griin]△ {coin.contents[4].text}",
                                      parent_align=0)
        last_day = ptg.Label(f"[rid]▽ {coin.contents[5].text}",
                             parent_align=0) if coin.contents[5].find(
                                 class_="icon-Caret-down") else ptg.Label(
                                     f"[griin]△ {coin.contents[5].text}",
                                     parent_align=0)
        market_cap = ptg.Label(f"[bold]{coin.contents[7].p.contents[0].text}",
                               parent_align=0)

        win.lazy_add(ptg.Splitter(name, price, last_hour, last_day,
                                  market_cap))
    return win


def _define_footer(manager: ptg.WindowManager):
    """Footer buttons: refresh, screenshot, and quit."""
    quit_btn = ptg.Button("Quit", lambda *_: _confirm_quit(manager))
    quit_btn.styles.highlight = "red"
    refresh_btn = ptg.Button("Refresh Now", lambda *_: None)  # Placeholder
    shot_btn = ptg.Button("Screenshot", lambda *_: screenshot(manager))
    return ptg.Window(ptg.Splitter(refresh_btn, shot_btn, quit_btn),
                      box="SINGLE")


# -------------------------
# Main Application Entry
# -------------------------
def main():
    """Run the Crypto TUI Tracker."""
    with ptg.WindowManager() as manager:
        _configure_widgets()
        _create_aliases()
        manager.layout = _define_layout(0)

        # Add all sections to the layout
        manager.add(_define_banner())
        manager.add(_define_header(), assign="header")
        manager.add(_define_filters(), assign="filter")
        manager.add(_define_body(), assign="body")
        manager.add(_define_footer(manager), assign="footer")


if __name__ == "__main__":
    main()
