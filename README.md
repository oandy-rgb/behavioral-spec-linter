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
2.  **Perturb & implement** — produce three *independent* interpretations of the spec — `literal`, `operational`, and `adversarial` — and have each emit a **shadow implementation**: a decision table over the same scenario set. When subagents are available, each runs blind, seeing only the original spec and its one role.
3.  **Judge** — compare the shadow tables cell by cell. Any scenario whose outcome differs across interpretations is a divergence — evidence that the original spec is ambiguous.
4.  **Report** — trace each divergence to the smallest source clause, classify it (`Ambiguity`, `Missing contract`, `Contradiction`, `Undefined term`, `Hidden assumption`, …), rank by impact, and propose a precise contract that converts directly into a test.

> The blind, multi-agent path is what reliably surfaces divergence. Run without subagents and SpecLint marks the review `degraded single-context (lower confidence)` rather than pretending the interpretations were independent.

---

## 📦 What's in here

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: the full review procedure and output contract. |
| `references/review-rubric.md` | Finding types, severity, review-resolution levels (`L1`–`L4`), evidence and revision standards. |
| `agents/openai.yaml` | Interface metadata (display name, default prompt). |

---

## 🚀 Usage

Invoke the skill on any spec, design doc, or under-specified request:

```
Use behavioral-spec-linter to stress-test this specification and propose precise revisions.
```

You get back a structured review:

- a **verdict** and a **stability score** (0–100), scoped to a declared review resolution;
- the interpretation **mode** (independent subagents vs. degraded single-context);
- a **findings table** ordered by severity, each with its source clause, divergent interpretations, impact, and a proposed contract;
- **Well-specified** clauses that are already deterministic and should not be touched;
- **hidden assumptions**, **acceptance criteria**, and **open decisions** (product policy the source can't resolve).

A worked end-to-end example is included at the bottom of [`SKILL.md`](SKILL.md).

---

## 🎯 Design principle

SpecLint optimizes for **low false positives**. It does not nag about every conceivable missing feature, audit log, or best practice — it reports a problem only when two readings produce materially different behavior, or an omission forces an implementer to guess. Deliberate freedom (`MAY`, explicit ranges, implementation-defined choices) is not treated as a defect.
