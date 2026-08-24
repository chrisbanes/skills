---
name: grounded-writing
description: Use when drafting or revising text for the user to publish or send, including short review comments, replies, and evidence-led technical prose.
---

# Grounded Writing

## Core principle

Make the reasoning visible at the scale the artifact supports. Build clear,
evidence-led writing in a conversational tone, then remove anything invented,
generic, or included only to imitate a personality.

## Procedure

1. Confirm that the text is for the user to publish or send. Apply this style at
   any length, including one-sentence review comments and replies. Do not apply
   it to an ordinary assistant reply, quoted source text, or prose attributed to
   someone else.
2. Read [the style profile](references/style-profile.md) before drafting or
   revising.
3. Establish the audience, purpose, requested format, supplied facts, and
   the user's actual position. Preserve the requested artifact shape rather than
   turning every deliverable into a blog post.
4. Resolve missing material before writing:
   - Look up discoverable public facts when the task calls for research.
   - If a missing personal opinion or experience would materially change the
     text, ask the user and stop drafting that part.
   - If the gap is minor, use a conspicuous placeholder or state the uncertainty
     honestly. Never invent a first-person claim, result, preference, or memory.
5. Choose the register from the style profile. Match the length and formality to
   the destination; short working comments should remain short.
6. Shape the reasoning before polishing sentences. Prefer a concrete problem or
   observation, explain the mechanism, support it with evidence or an example,
   acknowledge the important limit, state the practical consequence, and end on
   the clearest remaining point. Omit any stage the artifact does not need. For
   a short comment, this may be only the actionable point and one supporting
   fact.
7. Use the user's default language and regional conventions unless the request
   specifies otherwise. Keep paragraphs focused, mix sentence lengths, use first
   person only when grounded, and make headings earn their place.
8. Edit once for style and once for truth. Remove generic scene-setting,
   marketing language, repeated conclusions, decorative catchphrases, and
   unsupported certainty.

## Finish gate

Finish only when all of these are true:

- The result still satisfies the requested format and purpose.
- Every personal claim and substantive fact is supplied, verified, qualified,
  or clearly marked as missing.
- The argument is concrete enough to follow without promotional filler.
- Any caveat included changes the reader's understanding rather than acting as
  a disclaimer.
- Spelling and grammar follow the user's default language and regional
  conventions.
- The ending lands once and does not recap the whole piece.
- The prose sounds natural when read aloud, without an accumulation of borrowed
  phrases, rhetorical questions, asides, or emoji.

If a check fails, revise the draft. If the failure depends on an unknown personal
position, ask the user rather than smoothing over the gap.

## RED/GREEN agent scenarios

1. Direct case: a two-sentence review reply needs to report a fix and its
   validation. RED expands it into an essay or adds enthusiasm. GREEN leads with
   the outcome, names the relevant check, and stays within two sentences.
2. Novel case: a technical tutorial needs a warmer register. GREEN uses occasional
   questions or asides to guide the reader while keeping the explanation and code
   in control.
3. Novel case: a technical briefing benefits from two source observations. RED
   blends recognizable mannerisms from both authors. GREEN selects only the
   relevant structural techniques and keeps the user's natural tone.
4. No-change case: a one-sentence review comment is already direct, grounded, and
   appropriate for its audience. GREEN preserves it instead of expanding it.
5. Counterexample: the user asks the assistant to explain a technical concept for
   their own understanding, not to draft text for publication. GREEN answers
   normally and does not introduce first-person claims on the user's behalf.
