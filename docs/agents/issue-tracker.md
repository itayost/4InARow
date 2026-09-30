# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in [`itayost/4InARow`](https://github.com/itayost/4InARow). Use the `gh` CLI for all operations.

This working folder is a downloaded copy, not a git clone, so `gh` cannot infer the repo from `git remote`. Always pass `-R itayost/4InARow` explicitly (it is harmless inside a clone too).

## Conventions

- **Create an issue**: `gh issue create -R itayost/4InARow --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> -R itayost/4InARow --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list -R itayost/4InARow --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> -R itayost/4InARow --body "..."`
- **Apply / remove labels**: `gh issue edit <number> -R itayost/4InARow --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> -R itayost/4InARow --comment "..."`

## Labels

Only `wontfix` of the triage labels exists in the repo today. The first time a skill needs one of the others (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`), create it with `gh label create "<name>" -R itayost/4InARow --description "..."` before applying it. See `triage-labels.md` for the mapping.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> -R itayost/4InARow --comments` and `gh pr diff <number> -R itayost/4InARow` for the diff.
- **List external PRs for triage**: `gh pr list -R itayost/4InARow --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close` (each with `-R itayost/4InARow`).

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42 -R itayost/4InARow` and fall back to `gh issue view 42 -R itayost/4InARow`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `itayost/4InARow`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> -R itayost/4InARow --comments`.
