# LLM Wiki starter

A second brain that an LLM agent maintains for you. You drop documents in and ask questions; the agent files, summarises, cross-references, and corrects itself over time.

This is a working setup rather than a sketch. Every rule in it exists because its absence caused a specific, repeatable problem.

## The one idea

**Split what you captured from what was concluded.**

```
10 Sources/     immutable. Never edited. What actually arrived.
20 Wiki/        LLM-owned. Freely rewritten. What it currently means.
```

That single boundary is what makes the whole thing safe to hand to an agent. The wiki can be wrong, get corrected, be restructured, or be regenerated from scratch, and you lose nothing, because the sources underneath were never touched. Without it you get one pile of notes that an agent slowly edits into something you no longer trust.

Everything else in this kit follows from that split.

## What you get

```
setup                      One-time bootstrap script. Run it first.
CLAUDE.md                  The schema. The behavioural contract for every agent session.
AGENTS.md                  Symlink to CLAUDE.md, so Codex and others load the same contract.
.claude/skills/            The two skills: vault-setup (onboarding) and vault-maintenance.
.agents/skills/            The same two, symlinked, so Codex discovers them too.
.gitignore                 Markdown tracked, binaries ignored. Keeps the vault a readable diff.
00 Inbox/                  Staging. Ingest empties it.
10 Sources/                Immutable raw material, grouped by life area, plus Clippings/.
20 Wiki/                   Areas, Projects, People, Topics, Deliverables, index.md, log.md
20 Wiki/dashboard.base     Obsidian Bases dashboard: stale pages, active projects, people.
.claude/skills/vault-setup/
    SKILL.md               One-time onboarding: interviews you, writes your schema.
.claude/skills/vault-maintenance/
    SKILL.md               How to run an ingest or lint pass well, and the traps.
    references/            Four invented worked examples, one per failure pattern.
    scripts/               Three Python 3 scripts, no dependencies:
      inbox_triage.py        which Inbox items are genuinely new (hash, not filename)
      check_links.py         broken links, orphans, index gaps, stale frontmatter
      find_stubs.py          notes that embed a document but never transcribed it
```

## Setup

Two steps, about five minutes.

**1. Clone it and run the bootstrap.**

```bash
git clone --depth 1 https://github.com/Inkvi/llm-wiki-starter ~/my-vault
cd ~/my-vault
./setup
```

`setup` does only the mechanical work: checks the tools the vault needs, replaces this template's git history with a fresh one, creates the two gitignored folders a clone cannot carry, fetches [kepano's Obsidian agent skills](https://github.com/kepano/obsidian-skills), and makes a baseline commit. It is safe to run twice, and it refuses to touch a git history that is not this template's, so it cannot eat an existing vault.

On the tool check, it offers to install anything missing via whichever package manager it finds (Homebrew, apt, dnf, pacman):

| Tool | | Why |
|---|---|---|
| `git` | required | The review layer. Every agent edit becomes a diff you can read and revert. |
| `python3` | required | The three maintenance scripts. 3.8 or newer. |
| `pdftotext` | recommended | Triaging PDFs: finding which page holds a value, confirming a transcription. Without it every PDF has to be read by the agent's vision on each pass. |
| `qmd` | later | Local full-text and semantic search. Genuinely not needed yet: index-first navigation is fine until a few hundred sources, so skipping this is the sensible default. |
| Obsidian | optional | Only the viewer. Nothing breaks without it. |

Nothing is installed without asking, and it tells you before running anything under `sudo`. `--yes` accepts every offer for an unattended run, `--no-install` only reports what is missing. With no terminal to prompt on it declines everything rather than hanging, so piping it somewhere is safe. A missing required tool stops the script before it touches the vault.

Dropping the template's `origin` matters more than it looks. Left in place, one absent-minded `git push` would send your private notes to a public repo. You end up with no remote at all, which is the right default: the git history here is a local review layer, not a backup. Add a **private** remote later if you want one.

**2. Put a few documents in `00 Inbox/`, then let an agent finish the setup.**

Open the folder in your agent and ask for the `vault-setup` skill:

- Claude Code: `/vault-setup`
- Codex: `use the vault-setup skill`
- Anything else: `read .claude/skills/vault-setup/SKILL.md and follow it`

Both skills are registered for both harnesses out of the box, so neither one needs to be told where they live.

The step that cannot be scripted is deciding what this vault is *about*: which life areas you file under, and whether an agent may synthesize your medical records and ID scans into wiki pages or should only cite them. `vault-setup` reads whatever is in your inbox, proposes areas based on what it actually finds, asks you to confirm or edit, then writes the result into `CLAUDE.md`, creates the matching folders, and commits.

That is why the documents come first. Confirming "Health, Home, Finance, based on these five files" takes seconds; inventing a folder taxonomy from a blank page does not, and tends to produce areas that never get used.

It stops there deliberately, without ingesting, so your first ingest is its own reviewable diff.

**3. Ingest.**

```
ingest my inbox
```

That is the whole interface from here on. The schema and the maintenance skill carry the rest.

**Obsidian is optional.** It is only the viewer and editor, so nothing breaks without it, but wikilinks, graph view, and `dashboard.base` stop working. `dashboard.base` needs Obsidian 1.9 or later, where Bases is a core plugin.

## The daily loop

Three operations, all defined in `CLAUDE.md`.

**Ingest.** Drop anything into `00 Inbox/` and say "ingest my inbox". The agent hashes the inbox against what is already filed, reads what is new, files it under `10 Sources/`, distills it into the affected wiki pages, updates `index.md`, appends to `log.md`, and commits. Inbox ends empty.

**Query.** Ask a question in plain language. The agent reads `index.md` first, follows links into the relevant pages, and answers with citations. If the answer is durable (a comparison, a decision, an analysis) it files the answer back as a wiki page, so the vault gets smarter from being used.

**Lint.** Weekly-ish, say "run the lint". The agent checks for broken links, orphan pages, stale claims, contradictions between sources, and index drift. Mechanical problems get fixed; judgement calls get reported to you.

Ingest is the expensive operation by design, because that is where reading happens. Queries are cheap once the wiki is compiled.

## The parts that are easy to skip and shouldn't be

These two steps produce most of the value, and both are boring:

**Hash the inbox before reading anything.** Bulk exports and sync artifacts re-emit files you already filed, so a batch that looks substantial is often mostly duplicates. Reading first creates duplicate source notes, and because `10 Sources/` is immutable, cleaning those up needs you rather than the agent. `inbox_triage.py` also catches duplicates that arrive renamed, which comparing filenames does not.

**Reconcile every new primary document against what the wiki already claims.** Not just the interesting field, all of them. When a document arrives for something the wiki already holds second-hand, matching every field is what proves the two records describe the same event, and that is what licenses you to trust the one that disagrees. The field that fails to reconcile is the finding, and how it fails (a factor of ten, transposed digits, a swapped label) usually names the cause.

Four cases are written up in full in `.claude/skills/vault-maintenance/references/worked-examples.md`, deliberately set in an invented context so none of it reads as anyone's private history.

## Growing into it

- **Small vault**: index-first navigation is enough. Nothing else needed.
- **A few hundred sources**: add [qmd](https://github.com/tobi/qmd) for local full-text and semantic search. `CLAUDE.md` already documents the commands and the bootstrap.
- **Web capture**: Obsidian's official [Web Clipper](https://obsidian.md/clipper) feeds `00 Inbox/` directly. `CLAUDE.md` already carries the prompt-injection rule you need before auto-ingesting web content, which matters, because a clipped page can plant instructions that persist into your wiki.
- **Scheduled upkeep**: a weekly cron or GitHub Action that runs the lint keeps drift from accumulating.

## Known trade-offs

Worth knowing before you commit to this:

- **Hallucination compounds.** An error baked into a compiled page propagates through every page that links it. The lint pass is the mitigation, and it is a real mitigation, not a complete one. Read your diffs.
- **Synthesis is flat.** A recurring complaint from people who have compiled years of notes this way is that the output reads like a competent stranger wrote it: accurate, well-organised, and completely voiceless. Distillation defaults to consensus tone. Keep your own writing in `10 Sources/`, where nothing touches it.
- **You may learn less.** Filing and summarising is where insight forms, and delegating it is a genuine cost, not just a saving. This is the strongest objection to the whole pattern and it has academic support on cognitive offloading. The counter-position ("agents read, humans write") is respectable. This kit picks the delegation side deliberately, and you should know you are picking it.
- **Cloud sync plus git is undertested.** Running the vault in a synced folder with git as the audit layer does work, but iCloud in particular is documented to corrupt files when it fights git over locks. If `git status` hangs on a synced mount, it is usually slow rather than broken.
- **Agents delete things.** Keep git, review diffs, and require confirmation for deletions. The immutable-sources rule is your main structural protection here.

## Where this came from

Two sources, plus a handful of specific borrowings:

- **LLM Wiki**, Andrej Karpathy's gist (April 2026): immutable sources, an LLM-compiled layer on top, index-first navigation, and a lint pass as the correction mechanism.
- **Building a Second Brain** and **The PARA Method**, Tiago Forte: `Areas/` and `Topics/` are PARA's Areas and Resources, `Projects/` is Projects, and `status: archived` stands in for Archives. Forte's CODE loop gets split here: you Capture and Express, the agent Organises and Distills.

Borrowed pieces: the `stale`/`contradicted` page lifecycle from synthadoc, git-as-source-of-truth and the dedicated agent git identity from WUPHF, the Obsidian skills from kepano, qmd from Tobi Lütke, and the untrusted-web-capture rule from secure-llm-wiki. The `Deliverables/` page type is original to this kit: it tracks documents assembled out of the vault and sent to someone outside it, because the artifact is derivable but the judgement calls behind it are not, and a sent document is a snapshot that newer sources can quietly falsify.
