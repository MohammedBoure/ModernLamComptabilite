# Global Antigravity Preferences & Rules

## 1. Version Control & Git Commit Requirements
- **Git Commit per Task**: Every task or feature executed by the agent must culminate in a Git commit.
- **Commit Language**: All Git commit messages MUST be written in clear, descriptive English (e.g., `feat: update database schema initialization`).

## 2. Versioning Rules
- **Project Version File**: Every project must contain a dedicated version tracking file (e.g., `VERSION`, `version.txt`, `package.json`, or a version variable in the primary package `__init__.py`).
- **Patch Increment on Commit**: With every commit, increment the patch version number by 1 (e.g., `x.x.1` -> `x.x.2` -> `x.x.3`).
- **Strict Major/Minor Lock**: Do NOT modify the major or minor version numbers (`x.x._`) unless explicitly instructed by the user.
