# 🛡️ SpecLint

> **Stop letting AI agents "hallucinate" your business logic. Validate your specs before you write a single line of code.**

`SpecLint` is an **agent skill** (`behavioral-spec-linter`) that acts as a **semantic linter** for software design documents (SDDs), requirement specs, API contracts, user stories, and implementation plans.

Instead of just generating code, it **stress-tests** your requirements with adversarial semantic perturbation to find the hidden ambiguities that lead to AI-generated bugs — and proposes minimal, testable revisions.

---

## ❌ The Problem: "The Guessing Game"

When you give a vague or ambiguous spec to an AI agent (Claude, GPT, Gemini):

1.  **The agent guesses**: it fills the logical gaps with its own assumptions.
2.  **The silent fail**: it writes 500 lines of technically correct but logically wrong code.
3.  **The debug loop**: you spend hours fixing bugs that all trace back to a single ambiguous sentence.

## ✅ The Solution: SpecLint

SpecLint breaks the cycle by forcing the spec to *prove* it is unambiguous **before** development starts. It treats a specification as a behavioral contract and finds the places where two competent implementers would produce different observable behavior.

### How it works

1.  **Scope** — derive a single shared **scenario set**: concrete probe cases that exercise the boundaries, conflicting clauses, concurrency, and time/limit interactions.
2.  **Perturb & implement** — produce blind `literal`, `operational`, and `adversarial` shadow implementations.
3.  **Judge** — compare scenarios, normalize candidate findings, and cluster semantically equivalent findings while rejecting merely similar or contradictory matches.
4.  **Report** — emit a compact stability profile and precise repairs. Optional reliability audits add repeated runs and finding-support metrics.

> The blind, multi-agent path is what reliably surfaces divergence. Run without subagents and SpecLint marks the review `degraded single-context (lower confidence)` rather than pretending the interpretations were independent.

---

## 📦 What's in here

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: the full review procedure and output contract. |
| `references/review-rubric.md` | Finding types, severity, review-resolution levels (`L1`–`L4`), evidence and revision standards. |
| `references/reliability-protocol.md` | Optional repeated-run finding matching and support-tier protocol. |
| `scripts/aggregate_reliability.py` | Deterministic aggregation for an optional reliability audit. |

---

## 🚀 Usage

Invoke the skill on any spec, design doc, or under-specified request:

```
Use behavioral-spec-linter to stress-test this specification and propose precise revisions.
```

You get back a structured review:

- a **verdict** and an uncalibrated **stability profile** showing scenario
  convergence, finding counts, highest severity, and review confidence;
- the interpretation **mode** (independent subagents vs. degraded single-context);
- a compact findings table with semantic identities, severity vectors, sources,
  and proposed contracts;
- **Well-specified** clauses that are already deterministic and should not be touched;
- **hidden assumptions**, **acceptance criteria**, and **open decisions**
  (product or architecture choices the source cannot resolve).

A worked end-to-end example is included at the bottom of [`SKILL.md`](SKILL.md).
Repeated runs are opt-in; ordinary reviews still use one three-role pass.

---

## 🎯 Design principle

SpecLint optimizes for **low false positives**. It does not nag about every conceivable missing feature, audit log, or best practice — it reports a problem only when two readings produce materially different behavior, or an omission forces an implementer to guess. Deliberate freedom (`MAY`, explicit ranges, implementation-defined choices) is not treated as a defect.
