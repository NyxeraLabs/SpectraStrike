# Schema Diff

No persistent DB schema migration in Sprint 2.1.

## Before vs After
- Before: only ad-hoc MITRE lookup behavior in legacy paths.
- After: explicit ATT&CK relational service with typed tables/mappings and import sync.

## Migration notes
- Persistent DB wiring intentionally deferred; service contracts are now ready for storage integration.
