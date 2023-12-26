import re
from datetime import datetime
from html import escape
from typing import Optional

from anki.cards import Card
from aqt import gui_hooks, mw


def style_text(text: str):
    style = inline_css(
        # language=CSS
        """
        font-size: 30px;
        font-weight: bold;
        background-color: rgb(0, 0, 0, 0.1);
        color: rgba(255, 255, 255, 0.9);
        padding: 15px 0;

        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        """
    )
    code = f"""<div style="{escape(style)}">{escape(text)}</div>\n"""
    code += verticle_spacer()
    return code


def verticle_spacer():
    return """<div style="margin: 100px 0;"></div>\n"""


def inline_css(code):
    return re.sub(r"\s+", " ", code).strip()


def prepare(html: str, card: Card, context):
    if card.reps == 0:
        return style_text("First time seeing card!") + "\n" + html

    today = datetime.now().strftime("%Y%m%d")
    earliest_review = get_card_review_date(card)
    if earliest_review is None or today == earliest_review:
        return style_text("New card today!") + "\n" + html

    return html


def get_card_review_date(card: Card) -> Optional[str]:
    assert mw is not None
    assert mw.col is not None
    assert mw.col.db is not None

    # Query the revlog table for the earliest review of the card
    earliest_review = mw.col.db.scalar("SELECT id FROM revlog WHERE cid = ? ORDER BY id ASC LIMIT 1", card.id)
    if earliest_review:
        # Convert the timestamp to a date string
        return datetime.fromtimestamp(earliest_review / 1000).strftime("%Y%m%d")
    return None


gui_hooks.card_will_show.append(prepare)
