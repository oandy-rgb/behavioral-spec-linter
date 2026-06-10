# Behavioral Spec Linter Review Rubric

Use this reference to classify findings consistently.

## Review Resolution

Select one level before scoring. Include all lower levels.

| Level | Focus | Typical checks |
|---|---|---|
| L1 Core behavior | Whether the main feature has deterministic business behavior. | actors, triggers, inputs, outputs, primary state transitions, main failures |
| L2 Boundary contract | Whether callers can handle boundaries and exceptional paths consistently. | validation, status codes, permissions, retries, idempotency, time boundaries, concurrency outcomes |
| L3 System interaction | Whether components preserve behavior across integration and failure. | transaction boundaries, queues, delivery guarantees, partial failure, restore behavior, cross-service ordering |
| L4 Implementation contract | Whether independently built components can interoperate at the concrete technical boundary. | wire schema, serialization, clock precision, isolation semantics, key rotation, protocol framing |

Default to `L2`. Use `L1` for early product discovery. Use `L3` for high-risk
stateful or distributed workflows. Use `L4` only when the user requests an
implementation-ready technical contract or supplies enough architecture and
platform context to evaluate it.

Do not penalize a document for omitting details above the selected level. Record
important deeper concerns as `Out-of-resolution observations`; exclude them
from the score and severity counts.

## Score Comparability

A stability score is comparable only when all three remain fixed:

1. review resolution;
2. functional scope;
3. assumed external contracts and architecture.

A revision that only removes ambiguity, fixes a contradiction, or clarifies
existing behavior does **not** change functional scope; only adding, removing,
or repurposing a feature does. Bug-fix and clarification revisions therefore
remain score-comparable to the original at the same resolution.

When comparing revisions, score both at the same resolution first. A separate
deeper review may be useful, but it is a new measurement rather than evidence
that the revision regressed.

## Finding Types

| Type | Definition | Typical signal |
|---|---|---|
| Ambiguity | Two or more readings are supported by the same wording. | "active users", "after validation", unclear pronoun |
| Missing contract | Implementation requires a decision the document never addresses. | no timeout, default, tie-breaker, or failure behavior |
| Contradiction | Two clauses require incompatible behavior. | one section permits an action another forbids |
| Undefined term | A key noun, state, threshold, or unit lacks a stable definition. | "recent", "large", "owner", "day" |
| Unverifiable requirement | Compliance cannot be tested objectively. | "fast", "user-friendly", "secure" without criteria |
| Hidden assumption | A plausible implementation depends on an unstated fact. | one currency, one time zone, synchronous processing |
| Scope leak | Requirement unintentionally affects actors or data outside its stated scope. | tenant boundary or inherited permission unspecified |

## Severity

- **Critical**: could cause security exposure, data loss, regulatory breach, or
  irreversible incorrect state.
- **High**: likely to produce materially different business behavior, API
  compatibility, billing, authorization, or data writes.
- **Medium**: affects edge cases, recoverability, operational behavior, or a
  limited user flow.
- **Low**: minor inconsistency or testability issue with little behavioral
  impact.

Severity measures impact, not how confusing the sentence looks.

## Evidence Standard

A material finding must show:

1. the exact source passage, or `Missing contract`;
2. at least two plausible implementation behaviors;
3. an observable consequence;
4. a revision that closes the decision without adding unrelated policy.

Downgrade or omit a finding when one interpretation requires ignoring explicit
text, violating a defined term, or assuming implausible domain behavior.

For a `Missing contract`, also ask:

1. Must an implementer choose this behavior to deliver the stated feature?
2. Would two plausible choices change observable behavior or violate an
   explicit invariant?

If either answer is no, omit it or place it under `Open decisions`. Do not treat
every conceivable feature, operational control, or business rule as missing.

## Deliberate Freedom

Do not classify multiple outcomes as ambiguity when the specification clearly
permits them. Examples include:

- `MAY` behavior;
- "at most N", "between X and Y", or another explicit range;
- implementation-defined choices identified as such;
- unordered output explicitly described as unordered.

Only report the flexibility when it prevents interoperability, violates another
clause, or makes an explicit acceptance criterion impossible. Describe it as a
contract tradeoff, not noncompliance, and do not propose a narrower policy as
though it were required.

## High-Risk Checks

Apply relevant checks, not every check mechanically:

- authorization evaluated before or after resource lookup;
- information leaked through different error responses;
- transaction boundary and partial writes;
- duplicate requests and idempotency keys;
- concurrent updates, locking, and conflict resolution;
- retry ownership, limits, and backoff;
- null, empty, omitted, malformed, and duplicate inputs;
- pagination stability and sorting tie-breakers;
- clock source, time zone, daylight-saving behavior, and inclusive boundaries;
- numeric rounding, currency, units, overflow, and precision;
- deletion semantics, retention, restoration, and cascading effects;
- event ordering, delivery guarantees, deduplication, and replay;
- versioning, backward compatibility, and migration rollback.

## Revision Quality

A strong proposed contract:

- names the actor and triggering condition;
- uses a precise term already defined by the document;
- specifies ordering where ordering changes results;
- defines defaults and boundary values;
- states failure behavior and side effects;
- can be converted directly into a test.

Before proposing a contract, run a revision preflight:

1. **Conflict**: Does it contradict another requirement?
2. **Capability**: Can the stated platform implement it?
3. **Strength**: Does it silently require distributed atomicity, exact timing,
   stronger isolation, or permanent retention?
4. **Vocabulary**: Does it introduce an undefined term?
5. **Scope**: Does it add a product feature rather than clarify behavior?
6. **Resolution**: Is it necessary at the selected review level?

If a check cannot be answered from available context, state the prerequisite
and put the choice under `Open decisions`. Do not present a speculative
architecture choice as the only valid repair.

Do not add requirements merely because they are common good practice. For
example, audit logs, fees, notifications, retention periods, and administrative
approval flows require support from the source or a demonstrated risk tied to
the stated behavior.

Example:

Weak: "The request should fail when the token is invalid."

Strong: "The API MUST validate the bearer token before querying the requested
resource. For an absent, expired, or invalid token, it MUST return HTTP 401 with
error code `invalid_token` and MUST NOT reveal whether the resource exists."
