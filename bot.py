from datetime import datetime
import time, random
from playwright.sync_api import sync_playwright
import os


# random start delay to avoid exact-time pattern (5–20 minutes)
delay_minutes = random.randint(5, 20)
delay_seconds = delay_minutes * 60

print(f"⏳ Waiting {delay_minutes} minutes before starting...")
time.sleep(delay_seconds)


# Recreate state.json when running in GitHub Actions
if not os.path.exists("state.json"):
    fb_state = os.getenv("FB_STATE")

    if fb_state:
        with open("state.json", "w", encoding="utf-8") as f:
            f.write(fb_state)
        print("state.json recreated from GitHub secret")

    else:
        print("Running locally — using existing state.json")



POST_LINK_1 = "https://www.facebook.com/permalink.php?story_fbid=pfbid0zTKLvZUh4AyRJyXu3UPNNV9c8GQxJxRaWFsdNAhZFf98z3XAiPv3HRWxJ5WhNx3Nl&id=100012472296110"
POST_LINK_2 = "https://www.facebook.com/permalink.php?story_fbid=pfbid0qRDBtCGeNtkn4YbCP79Vp7yXTT6rqxBR7SJtRCt3iJycwAAaBSszaj9C87XkvLVml&id=100012472296110"

CAMPAIGNS = [
    # {
    #     "post": POST_LINK_1,
    #     "groups_file": "groupsA.txt",
    #     "desc_file": "groupsA_descriptions.txt"
    # },
        {
        "post": POST_LINK_2,
        "groups_file": "groupsB.txt",
        "desc_file": "groupsB_descriptions.txt"
    },
]

# ---------- HELPERS ----------
def load_lines(file):
    with open(file, encoding="utf-8") as f:
        return [l.strip() for l in f.readlines() if l.strip()]



def pick_groups_by_day_parity(groups):
    day_of_year = datetime.now().timetuple().tm_yday
    
    if not day_of_year % 2 == 0:
        print("EVEN DAY → using EVEN lines")
        return groups[1::2]   # index 1,3,5,7...
    else:
        print("ODD DAY → using ODD lines")
        return groups[0::2]   # index 0,2,4,6...

# ---------- FACEBOOK ACTIONS ----------
def open_share_dialog(page, post_url):
    page.goto(post_url)
    page.wait_for_timeout(random.randint(3000, 5000))

    page.get_by_role("button", name="Wyślij do znajomych lub").click()
    page.wait_for_timeout(random.randint(2000, 3000))

    page.get_by_role("button", name="Udostępnij w grupie").click()
    page.wait_for_timeout(random.randint(2500, 3500))



def post_to_group(page, group, description):

    # scroll group list to load more groups
    for _ in range(random.randint(7,10)):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(random.randint(300,600))

    # choose group
    page.locator('div[role="dialog"] span').filter(has_text=group).first.click()
    page.wait_for_timeout(random.randint(2500,3500))

    # textbox
    textbox = page.get_by_role("textbox")
    textbox.wait_for(state="visible", timeout=20000)

    textbox.click()
    page.keyboard.type(description, delay=random.randint(25,40))
    page.wait_for_timeout(random.randint(800,1500))

    # publish
    page.get_by_role("button", name="Opublikuj").click()

    delay = random.randint(12, 25)
    print("⏳ Waiting", delay, "sec")
    time.sleep(delay)

# ---------- MAIN ----------
with sync_playwright() as p:

    #browser = p.chromium.launch(headless=False, slow_mo=250)
    RUNNING_IN_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"

    # Launch browser differently depending on environment
    if RUNNING_IN_GITHUB:
        print("☁️ Running in GitHub Actions (headless)")
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
    else:
        print("💻 Running locally (visible browser)")
        browser = p.chromium.launch(
            headless=False,
            slow_mo=250
        )


    context = browser.new_context(storage_state="state.json")
    page = context.new_page()


    for campaign in CAMPAIGNS:

        groups = load_lines(campaign["groups_file"])
        descriptions = load_lines(campaign["desc_file"])

        today_groups = pick_groups_by_day_parity(groups)

        print("\n🎯 Groups for today:")
        for g in today_groups:
            print("  •", g)

        for group in today_groups:

            # human delay before every post
            time.sleep(random.randint(5,12))

            # IMPORTANT → fresh dialog every post
            open_share_dialog(page, campaign["post"])

            desc = random.choice(descriptions)
            print("\n📢 Posting to:", group)
            post_to_group(page, group, desc)

    browser.close()
