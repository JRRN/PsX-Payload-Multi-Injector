#!/usr/bin/env python3
"""
Automatic version bumping using semantic versioning.
Analyzes git commits to determine version increment.

Commit message format (Conventional Commits):
- feat: new feature -> minor bump (1.0.0 -> 1.1.0)
- fix: bug fix -> patch bump (1.0.0 -> 1.0.1)
- breaking: breaking change -> major bump (1.0.0 -> 2.0.0)
- docs, style, chore, test: no bump

Usage:
    python build_local/bump_version.py [--dry-run]
"""

import re
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


def get_git_log(since_tag: Optional[str] = None) -> list[str]:
    """Get commit messages since last tag or all commits."""
    try:
        if since_tag:
            cmd = f"git log {since_tag}..HEAD --pretty=format:%B --no-merges".split()
        else:
            # Get commits since last tag, or all if no tags exist
            try:
                last_tag = subprocess.check_output(
                    "git describe --tags --abbrev=0".split(),
                    stderr=subprocess.DEVNULL,
                    text=True
                ).strip()
                cmd = f"git log {last_tag}..HEAD --pretty=format:%B --no-merges".split()
            except subprocess.CalledProcessError:
                # No tags exist, get all commits
                cmd = "git log --pretty=format:%B --no-merges".split()
        
        output = subprocess.check_output(cmd, text=True).strip()
        return output.split('\n') if output else []
    except subprocess.CalledProcessError:
        return []


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse version string into (major, minor, patch)."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(int(x) for x in match.groups())


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple to string."""
    return f"{major}.{minor}.{patch}"


def analyze_commits(commit_messages: list[str]) -> str:
    """
    Analyze commit messages and determine version bump type.
    Returns: 'major', 'minor', 'patch', or 'none'
    """
    has_breaking = False
    has_feature = False
    has_fix = False
    
    for message in commit_messages:
        lower_msg = message.lower().strip()
        
        # Check for breaking changes (BREAKING CHANGE: or breaking: prefix)
        if 'breaking change:' in lower_msg or lower_msg.startswith('breaking:'):
            has_breaking = True
            break
        
        # Check for feature
        if lower_msg.startswith('feat:') or lower_msg.startswith('feat('):
            has_feature = True
        
        # Check for fix
        if lower_msg.startswith('fix:') or lower_msg.startswith('fix('):
            has_fix = True
    
    if has_breaking:
        return 'major'
    elif has_feature:
        return 'minor'
    elif has_fix:
        return 'patch'
    else:
        return 'none'


def update_version_file(new_version: str, version_file: Path) -> None:
    """Update version.py with new version."""
    content = version_file.read_text()
    new_content = re.sub(
        r'__version__\s*=\s*"[^"]*"',
        f'__version__ = "{new_version}"',
        content
    )
    version_file.write_text(new_content)
    print(f"✓ Updated {version_file}: {new_version}")


def update_changelog(old_version: str, new_version: str, changelog_file: Path) -> None:
    """Update CHANGELOG.md with new version entry."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get commit messages since last version
    commits = get_git_log()
    
    # Categorize commits
    features = []
    fixes = []
    breaking = []
    
    for msg in commits:
        msg_clean = msg.strip()
        if not msg_clean:
            continue
        
        if 'breaking:' in msg_clean.lower():
            breaking.append(msg_clean.split('\n')[0])
        elif msg_clean.lower().startswith('feat:') or msg_clean.lower().startswith('feat('):
            features.append(msg_clean.split('\n')[0])
        elif msg_clean.lower().startswith('fix:') or msg_clean.lower().startswith('fix('):
            fixes.append(msg_clean.split('\n')[0])
    
    # Build changelog entry
    entry_lines = [f"## [{new_version}] - {today}"]
    
    if breaking:
        entry_lines.append("### Breaking Changes")
        for item in breaking:
            entry_lines.append(f"- {item}")
        entry_lines.append("")
    
    if features:
        entry_lines.append("### Added")
        for item in features:
            entry_lines.append(f"- {item}")
        entry_lines.append("")
    
    if fixes:
        entry_lines.append("### Fixed")
        for item in fixes:
            entry_lines.append(f"- {item}")
        entry_lines.append("")
    
    if not breaking and not features and not fixes:
        entry_lines.append("### Changed")
        entry_lines.append("- No specific changes detected")
        entry_lines.append("")
    
    entry = "\n".join(entry_lines) + "\n"
    
    # Read existing changelog
    changelog_content = changelog_file.read_text()
    
    # Insert new entry after "# Changelog" heading
    header_match = re.search(r'# Changelog\n+', changelog_content)
    if header_match:
        insert_pos = header_match.end()
        new_content = changelog_content[:insert_pos] + entry + "\n" + changelog_content[insert_pos:]
    else:
        # Fallback: prepend
        new_content = f"# Changelog\n\n{entry}\n{changelog_content}"
    
    changelog_file.write_text(new_content)
    print(f"✓ Updated {changelog_file}")


def create_git_tag(version: str, tag_prefix: str = "v") -> None:
    """Create and push git tag."""
    tag_name = f"{tag_prefix}{version}"
    
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
            check=True,
            capture_output=True
        )
        print(f"✓ Created git tag: {tag_name}")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: Failed to create tag: {e}")


def bump_version(dry_run: bool = False) -> str:
    """
    Main function: detect changes and bump version.
    Returns new version string.
    """
    version_file = Path(__file__).parent.parent / "src/models/version.py"
    changelog_file = Path(__file__).parent.parent / "docs/CHANGELOG.md"
    
    if not version_file.exists():
        raise FileNotFoundError(f"Version file not found: {version_file}")
    
    # Read current version
    current_version = version_file.read_text()
    match = re.search(r'__version__\s*=\s*"([^"]*)"', current_version)
    if not match:
        raise ValueError("Could not parse current version")
    
    old_version = match.group(1)
    print(f"Current version: {old_version}")
    
    # Get recent commits
    commits = get_git_log()
    if not commits:
        print("No new commits found. Version unchanged.")
        return old_version
    
    # Analyze commits to determine bump type
    bump_type = analyze_commits(commits)
    print(f"Detected change type: {bump_type}")
    
    if bump_type == 'none':
        print("No version-relevant commits found. Version unchanged.")
        return old_version
    
    # Calculate new version
    major, minor, patch = parse_version(old_version)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    
    new_version = format_version(major, minor, patch)
    print(f"New version: {new_version}")
    
    if dry_run:
        print("\n[DRY RUN] No files modified.")
        return new_version
    
    # Update files
    update_version_file(new_version, version_file)
    if changelog_file.exists():
        update_changelog(old_version, new_version, changelog_file)
    
    # Create git tag
    create_git_tag(new_version)
    
    return new_version


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    try:
        new_version = bump_version(dry_run=dry_run)
        print(f"\n✓ Version bumping complete: {new_version}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
