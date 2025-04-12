import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import platform
import argparse

def get_chrome_path():
    system = platform.system()
    if system == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        return "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    elif system == "Linux":
        return "/usr/bin/google-chrome"
    else:
        raise RuntimeError("Unsupported OS")

def get_profile_path():
    return Path.home() / ".chrome-playwright-profile"

def get_auth_path():
    return Path.home() / ".config" / "playwright" / "auth.json"

def save_auth_with_persistent_context():
    print("🔐 Launching persistent browser for login...")
    chrome_path = get_chrome_path()
    profile_path = get_profile_path()
    profile_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            executable_path=chrome_path,
            headless=False,
            slow_mo=300,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.new_page()
        page.goto("https://accounts.google.com/")

        print("📝 Sign in manually in the browser.")
        input("⏸️  After sign-in, press [Enter] to continue...")

        print("🌐 Going to form to verify session...")
        page.goto("https://docs.google.com/forms/d/e/1FAIpQLSfmkdQ5mYRyKZpHUtJTGOWOS7jarU-4h5n9w-PxxscoE3AltQ/viewform")

        # Save session
        context.storage_state(path=get_auth_path())
        print(f"✅ Auth state saved to: {get_auth_path()}")
        context.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Submit work breakdown to Google Form.")
    parser.add_argument("--date", required=True, help="Date to fill in the form (MM-DD-YYYY or YYYY-MM-DD)")
    parser.add_argument("--repair", default="0", help="Repair hours")
    parser.add_argument("--deploy", default="0", help="Deployment hours")
    parser.add_argument("--project", default="0", help="Project hours")
    parser.add_argument("--decom", default="0", help="Decommission hours")
    parser.add_argument("--admin", default="0", help="Admin hours")
    parser.add_argument("--ooo", default="0", help="Out of Office hours")
    parser.add_argument("--ldap", required=True, help="LDAP of user filling form")
    return parser.parse_args()


def fill_google_form(date, groups):
    print("🟢 Starting clean session with saved login...")

    chrome_path = get_chrome_path()
    auth_path = get_auth_path()
    # --repair {time}
    repair_time = groups["repair"]
    # --deploy {time}
    deploy_time = groups["deploy"]
    project_time = groups["project"]
    decom_time = groups["decom"]
    admin_time = groups["admin"]
    ooo_time = groups["ooo"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome_path,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(storage_state=str(auth_path))
        page = context.new_page()

        print("🔗 Navigating to the Google Form...")
        page.goto("https://docs.google.com/forms/d/e/1FAIpQLSfmkdQ5mYRyKZpHUtJTGOWOS7jarU-4h5n9w-PxxscoE3AltQ/viewform")
        page.get_by_role("textbox", name="Date").click()
        page.get_by_role("textbox", name="Date").fill(date)
        page.locator(".e2CuFe").click()
        page.get_by_role("option", name=groups["ldap"]).locator("span").click()
        page.get_by_role("group", name="Repairs").get_by_label("Hours").click()
        page.get_by_role("group", name="Repairs").get_by_label("Hours").fill(repair_time)
        page.get_by_role("group", name="Deployments").get_by_label("Hours").click()
        page.get_by_role("group", name="Deployments").get_by_label("Hours").fill(deploy_time)
        page.get_by_role("group", name="Projects").get_by_label("Hours").click()
        page.get_by_role("group", name="Projects").get_by_label("Hours").fill(project_time)
        page.get_by_role("group", name="Decomms").get_by_label("Hours").click()
        page.get_by_role("group", name="Decomms").get_by_label("Hours").fill(decom_time)
        page.get_by_role("group", name="Administrative").get_by_label("Hours").click()
        page.get_by_role("group", name="Administrative").get_by_label("Hours").fill(admin_time)
        page.get_by_role("group", name="OOO Time").get_by_label("Hours").click()
        page.get_by_role("group", name="OOO Time").get_by_label("Hours").fill(ooo_time)
        page.pause()
        page.get_by_role("textbox", name="Date").fill(date)
        # Your form-filling logic...
        # (Don't use page.get_by_role(..., name=...) unless you've confirmed the labels)

        context.close()
        browser.close()

if __name__ == "__main__":
    args = parse_args()
    groups = {
        "repair": args.repair,
        "deploy": args.deploy,
        "project": args.project,
        "decom": args.decom,
        "admin": args.admin,
        "ooo": args.ooo,
        "ldap": args.ldap
    }

    if not get_auth_path().exists():
        save_auth_with_persistent_context()
        print("🔁 Auth saved. Re-run the script to submit the form.")
    else:
        fill_google_form(args.date, groups)