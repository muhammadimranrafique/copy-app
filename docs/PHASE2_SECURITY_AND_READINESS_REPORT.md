# Phase 3 — Repository Security Cleanup & Release Readiness

**Role:** Act as a Senior Software Engineer, Git Security Specialist, and DevOps Engineer.

## Project Context

The School Copy Vendor Payment ERP uses a React + TypeScript frontend deployed on Vercel, a FastAPI backend planned for a VPS, and an existing Neon PostgreSQL production database.

Phase 2 security remediation is complete in the local workspace. Three commits exist locally on `main` and have **not been pushed**. The Neon database password has been rotated by the owner and the new credential has been saved in the local `backend/.env` file.

Refer to the Phase 2 report and the existing repository state before making decisions.

## Objective

Prepare a safe, verified, and reversible repository cleanup and release plan before VPS deployment.

## Mandatory Rules

1. Start with a read-only inspection of the current Git repository, branches, remotes, commits, working tree, `.gitignore`, and tracked sensitive-file history.
2. Verify whether `.env` files, database files, PDFs, credentials, private keys, or other sensitive data remain in the current Git index or historical commits. Do not print, copy, or expose any secret values.
3. Confirm that the three Phase 2 commits are present and inspect their summaries and affected file lists.
4. Treat the rotated Neon password as compromised if it exists in public Git history. Password rotation does not remove historical exposure.
5. Do not read out, log, overwrite, delete, or transmit the owner's current `.env` credentials. Preserve all local environment files and business data.
6. Do not connect to Neon, run database queries or migrations, change production data, or modify the database schema.
7. Do not push, force-push, rewrite Git history, delete branches, change GitHub visibility, or rotate credentials. These actions require explicit owner approval.
8. Do not provision a VPS, change DNS, or modify Vercel production settings in this phase.
9. Do not remove dependencies or refactor application logic unrelated to repository security.
10. Do not assume that removing a file from the latest commit removes it from Git history.

## Required Tasks

### A. Repository Verification

- Check the current branch, working-tree status, remote configuration, and commits ahead of the remote.
- Verify that `.env`, `.db`, generated PDFs, virtual environments, build artifacts, and other sensitive files are excluded from tracking.
- Check whether `.env.example` files contain safe placeholders only.
- Inspect historical commits for previously exposed credentials, customer documents, database files, and other sensitive information without displaying secret values.
- Identify any Git LFS objects, tags, branches, or other repository references that may retain sensitive files, where applicable.

### B. History-Cleanup Planning

- Determine whether Git history rewriting is necessary.
- Recommend an appropriate tool, such as `git-filter-repo`, based on the actual repository.
- Document the exact files and historical paths requiring removal.
- Explain the risks of rewriting history, force-pushing, disrupting collaborators, and existing clones.
- Provide a backup and recovery plan before any proposed history rewrite.
- Produce proposed commands for owner review, but do not execute destructive commands or rewrite history.
- Explain how to verify the cleaned history before any future push.

### C. Security and Release Checks

- Review the Phase 2 changes for consistency with the report.
- Verify that no live Railway API URL or real Neon connection details remain in tracked current files.
- Confirm that the frontend production build requires `VITE_API_BASE_URL`.
- Confirm that production backend configuration requires a valid `SECRET_KEY` and explicit `ALLOWED_ORIGINS`.
- Verify that public registration remains disabled by default in production.
- Run only safe, local, non-production checks where needed. Do not expose secrets in test output.

### D. Documentation

Create or update:

`docs/PHASE3_REPOSITORY_SECURITY_AND_RELEASE_READINESS.md`

Include:

- Executive summary and GO/NO-GO recommendation.
- Repository and commit status.
- Current-file versus historical-exposure findings.
- Sensitive-file verification results.
- History-cleanup plan and rollback procedure.
- Tests and commands executed with their outcomes.
- Owner decisions and approvals required.
- Remaining blockers before release and VPS deployment.

Do not include passwords, tokens, full connection strings, or other secret values in the report.

## Approval Gate

Complete the inspection and documentation first. Stop before any history rewrite, force-push, remote mutation, credential change, or production action.

At the end, provide a concise summary and ask for explicit approval before proposing execution of the history cleanup.

**Definition of Done:** The repository has been audited, findings are evidence-based, the Phase 3 report is saved, local business data and credentials are preserved, no production database or infrastructure has been modified, and no remote changes have been made.


