# GitHub Push Instructions (TigerEx)

This repository currently has no configured `origin` remote in this environment.

To push the latest work to GitHub `main` safely:

1. Run:
   ```bash
   ./scripts/push_main.sh <your-github-repo-url>
   ```
2. Example:
   ```bash
   ./scripts/push_main.sh git@github.com:YOUR_ORG/TigerEx-.git
   ```
3. The script will:
   - configure `origin`
   - ensure local `main` exists
   - fast-forward merge current branch into `main` (no history rewrite)
   - push `main` to GitHub

## If force push is absolutely required

Use only when you understand history rewrite impact:

```bash
git push --force-with-lease origin main
```

Prefer `--force-with-lease` over `--force` for safer collaboration.
