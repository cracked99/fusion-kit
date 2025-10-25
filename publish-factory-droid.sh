#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Publishing Factory Droid Support to Your Fork                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect GitHub username
GITHUB_USER=$(git config --get user.name)
if [ -z "$GITHUB_USER" ]; then
    echo -e "${YELLOW}⚠ GitHub username not found in git config${NC}"
    echo -n "Enter your GitHub username: "
    read GITHUB_USER
fi

echo -e "${BLUE}GitHub Username: ${GITHUB_USER}${NC}"
echo

# Check if fork remote already exists
if git remote | grep -q "^myfork$"; then
    echo -e "${YELLOW}⚠ Remote 'myfork' already exists${NC}"
    echo "Current remotes:"
    git remote -v
    echo
    echo -n "Do you want to update it? (y/n): "
    read UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url myfork "https://github.com/${GITHUB_USER}/spec-kit.git"
        echo -e "${GREEN}✓ Updated myfork remote${NC}"
    fi
else
    # Add fork as remote
    echo -e "${BLUE}Step 1: Adding your fork as remote...${NC}"
    git remote add myfork "https://github.com/${GITHUB_USER}/spec-kit.git"
    echo -e "${GREEN}✓ Added myfork remote${NC}"
fi

echo
git remote -v
echo

# Commit changes
echo -e "${BLUE}Step 2: Committing changes...${NC}"
git add .
git commit -m "feat: add Factory Droid AI agent support

- Added Factory Droid to AGENT_CONFIG with .factory/ folder structure
- Updated CLI help text and documentation
- Added to release packaging scripts
- Updated agent context scripts (bash & PowerShell)
- Bumped version to 0.0.21
- Updated CHANGELOG and README

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"

echo -e "${GREEN}✓ Changes committed${NC}"
echo

# Push to fork
echo -e "${BLUE}Step 3: Pushing to your fork...${NC}"
echo -e "${YELLOW}⚠ This will push to: https://github.com/${GITHUB_USER}/spec-kit.git${NC}"
echo -n "Continue? (y/n): "
read CONTINUE

if [ "$CONTINUE" != "y" ]; then
    echo "Aborted."
    exit 0
fi

git push myfork main

echo -e "${GREEN}✓ Pushed to your fork${NC}"
echo

# Instructions for creating release
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Next Steps: Create a Release                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo
echo -e "${BLUE}Option 1: Via GitHub Web UI${NC}"
echo "  1. Go to: https://github.com/${GITHUB_USER}/spec-kit/releases/new"
echo "  2. Tag: v0.0.21"
echo "  3. Target: main"
echo "  4. Title: v0.0.21 - Factory Droid Support"
echo "  5. Description: Added Factory Droid AI agent support"
echo "  6. Click 'Publish release'"
echo
echo -e "${BLUE}Option 2: Via GitHub CLI (if installed)${NC}"
echo "  gh release create v0.0.21 \\"
echo "    --repo ${GITHUB_USER}/spec-kit \\"
echo "    --title 'v0.0.21 - Factory Droid Support' \\"
echo "    --notes 'Added Factory Droid AI agent support'"
echo
echo -e "${BLUE}After release is created:${NC}"
echo "  1. Check GitHub Actions: https://github.com/${GITHUB_USER}/spec-kit/actions"
echo "  2. Wait for templates to build (droid-sh and droid-ps zips)"
echo "  3. Install from your fork:"
echo "     uv tool install --force --from git+https://github.com/${GITHUB_USER}/spec-kit.git@v0.0.21 specify-cli"
echo "  4. Test: specify init test-project --ai droid"
echo
echo -e "${GREEN}✓ Ready to create release!${NC}"
