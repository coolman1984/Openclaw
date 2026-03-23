#!/bin/bash
# OpenClaw GitHub SSH Setup for Termux (Android)
# Run this script inside Termux: bash setup-github.sh

set -e

GITHUB_USER="coolman1984"
REPO_NAME="Openclaw"
KEY_FILE="$HOME/.ssh/id_ed25519"

echo "======================================"
echo " OpenClaw GitHub SSH Setup for Termux"
echo "======================================"
echo ""

# Step 1: Install required packages
echo "[1/5] Installing required packages..."
pkg update -y -q
pkg install -y git openssh 2>/dev/null || true
echo "Done."
echo ""

# Step 2: Configure git identity
echo "[2/5] Configuring git identity..."
read -p "Enter your name for git commits: " GIT_NAME
read -p "Enter your GitHub email address: " GIT_EMAIL
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
echo "Git configured: $GIT_NAME <$GIT_EMAIL>"
echo ""

# Step 3: Generate SSH key if not already present
echo "[3/5] Setting up SSH key..."
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ -f "$KEY_FILE" ]; then
    echo "SSH key already exists at $KEY_FILE"
else
    ssh-keygen -t ed25519 -C "$GIT_EMAIL" -f "$KEY_FILE" -N ""
    echo "SSH key generated."
fi
echo ""

# Step 4: Display the public key
echo "[4/5] Your SSH public key (copy this to GitHub):"
echo ""
echo "------------------------------------------------------"
cat "${KEY_FILE}.pub"
echo "------------------------------------------------------"
echo ""
echo "Add this key to GitHub:"
echo "  https://github.com/settings/ssh/new"
echo ""
read -p "Press ENTER after you have added the key to GitHub..."
echo ""

# Step 5: Test connection and configure remote
echo "[5/5] Testing GitHub SSH connection..."
ssh -T git@github.com -o StrictHostKeyChecking=accept-new 2>&1 || true
echo ""

# Configure git to use SSH for this repo
CLONE_DIR="$HOME/$REPO_NAME"
if [ -d "$CLONE_DIR/.git" ]; then
    echo "Repo already cloned at $CLONE_DIR"
    echo "Setting remote to SSH..."
    cd "$CLONE_DIR"
    git remote set-url origin "git@github.com:$GITHUB_USER/$REPO_NAME.git"
    echo "Remote updated."
else
    echo "Cloning repo via SSH..."
    git clone "git@github.com:$GITHUB_USER/$REPO_NAME.git" "$CLONE_DIR"
    echo "Cloned to $CLONE_DIR"
fi

echo ""
echo "======================================"
echo " Setup complete!"
echo "======================================"
echo ""
echo "Your repo is at: $CLONE_DIR"
echo "Remote:          git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "Common git commands:"
echo "  cd $CLONE_DIR"
echo "  git pull              # get latest changes"
echo "  git add .             # stage changes"
echo "  git commit -m 'msg'  # commit"
echo "  git push              # push to GitHub"
