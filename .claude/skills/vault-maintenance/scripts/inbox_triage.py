#!/usr/bin/env python3
"""Triage 00 Inbox/ before reading anything.

Run this first, every time. Bulk exports and sync artifacts re-emit files the
vault already holds, so a batch that looks substantial is often mostly copies of
things already filed under 10 Sources/. Reading first means creating duplicate
source notes for documents the vault already had. Hashing takes a second and tells you which
items are byte-for-byte copies of something already filed.

Note the limit: this proves identity, not novelty. A document re-scanned at a
different resolution has different bytes and a different hash, so a clean report
means "no exact re-drops" rather than "everything here is new". For a large batch,
compare page counts and opening lines before creating notes.

Output per item:
  DUP  - identical content already filed; the existing path is shown. Safe to
         delete the Inbox copy once you have eyeballed the match.
  NEW  - genuinely new. Read it.

Usage:
  python3 inbox_triage.py [vault_root]
"""

import collections
import hashlib
import os
import sys

from vaultlib import find_vault_root, human_size, walk_files


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else find_vault_root()
    inbox = os.path.join(root, "00 Inbox")
    if not os.path.isdir(inbox):
        raise SystemExit(f"No '00 Inbox' under {root}")

    items = sorted(
        (ap, rel)
        for ap, rel in walk_files(root, "00 Inbox")
        if os.path.basename(ap) != ".writetest"
    )
    if not items:
        print("Inbox is empty. Nothing to ingest.")
        return

    # Size-first filtering. 10 Sources/ can hold gigabytes of scans, often on a
    # cloud-synced mount, and hashing all of it takes minutes. But byte-identical files must
    # have identical sizes, so only same-size candidates can possibly be
    # duplicates - which in practice is a handful of files instead of thousands.
    inbox_sizes = {}
    for ap, _ in items:
        try:
            inbox_sizes.setdefault(os.path.getsize(ap), []).append(ap)
        except OSError:
            pass

    print(f"Scanning 10 Sources/ for files matching the {len(inbox_sizes)} "
          f"distinct Inbox file size(s) ...", file=sys.stderr)
    candidates = collections.defaultdict(list)   # size -> [relpath]
    seen = 0
    for ap, rel in walk_files(root, "10 Sources"):
        seen += 1
        try:
            sz = os.path.getsize(ap)
        except OSError:
            continue
        if sz in inbox_sizes:
            candidates[sz].append((ap, rel))
    n_cand = sum(len(v) for v in candidates.values())
    print(f"  {seen} files scanned, {n_cand} size-match candidate(s) to hash",
          file=sys.stderr)

    # Hash only the candidates, grouped by size.
    by_hash = {}
    for sz, entries in candidates.items():
        for ap, rel in entries:
            try:
                by_hash.setdefault((sz, md5(ap)), []).append(rel)
            except OSError as e:
                print(f"  (skipped {rel}: {e})", file=sys.stderr)

    dups, news = [], []
    for ap, rel in items:
        name = os.path.basename(ap)
        try:
            sz = os.path.getsize(ap)
            key = (sz, md5(ap))
        except OSError as e:
            news.append((name, f"unreadable: {e}"))
            continue
        if key in by_hash:
            dups.append((name, by_hash[key][0]))
        else:
            news.append((name, human_size(sz)))

    print(f"\n=== INBOX: {len(items)} item(s) | {len(news)} new, {len(dups)} duplicate ===\n")
    for name, target in dups:
        print(f"DUP  {name}\n       already filed at: {target}")
    if dups:
        print()
    for name, info in news:
        print(f"NEW  {name}  ({info})")

    if dups:
        print(
            "\nDuplicates are byte-identical to files already under 10 Sources/. "
            "Confirm a couple of the matches, then delete the Inbox copies - the "
            "originals stay where they are. Note this in the log so the pattern is "
            "visible if it recurs (bulk re-exports tend to repeat)."
        )
    if news:
        print(
            "\nFor each NEW item: read it, then check whether the vault already "
            "describes the same underlying event from a secondary source. "
            "See the 'Reconcile' step in SKILL.md - that is where the real findings "
            "have come from."
        )


if __name__ == "__main__":
    main()
