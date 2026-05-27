import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

# Enterprise master streams that welcome direct, unproxied automation traffic
MASTER_FEEDS = [
    "https://www.techradar.com/rss",
    "https://www.engadget.com/rss.xml",
    "https://www.whathifi.com/rss"
]

BRANDS = [
    "Bose", "Denon", "Elac", "Hisense", "JBL", "KEF", "Klipsch", "LG", 
    "Marantz", "Nakamichi", "Onkyo", "Pioneer", "Polk Audio", "Samsung", 
    "Sennheiser", "Sonos", "Sony", "SVS", "TCL", "Ultimea", "Yamaha"
]

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "kalpdev2010-hub/dubai-cinema-guide"

def create_github_issue(title, link, brand):
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    check_url = f"{url}?labels={urllib.parse.quote(brand)}&state=all"
    try:
        with urllib.request.urlopen(urllib.request.Request(check_url, headers=headers)) as resp:
            existing = json.loads(resp.read().decode())
            if any(issue['title'] == title for issue in existing):
                return
    except Exception:
        pass

    data = json.dumps({"title": title, "body": link, "labels": [brand]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        urllib.request.urlopen(req)
        print(f"✅ Posted to Radar [{brand}]: {title}")
    except Exception as e:
        print(f"❌ GitHub API Error: {e}")

# Collect raw data directly from open syndication channels
seen_links = set()
all_articles = []

for url in MASTER_FEEDS:
    print(f"📡 Fetching open channel stream: {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                if title_elem is not None and link_elem is not None:
                    t_text = title_elem.text
                    l_text = link_elem.text
                    if l_text not in seen_links:
                        seen_links.add(l_text)
                        all_articles.append({"title": t_text, "link": l_text})
    except Exception as e:
        print(f"⚠️ Channel skip warning: {e}")

print(f"🔍 Sorting {len(all_articles)} live industry updates into brand blueprints...")

brand_counts = {b: 0 for b in BRANDS}

# Validate content matching rules to avoid scrambled results
for article in all_articles:
    title_lower = article["title"].lower()
    
    for brand in BRANDS:
        if brand_counts[brand] >= 3:
            continue
            
        keyword = "polk" if brand.lower() == "polk audio" else brand.lower()
        
        if keyword in title_lower:
            create_github_issue(article["title"], article["link"], brand)
            brand_counts[brand] += 1
            time.sleep(1)

print("🏁 Automation process concluded cleanly.")
