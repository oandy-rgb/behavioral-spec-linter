---
name: behavioral-spec-linter
description: Stress-test software requirements, product specifications, SDDs, API contracts, user stories, acceptance criteria, and implementation plans for ambiguity, contradictions, missing edge cases, and hidden assumptions before coding. Use when asked to review, lint, clarify, harden, validate, or compare interpretations of a specification, or when an implementation request is underspecified and semantic mistakes would be costly.
---

# Behavioral Spec Linter

Analyze a specification as a behavioral contract. Find places where competent
implementers could produce different observable behavior, then propose minimal,
testable revisions.

## Workflow

1. Select and state the review resolution using
   [references/review-rubric.md](references/review-rubric.md):
   - `L1 Core behavior`;
   - `L2 Boundary contract` (default);
   - `L3 System interaction`;
   - `L4 Implementation contract`.
2. Identify the document's scope, actors, inputs, state, outputs, side effects,
   ordering constraints, failures, and invariants.
3. Build a compact behavior model from explicit statements only. Mark every
   necessary inference as an assumption. From it, derive a single shared
   **scenario set**: 5-9 concrete probe cases that exercise the boundaries,
   exceptional paths, and clause interactions at the selected resolution
   (e.g. a value at the limit, two clauses that may conflict, a concurrent
   pair, a time/day boundary). All interpretations are tested against this
   same set so divergence is mechanically comparable, not a matter of wording.
4. Produce three independent interpretations:
   - literal: follow the narrowest defensible reading;
   - operational: infer what an implementer must decide to make it work;
   - adversarial: seek boundary cases, conflicting clauses, and alternative
     readings.
   Each interpretation MUST emit a **shadow implementation**: a decision table
   over the shared scenario set with one row per scenario and the columns
   `Scenario | Outcome | Forced assumption or decision`. State the observable
   outcome each scenario produces under that reading; never leave a cell as
   prose hand-waving. The three tables must cover the identical scenarios in
   the same order.
5. Keep the interpretations independent. When subagents are available, give
   each subagent only the original specification, the shared scenario set, and
   one interpretation role — never the other roles' output. This blind,
   independent mode is the intended path and the only one that reliably
   surfaces divergence.
   If subagents are not available, run separate passes without carrying
   assumptions between them, but treat this as a **degraded single-context
   mode**: a single model role-playing three readings tends to reconcile them
   and hide real divergence. When operating this way, state in the output
   `Mode: degraded single-context (lower confidence)` and note that
   borderline divergences may be under-reported.
6. Compare the shadow implementations cell by cell over the shared scenario
   set. A divergence is any scenario whose `Outcome` differs across two or
   more interpretations; that scenario, traced to its source clause, is the
   seed of a finding. Compare observable behavior, not wording. Apply only
   checks at or below the selected resolution:
   - trigger and eligibility conditions;
   - validation precedence;
   - state transitions and data ownership;
   - ordering, concurrency, retries, and idempotency;
   - errors, status codes, recovery, and partial failure;
   - permissions, privacy, and security boundaries;
   - time, locale, units, precision, limits, and defaults;
   - compatibility and migration behavior.
7. Trace each meaningful divergence to the smallest relevant source passage.
   Do not invent a source quote. If the issue is an omission, label it
   `Missing contract` instead.
8. Classify findings with the rubric in
   [references/review-rubric.md](references/review-rubric.md).
   Use only these finding types: `Ambiguity`, `Missing contract`,
   `Contradiction`, `Undefined term`, `Unverifiable requirement`,
   `Hidden assumption`, and `Scope leak`. Choose the closest defined type
   instead of inventing a new category.
9. Propose the smallest revision that makes behavior deterministic. Before
   recommending it, check that it:
   - does not contradict another clause;
   - is implementable using known platform capabilities;
   - does not require stronger atomicity, timing, or consistency than the
     stated architecture can provide;
   - does not introduce new undefined terms or expand product scope.
   If implementation context is missing, present the revision as an open
   decision with its prerequisite rather than as a definitive contract.
10. Convert important revisions into concrete acceptance criteria or examples.

## Analysis Rules

- Treat paraphrase disagreement as evidence only when it changes observable
  behavior. Stylistic variation is not ambiguity.
- Do not claim rewritten versions are semantically equivalent before testing
  them; a rewrite can introduce its own defect.
- Separate facts explicitly stated by the document from inferred assumptions.
- Prefer a few defensible findings over a long list of speculative concerns.
- Preserve product intent. Do not silently choose policy on the author's behalf.
- Distinguish ambiguity from deliberate freedom. Language such as MAY, "at
  most", a stated range, or explicitly implementation-defined behavior can
  permit multiple conforming outcomes without being defective. Do not narrow
  that freedom unless it conflicts with another requirement or makes a stated
  client contract, invariant, or acceptance test impossible.
- Report a missing contract only when an implementer must choose that behavior
  to implement the stated scope, or when the omission creates a concrete
  correctness, security, interoperability, or testability risk.
- Do not introduce adjacent product features such as fees, notifications,
  auditing, currency conversion, retention, or administrator policy unless the
  source implies them or they are required to satisfy an explicit invariant.
  Put genuinely useful but optional ideas under `Open decisions`, not findings.
- When flexibility itself creates a material interoperability risk, report that
  risk without claiming the permitted alternatives violate the specification.
- State when domain context, existing code, or an external contract resolves an
  apparent ambiguity.
- Do not escalate review resolution silently. A newly detailed specification
  may expose L3 or L4 questions that were intentionally outside an earlier L2
  review. List them as out-of-resolution observations unless the selected level
  is explicitly raised.
- Compare stability scores only when scope, review resolution, and external
  assumptions are the same. A lower score at a deeper resolution does not prove
  that the specification regressed.
- For long documents, analyze sections separately, then run a cross-section
  pass for terminology drift and contradictions.
- If the user asks to revise the specification, preserve the original structure
  unless restructuring is necessary to remove ambiguity.

## Output

Start with:

- **Verdict**
- **Stability score**
- **Review resolution**: `L1`, `L2`, `L3`, or `L4`
- **Review scope**: the behavior and interfaces included in the score
- **Mode**: `independent subagents` or `degraded single-context (lower
  confidence)` — state which path produced the interpretations

The score is a communication aid scoped to the declared resolution, not a
scientific measurement:

- `90-100`: implementation-ready; only editorial issues remain.
- `70-89`: mostly stable; a few decisions or edge cases remain.
- `40-69`: material ambiguity likely to produce divergent implementations.
- `0-39`: core behavior or policy is not specified consistently.

Then report findings in severity order:

| Severity | Type | Source | Divergent interpretations | Impact | Proposed contract |
|---|---|---|---|---|---|

After the table, include:

1. **Well-specified**: clauses whose behavior is already deterministic at the
   selected resolution and should not be changed. State this so the author does
   not revise sections that are already unambiguous and risk introducing defects.
   Name the specific clause; do not list the whole document.
2. **Hidden assumptions**: assumptions required by at least one interpretation.
3. **Acceptance criteria**: testable examples for high-impact revisions.
4. **Open decisions**: policy choices that cannot be resolved from the source.

Omit empty sections. If no material ambiguity is found, say so directly and
list only residual risks or missing external context.

Before returning a full review, verify that it contains:

- a verdict and numeric stability score;
- a review resolution, review scope, and the interpretation mode;
- the findings table, unless there are no material findings;
- hidden assumptions when any interpretation required them;
- acceptance criteria for every Critical or High proposed contract;
- open decisions only for unresolved product policy.

Do not replace the required structure with an informal bullet list. For a
user-requested brief review, keep the same fields but shorten their contents.

When comparing revisions, use:

| Version | Stability | Resolution | Critical | High | Notes |
|---|---:|---|---:|---:|---|

Hold resolution and scope constant for the primary comparison. Report deeper
findings separately instead of mixing them into the same score.

## Worked Example

A compact end-to-end run. The specification under review:

> Users can withdraw money from their account. A withdrawal is rejected if the
> account has insufficient funds. Withdrawals over $10,000 require manager
> approval. The daily withdrawal limit is $5,000.

**Shared scenario set** (step 3), chosen to probe the clause interactions:

- S1 `$6,000` single withdrawal, balance `$20,000`, nothing withdrawn yet today
- S2 `$12,000`, balance `$50,000`, nothing withdrawn yet today
- S3 `$4,000` now after `$4,000` earlier today, balance `$20,000`
- S4 `$11,000`, balance `$4,000`
- S5 two `$3,000` withdrawals at the same instant, balance `$5,000`

**Shadow implementations** (step 4) — each role tested against the same set:

| Scenario | Literal | Operational | Adversarial |
|---|---|---|---|
| S1 | Allowed (limit has no stated reject action) | Rejected (over daily limit) | Allowed |
| S2 | Approval-gated | Rejected (limit supersedes approval) | Allowed, no approval |
| S3 | Allowed | Rejected (limit is cumulative) | Allowed (limit is per-withdrawal) |
| S4 | Rejected (insufficient funds) | Rejected (insufficient funds) | Pending approval |
| S5 | Undefined (no concurrency rule) | One allowed, one rejected | Both allowed, account overdraws |

**Divergence read-off** (step 6): every row diverges. S1/S3 trace to "daily limit
$5,000" (no reject verb; per-withdrawal vs cumulative). S2 traces to the
interaction of "over $10,000 require approval" with the "$5,000" limit — nothing
under $5,000 can reach $10,000, so the approval clause is either dead or the
limit is per-withdrawal. S4 traces to undefined check ordering. S5 traces to a
missing concurrency contract.

**Condensed output:**

- **Verdict:** Not implementable — daily-limit enforcement is unspecified and
  collides with the approval rule.
- **Stability score:** 24/100
- **Review resolution:** `L2` · **Review scope:** withdrawal accept/reject,
  limit enforcement, ordering, concurrency · **Mode:** independent subagents

| Severity | Type | Source | Divergent interpretations | Proposed contract |
|---|---|---|---|---|
| Critical | Contradiction | "require manager approval" ✕ "$5,000" limit | approval clause is dead vs limit is per-withdrawal | State the relation explicitly: daily limit is cumulative; a `>$10,000` withdrawal is approval-gated and still bound by (or explicitly exempt from) the cumulative limit |
| Critical | Missing contract | "daily withdrawal limit is $5,000" | advisory vs hard reject | A withdrawal exceeding the cumulative daily limit MUST be rejected `daily_limit_exceeded` |

**Well-specified:** "rejected if insufficient funds" — the one clause with a
stated consequence; all three readings reject S4 on funds (only `<` vs `<=`
boundary is open). Do not reword it while fixing the rest.

This is the target shape: one shared scenario set, three blind tables, divergence
traced to the smallest source clause, and findings that convert directly to tests.
