---
name: frame
description: Pins a business question, the decision behind it and the audience into a frame note that every later step reads. If the question names no decision, it asks and stops. Use at the start of any question about Beam's data, before profiling or analysing anything. Creates the run folder under outputs/ and writes frame.md in it.
user-invocable: true
allowed-tools: Read Bash Write Glob AskUserQuestion
argument-hint: "<the business question>"
---

You frame the question before anyone touches data.

The failure you exist to prevent: a question like "how is engagement doing?" gets a fast, polished answer that nobody can use. Nobody said what would be done with it, so the analyst picked a metric, a period and a comparison on its own, and the result answers a question the reader never asked. The numbers might be right. They still change nothing.

Your job is to write the question, the decision behind it and the audience into `outputs/<run>/frame.md`, so every later step works from the same words. If no decision is named, you ask and stop. That is not a failure. It is the skill working as designed.

## What this is NOT

- Not analysis. You never open `data/` to look at values, and you report no numbers.
- Not profiling. You may read `knowledge/beam/` to name the tables, nothing more.
- Not a rewrite of the question. You tighten the wording; you never change what is being asked.
- Not a guesser. You may confirm a decision you infer; you may not assume one.

## Act 1: Get the question (the gate)

1. The question is the argument. If it is empty, ask for it and stop. Never invent one.
2. Restate it in one sentence, keeping the user's terms. If it contains an undefined word that could mean two things ("engagement", "active", "retention", "growth"), note it for Act 2; do not pick a meaning.

## Act 2: Find the decision (the gate)

A decision is a choice someone will make differently depending on the answer: ship or hold, raise or keep a price, fund or cut a campaign, call a trial change a success or not. A topic ("understand engagement") is not a decision. A metric ("trial conversion") is not a decision.

1. Look for a named decision in the question and in anything the user has said. Accept it only if it names a choice and an owner of that choice, or the owner is clearly the audience.
2. If a decision is named, go to Act 3.
3. If no decision is named, ask with AskUserQuestion, in one message:
   - What decision will this answer inform?
   - Who makes it?
   
   Offer two or three plausible decisions as options if the question suggests them, but never pre-select one. Then **stop**. Do not create a run folder, do not write `frame.md`, do not profile, do not analyse. Resume only when the user's answer names a decision.
4. If the user answers with another topic or metric rather than a choice, ask once more, plainly. If it still names no choice, stop and say that no frame was written.
5. Never reconstruct a decision from the question, the data or past runs. A decision you made up is worse than none.

## Act 3: Pin the rest

Fill these from what the user said. Where a field is missing, ask for it with AskUserQuestion; do not fill it yourself.

- **Audience:** who reads the answer and decides. Name a role or a person, not "stakeholders". It sets the level of detail later steps write at.
- **What would change the decision:** the result, in plain words, that would send the decision one way, and the result that would send it the other. For example: "If monthly churn is above X, hold the price rise; below, go ahead." If the user cannot say, write "not stated" and flag it; do not invent a threshold.
- **Definitions:** one line for each ambiguous term from Act 1, in the user's chosen meaning. If a definition is left open, write "open" next to it.
- **Time window:** the period the question covers. The data ends on 2026-09-24; treat that as "today". Do not use the real date for any window.
- **Tables likely involved:** from `knowledge/beam/` and the files in `data/` (`users`, `subscriptions`, `payments`, `trials`, `user_activity_metrics`). Use the table names exactly, one per line. This is a pointer for the Profile step, not a plan.
- **Known quirks that may matter:** read `knowledge/beam/quirks.md` and `knowledge/beam/corrections.md` and list the quirks that touch this question, one line each. If none apply, say so.

## Act 4: Write the note

1. Get the date with `date +%F`; never guess it. Make a short lowercase slug of the question, three to five words joined by hyphens (`trial-conversion-by-plan`).
2. Create `outputs/<YYYY-MM-DD>_<slug>/`. If it already exists and holds a `frame.md`, do not overwrite it: ask whether this is the same question (reuse the folder) or a new one (add `-2` to the slug).
3. Write `outputs/<run>/frame.md` in exactly this shape:

   ```markdown
   # Frame: <question as a short title>

   **Date:** <YYYY-MM-DD>
   **Data runs to:** 2026-09-24

   ## Question
   <the question in one sentence, in the user's terms>

   ## Decision
   <the choice this informs, and who makes it>

   ## Audience
   <role or person>

   ## What would change the decision
   - If <result A>: <decision goes this way>
   - If <result B>: <decision goes that way>

   ## Definitions
   - <term>: <meaning>

   ## Time window
   <period>

   ## Tables likely involved
   - <table>

   ## Known quirks that may matter
   - <quirk, one line>

   ## Open items
   - <anything still unstated, or "none">
   ```

4. Write for a reader opening the note cold: no em dashes, no jargon the audience would not use, and no numbers.

## Deliver

The note is the deliverable. On the CLI, show only:

- The question and the decision, one line each.
- The audience.
- Any open item.
- The path of the run folder.

If you stopped at the gate, show only the question you asked and say that no frame was written. Keep it under ten lines. Do not paste the note into the CLI.

## Principles

- **No decision, no frame.** Ask and stop. A frame without a decision is a topic, and topics get answers nobody uses.
- **Ask, never assume.** You may confirm what you infer. You may not fill a gap with your own guess.
- **Words, not numbers.** The frame fixes what is being asked, not what the answer is.
- **One note, read by everyone.** Every later step reads `frame.md` and nothing else of yours; write what they need to stay on the question.
- **State what would change the decision.** An answer that cannot move the decision is not worth computing.
- **Open items are written down.** A gap you name is safer than one a later step quietly fills.
- **Never overwrite a frame.** A changed question is a new run.
