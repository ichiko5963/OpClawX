"""Slide bodies inserted after S007 and replacing old S008-009; Discord block replaces old S058."""
import re
from pathlib import Path

DIR = Path(__file__).parent


def _split(path: str) -> list[str]:
    t = (DIR / path).read_text(encoding="utf-8")
    parts = re.split(r"\n---\n\n(?=### S)", t.strip())
    return [p.strip() + "\n" for p in parts if p.strip()]


ALEX_OPENROUTER_LIST = _split("insert_alex_openrouter.md")
DISCORD_LIST = _split("insert_discord.md")
