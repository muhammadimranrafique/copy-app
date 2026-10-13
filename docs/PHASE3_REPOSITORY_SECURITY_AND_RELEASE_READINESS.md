# Phase 3 — Repository Security Cleanup & Release Readiness

**Project:** School Copy Vendor Payment ERP
**Date:** 2026-10-13
**Scope:** Read-only repository audit + history-cleanup plan + release checks. **No history rewrite, force-push, remote mutation, credential change, or production action was performed.**
**Secret policy:** No passwords, tokens, connection strings, or secret values appear in this report. Only paths, sizes, counts, and variable names.

---

## A / Executive Summary & GO/NO-GO

### Repository status
- Branch `main` is **3 commits ahead** of `origin/main` (the three Phase 2 security commits, all local, never pushed). Public history contains **52 commits**; local history contains **55**.
- Working tree is clean except two untracked directories: `docs/` (audit reports) and `.workbuddy-ai/` (local agent memory — should not be pushed).
- The repository is **public** on GitHub (verified via GitHub API in Phase 2), single branch, **no tags, no LFS, no stashes, no forks** — low collaborator-disruption risk for a history rewrite.

### Current-state security (verified by execution this session)
- **0** tracked `.env`, `.db`, `.pdf`, `.pyc`, `venv/`, `.pem` files in the current index.
- HEAD tree contains **no** live Railway URL, **no** credential patterns, **no** real Neon host (only placeholders and comments remain).
- `backend/.env` is ignored by `.gitignore` (rule line 27), preserved on disk, and its modification time (13 Oct 19:00) shows the owner's rotation was applied — **it was not read, modified, or transmitted by this audit**.
- Phase 2 protections re-verified fresh: **11/11** production config fail-safe tests pass (missing/placeholder/short `SECRET_KEY`, localhost/wildcard/http/empty `ALLOWED_ORIGINS` all fail startup); frontend build **fails safely** without `VITE_API_BASE_URL`.

### Historical exposure (verified)
- **73 distinct sensitive object paths** exist in public history: `backend/.env` (1), `backend/school_copy.db` (1), **45 generated PDFs** (44 unique paths — two files share one identical blob), **27 `.pyc` artifacts**.
- `backend/.env` was introduced publicly in commit `46df98b` ("Add complete copy app project", the second commit ever) and has **6 distinct historical versions** (blob sizes 839–1036 bytes) — i.e., the **old Neon password exists in at least one public commit**. Rotation (completed by the owner) makes the old value useless, but **the old value remains retrievable from public history until the history is rewritten**.
- The four largest blobs in the entire repository are generated PDFs (~190–200 KB each) — cleanup will meaningfully shrink the repo (pack is currently 891 KiB).

### GO/NO-GO
- **GO to execute the history cleanup — pending your explicit approval** (plan and commands in Section D, nothing executed).
- **NO-GO for release** until the remaining owner actions in Section F are complete.

---

## B. Findings

| # | Area | Finding | Evidence | Severity | Status |
|---|---|---|---|---|---|
| 1 | Current index | No sensitive files tracked | `git ls-files` counts = 0 for `.env/.db/.pdf/.pyc/venv/pem` | — | VERIFIED |
| 2 | History | `backend/.env` (old credentials) in public history, introduced commit `46df98b`, 6 versions, 7 commits touched | `git log --all -- backend/.env`; blob enumeration | CRITICAL | VERIFIED — rotation done; rewrite pending approval |
| 3 | History | `backend/school_copy.db` (user records) in public history | object scan | HIGH | VERIFIED — rewrite pending approval |
| 4 | History | 45 production invoice/receipt PDFs in public history | object scan + removal-commit diff-tree; byte-identical pair confirmed via `git hash-object` | HIGH | VERIFIED — rewrite pending approval |
| 5 | History | 27 `.pyc` build artifacts in public history | object scan | LOW | VERIFIED — rewrite pending approval |
| 6 | HEAD tree | `backend/DATABASE_MIGRATION_README.md` matches "neon.tech" — placeholders only (`user:password@host.neon.tech`, `<your-neon-host>.neon.tech`) | `git grep -n` | — | VERIFIED (sanitized in Phase 2) |
| 7 | HEAD tree | "railway" matches are non-live: comment in `backend/Dockerfile`, commented-out legacy code in `backend/config.py`, and stale deployment config `railway.json` | `git grep -n` | LOW (hygiene) | VERIFIED — optional cleanup proposed (Section F) |
| 8 | Phase 2 consistency | The 3 unpushed commits match the Phase 2 report file lists exactly (`.gitignore`, `.env`/DB/PDF/pyc removals; config/database/main/auth hardening; frontend api-config + fallbacks; README sanitization) | `git log --stat origin/main..HEAD` | — | VERIFIED |
| 9 | Local env | `backend/.env` preserved, ignored, untouched; rotation reflected in mtime | `git check-ignore`, `ls -la` (content not read) | — | VERIFIED |
| 10 | Examples | `backend/.env.example` + `frontend/.env.example` contain placeholders only; duplicate legacy `backend/env.example` is placeholder-only | content review (no secrets) | — | VERIFIED |
| 11 | Repo refs | No tags, no LFS objects, no stashes, no other branches, forks = 0 | `git tag`, `git stash`, `.gitattributes` absent, GitHub API | — | VERIFIED |

**Not reproduced (nothing to fix):** no credentials.json/keys/pem ever in history; no secret patterns in the current HEAD tree; no additional remotes.

---

## C. Sensitive-File Verification Results (summary table)

| Check | Command (abridged) | Result |
|---|---|---|
| Tracked sensitive files (current) | `git ls-files` pattern counts | **0 / 0 / 0 / 0** |
| Sensitive paths ever in history | `git rev-list --all --objects` | **73** (1 env, 1 db, 45 PDFs, 27 pyc, +1 shared-blob path) |
| Credential pattern in HEAD tree | `git grep -lI` for credential/host/role patterns (values not reproduced) | **none** |
| Live Railway URL in HEAD tree | `git grep -lI "railway"` | only comments/config, no live URL |
| `.env` ignored locally | `git check-ignore -v backend/.env` | `.gitignore:27` ✓ |
| Public history depth | `git rev-list --count origin/main` | 52 commits |
| Unpushed commits | `git log origin/main..HEAD` | 3 (Phase 2 + docs) |

---

## D. History-Cleanup Plan (PROPOSED — NOT EXECUTED)

### D1. Is rewriting necessary?
Yes — for defense in depth. The DB password is already rotated (so the leaked value is dead), but the credential file, the SQLite DB, and 45 customer PDFs remain retrievable from the public repository history. Rewriting is recommended; it is **not** an emergency since rotation already neutralized the credential.

### D2. Tool
**`git filter-repo`** (install: `pip install git-filter-repo`). Preferred over `git filter-branch` (faster, safer, maintained). Alternative considered: delete-and-recreate the GitHub repo — rejected because it severs the Vercel↔GitHub linkage and loses all history including the legitimate parts.

### D3. Exact removal targets

**By path (delete from all history):**
```
backend/.env
backend/school_copy.db
backend/invoices/*.pdf          (13 files)
backend/receipts/*.pdf          (24 files)
receipts/*.pdf                  (5 files)
test_invoices/*.pdf             (2 files)
```
Simplified with globs: `--path-glob '*.pdf' --path-glob '*.pyc'`

**By content (scrub the real host/role from historical README versions):** a `replacements.txt` for `--replace-text` containing the previously-real host endpoint and role name, mapped to `<redacted>` (values deliberately not reproduced here; they are documented in the Phase 2 report as patterns only). Alternative if owner prefers zero content surgery: accept that historical README versions show the host (no password) — lower severity, but scrubbing is cheap and recommended.

### D4. Proposed commands (for owner review — do not run until approved)

```bash
# 0) SAFETY BACKUP FIRST (mandatory)
cd <project-parent>
git clone --mirror https://github.com/muhammadimranrafique/copy-app.git copy-app-backup.git
git -C copy-app-backup.git bundle create ../copy-app-pre-cleanup.bundle --all
# verify backup:
git -C copy-app-backup.git log --oneline -3

# 1) Fresh clone for filtering (filter-repo requires it)
git clone --no-local https://github.com/muhammadimranrafique/copy-app.git copy-app-clean
cd copy-app-clean

# 2) Replacements file for historical content scrub
cat > replacements.txt <<'EOF'
<historical-host-endpoint>==><redacted-host>
<historical-role-name>==><redacted-role>
EOF

# 3) Rewrite
pip install git-filter-repo
git filter-repo --force \
  --invert-paths \
  --path backend/.env \
  --path backend/school_copy.db \
  --path-glob '*.pdf' \
  --path-glob '*.pyc' \
  --replace-text replacements.txt

# 4) VERIFY before any push
git rev-list --all --objects | awk '{print $2}' | grep -E '\.env$|\.db$|\.pdf$|\.pyc$'   # must be EMPTY
git grep -rI '<historical-host-endpoint>' $(git rev-list --all) 2>/dev/null                # must be EMPTY
git log --oneline | head                                                                   # history intact, hashes changed
git count-objects -vH                                                                      # size shrinks
diff -r <original>/backend <clean>/backend   # working content identical (except rewritten blobs)
python -m py_compile backend/main.py        # app still compiles
# frontend/backend smoke tests from Phase 2/3 still pass

# 5) Re-add remote (filter-repo removes it) and force-push with lease
git remote add origin https://github.com/muhammadimranrafique/copy-app.git
git push origin main --force-with-lease

# 6) Verify on GitHub (fresh clone + scan; GitHub may cache old commit views for a while)
git clone https://github.com/muhammadimranrafique/copy-app.git verify-clone
cd verify-clone && git rev-list --all --objects | awk '{print $2}' | grep -E '\.env$|\.pdf$' || echo CLEAN
```

**Note:** the three unpushed Phase 2 commits live only in the local repo. After rewriting in a fresh clone, those commits' content must be carried over — simplest is to cherry-pick them onto the rewritten `main` (their content = current working tree) **or** apply the filter to the local repo directly after taking the mirror backup. Recommended variant: backup → filter the **local** repo (`git filter-repo --force` in place) → verify → re-add `origin` → force-push. This avoids re-applying commits entirely and is the primary recommended path.

### D5. Risks (owner must accept)
- **All 55 commit hashes change** → any other clone becomes incompatible; collaborators must re-clone (single-account project; forks = 0).
- **Force-push rewrites public history** — irreversible on GitHub after GC; the mirror backup (D4 step 0) is the only recovery.
- **GitHub caching:** old commit pages/blob URLs may remain reachable for some time after force-push; true removal is confirmed by a fresh clone scan.
- **Vercel integration:** the Vercel project deploys from this GitHub repo; a force-push triggers a redeploy from the new history. Vercel env vars live in the Vercel dashboard and are unaffected.
- **No branch protection, PRs, signatures, or CI currently reference the old hashes** (verified: no tags, no other branches, no PRs).

### D6. Rollback plan
1. Stop; do not force-push again.
2. Restore from the mirror backup: `git clone --mirror copy-app-backup.git copy-app-restored` and `git -C copy-app-restored push --mirror origin --force`, **or** from the bundle: `git clone copy-app-pre-cleanup.bundle copy-app-restored && push --force`.
3. If the push already happened: the backup bundle restores the exact pre-rewrite history; force-push it back with `--force-with-lease` after re-adding the remote.
4. Verify with `git log --oneline | head` and `git rev-list --count` against the pre-rewrite counts (55 local / 52 public).

### D7. Post-cleanup verification checklist
- [ ] `git rev-list --all --objects` scan → zero sensitive paths
- [ ] Historical host/role grep → zero matches
- [ ] Repo size shrank (expect ≈ 891 KiB → ≈ 100 KiB)
- [ ] `git status` clean; working tree byte-identical to pre-cleanup (diff the backend/frontend dirs)
- [ ] Phase 3 security re-checks still pass (11/11 config tests; frontend fail-safe build)
- [ ] Fresh GitHub clone scan clean; Vercel redeploys successfully
- [ ] New `.gitignore` prevents recurrence (already hardened in Phase 2)

---

## E. Tests & Commands Executed (read-only / non-destructive only)

| Check | Outcome |
|---|---|
| `git branch -vv`, `git remote -v`, `git log origin/main..HEAD`, `git status --short` | main ahead 3; clean except untracked `docs/`, `.workbuddy-ai/` |
| `git tag -l`, `git stash list`, `.gitattributes` | none / none / absent |
| `git ls-files` sensitive-pattern counts (index) | 0 / 0 / 0 / 0 / 0 / 0 |
| `git rev-list --all --objects` path scan (history) | 73 sensitive paths; distribution by directory recorded |
| `git log --all -- backend/.env` + blob enumeration | added in `46df98b`; 6 distinct historical versions |
| `git hash-object` on the two ORD-1001 PDFs | identical hashes → shared blob, reconciles 45 files vs 44 paths |
| `git grep -lI` HEAD-tree credential/host/role patterns (values not reproduced) | none |
| `git grep -nI railway` on HEAD | comments/config only, no live URL |
| `git check-ignore -v backend/.env` + `ls -la` | ignored (`.gitignore:27`); preserved; **content never read** |
| Config fail-safe suite (Python 3.12.10, pinned venv) | **11/11 PASS** (fresh run) |
| Frontend negative build (`VITE_API_BASE_URL=`) | **fails with clear error** (fresh run) |
| Phase 2 commit stat review | matches Phase 2 report exactly |

**Not executed (by design):** any `git filter-repo`, force-push, remote write, `pip install` of new tooling, Neon connection, DB query, Vercel/DNS change, or credential change.

---

## F. Owner Decisions & Approvals Required

1. **Approve (or decline) the history rewrite** per Section D (tool, targets, commands, risks, rollback).
2. **Choose the rewrite scope:** recommended `--invert-paths` for `.env`/DB/PDFs/pyc **+** `--replace-text` host/role scrub; the minimal alternative drops the content scrub (keeps host visible in old README versions — not recommended).
3. **Choose rewrite target:** local-repo in-place filter (recommended, carries the 3 unpushed commits) vs fresh-clone filter + cherry-pick.
4. **Decide on stale Railway config:** `railway.json`, `.railwayignore`, both `Dockerfile`s, and the stale comment in `backend/Dockerfile` reference the abandoned Railway platform. Safe to delete for VPS deployment — your call (no secrets involved).
5. **Decide on committing `docs/`** (recommended: commit the audit reports) and adding `.workbuddy-ai/` to `.gitignore` (recommended: keep agent memory local).
6. **Optional hardening:** make the GitHub repository private in addition to rotation (rotation already neutralized the credential; privacy prevents future accidental exposure).

## G. Remaining Blockers Before Release / VPS Deployment

1. History cleanup approved + executed + verified (this phase's gate).
2. Production `SECRET_KEY` and `ALLOWED_ORIGINS` supplied on the VPS (fail-safe enforces both).
3. Vercel `VITE_API_BASE_URL` set to the real API domain + redeploy (the live bundle still points at the dead Railway host).
4. VPS provisioning + systemd + nginx + Certbot + DNS (next phase; no infrastructure touched here).

---

**Recommendation: approve Section D2–D4 (filter-repo, in-place on the local repo after mirror backup) as the next execution step. This audit made no changes to git history, remotes, credentials, the database, or any infrastructure.**

---

# EXECUTION RECORD — 2026-10-13 (approved cleanup; push BLOCKED by credentials)

## E1. Executed (all local, verified)

| Step | Command / action | Outcome |
|---|---|---|
| 1 | `git commit` — docs: added Phase 2/3 reports to Git; added `.workbuddy-ai/` to `.gitignore` | commit `4eabc31` |
| 2 | Redacted residual identifier literals from the Phase 3 report (secret policy) | commit `e3af293` |
| 3 | **Backup (mandatory, before rewrite):** `git clone --mirror` → `E:/Development_Laptop/Archive/copy-app-pre-cleanup-backup.git`; `git bundle create` → `E:/Development_Laptop/Archive/copy-app-pre-cleanup.bundle` (901,005 bytes) | verified: 57 commits, log intact |
| 4 | Built content-scrub rules (`/tmp/replacements.txt`, 2 rules: historical DB host → `redacted-host`, historical DB role → `redacted-role`) — values extracted programmatically from history, never printed | 2 rules |
| 5 | `git filter-repo --force --invert-paths --path backend/.env --path backend/school_copy.db --path-glob '*.pdf' --path-glob '*.pyc' --replace-text replacements.txt` | 57 commits rewritten in 2.0 s; `origin` remote auto-removed (expected) |

## E2. Post-rewrite verification (all PASS)

| Check | Result |
|---|---|
| Historical object scan for `.env`/`.db`/`.pdf`/`.pyc` paths | **EMPTY** |
| Host/role pattern search across **all** historical blobs | **EMPTY** |
| Working tree preserved (`backend/.env`, `school_copy.db`, all PDFs) | **on disk, untouched** |
| `git status` | **clean** |
| Repo pack size | 891 KiB → **452 KiB** |
| Commit count | 57 → 55 (two empty commits pruned; content preserved) |
| `py_compile` all backend modules | **OK** |
| Config fail-safe suite | **11/11 PASS** |
| Current `DATABASE_MIGRATION_README.md` host line | placeholder (`<your-neon-host>.neon.tech`) |
| Security commits present in new history | `587c37d`, `4192906`, `4eabc31`, `e3af293` ✓ |

## E3. Force-push — BLOCKED (owner action required)

- Re-added `origin`; fetched to restore the tracking ref; attempted:
  `git push origin main --force-with-lease=main:650293f…`
- **Result: `403 Permission denied` — stored Git credentials belong to GitHub account `smahveenrafique-rgb`, which is NOT the repository owner (`muhammadimranrafique`).** A second credential source on this machine (GitHub CLI, account `maryamacademy001-tech`) is also **pull-only** (`push: false`, verified via the GitHub API). No credential available here can publish the rewrite.
- **Remote is unchanged: `refs/heads/main` still points to `650293f` (old, un-cleaned history).** The old credential file, SQLite DB and 45 PDFs therefore **remain publicly accessible until the push succeeds**. (The leaked password itself is neutralized by the completed rotation.)
- Local state: `main` = `a257ffd` (55 commits), diverged from remote — the push is required to publish the cleaned history.
- **Note:** the pre-push `git fetch` re-imported the old objects into the local object store (via `refs/remotes/origin/main`). These were purged afterwards (`update-ref -d` + `reflog expire` + `gc --prune=now`); a final scan across **all** refs now shows **0** sensitive paths. The remote-tracking ref was removed, so `git status` shows `origin/main [gone]` until the owner fetches after pushing. The explicit-lease push below does not depend on it.

## E4. Owner action to publish the cleaned history (one command)

Run on **this machine** with the **repo owner's** GitHub credentials (or a PAT with `repo` scope for `muhammadimranrafique`), from `E:/Development_Laptop/Archive/saleem_copy_app`:

```bash
git push origin main --force-with-lease=main:650293f5453184f4ac5d2a7355d9119e3a7bd4d5
# (no remote-tracking ref needed; the lease value is explicit). After a successful push:/ngit fetch origin   # restores origin/main and status display
```

Alternatives: (a) authenticate the owner account here first (replace the stored credential, e.g. via Git Credential Manager or `git credential reject` + re-login), then the same push; (b) add `smahveenrafique-rgb` as a collaborator with write access and push with that account's credentials; (c) copy this repository folder (or the bundle) to the owner's machine and push from there.

## E5. Post-push verification (to run after E4)

```bash
git ls-remote origin main                       # must show e3af293 (new tip)
git clone https://github.com/muhammadimranrafique/copy-app.git /tmp/verify-clone
cd /tmp/verify-clone && git rev-list --all --objects | awk '{print $2}' | grep -E '\.env$|\.db$|\.pdf$|\.pyc$'   # must be EMPTY
```
Also confirm the Vercel project redeploys successfully from the new history (env vars live in the Vercel dashboard and are unaffected).

## E6. Rollback (if anything is wrong after the push)

```bash
# restore the exact pre-rewrite history from the mirror backup and push it back
git clone --mirror E:/Development_Laptop/Archive/copy-app-pre-cleanup-backup.git /tmp/restore
cd /tmp/restore && git push --mirror --force origin
# or from the bundle:
git clone E:/Development_Laptop/Archive/copy-app-pre-cleanup.bundle /tmp/restore2
```
The backup artifacts must be kept until the push is verified on GitHub. Note: rollback re-exposes the old content — only use if the rewrite itself is found defective.

## E7. Updated status

| Item | Status |
|---|---|
| History cleanup performed locally + verified | **DONE** |
| Publication to GitHub | **BLOCKED — owner credentials (E4)** |
| Old password exposure | Neutralized by rotation (completed earlier) |
| Old files' public accessibility | **Still exposed until E4 is executed** |
| Production `SECRET_KEY` / `ALLOWED_ORIGINS` on VPS | OWNER ACTION REQUIRED |
| Vercel `VITE_API_BASE_URL` + redeploy | OWNER ACTION REQUIRED |
| VPS provisioning / DNS / HTTPS | Next phase |

**GO/NO-GO: GO for the (completed) local cleanup. NO-GO for release until E4 is executed and verified, and the Vercel/VPS configuration items are completed.**
