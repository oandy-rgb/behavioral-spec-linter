---
name: behavioral-spec-linter
description: Stress-test software requirements, product specifications, SDDs, API contracts, user stories, acceptance criteria, and implementation plans for ambiguity, contradictions, missing edge cases, and hidden assumptions before coding. Use when asked to review, lint, clarify, harden, validate, or compare interpretations of a specification, or when an implementation request is underspecified and semantic mistakes would be costly.
---

# Behavioral Spec Linter

Analyze a specification as a behavioral contract: find places where competent
implementers could produce different observable behavior, then propose minimal,
testable revisions. Read [references/review-rubric.md](references/review-rubric.md)
first — it defines the review resolutions, finding types, severity vectors,
identity and merge rules, evidence standards, and verdict derivation used
throughout this workflow.

## Workflow

1. Select and state the review resolution from the rubric (`L1`-`L4`,
   default `L2`).
2. Identify the document's scope, actors, inputs, state, outputs, side effects,
   ordering constraints, failures, and invariants. Build a compact behavior
   model from explicit statements only; mark every necessary inference as an
   assumption.
3. Derive a single shared **scenario set**: 5-9 concrete probe cases that
   exercise the boundaries, exceptional paths, and clause interactions at the
   selected resolution (e.g. a value at the limit, two clauses that may
   conflict, a concurrent pair, a time/day boundary). Every interpretation is
   tested against this same set so divergence is mechanically comparable, not
   a matter of wording.
4. Produce three independent interpretations:
   - **literal**: follow the narrowest defensible reading;
   - **operational**: infer what an implementer must decide to make it work;
   - **adversarial**: seek boundary cases, conflicting clauses, and
     alternative readings.
   Each interpretation MUST emit a **per-role table**: one row per scenario,
   columns `Scenario | Outcome | Forced assumption or decision`, stating the
   observable outcome — never prose hand-waving. The three tables cover the
   identical scenarios in the same order. Keep them separate; do not collapse
   them into the merged matrix yet.
5. Keep the interpretations independent. If the orchestrating agent's toolset
   can spawn agents (an Agent/Task tool is present), it MUST run the three
   roles as blind subagents and declare `Mode: independent subagents`, giving
   each subagent only the original specification, the shared scenario set, and
   its one role — never the other roles' output. Judge availability once, at
   the orchestrator, by tool presence only: having the tool but running
   single-context is not permitted, and a subagent lacking the tool does not
   flip the run to degraded. If subagents are unavailable, run separate passes
   without carrying assumptions between them and declare
   `Mode: degraded single-context (lower confidence)` — a single context
   role-playing three readings tends to reconcile them, so note that
   borderline divergences may be under-reported.
6. Build the **merged matrix**: one row per scenario, columns
   `Scenario | Literal | Operational | Adversarial`, each cell carrying that
   role's `Outcome` from its per-role table. A divergence is any scenario
   whose row differs across two or more interpretations; that scenario, traced
   to its source clause, is the seed of a finding. Compare observable
   behavior, not wording. Apply only the checks assigned to the selected
   resolution or lower by the rubric; record deeper concerns only as
   `Out-of-resolution observations`.
7. Trace each meaningful divergence to the smallest relevant source passage.
   Do not invent a source quote. If the issue is an omission, label it
   `Missing contract`.
8. Classify findings using only the rubric's defined types; choose the closest
   type instead of inventing a category. Normalize each candidate into the
   canonical identity fields and cluster with contradiction-aware semantic
   matching: label each pair `same`, `related`, `contradictory`, or
   `different`; merge only `same`, never on wording similarity alone. Preserve
   every member identity, source clause, and scenario ID in the cluster audit
   trail.
9. Propose the smallest revision that makes behavior deterministic, after
   passing the rubric's revision preflight. If implementation context is
   missing, present the revision as `Open decision — prerequisite: ...` rather
   than a definitive contract.
10. Convert definitive Critical or High revisions into concrete acceptance
    criteria or examples. For an unresolved architecture or product decision,
    provide decision criteria instead of acceptance criteria for an unselected
    alternative.

**Reliability audit (opt-in).** Only when the user explicitly requests a
reliability audit, repeated testing, or calibration: run two or more rounds
per [references/reliability-protocol.md](references/reliability-protocol.md),
holding the specification, resolution, scope, assumptions, and scenarios fixed
across rounds; assign stable cluster IDs and use
`python3 scripts/aggregate_reliability.py <artifact.json>` when available to
calculate support tiers and agreement. Standard reviews use one round and skip
all of this.

## Analysis Rules

- Treat paraphrase disagreement as evidence only when it changes observable
  behavior. Stylistic variation is not ambiguity.
- Do not claim rewritten versions are semantically equivalent before testing
  them; a rewrite can introduce its own defect.
- Separate facts explicitly stated by the document from inferred assumptions.
  Prefer a few defensible findings over a long list of speculative concerns.
- Preserve product intent; do not silently choose policy on the author's
  behalf. Apply the rubric's Deliberate Freedom, Evidence Standard, and
  feature-scope rules before reporting: explicitly permitted flexibility is
  not a defect, and adjacent product features the source does not imply belong
  under `Open decisions`, not findings.
- State when domain context, existing code, or an external contract resolves
  an apparent ambiguity.
- Do not escalate review resolution silently. List deeper questions as
  out-of-resolution observations unless the selected level is explicitly
  raised.
- Compare stability profiles only when scope, review resolution, scenario set,
  number of runs, and external assumptions are the same. A deeper review is a
  different measurement and does not prove that the specification regressed.
- For long documents, analyze sections separately, then run a cross-section
  pass for terminology drift and contradictions.
- If the user asks to revise the specification, preserve the original
  structure unless restructuring is necessary to remove ambiguity.

## Output

Start with:

- **Verdict**: exactly one of `Implementation-ready`, `Implementable with
  caveats`, or `Not implementable` — derived exactly from the rubric's
  Stability Profile table — followed by a one-sentence reason
- **Stability profile**: scenario convergence as `unanimous / total`;
  deduplicated open-finding counts by severity; highest severity; review
  confidence as `independent` or `degraded`; calibration as `uncalibrated`.
  Never emit a numeric stability score for an uncalibrated review.
- **Review resolution**: `L1`, `L2`, `L3`, or `L4`
- **Review scope**: the behavior and interfaces included in the profile
- **Mode**: `independent subagents` or `degraded single-context (lower
  confidence)`

Then report findings in severity order:

| Severity | Vector | Type | Identity | Sources / scenarios | Divergent interpretations | Proposed contract |
|---|---|---|---|---|---|---|

After the table, include (omitting empty sections):

1. **Well-specified**: specific clauses already deterministic at the selected
   resolution, named so the author does not revise them and risk introducing
   defects. Name the clause; do not list the whole document.
2. **Hidden assumptions**: assumptions required by at least one interpretation.
3. **Acceptance criteria**: testable examples for high-impact revisions.
4. **Open decisions**: product-policy or architecture-capability choices that
   cannot be resolved from the source.
5. **Out-of-resolution observations**: deeper-level concerns excluded from the
   verdict and finding counts.

In reliability-audit mode, append a compact `Reliability` section with Core,
Supported, and Contested cluster counts plus only disagreements that affect
the verdict or severity.

If no material ambiguity is found, say so directly, omit the findings table,
keep the required metadata, and list residual risks or missing external
context.

Before returning a full review, verify that it contains: a verdict and
complete stability profile with no uncalibrated numeric score; a review
resolution, review scope, and the interpretation mode; the findings table,
unless there are no material findings; a semantic identity and severity vector
for every finding; hidden assumptions when any interpretation required them;
acceptance criteria for every definitive Critical or High proposed contract;
and decision criteria for unresolved Critical or High open decisions. For a
user-requested brief review, keep the same fields but shorten their contents —
never replace the structure with an informal bullet list.

When comparing revisions, use:

| Version | Scenario convergence | Open findings C/H/M/L | Verdict | Resolution | Notes |
|---|---:|---|---|---|---|

Hold resolution and scope constant for the primary comparison. Report deeper
findings separately instead of mixing them into the same profile.

## Worked Example

A compact end-to-end run. The specification under review:

> Users can withdraw money from their account. A withdrawal is rejected if the
> account has insufficient funds. Withdrawals over $10,000 require manager
> approval. The daily withdrawal limit is $5,000.

**Shared scenario set**, chosen to probe the clause interactions:

- S1 `$6,000` single withdrawal, balance `$20,000`, nothing withdrawn yet today
- S2 `$12,000`, balance `$50,000`, nothing withdrawn yet today
- S3 `$4,000` now after `$4,000` earlier today, balance `$20,000`
- S4 `$11,000`, balance `$4,000`
- S5 two `$3,000` withdrawals at the same instant, balance `$5,000`

**Merged matrix** — the three blind per-role tables collapsed into one view,
each role tested against the same set:

| Scenario | Literal | Operational | Adversarial |
|---|---|---|---|
| S1 | Allowed (limit has no stated reject action) | Rejected (over daily limit) | Allowed |
| S2 | Approval-gated | Rejected (limit supersedes approval) | Allowed, no approval |
| S3 | Allowed | Rejected (limit is cumulative) | Allowed (limit is per-withdrawal) |
| S4 | Rejected; approval side effect unspecified | Rejected before approval | Approval requested, then rejected |
| S5 | Undefined (no concurrency rule) | One allowed, one rejected | Both allowed, account overdraws |

**Divergence read-off**: S1/S3 trace to "daily limit $5,000" (no reject verb;
per-withdrawal vs cumulative). S2 traces to the interaction of "over $10,000
require approval" with the "$5,000" limit — nothing under $5,000 can reach
$10,000, so the approval clause is either dead or the limit is per-withdrawal.
S4 agrees on the final rejection but diverges on validation precedence and
approval side effects. S5 traces to a missing concurrency contract.

**Condensed output:**

- **Verdict:** Not implementable — the core withdrawal eligibility contract is
  unresolved.
- **Stability profile:** scenario convergence `0/5`; open findings
  `C=0, H=2, M=1, L=0`; highest severity `High`; review confidence
  `independent`; calibration `uncalibrated`
- **Review resolution:** `L2` · **Review scope:** withdrawal accept/reject,
  limit enforcement, ordering, concurrency · **Mode:** independent subagents

| Severity | Vector | Type | Identity | Sources / scenarios | Divergent interpretations | Proposed contract |
|---|---|---|---|---|---|---|
| High | `major/core/recoverable/external/explicit` | Missing contract | account holder \| requests withdrawal \| daily-limit meaning and enforcement \| withdrawal is accepted, rejected, or approval-gated | "daily withdrawal limit is $5,000"; "over $10,000 require approval" / S1-S3 | advisory vs cumulative reject vs per-withdrawal approval | Open decision — prerequisite: product policy for limit accumulation, reset boundary, rejection behavior, and approval exemptions |
| High | `major/core/recoverable/external/explicit` | Missing contract | account holder \| concurrent withdrawals \| balance and limit conflict resolution \| both, one, or neither withdrawal commits | Missing contract / S5 | undefined vs one commits vs both commit | Open decision — prerequisite: required concurrency invariant and available storage/transaction capabilities |
| Medium | `moderate/boundary/transient/external/explicit` | Missing contract | account holder \| unfunded approval-sized withdrawal \| validation precedence \| approval may be created for a rejected withdrawal | "insufficient funds"; "over $10,000 require approval" / S4 | reject before approval vs approval then reject | Open decision — prerequisite: whether rejected withdrawals may create approval records |

**Well-specified:** "rejected if insufficient funds" deterministically fixes
the final decision for S4. Preserve that consequence while specifying whether
approval has any preceding side effect.

**Open decisions:**

- Select daily-limit semantics that make the `$5,000` limit and `>$10,000`
  approval rule jointly reachable or explicitly state that one supersedes the
  other.
- Define the concurrent invariant first; accept a mechanism only if the stated
  storage architecture can enforce it under simultaneous requests.
- Decide whether approval creation is an allowed side effect of a withdrawal
  that must ultimately be rejected.

This is the target shape: one shared scenario set, three blind tables,
divergence traced to source clauses, definitive repairs converted to tests,
and unresolved repairs exposed as explicit decisions.
