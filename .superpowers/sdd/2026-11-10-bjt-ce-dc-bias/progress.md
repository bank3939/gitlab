# SDD ledger — plan: docs/superpowers/plans/2026-11-10-bjt-ce-dc-bias.md

## Setup
- Spec: docs/superpowers/specs/2026-11-10-bjt-ce-dc-bias-design.md (read)
- Base HEAD: c8451de
- Ruling: git CLI at C:\Users\B6821241\AppData\Local\Programs\Git\cmd\git.exe (not in PATH); SDD bash scripts unavailable on Windows so workspace/briefs/review packages handled manually. No isolated worktree created (ruling: existing lab repo, user wants demo+commit today in this workspace; keep existing files intact).
- Tasks: 1) engineering logic+tests 2) Flask UI 3) final verification/demo/commit

## Progress
- [x] Task 1: complete (commits c8451de..e8aaa01, review clean/spec+quality approved). Tests: `python -m unittest tests.test_bjt_bias -v` 4/4 OK. Minor notes parked: invalid-state region contract (`unknown`) and tighter invalid-input assertions.
- [x] Task 2: complete (commits e8aaa01..f5dcb70, review clean/spec+quality approved). Tests: `python -m unittest tests.test_app` 2/2 OK, `python -m unittest tests.test_bjt_bias` 4/4 OK, test_client smoke GET/POST OK. Minor notes parked: limited UI/error-path test coverage, debug=True in __main__.
- [ ] Task 3
