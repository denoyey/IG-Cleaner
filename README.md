<div align="center">
  
# 🧹 IG-CLEANER

<p align="center">
<strong>IG‑Cleaner</strong> is a terminal-based Python automation tool designed to help you clean up your Instagram account more efficiently.
It allows you to automatically unfollow accounts in bulk, remove users who don’t follow you back, and export your followers/following lists for further analysis — all from a simple command-line interface.
Ideal for personal cleanup or account optimization, IG‑Cleaner helps you regain control of your social graph with minimal effort.
</p>

<div align="center">

![Build](https://img.shields.io/badge/build-stable-28a745?style=for-the-badge&logo=github)
![Platform](https://img.shields.io/badge/platform-Linux-0078D6?style=for-the-badge&logo=linux&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/denoyey/IG-Cleaner?style=for-the-badge&logo=git)
![Language](https://img.shields.io/github/languages/top/denoyey/IG-Cleaner?style=for-the-badge&color=informational)
![Technologies](https://img.shields.io/badge/technologies-%20Python-yellow?style=for-the-badge&logo=terminal)
![Stars](https://img.shields.io/github/stars/denoyey/IG-Cleaner?style=for-the-badge&color=ffac33&logo=github)
![Forks](https://img.shields.io/github/forks/denoyey/IG-Cleaner?style=for-the-badge&color=blueviolet&logo=github)
![Issues](https://img.shields.io/github/issues/denoyey/IG-Cleaner?style=for-the-badge&logo=github)
![Contributors](https://img.shields.io/github/contributors/denoyey/IG-Cleaner?style=for-the-badge&color=9c27b0)

<br />

<img src="https://api.visitorbadge.io/api/VisitorHit?user=denoyey&repo=IG-Cleaner&countColor=%237B1E7A&style=flat-square" alt="visitors"/>

</div>

</div>

## 📖 Table of Contents

- [🔍 Overview](#-overview)
- [🛠 Features](#-features)
- [📎 Requirements](#-requirements)
- [📦 Installation](#-installation)
- [💡 Usage](#-usage)
  - [🔄 Auto Unfollow All Followers](#-auto-unfollow-all-followers)
  - [🚫 Auto Unfollow Non‑Followers Only](#-auto-unfollow-nonfollowers-only)
  - [📤 Export Follower/Following List](#-export-followerfollowing-list)
- [⚙️ Settings & Limits](#%EF%B8%8F-settings--limits)
- [📋 Logging](#-logging)
- [🧯 Safety Guidelines](#-safety-guidelines)
- [🤝 Contributing](#-contributing)
- [🧾 License](#-license)

## 🔍 Overview

IG‑Cleaner is a terminal-based Python tool that simplifies Instagram cleanup through automated unfollowing and exporting features. Built with `selenium`, enhanced by `rich` for UI, and designed with safety in mind, it ensures fast and controlled sessions.
<p align="left">
  <img src="https://github.com/denoyey/IG-Cleaner/blob/3c4ce28a5ac11d0f960eeea91df3c3803f9ecdc1/img/Review-Tools.png" alt="IG-Cleaner"/>
</p>

## 🛠 Features

-  **Auto Unfollow All Followers**: Remove everyone you're following in batches.
-  **Auto Unfollow Non-Followers**: Only unfollow users who don't follow you back.
-  **Export Data**: Save lists of followers/followings for analysis.
-  **Configurable Limits**: Use `settings.json` to adjust batch size, delays, and cooldowns.
-  **Stylish CLI**: Colorful branding and prompts using `rich`.
-  **Daily Log Rotation**: Keep organized records with automated date-based separation.

## 📎 Requirements

- Python 3.8+
- `selenium`
- `rich`
- `pandas`
- Chrome + matching `chromedriver` in the `drivers/` directory.

## 📦 Installation

```bash
git clone https://github.com/denoyey/IG-Cleaner.git
cd IG-Cleaner
pip install selenium rich pandas --break-system-packages
```
> Place chromedriver binary under drivers/, matching your OS. <br />
> (Optional) Customize settings via settings.json.

## 💡 Usage

```bash
python ig_cleaner.py
```
Menu-based interface will appear:
#### 🔄 Auto Unfollow All Followers: 
> Batch-unfollow all users you're following, with delays and cooldowns to reduce risk.
#### 🚫 Auto Unfollow Non‑Followers Only: 
> Unfollow only users who don't reciprocate, up to a safe limit per session.
#### 📤 Export Follower/Following List: 
> Save follower/following usernames to files, supporting later review or custom actions.

## ⚙️ Settings & Limits

Customize behavior via settings.json, with the following options:
```json
{
  "MAX_SAFE_LIMIT": 150,
  "BATCH_DELAY": 20,
  "SLEEP_BETWEEN": [2, 5],
  "SLEEP_AFTER_BATCH": 60
}
```
> Defaults will be used if the file is missing.

## 📋 Logging

Logs are saved in `log/logfile.log`, with daily separation if dates change. The tool automatically alerts if log files exceed 500 KB and resets them to keep output clean.

## 🧯 Safety Guidelines

- Always review Instagram's automation policies.
- Use conservative batch sizes and delays to minimize detection risk.
- Best to test on a secondary or test account.
- Manual login required—logout from other sessions to avoid conflicts.

## 🤝 Contributing

Contributions are welcome! Please follow the steps:
1. Fork the repo
2. Create a feature branch
3. Submit a pull request with clear description

## 🧾 License

Released under the **MIT License**. See the <a href="https://raw.githubusercontent.com/denoyey/IG-Cleaner/refs/heads/main/LICENSE">LICENSE</a> file for details.
