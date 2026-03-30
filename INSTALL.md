# VAST SE Toolkit — Install Guide

Welcome! This guide will get the VAST SE Toolkit running on your laptop in about 10 minutes.

---

## Before you start

You'll need three things:

| | What | Why |
|--|------|-----|
| 1 | **Docker Desktop** | Runs the app |
| 2 | **Git** | Downloads the code |
| 3 | **GitHub access** | The repo is private — request access from Kimo first |

---

## Request access from Kimo

Before installing anything, make sure Kimo has added you to the repo.

1. Log in to [github.com](https://github.com) — your username is shown in the top-right corner
2. Send Kimo a Slack message:
   > *"Hi Kimo, can you add me to the VAST SE Toolkit repo? My GitHub username is: `your-username`"*
3. You'll get an email from GitHub — open it and click **Accept invitation**

> Don't skip this — the install will fail at the download step if you haven't accepted the invite.

---

## Choose your OS

Follow the guide for your operating system:

- [macOS Install Guide](docs/INSTALL_MAC.md)
- [Windows Install Guide](docs/INSTALL_WINDOWS.md)
- [Linux Install Guide](docs/INSTALL_LINUX.md)

---

## Day-to-day use

Once installed, double-click the Desktop launcher. It will start the app and open your browser automatically.

Or go to **http://localhost:8501** in any browser.

---

## Updating

When Kimo releases a new version, open a terminal and run:

```bash
cd ~/projects/vast-se-toolkit
git pull
docker compose up --build -d
```

Your saved projects are never affected by updates.

---

## Need help?

Ping **Kimo** on Slack.
