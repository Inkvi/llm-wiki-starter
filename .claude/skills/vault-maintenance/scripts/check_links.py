#!/usr/bin/env python3
"""Structural lint over 20 Wiki/: links, orphans, index coverage, frontmatter.

Checks, in the order printed:
  1. Broken wikilinks     - every [[target]] resolves to a real file
  2. Orphans              - every page has at least one inbound wikilink
  3. Frontmatter          - `updated` present and inside the freshness window
  4. Statuses             - counts, and which pages are flagged stale/contradicted
  5. Index coverage       - every page reachable from index.md
  6. Oversized topics     - Topic pages past the ~400-line split threshold
  7. Stale deliverables   - sent documents that newer sources may have falsified

Check 7 catches a failure that is invisible otherwise: a deliverable asserting
something that a source ingested after the send contradicts. The sentence is
already written and the file already sent, so nothing else will tell you. A sent document is a snapshot, and the
vault keeps moving underneath it, so anything a deliverable draws on that was
updated after the send date is a candidate defect. It is a prompt to look, not a
verdict: most such hits will be harmless.

Two resolution rules earn their place here, because hand-rolled checkers keep
getting them wrong and then report hundreds of phantom failures:

  `\\|` inside a table cell IS an alias separator. In Obsidian the backslash
  escapes the pipe from the *table* syntax; the pipe still separates target from
  alias. Checkers that treat `\\|` as a literal report every aliased link in a
  table as broken. They always resolved fine. They always resolved fine.

  Only strip extensions you recognise. A naive splitext() truncates
  "Budget v2.1 final" at the dot before the "1", so the target
  never matches. This produces hundreds of spurious broken-link
  reports at once. vaultlib.split_ext handles it.

Exit status is always 0 - this is a report, not a gate.

Usage:
  python3 check_links.py [vault_root] [--days N] [--today YYYY-MM-DD]
"""

import argparse
import collections
import datetime
import os
import re
import sys

from vaultlib import KNOWN_EXT, find_vault_root, nfc, split_ext, walk_files

LINK_RE = re.compile(r"!?\[\[([^\[\]]+?)\]\]")
STRUCTURAL = {"index", "log"}  # no `status`/inbound expectations


def build_target_index(root):
    """Every file in the vault, keyed the several ways a wikilink might name it."""
    by_key = collections.defaultdict(list)
    for _, rel in walk_files(root):
        rel = nfc(rel)
        base = os.path.basename(rel)
        stem, _ = split_ext(base)
        rel_stem, _ = split_ext(rel)
        for key in (rel, rel_stem, base, stem):
            by_key[key].append(rel)
    return by_key


def link_target(raw):
    """Extract the target from a wikilink body, dropping alias/heading/block."""
    raw = raw.replace("\\|", "|")          # table-escaped pipe is still an alias sep
    target = raw.split("|")[0]
    target = target.split("#")[0].split("^")[0]
    return target.strip()


def resolves(target, by_key):
    t = nfc(target).strip()
    if not t:
        return True                        # [[#heading]] - same file
    if t.startswith(("http://", "https://", "mailto:", "obsidian://")):
        return True
    t = t.lstrip("./")
    if t in by_key:
        return True
    stem, _ = split_ext(t)
    if stem in by_key:
        return True
    tail = t.split("/")[-1]
    if tail in by_key:
        return True
    tail_stem, _ = split_ext(tail)
    return tail_stem in by_key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_root", nargs="?")
    ap.add_argument("--days", type=int, default=90,
                    help="freshness window for `updated` (default 90)")
    ap.add_argument("--today", help="override today's date, YYYY-MM-DD")
    args = ap.parse_args()

    root = args.vault_root or find_vault_root()
    wiki = os.path.join(root, "20 Wiki")
    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.date.today())
    cutoff = today - datetime.timedelta(days=args.days)

    by_key = build_target_index(root)
    pages = sorted(
        ap_ for ap_, _ in walk_files(root, "20 Wiki") if ap_.endswith(".md")
    )

    broken = []
    inbound = collections.defaultdict(set)
    for path in pages:
        rel = os.path.relpath(path, root)
        src = split_ext(os.path.basename(path))[0]
        text = open(path, encoding="utf-8").read()
        for m in LINK_RE.finditer(text):
            target = link_target(m.group(1))
            if not resolves(target, by_key):
                broken.append((rel, text[: m.start()].count("\n") + 1, target))
            tail = nfc(target.lstrip("./").split("/")[-1])
            key = split_ext(tail)[0]
            if key and key != src:
                inbound[key].add(src)

    print(f"=== BROKEN LINKS ({len(broken)}) ===")
    for rel, line, target in broken:
        print(f"  {rel}:{line}  ->  {target}")
    if broken:
        print(
            "\n  Note: the literal token [[wikilinks]] appears in log.md prose "
            "describing the convention. Those are expected and not real links - "
            "check each hit before chasing it."
        )

    print("\n=== ORPHANS (no inbound wikilink) ===")
    orphans = [
        os.path.relpath(p, root)
        for p in pages
        if split_ext(os.path.basename(p))[0] not in STRUCTURAL
        and not inbound.get(split_ext(os.path.basename(p))[0])
    ]
    print("\n".join(f"  {o}" for o in orphans) or "  none")

    missing_updated, stale = [], []
    statuses = collections.Counter()
    flagged = []
    for path in pages:
        rel = os.path.relpath(path, root)
        stem = split_ext(os.path.basename(path))[0]
        head = open(path, encoding="utf-8").read(4000)
        ms = re.search(r"^status:\s*\"?([A-Za-z]+)", head, re.M)
        statuses[ms.group(1) if ms else "(none)"] += 1
        if ms and ms.group(1) in ("stale", "contradicted"):
            flagged.append((rel, ms.group(1)))
        if stem == "log":
            continue
        mu = re.search(r"^updated:\s*\"?(\d{4}-\d{2}-\d{2})", head, re.M)
        if not mu:
            missing_updated.append(rel)
        elif datetime.date.fromisoformat(mu.group(1)) < cutoff:
            stale.append((rel, mu.group(1)))

    print(f"\n=== MISSING `updated` ({len(missing_updated)}) ===")
    print("\n".join(f"  {m}" for m in missing_updated) or "  none")

    print(f"\n=== `updated` OLDER THAN {args.days} DAYS (before {cutoff}) ({len(stale)}) ===")
    print("\n".join(f"  {r}  ({d})" for r, d in sorted(stale, key=lambda x: x[1])) or "  none")

    print("\n=== STATUS COUNTS ===")
    for k, v in statuses.most_common():
        print(f"  {k:<14} {v}")
    for rel, st in flagged:
        print(f"  FLAGGED: {rel} -> {st}")
    print(
        "  (index.md and log.md carry no `status` by design.\n"
        "   A page left deliberately stale should say so in its own body.)"
    )

    idx = ""
    for name in ("index.md",):
        p = os.path.join(wiki, name)
        if os.path.exists(p):
            idx += open(p, encoding="utf-8").read()
    idx_targets = {
        split_ext(nfc(link_target(m.group(1)).lstrip("./").split("/")[-1]))[0]
        for m in LINK_RE.finditer(idx)
    }
    missing_idx = [
        os.path.relpath(p, root)
        for p in pages
        if split_ext(os.path.basename(p))[0] not in STRUCTURAL
        and split_ext(os.path.basename(p))[0] not in idx_targets
    ]
    print(f"\n=== NOT REFERENCED FROM index.md ({len(missing_idx)}) ===")
    print("\n".join(f"  {m}" for m in missing_idx) or "  none")

    print("\n=== TOPIC PAGES OVER 400 LINES (split candidates) ===")
    big = []
    for path in pages:
        if f"{os.sep}Topics{os.sep}" in path:
            n = sum(1 for _ in open(path, encoding="utf-8"))
            if n > 400:
                big.append((os.path.relpath(path, root), n))
    print("\n".join(f"  {r}  ({n} lines)" for r, n in sorted(big, key=lambda x: -x[1]))
          or "  none")
    if big:
        print("  Splitting is the one structural change to make without asking - see SKILL.md.")

    # 7. Sent deliverables against sources that moved after the send.
    print("\n=== SENT DELIVERABLES WITH SOURCES UPDATED SINCE ===")
    updated_of = {}
    for path in pages:
        stem = split_ext(os.path.basename(path))[0]
        mu = re.search(r"^updated:\s*\"?(\d{4}-\d{2}-\d{2})",
                       open(path, encoding="utf-8").read(4000), re.M)
        if mu:
            updated_of[stem] = mu.group(1)

    any_drift = False
    for path in pages:
        text = open(path, encoding="utf-8").read()
        head = text[:4000]
        if not re.search(r"^type:\s*\"?deliverable", head, re.M):
            continue
        if not re.search(r"^status:\s*\"?sent", head, re.M):
            continue
        msent = re.search(r"^sent:\s*\"?(\d{4}-\d{2}-\d{2})", head, re.M)
        if not msent:
            print(f"  {os.path.relpath(path, root)}: status is sent but no `sent:` date")
            any_drift = True
            continue
        sent = msent.group(1)
        newer = set()
        for m in LINK_RE.finditer(text):
            key = split_ext(nfc(link_target(m.group(1)).lstrip("./").split("/")[-1]))[0]
            if updated_of.get(key, "") > sent:
                newer.add((key, updated_of[key]))
        if newer:
            any_drift = True
            print(f"  {os.path.relpath(path, root)}  (sent {sent})")
            for key, upd in sorted(newer):
                print(f"      {key} updated {upd}")
    if not any_drift:
        print("  none")
    else:
        print("  A prompt to look, not a verdict. Check whether the newer material\n"
              "  contradicts what the document asserts, then record it under the\n"
              "  deliverable's 'Known defects since sending' heading.")

    print(f"\n=== TOTALS ===\n  wiki pages: {len(pages)}")


if __name__ == "__main__":
    main()
