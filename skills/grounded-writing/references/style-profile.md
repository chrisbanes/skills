# Grounded writing style profile

This profile distils durable patterns from the published writing sampled below.
It is a decision guide, not a phrase bank. Treat each source as evidence for a
structural technique, not as a personality to imitate or average with the other
authors. Do not copy sentences or force every trait into one draft.

## Style characteristics

### Start from something concrete

Open with the problem, observation, changed belief, or release that gives the
piece a reason to exist. Personal context is useful when it explains why the
subject matters. Avoid broad claims about the industry, dictionary definitions,
and ceremonial introductions.

### Explain in a visible chain

Move from the familiar surface to the underlying mechanism and then to the
consequence. Introduce technical terms close to where they become useful. Place
code, measurements, tables, or small examples immediately after the claim they
support.

Contrasts often sharpen the reasoning: what the data appears to say versus what
it can actually tell us; the old architecture versus the new seam; the expected
benchmark result versus the measured one. Use a contrast only when it sharpens
the explanation.

### Let evidence change the claim

State the relevant setup for measurements and research. Qualify narrow evidence,
separate fact from inference, and include surprise only when the source material
supports it. A candid correction is stronger than defending an earlier
assumption.

Treat limitations as part of the argument. Name the boundary, explain its impact,
and continue with the narrower claim that still holds.

### Keep the relationship conversational

Use plain language, contractions, and first person where the source material
supports it. Address the reader directly when it makes an explanation easier to
follow. Rhetorical questions can introduce the reader's likely objection, but
answer them quickly.

Paragraphs are usually short and focused. A single-sentence paragraph can give a
turn or conclusion room to land. Sentence rhythm should vary naturally rather
than becoming uniformly clipped or elaborate.

### End on the remaining insight

Prefer a short consequence, decision rule, or reframing over a summary of every
section. Do not append a generic call to action unless the artifact needs one.

## Registers

| Register | Use when | Adjustment |
|---|---|---|
| Concise working note | Review comments, replies, status updates, and short messages | Lead with the actionable point, include only the context or evidence needed to support it, and stop. Do not manufacture an introduction or conclusion. |
| Restrained long form | Essays, product or architecture announcements, design documents, substantial emails, issue narratives, and release notes | Lead directly, keep humour light, use fewer rhetorical questions, and let one final sentence carry the ending. |
| Playful explanation | Tutorials and deep technical walkthroughs | Allow occasional reader questions, candid asides, or a well-placed emoji, while keeping evidence and code central. |

The requested format wins. An email should remain an email; release notes should
remain scannable; a design document should retain its decision and evidence
sections.

## Language and presentation

- Use the user's default language and regional conventions unless the request
  specifies otherwise. Do not treat the English-language source posts as a
  reason to override the language of the current conversation.
- Prefer concrete nouns and ordinary verbs to promotional adjectives.
- Use technical vocabulary precisely, with inline code for identifiers.
- Use headings to expose the argument, not to manufacture symmetry.
- Use lists and tables when they make comparisons or decision rules easier to
  scan.
- Keep punctuation natural. Do not use ellipses, dashes, parentheses, italics,
  or emoji as a substitute for a clear sentence.
- Preserve intentional humour and humility, but never imitate accidental typos
  or rough grammar from older posts.

## Patterns to remove

- Generic openings such as claims about a fast-moving world or an exciting era.
- Marketing words such as "revolutionary", "game-changing", or "seamless" when
  the evidence does not require them.
- Unsupported superlatives and certainty.
- A fake personal anecdote, opinion, emotion, benchmark, or lesson.
- Repetition of a distinctive construction merely to make the style recognizable.
- A conclusion that restates the introduction section by section.
- Excessive rhetorical questions, sentence fragments, parenthetical asides, or
  emoji.

## Source observations

Choose observations by the job the artifact needs to do. Do not privilege a
source because it is newer, more popular, or more distinctive.

- [Shopping Is Not a Category](https://chrisbanes.me/posts/shopping-is-not-a-category/)
  starts from a mundane data problem, explains the cross-system mechanism and
  its error boundary, then ends by reframing the original category.
- [Haze 2.0: A Pluggable Visual Effects Engine](https://chrisbanes.me/posts/haze-2.0/)
  moves directly from the old architectural constraint to the new seam,
  migration impact, limitations, and next step.
- [The Disappearing Middle](https://chrisbanes.me/posts/disappearing-middle-ai-software-apprenticeship/)
  states a changed personal position, uses research with explicit caveats,
  separates personas, and turns the argument into practical guardrails.
- [Should you use Kotlin Sequences for Performance?](https://chrisbanes.me/posts/use-sequence/)
  teaches the mechanism, tests an assumption, publishes the surprising result,
  and corrects the earlier belief without defensiveness.
- [Retaining beyond ViewModels](https://chrisbanes.me/posts/retaining-beyond-viewmodels/)
  represents the more playful tutorial register: reader questions, concrete
  lifecycle examples, code, and occasional asides.
- [Why you should understand (a little) about TCP](https://jvns.ca/blog/2015/11/21/why-you-should-understand-a-little-about-tcp/)
  starts with a real performance problem, introduces only the networking detail
  needed to explain it, shows the fix, and returns to the narrow lesson.
- [Things we learned about LLMs in 2024](https://simonwillison.net/2024/Dec/31/llms-in-2024/)
  shows how to synthesize a fast-moving subject: divide it into testable claims,
  link evidence close to each claim, quantify changes, and distinguish
  observation from judgment.
- [Normalization of deviance](https://danluu.com/wat/) accumulates concrete cases
  before naming the general mechanism. Use that pattern only when several cases
  materially strengthen the argument; do not inherit the post's length or
  sardonic register by default.

## Editorial reference

For technical explanations, use
[Patterns in confusing explanations](https://jvns.ca/blog/confusing-explanations/)
as a final review lens. Check that the draft has a specific audience, starts
concretely, uses realistic examples, introduces jargon only when it carries
meaning, supports substantive claims, and explains why the subject matters.
Apply the checks that fit the artifact; do not turn them into mandatory sections.
