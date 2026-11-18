---
name: superpowers-artifacts
description: Use when creating, revising, publishing, or resuming specifications or implementation plans, including Superpowers specs/plans and GitHub issue artifacts or pull request document references.
---

# Superpowers Artifacts

## Purpose and Scope

Apply this repository's spec/plan conventions alongside the relevant
Superpowers process skills. These storage and publication conventions override
Superpowers defaults; they do not replace brainstorming, plan review, or
execution approval.

## Workflow

- Brainstorm and iterate on local specs in `.superpowers/specs/` and
  implementation plans in `.superpowers/plans/`. An issue is not required
  during drafting. Do not commit these documents or store them under `docs/`.
- Obtain approval of the spec and plan before publishing them as named
  GitHub issue artifacts (`generic` for specs, `plan` for implementation plans),
  not as comment attachments or full
  inline copies. After verified publication, the latest explicitly approved
  artifacts are canonical; local documents remain working copies.
- Prefer automated publication with `gh issue artifact create --body-file`,
  supplying an explicit name and type (requires GitHub CLI 2.103.0+).
  Check available artifact tooling before assuming manual uploads are needed.
  If unavailable, report the limitation and agree a fallback with the user;
  user-assisted Markdown uploads are acceptable. Named issue artifacts are
  distinct from comment attachments and GitHub Actions artifacts.
- Use concise inline summaries and decisions, linking to the artifacts
  wherever relevant. Cite the document version, section number, and heading
  (for example, "Spec v1, section 2 — Acceptance criteria"); do not assume
  download links support heading anchors.
- Give every spec/plan section and list item an explicit number, including
  requirements, acceptance criteria, tasks, and steps. Use numbered lists
  rather than unordered lists; identify nested items by their parent numbers.
  Keep published identifiers stable and append new identifiers for follow-ups,
  so issue/PR references such as "Spec v1, section 4, item 3" stay unambiguous.
- Preserve published history. Update existing artifacts for approved revisions,
  retaining their built-in version history and stable numbered identifiers.
  Cite explicit document versions and identify what revisions supersede.
- Preserve completed tasks. Record subsequent work in clearly labeled
  follow-up sections rather than replacing the original plan.
- Link the associated issue and relevant document references from any later
  pull request; a planning-only rehearsal does not require a pull request.
- Ask before creating or modifying GitHub issues or pull requests, including
  creating or updating their artifacts.
- Verify artifact URLs, names, types, and downloaded contents against the
  approved local documents before reporting publication complete. Report blocked
  or unverified publication explicitly.
