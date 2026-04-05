# VAST SE Toolkit — Install Guide

Welcome! This guide will get the VAST SE Toolkit running on your laptop in about 10 minutes.

---

## Before you start

You'll need two things:

| | What | Why |
|--|------|-----|
| 1 | **Docker Desktop** | Runs the app |
| 2 | **Git** | Downloads the code |

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
docker compose pull
docker compose up -d
```

Your saved projects are never affected by updates.

---

## Need help?

Ping **Kimo** on Slack.
