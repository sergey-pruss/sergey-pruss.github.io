#!/usr/bin/env python3
"""
MVP importer for Telegram channel posts.

What it does:
1) Reads latest messages from a Telegram channel via Telethon.
2) Builds draft post records (slug/date/title/description/body/source_url).
3) Saves JSON export + JS snippet you can paste into posts.js.
4) Optionally downloads media.

Usage:
  TG_API_ID=... TG_API_HASH=... python3 telegram_import_mvp.py \
    --channel @sergeypruss --limit 20

Optional:
  --download-media      Download photos/files into output folder
  --output-dir drafts/telegram
  --session tg_session
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    from telethon import TelegramClient
except ImportError:
    raise SystemExit(
        "Telethon is not installed.\n"
        "Install it with: pip install telethon"
    )


MONTH_EN = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

RU_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


@dataclass
class DraftPost:
    message_id: int
    slug: str
    date: str
    title: str
    description: str
    body: str
    source_url: str
    media_file: Optional[str] = None


def translit_slug(text: str, max_len: int = 64) -> str:
    text = text.lower()
    out = []
    for ch in text:
        if ch in RU_TO_LAT:
            out.append(RU_TO_LAT[ch])
        elif ch.isascii() and (ch.isalnum() or ch in "-_ "):
            out.append(ch)
        else:
            out.append(" ")
    s = "".join(out)
    s = re.sub(r"[^a-z0-9\\s-]", " ", s)
    s = re.sub(r"[\\s_-]+", "-", s).strip("-")
    return (s[:max_len].rstrip("-") or "post").lower()


def to_human_date(dt: datetime) -> str:
    return f"{dt.day} {MONTH_EN[dt.month]} {dt.year}"


def split_title_description(text: str) -> tuple[str, str]:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if not lines:
        return "Новый пост", ""
    title = lines[0]
    rest = " ".join(lines[1:]).strip()
    if not rest:
        rest = title
    if len(title) > 110:
        title = title[:110].rstrip() + "…"
    if len(rest) > 180:
        rest = rest[:180].rstrip() + "…"
    return title, rest


def js_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("`", "\\`")


async def build_drafts(args: argparse.Namespace) -> List[DraftPost]:
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    if not api_id or not api_hash:
        raise SystemExit("Set TG_API_ID and TG_API_HASH environment variables.")

    client = TelegramClient(args.session, int(api_id), api_hash)
    await client.start()

    entity = await client.get_entity(args.channel)
    username = getattr(entity, "username", None)

    messages = []
    async for msg in client.iter_messages(entity, limit=args.limit):
        if not getattr(msg, "message", None):
            continue
        if len(msg.message.strip()) < 5:
            continue
        messages.append(msg)

    # Oldest first for easier append to posts.js
    messages.reverse()

    drafts: List[DraftPost] = []
    used_slugs = set()

    for msg in messages:
        text = msg.message.strip()
        title, description = split_title_description(text)
        base_slug = translit_slug(title)
        slug = base_slug
        i = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{i}"
            i += 1
        used_slugs.add(slug)

        source_url = ""
        if username:
            source_url = f"https://t.me/{username}/{msg.id}"

        media_file = None
        if args.download_media and msg.media:
            media_dir = Path(args.output_dir) / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            saved = await client.download_media(msg, file=str(media_dir))
            if saved:
                media_file = str(Path(saved).relative_to(Path(args.output_dir)))

        drafts.append(
            DraftPost(
                message_id=msg.id,
                slug=slug,
                date=to_human_date(msg.date),
                title=title,
                description=description,
                body=text,
                source_url=source_url,
                media_file=media_file,
            )
        )

    await client.disconnect()
    return drafts


def save_outputs(drafts: List[DraftPost], output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    json_path = out / f"telegram-import-{stamp}.json"
    json_path.write_text(
        json.dumps([asdict(x) for x in drafts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    js_lines = []
    for d in drafts:
        js_lines.append(
            "  {slug:`%s`,date:`%s`,title:`%s`,description:`%s`},"
            % (
                js_escape(d.slug),
                js_escape(d.date),
                js_escape(d.title),
                js_escape(d.description),
            )
        )

    snippet_path = out / f"posts-snippet-{stamp}.txt"
    snippet_path.write_text(
        "Paste these lines at the top of POSTS in posts.js:\n\n" + "\n".join(js_lines) + "\n",
        encoding="utf-8",
    )

    print(f"Saved: {json_path}")
    print(f"Saved: {snippet_path}")
    print(f"Drafts: {len(drafts)}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MVP Telegram channel importer.")
    p.add_argument("--channel", required=True, help="Channel username/link/id, e.g. @sergeypruss")
    p.add_argument("--limit", type=int, default=20, help="How many latest messages to import")
    p.add_argument("--output-dir", default="telegram-import", help="Output directory for drafts")
    p.add_argument("--session", default="telegram_mvp", help="Telethon session name")
    p.add_argument("--download-media", action="store_true", help="Download attached media")
    return p.parse_args()


async def _main() -> None:
    args = parse_args()
    drafts = await build_drafts(args)
    save_outputs(drafts, args.output_dir)


if __name__ == "__main__":
    asyncio.run(_main())
