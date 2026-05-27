# Blueprint AI Test Identity Policy

Use a unique email for every monitored proof run unless the test is explicitly checking repeat-submit behavior.

## Rules

- Use plus-addressing when the mailbox supports it, for example `bennett+blueprint-20260527@franchiseki.com`.
- Keep the same email and phone for repeat-submit tests that are intended to prove one GHL contact is updated.
- Do not use a real prospect email in automated tests without approval.
- Do not delete or merge CRM records during tests. If cleanup is needed, write the contact ID and ask Bennett for approval.
- Every customer-proof run needs a run ledger entry with the blueprint URL, qualifier URL, GHL contact ID, and appointment ID when available.

## Acceptance

A clean test has one contact, one identity chain, and either one attached appointment or a labeled `Calendar partial` blocker.
