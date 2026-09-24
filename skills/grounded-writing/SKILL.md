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
4. In public developer documentation, explain observable behaviour, setting
   choices, trade-offs, and relevant limitations. Remove implementation, test,
   or diagnostic mechanics such as sampling thresholds, CPU masks, interpolation
   details, and cooldown timing. Include a mechanic only when it is required for
   correct API use, the mechanism itself is necessary to distinguish a
   reader-facing setting choice, or the user explicitly requests it. If the
   visible outcome informs the choice but the mechanism does not, explain the
   outcome without the mechanism. Do not ask to expand internal mechanics as a
   way to fill a public-documentation gap. Retain public contracts and the
   context needed to interpret claims. This boundary does not apply to internal
   design documents or technical reports.
5. Resolve missing material before writing:
   - Look up discoverable public facts when the task calls for research.
   - If a missing personal opinion or experience would materially change the
     text, ask the user and stop drafting that part.
   - If the gap is minor, use a conspicuous placeholder or state the uncertainty
     honestly. Never invent a first-person claim, result, preference, or memory.
6. Choose the register from the style profile. Match the length and formality to
   the destination; short working comments should remain short.
7. Shape the reasoning before polishing sentences. Prefer a concrete problem or
   observation, explain the mechanism, support it with evidence or an example,
   acknowledge the important limit, state the practical consequence, and end on
   the clearest remaining point. Omit any stage the artifact does not need. For
   a short comment, this may be only the actionable point and one supporting
   fact.
8. Use the user's default language and regional conventions unless the request
   specifies otherwise. Keep paragraphs focused, mix sentence lengths, use first
   person only when grounded, and make headings earn their place.
9. Edit once for style and once for truth. Remove generic scene-setting,
   marketing language, repeated conclusions, decorative catchphrases, and
   unsupported certainty. Treat the headline and opening claim as substantive:
   remove or qualify promotional framing that the supplied evidence does not
   directly support.
10. For a review that permits edits only for material clarity or truth problems,
   leave an adequate draft unchanged. Do not add a placeholder for an unverified
   detail unless that missing detail blocks the draft's intended use. Explain
   the material facts, mechanism, and qualification that make a no-change
   result appropriate; a bare “no edit needed” does not show that the checks
   were completed.

## Finish gate

Finish only when all of these are true:

- The result still satisfies the requested format and purpose.
- For reader-facing setting documentation, a developer can tell what changes,
  when to choose each setting, the practical trade-off, the public contract,
  and the meaningful limitation. Keep implementation mechanics out unless they
  are required for correct API use, the mechanism itself is necessary to
  distinguish the setting choice, or the user explicitly requests it. When an
  observable effect informs that choice but its mechanism is unnecessary,
  describe the effect rather than the mechanism.
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
