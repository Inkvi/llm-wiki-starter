# Worked examples

**These are invented teaching scenarios.** Every person, document, number and outcome below is fictional. To keep that unmistakable, all four are set in the records of an imaginary amateur astronomy society rather than in anyone's personal vault. The situations are the point: each one is a mistake this kind of vault invites, written out far enough that you can recognise it when it happens to you.

- [1. The conflict that wasn't](#1-the-conflict-that-wasnt) - two sources disagreeing about a unit, not a fact
- [2. The control that also moved](#2-the-control-that-also-moved) - a surprising measurement checked against something that should not have changed
- [3. Vague citations as an index](#3-vague-citations-as-an-index-of-blind-spots) - the vault telling you in writing where it has not looked
- [4. What hashing does not catch](#4-what-hashing-does-not-catch) - a clean duplicate report that was wrong

---

## 1. The conflict that wasn't

**Situation.** A wiki page says the society logged **312 hours** of telescope time across the 2019 observing season. It was written from a member's end-of-season email. The society's official logbook is ingested a year later and gives the same season as **18,720**.

**The temptation.** A 60x disagreement between a casual email and an official logbook looks like an easy call: trust the logbook, correct the page, move on.

**What actually settled it.** Both records share a third figure: **104 observing sessions**. Divide each total by it.

| Source | Season total | Per session |
|---|---|---|
| Member's email | 312 | 3 |
| Official logbook | 18,720 | 180 |

Three hours a session is an ordinary evening. A hundred and eighty is eight days without stopping. And 180 minutes is exactly 3 hours, so the two records agree perfectly and the logbook is simply keeping minutes.

**Why this matters more than the number.** There was never a contradiction to resolve. Marking the page `contradicted`, or "correcting" 312 to 18,720, would have introduced an error where none existed. The actual defect was that neither the page nor its citation recorded a unit, so the next ingest would have hit the same confusion and might have resolved it the wrong way.

**What got written down.** The unit, in the page and in the source citation: *312 hours, from a logbook kept in minutes.* Recording the conversion is what stops the question being asked a third time.

**Pattern to take away.** Before declaring a conflict, check whether the two sources are measuring the same thing in the same units. Divide both by a figure they share and ask which result is physically possible. A suspiciously round ratio (60, 100, 12, 2.54) is usually a unit or a definition, not an error, and "corrected" unit mismatches are worse than the original because they look settled.

---

## 2. The control that also moved

**Situation.** A member's photometry run reports a target star changing brightness by **2.4 magnitudes** over a single night. That would be dramatic, and worth reporting to a wider group.

**The temptation.** Write it up. The number came straight from the member's own measurements of their own images, with no intermediary to garble it.

**What actually settled it.** The same image frames contain three comparison stars, catalogued as constant and included precisely so there is something to check against. Two of them moved by **2.1 and 2.3 magnitudes** across the same frames. A genuinely variable star does not drag its neighbours with it. Whatever changed was in the light path, not in the sky: thin high cloud, or dew forming on the optics as the night cooled.

**How it was written up.** The open item was *rewritten, not deleted*. It became "re-run the sequence on a dry, clear night using the same comparison stars" rather than "prepare a variable-star report". It was deliberately not closed, because the target may well vary. This night simply cannot say either way, and recording *why* the data is unusable is what stops someone re-deriving the same false result from the same frames later.

**Pattern to take away.** When a measurement surprises you, look inside the same data for something that should not have moved. If it moved too, your instrument moved. This is stronger than checking whether a number is plausible, because it can distinguish a real effect from an artefact using only what you already have. Where a source provides its own control, use it before you believe the headline.

---

## 3. Vague citations as an index of blind spots

**Situation.** For several passes, `log.md` carried "Known issues carried forward: we still do not know the focal length of the club's loaner telescope." Members kept asking, because it determines which eyepieces are worth buying.

**The temptation.** Treat it as genuinely missing and go looking for the fact: search the wiki, search filenames, maybe email the member who donated the instrument.

**What actually worked.** Running `find_stubs.py`, which ignores the question entirely and instead ranks source notes that embed a document but transcribe nothing, ordered by how *vaguely* the wiki cites them. The top hit was cited as "an old equipment invoice, contents not transcribed". Opening the embedded scan gave the aperture, the focal length, the mount type and the purchase date.

**Why the route matters.** The fact was not hard to find. It was hard to *notice*, because the note holding it passed every structural check: it existed, it was linked, it had frontmatter, it was in the index. The phrase that gave it away was in the wiki's own prose. Expressions like "contents not transcribed", "(scan)", "undated", "presumably" and "unclear" are the vault admitting in writing that nobody has looked, which makes them a searchable index of your own blind spots.

**Pattern to take away.** Do not hunt individual missing facts. Hunt the places where the wiki hedges, and read the two or three vaguest each pass. That clears more unknowns than chasing the specific question, and it finds the ones nobody thought to ask about. A stub note is worse than a missing document precisely because it looks like coverage.

---

## 4. What hashing does not catch

**Situation.** A member mails in a decade of scanned society newsletters. The Inbox fills up. `inbox_triage.py` runs first, as always, and reports almost everything as NEW.

**The temptation.** The triage script is the designated duplicate check, it came back clean, so start reading and filing.

**What actually happened.** Many of those newsletters were already in the vault. The member had re-scanned their paper copies at a higher resolution, so the files were not byte-identical to the ones already filed. Different bytes, different hashes, and the script correctly reported them as distinct files. **Hashing proves identity, not novelty.**

**What caught it.** Two cheap properties that survive a re-scan: page count and the text of the first line. Two PDFs with the same page count opening on the same sentence, differing only in file size, are the same document scanned twice. Spot-checking the largest few before creating any notes was enough.

**Pattern to take away.** A clean hash report means "no exact re-drops", which is narrower than "everything here is new". Re-scans, re-exports at different quality, and a photograph of a page you already hold as a scan all pass a hash comparison. Use the hash as the cheap first filter it is, then glance at page counts and opening lines before committing to a batch. Knowing what a check does *not* cover is part of trusting it.
