# Security policy

A green scanner result reduces known risk; it does not prove that this project
is impossible to compromise.

## Report privately

Use this repository's private GitHub Security Advisory channel. Do not open a
public issue containing an exploit, personal data, credential, token or secret.
Include the affected revision, impact and redacted reproduction steps. Never
include live credentials.

## Response contract

`@qa` owns the release gate. `@data-engineer` owns database grants and RLS.
Only `@devops` may publish repository changes or releases. Credential rotation,
history rewriting, production scanning and database mutation require explicit
human approval.

Do not scan or exploit production, third-party systems or any target that is
not explicitly owned and authorized.

---
<!-- Output Signature -->
<!-- Agent: @qa v1.0.0 | Squad: system/security -->
<!-- Project: Django Communication Platform | Phase: enforcement -->
