# Import and upload

**Current review branch:** `docs/nano-edge-learning-2026-10-08` contains this update in `JJHE-1/Autonomous-UAVs`. It is intended for a pull request against `main`; it has not been merged. The upstream repository is unchanged. The local importer described below only prepares files and never calls GitHub.

## Recommended: import into a local clone of your fork

Keep the extracted bundle outside the target checkout. Use a clean checkout so that unrelated local changes cannot be mixed into this update. The importer does not need GitHub credentials or network access.

From the extracted bundle directory:

```bash
python import_into_repo.py --target /path/to/Autonomous-UAVs --update-readme
```

This is a dry run. Inspect the target and proposed changes. Then explicitly apply:

```bash
python import_into_repo.py --target /path/to/Autonomous-UAVs --update-readme --apply
```

On Windows, quote the local path, for example `--target "D:\research\Autonomous-UAVs"`. Omit `--update-readme` to leave the root README completely untouched. The destination is `learning/nano-uav-2026/`; the importer refuses an existing destination, a dirty checkout, symbolic links in affected paths, and attempts to operate on the upstream repository as the push origin.

The optional root-README update preserves a local byte-for-byte backup, adds a guide link, and fixes the exact known maplab hyperlink. It does not rewrite the rest of the original index.

## Create or obtain your fork first, when necessary

Use the original GitHub page's **Fork** action under your own account, or use an authenticated GitHub CLI locally. These commands are for you to run; they were not run successfully by the delivery session:

```bash
gh auth login
gh repo fork alexkoven/Autonomous-UAVs --clone=false
```

Then clone your fork. For the account identified in the delivery session:

```bash
gh repo clone JJHE-1/Autonomous-UAVs
```

Use your actual account/repository if different. A private or differently named destination should be selected deliberately; do not change visibility merely to make an upload work. Official CLI references: [fork](https://cli.github.com/manual/gh_repo_fork) and [clone](https://cli.github.com/manual/gh_repo_clone).

## Review and publish an explicit branch

Create a branch in the clean target checkout **before** applying the importer:

```bash
git switch -c docs/nano-edge-learning-2026-10-08
```

After import, inspect the diff and validate the imported guide:

```bash
git diff -- README.md
git status --short
python learning/nano-uav-2026/tools/validate_bundle.py
python -m unittest discover -s learning/nano-uav-2026/tests -v
git remote -v
```

Check that `origin` is your fork, not `alexkoven/Autonomous-UAVs`. Stage only this update:

```bash
git add learning/nano-uav-2026
```

Only when you used `--update-readme`, also run:

```bash
git add README.md
```

Then publish to your fork:

```bash
git commit -m "docs: add English nano-UAV edge-navigation learning guide"
git push -u origin docs/nano-edge-learning-2026-10-08
```

This creates a branch in your repository. It does **not** merge to the default branch or open a pull request to the original author. Open a pull request **inside your own fork** when you are ready to review/merge it. Do not use a CLI default PR target without checking whether it points upstream.

## Browser-only alternative

In your own repository, create the review branch and use GitHub's file-upload interface to add the extracted guide under a separate directory. Keep the original root README. Add a link to the guide manually if needed. Uploading the ZIP alone stores an archive but does not make the learning pages directly browsable on GitHub.

## GitHub write boundary

The learning materials were published to the `JJHE-1/Autonomous-UAVs` review branch named above. The fork's `main` branch and the original `alexkoven/Autonomous-UAVs` repository were not changed. Review and merge remain separate user decisions.

The local importer is deliberately local-only: it does not create branches, commits, pull requests, or GitHub uploads. Never paste access tokens into a conversation.
