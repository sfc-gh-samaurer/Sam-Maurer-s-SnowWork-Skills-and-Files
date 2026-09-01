# Security Policy — PS Engagement Dashboard

Last reviewed: April 8, 2026

## Dependency Inventory

### Runtime Dependencies (v2 — SPCS React)

| Package | Version | License | Weekly Downloads | Attack Surface | CVE History |
|---------|---------|---------|-----------------|----------------|-------------|
| **react** | 19.2.4 | MIT | 25M+ | RSC Flight protocol (server) | CVE-2025-55182 (CVSS 10.0), CVE-2025-55184, CVE-2025-67779, CVE-2026-23864 — all patched |
| **next** | 16.2.3 | MIT | 6M+ | App Router, API routes, SSR | CVE-2025-66478 (duplicate of React RSC RCE) — patched. 16.2.3 also fixes HTTP request smuggling, disk cache growth, and CSRF bypasses |
| **@tremor/react** | 4.0.0-beta-v4.4 | Apache 2.0 | 70K+ | UI components only, no network/fs. v4 beta adds React 19 support via @headlessui/react 2.2 | None reported |
| **@nivo/bar** | 0.99.0 | MIT | 200K+ (combined) | SVG/Canvas rendering only. v0.99 adds React 19 peer dep support | None reported |
| **@nivo/line** | 0.99.0 | MIT | (combined) | SVG/Canvas rendering only | None reported |
| **@nivo/pie** | 0.99.0 | MIT | (combined) | SVG/Canvas rendering only | None reported |
| **snowflake-sdk** | 2.4.0 | Apache 2.0 | 150K+ | Snowflake wire protocol, OAuth | Maintained by Snowflake Inc. |
| **tailwindcss** | 3.x | MIT | 14M+ | **Build-time only** — zero runtime JS | None reported |

### Transitive Dependencies of Note

| Package | Via | Risk | Stance |
|---------|-----|------|--------|
| **d3** (v7) | @nivo/* | Low — most audited viz library in ecosystem | Pin via lockfile |
| **recharts** (v2.15) | @tremor/react | Low — mature React charting library | Pin via lockfile |
| **@headlessui/react** (v2.2) | @tremor/react v4 | Low — accessibility primitives, maintained by Tailwind Labs | Pin via lockfile |

### Container Base

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.22.0+ (LTS) | Jan 2026 security release applied |
| **Alpine Linux** | 3.21+ | Minimal attack surface (~5MB base) |

---

## CVE Analysis

### Critical: React Server Components RCE (CVE-2025-55182)

- **CVSS**: 10.0 (Critical)
- **Disclosed**: December 3, 2025
- **Type**: Unauthenticated RCE via prototype pollution in RSC Flight deserialization
- **Exploit reliability**: Near 100%, no authentication required, default configs vulnerable
- **Active exploitation**: Confirmed by Unit 42 (Palo Alto), Microsoft, Datadog starting Dec 5, 2025
- **Observed post-exploitation**: Web shells (fm.js), Auto-color backdoor (PAM hijack), Mirai loaders, crypto miners
- **Threat actors**: UNC5174, North Korean and Chinese groups
- **CVE-2025-66478**: Initially assigned to Next.js separately, later rejected as duplicate of CVE-2025-55182
- **Patched in**: React 19.0.1, 19.1.2, 19.2.1; Next.js 16.0.7+
- **Our minimum version**: React 19.2.4, Next.js 16.1.6

**Why 19.2.4 and not 19.2.1**: Follow-up DoS vulnerabilities (CVE-2025-55184, CVE-2025-67779, CVE-2026-23864) were discovered through Jan 2026, each bypassing the previous patch. The Jan 26, 2026 release (19.0.4 / 19.1.5 / 19.2.4) addresses all known variants.

**Our mitigation posture**:
1. Pinned to safe versions (19.2.4+)
2. RSC used for layout rendering only — no server actions or functions exposed to external/untrusted input
3. SPCS public endpoint has Snowflake OAuth gating — unauthenticated requests never reach the Node.js process
4. `npm audit` runs at Docker build time and fails on critical/high findings

### High: Node.js January 2026 Security Release (8 CVEs)

| CVE | Severity | Impact | Applies to us? |
|-----|----------|--------|----------------|
| CVE-2025-55131 | High | Buffer memory leak via `vm` module race condition | **No** — we don't use the `vm` module |
| CVE-2025-55130 | High | Permissions model bypass via symlinks | **No** — we don't use `--experimental-permission` |
| CVE-2025-59465 | High | HTTP/2 crash via malformed HEADERS frame | **No** — SPCS ingress terminates HTTP/2; our container serves HTTP/1.1 on port 8080 |
| CVE-2025-59466 | Medium | AsyncLocalStorage stack overflow crash | **Low risk** — no deeply nested user input. Next.js uses ALS internally but input depth is bounded |
| CVE-2025-59464 | Medium | TLS cert memory leak | **No** — we don't process TLS client certificates |
| CVE-2026-21636 | Medium | Unix Domain Socket permission bypass | **No** — permissions model not used |
| CVE-2026-21637 | Medium | TLS PSK/ALPN callback DoS | **No** — no custom TLS callbacks |
| CVE-2025-55132 | Low | fs.futimes permission bypass | **No** — permissions model not used |

**Our minimum version**: Node.js 22.22.0 (LTS, all 8 CVEs patched)

### Awareness: September 2025 npm Supply Chain Attack

- **What happened**: Attacker phished an npm maintainer, published trojanized versions of 18 packages including `chalk` and `debug` (combined 2.6B weekly downloads). The "Shai-Hulud" worm used stolen npm tokens to self-replicate across 500+ packages.
- **CISA alert issued**: Yes — recommended pinning to pre-September 2025 releases and rotating credentials.

**Our mitigation posture**:
1. Neither `chalk` nor `debug` is a direct dependency of our stack
2. `package-lock.json` committed to repo — reproducible builds
3. `npm ci` used in Docker builds (lockfile-only, no resolution)
4. No `postinstall` scripts from any dependency (verified)
5. All transitive dependencies auditable via `npm ls --all`

### Library-Specific Assessment

#### Tremor (@tremor/react) — No known CVEs

- Apache 2.0 licensed, maintained by tremor.so
- Built on Radix UI (WorkOS-backed) + Recharts + Tailwind CSS
- Copy-paste component model — we own the source code
- **Zero runtime network calls**, no filesystem access, no native modules
- No npm advisories as of April 2026

#### Nivo (@nivo/*) — No known CVEs

- MIT licensed, maintained by Raphaël Benitte (active, regular releases)
- Built on D3.js v7 — the most battle-tested visualization library
- **Pure SVG/Canvas rendering**, no network calls, no filesystem access, no native modules
- D3 v7 has no known CVEs as of April 2026
- No npm advisories on any @nivo/* package as of April 2026

#### Tailwind CSS — No known CVEs

- MIT licensed, maintained by Tailwind Labs (well-funded, full-time team)
- **Build-time only** — produces pure CSS, zero runtime JavaScript
- No attack surface at runtime
- No npm advisories as of April 2026

#### snowflake-sdk — Snowflake-maintained

- Apache 2.0, maintained by Snowflake Inc.
- OAuth token authentication (token injected by SPCS, never stored in container image)
- Standard connector used across all Snowflake SPCS Node.js services
- Patching handled by Snowflake's release cycle

---

## Security Maintenance Policy

### Automated (CI/CD — every build)

- `npm audit --audit-level=high` — Docker build fails if high/critical CVEs found
- `npm ci` — lockfile-only installs, no resolution drift
- Docker base image `node:22-alpine` — OS-level patches via weekly rebuild

### Weekly

- Docker image rebuild from `node:22-alpine` latest — picks up Alpine security patches
- Automated dependency check via `npm outdated` (CI job, report only)

### Monthly

- Review `npm outdated` output for dependency drift
- Check React/Next.js security advisories at [react.dev/blog](https://react.dev/blog)
- Check Node.js security releases at [nodejs.org/en/blog/vulnerability](https://nodejs.org/en/blog/vulnerability)
- Review Snowflake SDK release notes

### Quarterly

- Full dependency tree audit (`npm ls --all`)
- Review Nivo and Tremor changelogs for security-related changes
- Rebuild Docker image from scratch (not cached layers)
- Update this document

### On CVE Disclosure

| Severity | Target | SLA |
|----------|--------|-----|
| Critical/High in React, Next.js, Node.js, snowflake-sdk | Patch and redeploy | 24 hours |
| Critical/High in Nivo, Tremor, D3, Radix | Patch and redeploy | 1 week |
| Medium in any runtime dependency | Batch into monthly review | 30 days |
| Low / build-time only | Batch into quarterly audit | 90 days |

### Supply Chain Controls

1. **Lockfile committed**: `package-lock.json` in git — every build is reproducible
2. **No floating versions**: All dependencies use exact version pins in `package.json`
3. **No postinstall scripts**: Verified — no dependency runs arbitrary code on install
4. **Minimal dependency tree**: Tremor + Nivo + snowflake-sdk — no utility libraries (no lodash, no moment)
5. **SBOM generation**: `npm sbom --sbom-format cyclonedx` run at build time, artifact stored with image

---

## Container Security

### Dockerfile Hardening

- Multi-stage build: build stage (full toolchain) → production stage (runtime only)
- Non-root user: container runs as `node` user, not root
- Read-only filesystem where possible
- No unnecessary binaries in production image (Alpine minimal)
- `.dockerignore` excludes: `.git`, `node_modules`, `.env`, `*.md`

### SPCS Security Boundary

- Public endpoint gated by Snowflake OAuth — unauthenticated requests rejected at SPCS ingress
- Container has no external network access (no external access integration)
- Snowflake credentials never stored in image — OAuth token injected at runtime by SPCS
- Container resource limits enforced: 2Gi memory, 1 CPU max

---

## Reporting Security Issues

If you discover a security vulnerability in this dashboard, contact the maintainer directly. Do not open a public GitHub issue for security vulnerabilities.
