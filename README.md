# OpenClaw — GitHub Connection Setup (Termux/Android)

Connect your OpenClaw instance running on Android (Termux) to this GitHub repository.

## Prerequisites

- Termux installed on your Android phone
- Internet connection
- A GitHub account (github.com/coolman1984)

---

## Quick Setup

Run this single command inside Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/coolman1984/Openclaw/main/setup-github.sh | bash
```

Or if you already have the repo cloned:

```bash
bash setup-github.sh
```

The script will walk you through all steps automatically.

---

## What the Script Does

1. **Installs packages** — `git` and `openssh` via `pkg`
2. **Configures git** — sets your name and email
3. **Generates SSH key** — creates an Ed25519 key pair (skips if already exists)
4. **Displays your public key** — copy this to GitHub
5. **Tests the connection** — verifies SSH auth works
6. **Clones or updates the repo** — sets up the remote with SSH

---

## Manual Steps (if you prefer)

### 1. Install packages
```bash
pkg update && pkg install git openssh
```

### 2. Generate SSH key
```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

### 3. Copy your public key
```bash
cat ~/.ssh/id_ed25519.pub
```

### 4. Add key to GitHub
Go to: https://github.com/settings/ssh/new
Paste your public key and save.

### 5. Test the connection
```bash
ssh -T git@github.com
```
You should see: `Hi coolman1984! You've successfully authenticated`

### 6. Clone the repo
```bash
git clone git@github.com:coolman1984/Openclaw.git ~/Openclaw
```

---

## Troubleshooting

**Permission denied (publickey)**
→ Make sure you added the key at https://github.com/settings/keys

**ssh: connect to host github.com port 22: Connection refused**
→ Try SSH over HTTPS port:
```bash
ssh -T -p 443 git@ssh.github.com
```
And add this to `~/.ssh/config`:
```
Host github.com
    Hostname ssh.github.com
    Port 443
```

**pkg command not found**
→ You're not in Termux. Make sure you're running this on Android inside the Termux app.

---

## Daily Usage

```bash
cd ~/Openclaw

# Get latest changes from GitHub
git pull

# After making changes
git add .
git commit -m "your message"
git push
```
