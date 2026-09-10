# Contributing

## Branch strategy (deviation from the standard `dev`/`main` flow)

This is a Code Ocean capsule, not a library. Code Ocean's web IDE pushes
commits directly to the capsule's attached branch and cannot open PRs, so
that branch can never carry a protection rule requiring review.

- **`main`** is attached to Code Ocean and is what a capsule run with
  `version=None` resolves to. It is **unprotected** — Code Ocean pushes
  ("Edited run", "Edited sessions.json", etc.) land here directly.
- **`dev`** is a staging branch for multi-commit programmatic work (e.g.
  work done outside the Code Ocean web IDE). It is not attached to anything
  in Code Ocean.

Sync direction is two-way by convention, not enforcement:
- Merge `main` into `dev` before starting work, so `dev` isn't stale.
- Merge `dev` into `main` to ship.

No branch protection on either branch — review happens by convention. See
`docs/standards-compliance.md` in
[aind-motion-energy](https://github.com/AllenNeuralDynamics/aind-motion-energy)
for the full rationale.

## Commit / PR title conventions

Where a PR is possible (i.e. merging `dev` into `main`), use
[Conventional Commits](https://www.conventionalcommits.org/) prefixes
(`fix:`, `feat:`, `feat!:`/`BREAKING CHANGE`) for consistency with the
library repo, even though this repo has no automated release workflow.
