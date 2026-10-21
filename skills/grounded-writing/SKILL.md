---
name: grounded-writing
description: Use when drafting or reviewing public developer documentation, other text the user will publish or send, or a user-owned draft under an explicit editorial review, including review comments, replies, and internal technical reports.
---

# Grounded Writing

## Core principle

Use Chris Banes's writing as the sole style model. Make the reasoning visible
at the scale the artifact supports. Preserve the user's meaning and evidence; remove anything invented, generic, or included
only to imitate a personality.

## Procedure

1. Establish scope and authority. Apply this skill to text the user will publish
   or send, at any length, or to an explicitly requested editorial review of
   their own draft. Identify whether the task permits drafting, editing, or
   recommendations only. Preserve the audience, purpose, and requested format.
   Exclude ordinary assistant replies, quoted source text, and prose attributed
   to someone else. For internal report reviews, apply truth and material-edit
   checks without imposing public-documentation style.
2. Establish the evidence and the user's actual position. Never invent personal
   opinions, experiences, results, preferences, memories, or certainty. Research
   discoverable public facts when research is in scope. If a missing personal
   position would materially change the text, ask and pause that part. Otherwise
   qualify uncertainty or mark a necessary gap conspicuously; do not add
   placeholders for details that do not affect the artifact's intended use.
3. Select detail for the reader. When public developer documentation compares
   options, check the observable difference, practical trade-off, and when to
   choose each separately. Preserve supported public contracts, shared guarantees (including
   compatibility), meaningful limitations, and context needed to interpret claims.
   Include implementation mechanics only when required for correct API use,
   necessary to distinguish a reader-facing choice, or explicitly requested.
   In reviews, explicitly recommend removing each irrelevant mechanic and name
   missing decision information rather than inventing it or asking for more
   internals. Distinguish behavior from implementation: preserve a supported
   return to another setting even if its timing is unverified; omit the internal
   timing term and delay unless their public or decision relevance is established.
   Verify uncertain contracts or relevance when research is in scope; otherwise
   flag material gaps rather than silently dropping or inventing behavior.
   Internal reports and design documents may need
   implementation and diagnostic detail; retain it for their intended use.
4. Read [the style profile](references/style-profile.md) and shape the argument
   before polishing. Use only the reasoning the artifact needs: a concrete
   observation, explanation, evidence, relevant limit, and practical consequence.
   A short reply may need just the actionable point and one supporting fact.
5. Review once for truth and once for style, including the headline and opening
   claim. Remove or qualify promotional framing and unsupported certainty.
   For material-only edits, identify the false claim or specific misreading that
   would prevent the intended use before changing anything. Optional polish is
   not a material fix. Add reproducibility details only when a stated claim or
   action depends on them; an internal report need not become a rerun protocol.
   Leave an adequate draft unchanged and briefly explain the relevant evidence,
   mechanism, or qualification that supports that conclusion.
6. Deliver the authorized result: write the requested text for a drafting task,
   apply fixes for an editing task, or give concrete recommendations for a
   review-only task. Drafting in the response does not authorize file edits.
   Resolve failed checks below within that boundary. If resolution needs an unknown personal position, ask rather
   than smoothing over the gap.

## Finish gate

Finish when the authorized draft, edit, or review:

- Preserves the requested purpose, format, and material-edit boundary.
- Grounds every personal claim and substantive fact in supplied or verified
  evidence, honest qualification, or a clearly identified necessary gap.
- Meets the reader-detail checks in step 3, retaining supported behavior and
  guarantees without irrelevant mechanics.
- Uses the appropriate register and language, with concrete reasoning, useful
  caveats, and no promotional filler or repeated conclusion.
