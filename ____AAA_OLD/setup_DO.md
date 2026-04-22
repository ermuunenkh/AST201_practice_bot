# AstroBot — DigitalOcean Deployment Guide

## 1. Create Droplet

1. Log in to [DigitalOcean](https://cloud.digitalocean.com) → **Create → Droplet**
2. Image: **Ubuntu 22.04 LTS**
3. Plan: **Basic — $6/month** (1 vCPU, 1 GB RAM, 25 GB SSD) — sufficient for 3 users
4. Datacenter: choose the region closest to your location
5. Authentication: **SSH Key** (add your public key)
6. Click **Create Droplet** and note the IP address

---

## 2. Initial Server Setup

```bash
# SSH in as root
ssh root@YOUR_DROPLET_IP

# Create a dedicated non-root user
adduser astrobot
usermod -aG sudo astrobot

# Configure UFW firewall (allow SSH only — bot uses outbound HTTPS, no inbound ports needed)
ufw allow OpenSSH
ufw enable
ufw status

# Switch to the astrobot user for all remaining steps
su - astrobot
```

---

## 3. Install Python

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Verify
python3.11 --version
```

---

## 4. Clone / Upload the Project

**Option A — git clone (recommended):**
```bash
sudo mkdir -p /opt/astrobot
sudo chown astrobot:astrobot /opt/astrobot
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git /opt/astrobot
cd /opt/astrobot
```

**Option B — scp from your local machine:**
```bash
# Run this on your local machine
scp -r ./AST201_practice_bot astrobot@YOUR_DROPLET_IP:/opt/astrobot
```

---

## 5. Set Up Virtual Environment

```bash
cd /opt/astrobot
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Configure Environment

```bash
cp .env.example .env
nano .env   # Fill in BOT_TOKEN and CHAT_ID_USER* values
chmod 600 .env
```

`.env` contents to fill in:
```
BOT_TOKEN=your_telegram_bot_token_here
DB_PATH=data/astrobot.db
LOG_LEVEL=INFO
CHAT_ID_USER1=123456789
CHAT_ID_USER2=987654321
CHAT_ID_USER3=111222333
```

To get your Telegram chat ID: message [@userinfobot](https://t.me/userinfobot) on Telegram.

---

## 7. Initialize Database & Images

```bash
source venv/bin/activate

# Create DB tables and seed questions
python -m db.database

# Generate sample diagram images
python -m utils.image_gen

# Run smoke tests to verify everything is wired correctly
python scripts/smoke_test.py
```

Expected output: `ALL SMOKE TESTS PASSED`

---

## 8. Set Up systemd Service

```bash
# Copy the unit file
sudo cp /opt/astrobot/astrobot.service /etc/systemd/system/

# Reload systemd, enable, and start
sudo systemctl daemon-reload
sudo systemctl enable astrobot
sudo systemctl start astrobot

# Verify it's running
sudo systemctl status astrobot
```

You should see `active (running)` in green.

---

## 9. View Logs

```bash
# Live tail (Ctrl+C to exit)
sudo journalctl -u astrobot -f

# Last hour
sudo journalctl -u astrobot --since "1 hour ago"

# File log (rotates at 5 MB, keeps 3 backups)
cat /opt/astrobot/logs/astrobot.log
```

---

## 10. Updating the Bot

```bash
cd /opt/astrobot
git pull                        # or scp new files
source venv/bin/activate
pip install -r requirements.txt # only if requirements changed
sudo systemctl restart astrobot
sudo systemctl status astrobot
```

---

## 11. Monitoring

```bash
sudo systemctl status astrobot  # service status
htop                            # CPU/RAM — expect ~50 MB RSS, <1% CPU
df -h                           # disk — logs capped at 15 MB, DB grows slowly
```

---

## 12. Troubleshooting

| Symptom | What to check |
|---|---|
| Bot not responding | `journalctl -u astrobot` — look for invalid token or network errors |
| `database is locked` | Only one process should access the DB — run `sudo systemctl status astrobot` to confirm no duplicate |
| Questions not sending | Check scheduler logs; verify `CHAT_ID_USER*` values in `.env` match actual chat IDs |
| Permission denied on `.env` | `sudo chown astrobot:astrobot /opt/astrobot/.env && chmod 600 /opt/astrobot/.env` |
| Bot keeps restarting | `journalctl -u astrobot --since "5 min ago"` for the actual exception |

---

## Adding New Questions

```bash
cd /opt/astrobot
source venv/bin/activate
python scripts/add_questions.py
sudo systemctl restart astrobot   # picks up new questions immediately
```
