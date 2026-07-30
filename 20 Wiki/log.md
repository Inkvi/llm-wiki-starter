---
type: log
updated: 2026-07-30
---

# Log

Append-only record of every operation on the vault. Newest entries at the bottom.

Format: `## [YYYY-MM-DD] ingest|query|lint | Title`

Write each entry for a reader six months out who has forgotten everything. Cover what was found, what was fixed, what needs the owner's decision, and what carries forward unresolved. Recording *why* a judgement went the way it did is the part that pays off, because it lets a later pass re-test a conclusion instead of inheriting it.

Two headings worth keeping at the end of a lint entry:

- **Known issues carried forward** - what this pass could not resolve. The next pass treats these as claims to re-test, not facts to re-copy.
- **Needs the owner's attention** - decisions an agent should not make alone.

Your first entry gets appended by the first ingest. Nothing has been logged yet.
