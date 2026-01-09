🏨 Yellow Pages & Hospitality Data Extraction Bot

📖 Overview
This project is an Advanced Lead Generation Tool designed to extract high-quality hospitality data from dynamic web directories.
Unlike basic scrapers, this bot is engineered to handle Single Page Applications (SPAs) and dynamic content that requires user interaction (scrolling, clicking, and waiting).
I built this to solve the problem of manual lead research for real estate and hospitality investors, turning hours of copy-pasting into a 30-second automated task.

✨ Key Features
-Anti-Bot Resilience: Implements playwright-stealth and randomized human-like behavioral patterns (scrolling, mouse jitters) to prevent IP flagging.
-Smart Data Normalization: A custom logic layer that translates complex CSS-based ratings (e.g., star icons) into clean numerical data (4.5/5).
-State Persistence: Saves the "last scraped page" locally. If your internet drops, the bot resumes from where it left off.
-Performance Optimized: Uses headless browser execution and efficient selective waiting to maximize speed while minimizing CPU usage.

🛠️ Tech Stack
-Language: Python
-Automation: Playwright (Chromium)
-Parsing: BeautifulSoup4
-Data File: .CSV
-Stealth: Manual User_Agent

🚀 Quick Start
1.Prerequisites
-Python 18.0+
-Playwright

2. Installation
-Clone the repository
-git clone https://github.com/BivekTamang/Yellow-Page-Web-Scraping-Project-1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

3.python main.py
The script will generate a hotel_leads_DATE.csv file in the root directory.

📊 Sample Output
-Hotel Name
-Phone No
-Address
-Link
-Rating

Ethical Considerations
-This tool was developed for educational and research purposes.
-It respects robots.txt directives.
-It includes a mandatory time.sleep() delay between requests to avoid over-burdening target servers.
-User is responsible for complying with the Terms of Service of the target website.
