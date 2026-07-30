#!/usr/bin/env python3
"""Find source notes that embed a binary but never transcribe it.

Why this exists: a vault will report facts as "not recorded anywhere in Sources"
that it demonstrably holds. The document establishing the fact is filed, but its
source note is frontmatter, a one-line summary and an embed, with nothing
transcribed, so the content is invisible to search and to every later question.
The gap then gets recopied forward pass after pass.

So a stub note is worse than a missing one: it looks like coverage. It satisfies
every structural check (it exists, it is linked, it has frontmatter) while the
content stays invisible to search and to every future question.

This script ranks stubs by how likely they are to be worth reading: notes whose
wiki citations describe them vaguely come first, then large binaries, then the
rest. Read the top few each pass rather than trying to clear the backlog.

Usage:
  python3 find_stubs.py [vault_root] [--max-body N] [--limit N]
"""

import argparse
import collections
import os
import re
import sys

from vaultlib import find_vault_root, human_size, nfc, split_ext, walk_files

EMBED_RE = re.compile(r"!\[\[([^\[\]]+?)\]\]")
LINK_RE = re.compile(r"!?\[\[([^\[\]]+?)\]\]")
FM_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)

# Phrases in a wiki citation that admit the note was never read. If a stub is
# cited this way, the vault is openly carrying an unknown it could just resolve.
VAGUE = [
    "not transcribed", "contents not transcribed", "scan)", "(scan",
    "undated", "unspecified", "unknown", "garbled", "may be related",
    "exists", "presumably", "unclear",
]


def body_of(text):
    """Note text minus frontmatter and embed lines."""
    body = FM_RE.sub("", text)
    lines = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s or EMBED_RE.fullmatch(s):
            continue
        lines.append(s)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_root", nargs="?")
    ap.add_argument("--max-body", type=int, default=3,
                    help="non-blank body lines at or below which a note counts as a stub (default 3)")
    ap.add_argument("--limit", type=int, default=25)
    args = ap.parse_args()

    root = args.vault_root or find_vault_root()

    # How does the wiki talk about each source note?
    wiki_mentions = collections.defaultdict(list)
    for path, _ in walk_files(root, "20 Wiki"):
        if not path.endswith(".md") or os.path.basename(path) == "log.md":
            continue
        text = open(path, encoding="utf-8").read()
        for line in text.splitlines():
            for m in LINK_RE.finditer(line):
                key = split_ext(nfc(m.group(1).replace("\\|", "|").split("|")[0]
                                    .split("#")[0].strip().split("/")[-1]))[0]
                wiki_mentions[key].append((os.path.basename(path), line.strip()))

    stubs = []
    for path, rel in walk_files(root, "10 Sources"):
        if not path.endswith(".md"):
            continue
        text = open(path, encoding="utf-8").read()
        embeds = EMBED_RE.findall(text)
        if not embeds:
            continue                       # nothing to transcribe
        body = body_of(text)
        if len(body) > args.max_body:
            continue                       # has real content

        stem = split_ext(os.path.basename(path))[0]
        # Resolve embed sizes so big scans can be prioritised.
        total = 0
        kinds = set()
        for e in embeds:
            tgt = e.replace("\\|", "|").split("|")[0].split("#")[0].strip().lstrip("./")
            cand = os.path.join(os.path.dirname(path), tgt)
            if os.path.exists(cand):
                total += os.path.getsize(cand)
                kinds.add(os.path.splitext(cand)[1].lower())

        mentions = wiki_mentions.get(stem, [])
        # Dedupe: two links to the same note on one line would otherwise repeat it.
        vague, seen_lines = [], set()
        for pg, ln in mentions:
            if any(v in ln.lower() for v in VAGUE) and (pg, ln) not in seen_lines:
                seen_lines.add((pg, ln))
                vague.append((pg, ln))
        stubs.append({
            "rel": rel, "stem": stem, "n_embeds": len(embeds), "bytes": total,
            "kinds": ",".join(sorted(kinds)) or "?",
            "cited": len(mentions), "vague": vague,
        })

    # Vague citations first, then size.
    stubs.sort(key=lambda s: (not s["vague"], -s["bytes"]))

    print(f"=== STUB SOURCE NOTES ({len(stubs)} of them; showing up to {args.limit}) ===")
    print("Notes that embed a file but transcribe <= "
          f"{args.max_body} lines of body text.\n")
    for s in stubs[: args.limit]:
        flag = "  <-- wiki cites this vaguely" if s["vague"] else ""
        print(f"{s['rel']}{flag}")
        print(f"    {s['n_embeds']} embed(s) [{s['kinds']}], {human_size(s['bytes'])}, "
              f"cited from {s['cited']} wiki line(s)")
        for pg, ln in s["vague"][:2]:
            print(f"    {pg}: {ln[:150]}")
        print()

    if len(stubs) > args.limit:
        print(f"({len(stubs) - args.limit} more not shown - use --limit)")

    print(
        "Pick the two or three whose citations are vaguest and read those binaries.\n"
        "Clearing the whole backlog in one pass is not the goal; the goal is that\n"
        "'the vault does not know X' stops being said about documents the vault holds."
    )


if __name__ == "__main__":
    main()
