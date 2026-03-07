#!/bin/bash
# Deploy x402-guide-site to GitHub Pages
set -e

REPO_NAME="x402-guide-site"
GITHUB_USER="pedropcruz"  # Update with your GitHub username

cd "$(dirname "$0")"

echo "=== x402 Guide Site — Deploy to GitHub Pages ==="

# Initialize git if needed
if [ ! -d ".git" ]; then
  echo "Initializing git repo..."
  git init
  git branch -M main
fi

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
EOF

# Create CNAME for custom domain (optional)
# echo "x402.guide" > CNAME

# Stage and commit
git add -A
git commit -m "Deploy x402 guide site" || echo "Nothing to commit"

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
  echo ""
  echo "No remote configured. To deploy:"
  echo ""
  echo "1. Create a repo on GitHub called '$REPO_NAME'"
  echo "2. Run:"
  echo "   git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
  echo "   git push -u origin main"
  echo ""
  echo "3. Go to Settings > Pages > Source: Deploy from branch (main)"
  echo "4. (Optional) Add custom domain: x402.guide"
  echo ""
else
  echo "Pushing to GitHub..."
  git push -u origin main
  echo ""
  echo "Pushed! Enable GitHub Pages in repo Settings > Pages"
fi

echo "=== Done ==="
