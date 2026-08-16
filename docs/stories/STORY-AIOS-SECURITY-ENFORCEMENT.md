# STORY-AIOS-SECURITY-ENFORCEMENT — Repository security gates

**Status:** InProgress
**Canonical story:** `/Users/sobral/AIOS/docs/stories/STORY-AIOS-SECURITY-ENFORCEMENT/spec/story.md`

## Scope

Add blocking Python dependency, secret-history and CodeQL gates; pin
supply-chain actions; configure weekly dependency updates; and publish a
private disclosure policy. No production systems are scanned or mutated.

## Acceptance evidence

- Production and development `pip-audit --strict` scans pass.
- Current-tree and full-history Gitleaks scans pass.
- Workflow YAML parses and all action references are immutable commit SHAs.
- Existing lint, typecheck and test gates pass.
