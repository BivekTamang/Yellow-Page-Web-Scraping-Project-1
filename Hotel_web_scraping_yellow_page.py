import asyncio
import csv
import random
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

yp_rating_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
              "one half": 1.5, "two half": 2.5, "three half": 3.5, "four half": 4.5
              }

STATE_FILE = "scraper_state.txt"

def get_last_page():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 1
    return 1


def save_state(page_num):
    with open(STATE_FILE, "w") as f:
        f.write(str(page_num))


async def scrape_hotels():
    start_page = get_last_page()
    all_hotels = []

    async with async_playwright() as p:
        try:
            # 1. Launch a real-looking browser
            browser = await p.chromium.launch(headless=False)

            # 2. MANUAL STEALTH: Use a real user agent and disable the 'automation' flag
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # 3. EXTRA STEALTH: Mask the webdriver property
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            page.set_default_timeout(60000)

            print(f"🚀 Resuming from page {start_page}...")
            base_url = "https://www.yellowpages.com/search?search_terms=Hotels&geo_location=Los+Angeles%2C+CA"
            target_url = base_url if start_page == 1 else f"{base_url}&page={start_page}"

            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(1, 3))

            for current_page in range(start_page, start_page + 3):
                try:
                    print(f"📄 Scraping Page {current_page}...")
                    await page.wait_for_selector(".result", timeout=20000)

                    # Human-like scroll
                    await page.mouse.wheel(0, random.randint(500, 1000))
                    await asyncio.sleep(random.uniform(2, 5))

                    soup = BeautifulSoup(await page.content(), "html.parser")
                    cards = soup.select(".result")

                    page_data = []
                    for card in cards:
                        name_el = card.select_one(".business-name span")
                        hotel_name = name_el.get_text(strip=True) if name_el else "N/A"

                        phone_el = card.select_one(".phones")
                        phone = phone_el.get_text(strip=True) if phone_el else "N/A"

                        street_adr_el = card.select_one(".street-address")
                        street_adr = street_adr_el.get_text(strip=True) if street_adr_el else "N/A"
                        locality_el = card.select_one(".locality")
                        locality = locality_el.get_text(strip=True) if locality_el else ""
                        full_adr = f"{street_adr}, {locality}".strip() or "N/A"

                        website_el = card.select_one(".track-visit-website")
                        website = website_el.get("href").strip() if website_el else "N/A"

                        yp_rating_el = card.select_one(".result-rating")
                        if yp_rating_el:
                            classes = yp_rating_el.get("class", [])
                            if len(classes) > 0:
                                yp_rating_word = " ".join(classes[1:]).lower().strip()
                            else :
                                yp_rating_word = "None"
                        else:
                            yp_rating_word = "N/A"
                        yp_rating_score = yp_rating_map.get(yp_rating_word, 0)

                        ta_rating_el = card.select_one(".ta-rating")
                        if ta_rating_el:
                            classes = ta_rating_el.get("class", [])
                            rating_class = next((c for c in classes if c.startswith("ta-") and c != "ta-rating"), "")
                            if rating_class:
                                try:
                                    ta_val = float(rating_class.replace("ta-", "").replace("-", "."))
                                except ValueError:
                                    ta_val = 0.0
                            else:
                                ta_val = 0.0
                        else:
                            ta_val = 0.0

                        page_data.append({"Name": hotel_name,
                                         "Phone No": phone,
                                         "Address": full_adr,
                                         "Website Link": website,
                                         "Yellow Page Rating": yp_rating_score,
                                         "Trip Advisor Rating": ta_val
                                          })

                    all_hotels.extend(page_data)

                    # Save to CSV
                    file_exists = os.path.isfile("hotel_leads.csv")
                    with open("hotel_leads.csv", "a", newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=["Name", "Phone No", "Address", "Website Link", "Yellow Page Rating", "Trip Advisor Rating"])
                        if not file_exists:
                            writer.writeheader()
                        writer.writerows(page_data)

                    save_state(current_page + 1)

                    next_btn = await page.query_selector("a.next")
                    if next_btn:
                        await next_btn.click()
                        await page.wait_for_load_state("networkidle")
                        sleep_time = random.uniform(5, 8)
                        print(f"😴 Page loaded. Resting for {sleep_time:.2f}s...")
                        await asyncio.sleep(sleep_time)
                    else:
                        break

                except PlaywrightTimeout:
                    print(f"⚠️ Page {current_page} timed out.")
                    continue

        except Exception as e:
            print(f"❌ Fatal error: {e}")
        finally:
            if 'browser' in locals():
                await browser.close()
            print(f"📊 Final Session Summary: Found {len(all_hotels)} hotels.")


if __name__ == "__main__":
    asyncio.run(scrape_hotels())