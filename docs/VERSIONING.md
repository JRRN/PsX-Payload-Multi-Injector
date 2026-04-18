# Automatic Version Management

This guide explains how automatic version bumping works in PS MultiInjector.

## Overview

The project uses **Semantic Versioning** (SemVer) with automatic version bumping based on conventional commit messages:

- **Patch bumps** (`1.0.0` → `1.0.1`): Bug fixes (`fix:` prefix)
- **Minor bumps** (`1.0.0` → `1.1.0`): New features (`feat:` prefix)  
- **Major bumps** (`1.0.0` → `2.0.0`): Breaking changes (`breaking:` prefix)

## How It Works

### Local Development

When you make commits with conventional commit messages:

```bash
# Example commits
git commit -m "feat: add new language support"     # → triggers minor bump
git commit -m "fix: resolve socat timeout issue"  # → triggers patch bump
git commit -m "breaking: change API format"       # → triggers major bump
git commit -m "docs: update readme"               # → no version change
```

### CI/CD Pipeline

When you push to `main`:

1. **Tests run** across all platforms (Linux, Windows, macOS)
2. **Version check** analyzes commits since last release
3. **If version-relevant commits found:**
   - Version is bumped in `src/models/version.py`
   - CHANGELOG.md is updated with new entry
   - Changes are committed to `main`
   - Git tag is created (e.g., `v1.1.0`)
4. **Build step** uses the updated version for executables
5. **Release job** publishes GitHub Release with new version

## Commit Message Format (Conventional Commits)

Use these prefixes in your commit messages:

### Version-Bumping Commits

```bash
# Feature (minor bump)
git commit -m "feat: add socat timeout configuration"
git commit -m "feat(ui): add dark mode support"

# Bug fix (patch bump)
git commit -m "fix: resolve crash when socat unavailable"
git commit -m "fix(lang): fix spanish translation"

# Breaking change (major bump)
git commit -m "breaking: rename payload format API"
git commit -m "breaking: change config file location"
```

### Non-Bumping Commits

```bash
# Documentation (no bump)
git commit -m "docs: update installation instructions"

# Style/formatting (no bump)
git commit -m "style: fix linting issues"

# Tests (no bump)
git commit -m "test: add integration test for socat"

# Chores (no bump)
git commit -m "chore: update dependencies"
```

## Local Version Bumping

To test version bumping locally before pushing:

```bash
# Dry run - shows what would happen
python ci-cd/bump_version.py --dry-run

# Actual bump - updates files and creates tag
python ci-cd/bump_version.py
```

This will:
- Analyze commits since last git tag
- Update `src/models/version.py`
- Update `CHANGELOG.md`
- Create a git tag with new version

## Files Updated by Automatic Versioning

1. **src/models/version.py**
   ```python
   __version__ = "1.1.0"  # Updated automatically
   ```

2. **CHANGELOG.md**
   - New entry added with today's date
   - Commits categorized as Added/Fixed/Breaking Changes

3. **Git tags**
   - Automatic tag created: `v1.1.0`

## Manual Version Updates

If you need to set a specific version manually:

1. Edit `src/models/version.py`:
   ```python
   __version__ = "2.0.0"
   ```

2. Update `CHANGELOG.md` with your changes

3. Create a tag:
   ```bash
   git tag -a v2.0.0 -m "Release 2.0.0"
   git push origin v2.0.0
   ```

## Pipeline Behavior

### Push to main (with version-relevant commits)

```
Tests Pass
    ↓
Analyze Commits → Detect feat/fix/breaking
    ↓
Bump Version → Update files
    ↓
Commit to main → git commit + git push
    ↓
Build Executables → with new version
    ↓
Create Release → GitHub Release with tag
```

### Push to main (no version-relevant commits)

```
Tests Pass
    ↓
Analyze Commits → Only docs/chore/style
    ↓
Version Unchanged → Skip version bump job
    ↓
Build Executables → with current version
    ↓
Skip Release → No new release created
```

## Examples

### Scenario 1: Bug Fix Release

```bash
# Local development
git commit -m "fix: resolve payload timeout on macOS"
git commit -m "fix: improve socat error messages"

# Push to main
git push origin main

# GitHub Actions:
# → Detects 2 "fix:" commits
# → Bumps: 1.1.0 → 1.1.1
# → Creates tag: v1.1.1
# → Releases: PS_MultiInjector-1.1.1-*
```

### Scenario 2: Feature Release

```bash
# Local development
git commit -m "feat: add support for PS5 Pro"
git commit -m "fix: handle edge case in endpoint validation"
git commit -m "docs: update README with new features"

# Push to main
git push origin main

# GitHub Actions:
# → Detects "feat:" + "fix:" commits
# → Bumps: 1.1.0 → 1.2.0 (minor takes precedence)
# → Creates tag: v1.2.0
# → Releases: PS_MultiInjector-1.2.0-*
```

### Scenario 3: Breaking Changes

```bash
# Local development
git commit -m "breaking: change config file format to YAML"
git commit -m "feat: add migration tool"

# Push to main
git push origin main

# GitHub Actions:
# → Detects "breaking:" commit
# → Bumps: 1.1.0 → 2.0.0
# → Creates tag: v2.0.0
# → Releases: PS_MultiInjector-2.0.0-*
```

## Troubleshooting

### Version didn't bump after push

**Check:**
1. Did you use conventional commit format? (`feat:`, `fix:`, `breaking:`)
2. Are you pushing to `main` branch?
3. Did tests pass?

Use `--dry-run` locally to test:
```bash
python ci-cd/bump_version.py --dry-run
```

### Git tag already exists

The pipeline will skip creating a tag if version hasn't changed (no version-relevant commits).

### Release notes are empty

The `softprops/action-gh-release` action uses conventional commits to auto-generate release notes. If you're using the commit format above, notes should populate automatically.

## Configuration

### Changing Version Bump Rules

Edit `ci-cd/bump_version.py`:

- `analyze_commits()` function - modify detection logic
- `parse_version()` - change version format (currently SemVer)
- Tag prefix - change `tag_prefix` parameter (currently `v`)

### Disabling Automatic Bumping

If you want to disable version auto-bumping:

1. Comment out the `version-bump` job in `ci-cd/pipeline.yml`
2. Manually update `src/models/version.py` when releasing

### Using Different Bump Strategy

To use incremental bumping (always patch):

```bash
# In pipeline, modify bump_version.py to always return 'patch'
# Or create a --strategy flag
```

## Related Files

- `ci-cd/bump_version.py` - Version bumping script
- `ci-cd/pipeline.yml` - GitHub Actions workflow
- `src/models/version.py` - Current version source
- `CHANGELOG.md` - Version history

## Learn More

- **Semantic Versioning**: https://semver.org/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **GitHub Actions**: https://docs.github.com/en/actions

## Questions?

Check the commit messages in `git log` to understand the bumping pattern:

```bash
git log --oneline --all
# Shows all commits with their messages
```

Use `git tag -l` to see all version tags:

```bash
git tag -l
# v1.0.0, v1.1.0, v1.2.0, etc.
```
