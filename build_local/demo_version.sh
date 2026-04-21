#!/bin/bash
# Demonstration script for version bumping
# Shows how commits with conventional format trigger version bumps

set -e

echo "=== Version Bump Demonstration ==="
echo ""

# Show current version
echo "📌 Current version:"
python3 -c "from src.models.version import __version__; print(f'   {__version__}')"
echo ""

# Show current git status
echo "📝 Recent commits (last 5):"
git log --oneline -5 2>/dev/null || echo "   (No git history available)"
echo ""

# Run dry-run to show what would happen
echo "🔍 Testing version bump (dry-run)..."
python3 build_local/bump_version.py --dry-run
echo ""

# Explain the result
echo "📚 To trigger version bumps in your commits, use:"
echo ""
echo "   Minor bump (feature):   git commit -m 'feat: description'"
echo "   Patch bump (bugfix):    git commit -m 'fix: description'"
echo "   Major bump (breaking):  git commit -m 'breaking: description'"
echo ""
echo "Non-bumping commits:"
echo "   git commit -m 'docs: description'"
echo "   git commit -m 'test: description'"
echo "   git commit -m 'chore: description'"
echo ""
echo "For details, see VERSIONING.md and VERSIONING_ES.md"
