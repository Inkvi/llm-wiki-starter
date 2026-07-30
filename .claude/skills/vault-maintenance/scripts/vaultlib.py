"""Shared helpers for the vault-maintenance scripts.

Kept in one place because all three scripts need the same two things: find the
vault root, and normalise filenames. Filename normalisation matters more than it
sounds - macOS stores names in NFD (decomposed) while Obsidian writes wikilinks
in NFC (composed), so a Cyrillic or accented filename compares unequal to its
own link unless both sides are normalised. Every path that gets compared or used
as a dict key goes through nfc() first.
"""

import os
import unicodedata

SKIP_DIRS = {".git", ".obsidian", ".trash", ".firecrawl", "node_modules", "__pycache__"}

# Extensions we recognise as real file suffixes. Needed because splitext() will
# happily treat the ".1" in "Budget v2.1 final" as an extension and truncate
# the name, which silently breaks link resolution for any note with a dot in it.
KNOWN_EXT = {
    ".md", ".pdf", ".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".gif",
    ".webp", ".heic", ".txt", ".csv", ".json", ".doc", ".docx", ".xls", ".xlsx",
    ".base", ".canvas", ".apkg", ".mp3", ".mp4", ".m4a", ".zip", ".html",
}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def find_vault_root(start=None):
    """Walk up from this script until we find the vault marker (CLAUDE.md).

    Deliberately not a hardcoded absolute path: vault paths often contain
    spaces and sit on a cloud-synced mount, and hardcoding one breaks the moment
    the skill is copied or the mount is renamed.
    """
    if start is None:
        start = os.path.dirname(os.path.abspath(__file__))
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, "CLAUDE.md")) and os.path.isdir(
            os.path.join(d, "20 Wiki")
        ):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit(
                "Could not find the vault root (a directory with CLAUDE.md and '20 Wiki'). "
                "Pass it explicitly as the first argument."
            )
        d = parent


def split_ext(name):
    """splitext, but only for extensions we actually recognise."""
    stem, ext = os.path.splitext(name)
    if ext in KNOWN_EXT:
        return stem, ext
    return name, ""


def walk_files(root, subdir=None):
    """Yield (abspath, relpath-from-vault-root) for every real file."""
    base = os.path.join(root, subdir) if subdir else root
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn == ".DS_Store" or fn.startswith("._"):
                continue
            ap = os.path.join(dirpath, fn)
            yield ap, nfc(os.path.relpath(ap, root))


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
