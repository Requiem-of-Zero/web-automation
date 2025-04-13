import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import platform
import argparse

# Get the path to the installed Chrome browser based on the OS
def get_chrome_path():
    system = platform.system()
    if system == "Darwin":  # macOS
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        return "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    elif system == "Linux":
        return "/usr/bin/google-chrome"
    else:
        raise RuntimeError("Unsupported OS")

# Get the directory path where the browser profile is stored (for saved login sessions)
def get_profile_path():
    return Path.home() / ".chrome-playwright-profile"

# Parse command-line arguments to get form data
def parse_args():
    parser = argparse.ArgumentParser(description="Submit work breakdown to Google Form.")
    parser.add_argument("--date", required=True, help="Date to fill in the form (YYYY-MM-DD)")
    parser.add_argument("--repair", default="2", help="Repair hours")
    parser.add_argument("--deploy", default="0", help="Deployment hours")
    parser.add_argument("--project", default="2", help="Project hours")
    parser.add_argument("--decom", default="0", help="Decommission hours")
    parser.add_argument("--admin", default="4", help="Admin hours")
    parser.add_argument("--ooo", default="0", help="Out of Office hours")
    parser.add_argument("--ldap", default="samwo", help="LDAP of user filling form")
    return parser.parse_args()

# Launch a persistent browser and fill out the Google Form using Playwright
def fill_google_form(date, groups):
    print("🟢 Starting clean session with persistent login...")

    chrome_path = get_chrome_path()
    profile_path = get_profile_path()

    with sync_playwright() as p:
        # Launch Chrome with a persistent context to preserve login session
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),       # Uses saved Chrome profile (keeps login session)
            executable_path=chrome_path,           # Use full Chrome, not bundled Chromium
            headless=False,                        # Show the browser window
            slow_mo=100,                           # Slow down each step for visibility/debugging, throttle control to ensure automation accuracy
            args=["--disable-blink-features=AutomationControlled"]  # Helps bypass bot detection
        )

        # Open a new page in the browser
        page = context.new_page()
        print("🔗 Navigating to the Google Form...")
        page.goto("https://docs.google.com/forms/d/e/1FAIpQLSfmkdQ5mYRyKZpHUtJTGOWOS7jarU-4h5n9w-PxxscoE3AltQ/viewform")

        # Fill in the form fields using roles and labels
        page.get_by_role("textbox", name="Date").fill(date)                                # Fill date field
        page.locator(".e2CuFe").click()                                                    # Click the LDAP dropdown
        page.get_by_role("option", name=groups["ldap"]).locator("span").click()            # Select the user's name
        page.get_by_role("group", name="Repairs").get_by_label("Hours").fill(groups["repair"])         # Repair hours
        page.get_by_role("group", name="Deployments").get_by_label("Hours").fill(groups["deploy"])     # Deployment hours
        page.get_by_role("group", name="Projects").get_by_label("Hours").fill(groups["project"])       # Project hours
        page.get_by_role("group", name="Decomms").get_by_label("Hours").fill(groups["decom"])          # Decommission hours
        page.get_by_role("group", name="Administrative").get_by_label("Hours").fill(groups["admin"])   # Admin hours
        page.get_by_role("group", name="OOO Time").get_by_label("Hours").fill(groups["ooo"])           # Out of Office hours
        page.pause()  # Pause the browser so you can inspect or submit manually if needed. Comment this line out to enable automation to get to submission

        # page.get_by_role("button", name="Submit").click() uncomment this line to enable submission
        context.close()  # Close the browser when done

# Entry point when the script is run from the command line
if __name__ == "__main__":
    args = parse_args()
    
    # Organize group hours into a dictionary for easier access
    groups = {
        "repair": args.repair,
        "deploy": args.deploy,
        "project": args.project,
        "decom": args.decom,
        "admin": args.admin,
        "ooo": args.ooo,
        "ldap": args.ldap
    }

    # ✅ Validate total hours add up to exactly 8
    try:
        total_hours = sum(float(groups[key]) for key in ["repair", "deploy", "project", "decom", "admin", "ooo"])
    except ValueError:
        print("❌ Error: One or more hour inputs are not valid numbers.")
        exit(1)

    if total_hours != 8:
        print(f"❌ Error: Total hours must equal 8. You entered: {total_hours}")
        print(f"Repair time: {args.repair}")
        print(f"Deployment time: {args.deploy}")
        print(f"Project time: {args.project}")
        print(f"Decommission time: {args.decom}")
        print(f"Administrative time: {args.admin}")
        print(f"OOO time: {args.ooo}")
        print(f"Please update default values in the parse arguments if what is set isn't what you prefer")
        exit(1)

    # Run the form-filling automation
    fill_google_form(args.date, groups)
