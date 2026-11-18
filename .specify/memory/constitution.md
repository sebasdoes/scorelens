# Scorelens Constitution (micro-project)

## Core Principles

### I. Static-only
One HTML file + vendored JS. No server-side logic, no secrets, no external CDNs at runtime.

### II. Accessible by design
High-contrast black on white; no information conveyed by color alone; large default note size. (User: achromatopsia.)

### III. Reuse infra
Existing oauth2-proxy + Pocket ID sidecar pattern (selfhosted-docker skill). No new auth plumbing.

### IV. Verify from outside
A deploy is done only when: nginx serves the app (verified on the proxy network), unauthenticated requests return 302 → id.akiha.nl, and no ports are published.

### V. Small scope ships
v1: file list from a mounted folder, score render, note-name toggle, size control. Playback/upload/edit are v2 candidates, not debt.

## Deployment policy
Deployed via the existing `abctools-web` nginx:alpine container (renamed `scorelens-web`) behind `scores-oauth2-proxy`; static content served read-only from this repo's `app/` and `files/` dirs.

## Governance
This constitution governs all features in this repo; amendments are documented here. Simplicity outranks features: anything not in an approved spec does not ship.

**Version**: 1.0.0 | **Ratified**: 2026-11-15 | **Last Amended**: 2026-11-15
