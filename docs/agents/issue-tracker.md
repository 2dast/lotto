# Issue Tracker

## Tracker

- **Provider:** none
- **Location:** n/a
- **Tool or procedure:** n/a
- **Mirror Spec-backed tasks:** no

## Authority

`plan.json` is the source of truth for Spec-backed task descriptions, dependencies, and
validation. Tracker entries only mirror execution state when mirroring is enabled.

## Operations

- **Create:** n/a — this repository does not use an issue tracker
- **Read:** n/a
- **Update:** n/a
- **Complete:** n/a
- **Dependencies:** n/a — track via `plan.json` only

## Status Mapping

| Plan state | Tracker state |
|------------|---------------|
| Ready | n/a |
| In progress | n/a |
| Blocked | n/a |
| Complete | n/a |

## Constraints

- No issue tracker is used. `plan.json` alone tracks Spec-backed work.
- Do not store credentials, tokens, or other secrets in this document.
