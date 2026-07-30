---
name: vault-setup
description: One-time onboarding for a fresh vault cloned from llm-wiki-starter. Use this when the user runs /vault-setup, says they just cloned or set up the vault, asks to configure or personalise the vault, asks what to do first, or when CLAUDE.md still carries an unconfigured setup marker. It interviews the user briefly, writes their life areas and sensitive-content decision into CLAUDE.md, creates the matching folders, and commits. Run it before the first ingest.
---

# Vault setup

This runs once, on a vault nobody has configured yet. Your job is to turn the shipped generic schema into *this person's* schema, then get out of the way.

Two things make this worth doing properly rather than fast:

**`CLAUDE.md` is read by you, not by them.** It is the contract every future session loads. Vague answers written into it become vague behaviour later, most visibly at filing time, when "where does this document go" has no good answer because the areas were never really decided.

**Do not interview from a blank page.** If the Inbox has anything in it, read it first and *propose* the answers. Confirming a draft takes seconds and produces better taxonomies than asking someone to invent one cold.

## 1. Check whether this has already run

```bash
grep -n "vault-setup:" CLAUDE.md
```

`<!-- vault-setup: pending -->` means go ahead. `<!-- vault-setup: configured ... -->` means this vault is already set up: say so, do not re-interview, and offer to change one specific thing instead (areas or the sensitive-content rule) if that is what they want.

Also confirm `./setup` has run, since it creates folders you are about to rely on:

```bash
ls -d "00 Inbox" Attachments .git 2>&1
```

If those are missing, tell them to run `./setup` first rather than doing its job by hand.

## 2. Survey the Inbox before asking anything

```bash
ls -la "00 Inbox/"
```

If it is empty, skip to the fallback questions in step 3.

If it is not empty, look at what is actually there. Filenames alone are weak evidence and they lie about dates, so open a few of the text ones and glance at the PDFs. **Read images and scans with your own vision**, never a CLI OCR tool, exactly as the schema requires for ingest. You are not ingesting yet: you only need enough to see what categories of life this person's documents fall into.

From that, draft two things:

- **A proposed life-area list.** Two lab reports, a lease and three pay stubs mean Health, Home, Finance. Propose only areas you have evidence for, plus `Misc`, and say which document suggested each one so the reasoning is visible and correctable.
- **A flag for anything sensitive.** Medical records, ID scans, financial statements, diary material. You need this for the second question and it is much better asked concretely.

## 3. Ask, briefly

Ask as few questions as will do. Two are usually enough. Use whatever question mechanism your harness gives you, or plain prose under Codex.

**Question 1: the life areas.** Present your proposal and invite edits. Explain what the answer controls: these become the subfolders of `10 Sources/` and the Area pages in `20 Wiki/`, and they are the buckets you will file everything into forever. Mention that adding one later is cheap but renaming one is not, because source paths are immutable once documents are filed under them.

The shipped defaults are Career, Finance, Health, Personal, Home & Car, Travel, Projects, Misc. Treat them as a fallback for an empty Inbox, not a recommendation. Most people need fewer.

**Question 2: sensitive content.** Ask it about what you actually found, not in the abstract. "Your inbox has what look like medical records and a passport scan. Should wiki pages synthesize their contents, or should those documents be filed and left out of the compiled layer?" Offer the middle option too, since it is often the real answer: synthesize health material but keep identity documents to a bare "this document exists and establishes X."

Whatever they choose, one rule is not up for negotiation and you should say so plainly: raw ID numbers, account numbers and credentials never get copied into a wiki page. The page cites the source and the number stays in the source.

**Only if the Inbox was empty**, add a third: ask roughly what they plan to keep here, so you have something to base an area list on.

Do not ask about clipping themes, qmd, Obsidian version, or anything else the schema already handles on demand. Those get decided when they first matter, and asking now just makes onboarding feel like a form.

## 4. Write the schema

Two spans in `CLAUDE.md` are marked for you. Replace what is between the markers and leave the markers in place, since they are how a later pass knows this vault is configured.

- `<!-- setup:areas:start -->` to `<!-- setup:areas:end -->` holds the sentence naming the life areas.
- `<!-- setup:sensitive:start -->` to `<!-- setup:sensitive:end -->` holds the Sensitive content section body.

Write the sensitive-content span as a **decision already made**, in their voice, not as a prompt. `Health documents are synthesized in full. Identity documents are filed and cited but never summarized beyond what they establish.` A future session must be able to act on that sentence without asking again, which is the entire point of writing it down.

Then flip the status marker at the top of the file to `<!-- vault-setup: configured YYYY-MM-DD -->` using today's date.

Then check nothing else still names the old defaults:

```bash
grep -n "Home & Car\|Travel, Projects\|Health, Finance, Career" CLAUDE.md
```

As shipped, the only occurrence is inside the areas span, so replacing that span is enough. Run the grep anyway, because the schema is meant to be edited and a later version may name areas elsewhere.

## 5. Make the folders match

Create a subfolder of `10 Sources/` for each chosen area, and **remove the shipped defaults they did not choose**. Empty unchosen folders are not harmless: they are filing targets, so a later session will eventually put something in `Travel/` for a vault whose owner does not travel, and the taxonomy quietly stops meaning anything.

Each shipped area folder contains a `.gitkeep`, so it is **not** empty and a plain `rmdir` fails. Worse, it fails quietly inside a loop, and you will report areas as removed when they are all still there. Check for real content, then remove the directory outright:

```bash
cd "10 Sources"
for d in "Home & Car" Career Travel Projects; do          # the ones NOT chosen
  [ -d "$d" ] || continue
  real=$(find "$d" -type f ! -name '.gitkeep' | wc -l | tr -d ' ')
  if [ "$real" = "0" ]; then rm -rf "$d"; echo "removed $d"
  else echo "KEPT $d, has $real real file(s)"; fi
done
```

The guard matters on a re-run or a vault someone has already started filing: never delete an area that has real documents in it, even if they now say they do not want it. Report it instead and let them move the files.

Verify against what they actually asked for, since a silent failure here is invisible until much later:

```bash
ls "10 Sources/"
```

Leave `Clippings/` alone. It is not a life area, it is where external captures go, and every vault needs it.

Do not create Area pages under `20 Wiki/` yet. Those are compiled from sources, and there are no sources. An empty `health.md` asserting nothing is worse than no page, because `check_links.py` will report it as an orphan and it will sit there looking like coverage.

## 6. Commit, then stop

```bash
git add -A && git commit -m "setup: configure vault schema"
```

A separate commit from the baseline one, so the diff shows exactly what onboarding decided on their behalf. That diff is worth pointing at: it is the first example of the review loop this vault runs on.

Then hand over, and do not keep going. **Do not ingest.** Tell them:

- what you wrote, in two lines: their areas, and their sensitive-content decision
- that the next step is to drop documents in `00 Inbox/` and say **"ingest my inbox"**
- that the first ingest reads `.claude/skills/vault-maintenance/SKILL.md`, which is where the actual procedure lives

Ingest is a bigger, more interesting diff and it deserves its own review rather than being buried under setup.

## Judgement calls

**Fewer areas beat more.** Eight near-empty areas make filing ambiguous, which is the failure this taxonomy exists to prevent. If they ask for many, suggest starting with the three or four that have documents today and adding others when something needs them.

**Push back on `Misc` as a habit.** It earns its place for genuine odds and ends. It becomes a problem when it turns into the default for anything mildly ambiguous, and the schema already forbids putting clippings there.

**Their words beat your proposal.** If someone wants `Boat` as a top-level area, that tells you something real about what they keep. Take it.

**Say what you were unsure about.** If a document could belong to two areas, mention it in the handoff rather than silently picking. It is the kind of thing that is cheap to settle now and annoying to unpick after fifty documents are filed.
