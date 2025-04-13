# 🧠 Web Automation: Google Form Filler

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This Python automation script uses [Playwright](https://playwright.dev/python/) to auto-fill a Google Form for daily work breakdown reporting. It preserves login state, validates your inputs, and gives helpful logging to guide you through the process.

---

## 🚀 Features

- ✅ Automates a daily work breakdown form
- 🔒 Preserves Google login using a persistent Chrome profile
- 📅 Accepts CLI arguments to fill in each category (repair, deploy, etc.)
- 🧮 Validates that total hours sum to exactly **8**
- 🧠 Intelligent CLI feedback: shows what you entered and if defaults were used
- ⏸️ Pauses at key steps for inspection or manual interaction

---

## ⚙️ Requirements

- Python 3.9+
- [Playwright](https://playwright.dev/python/)
- Google Chrome (installed)

---

## 📦 Setup

1. **Clone the repo:**

```bash
git clone https://github.com/Requiem-of-Zero/web-automation.git
cd web-automation
```

2. **Create a virtual environment and activate it:**

```bash
python3 -m venv .venv #required for MacOS
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
python -m playwright install
```

4. **First Time Google Login**

```bash
python fill_work_breakdown.py --date YYYY-MM-DD --ldap yourusername
```

5. **Usage**

```bash
# Values must add up to 8 hours
python fill_work_breakdown.py \
  # Date time is required input, format must meet criteria YYYY-MM-DD
  --date 2024-04-12 \ 
  # Repair time supports hours only, --repair {hours}
  --repair 2 \
  # Deploy time supports hours only, --deploy {hours}
  --deploy 1 \
  # Project time supports hours only, --project {hours}
  --project 2 \
  # Decoms time supports hours only, --decom {hours}
  --decom 0 \
  # Admin time supports hours only, --admin {hours}
  --admin 3 \
  # OOO time supports hours only, --ooo {hours}
  --ooo 0 \
  --ldap yourusername
```


🧼 Tips
- To reset login: delete ~/.chrome-playwright-profile and run again or logout of profile in the automation browser
- You can update the default settings to your specific preferences
- To run in headless mode, modify headless=True in the script
- To run automatically: use cron, launchd, or a simple loop

## 📜 License

This project is licensed under the [MIT License](LICENSE) © [Requiem-of-Zero](https://github.com/Requiem-of-Zero).