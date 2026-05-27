import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

FEEDS = {
    "Sony": "https://www.ecoustics.com/search/Sony/feed/rss2/",
    "LG": "https://www.ecoustics.com/search/LG/feed/rss2/",
    "Samsung": "https://www.ecoustics.com/search/Samsung/feed/rss2/",
    "TCL": "https://www.ecoustics.com/search/TCL/feed/rss2/",
    "Hisense": "https://www.ecoustics.com/search/Hisense/feed/rss2/",
    "Epson": "https://www.ecoustics.com/search/Epson/feed/rss2/",
    "JVC": "https://www.ecoustics.com/search/JVC/feed/rss2/",
    "BenQ": "https://www.ecoustics.com/search/BenQ/feed/rss2/",
    "AWOL Vision": "https://www.ecoustics.com/search/AWOL+Vision/feed/rss2/",
    "Formovie": "https://www.ecoustics.com/search/Formovie/feed/rss2/",
    "Denon": "https://www.ecoustics.com/search/Denon/feed/rss2/",
    "Marantz": "https://www.ecoustics.com/search/Marantz/feed/rss2/",
    "Yamaha": "https://www.ecoustics.com/search/Yamaha/feed/rss2/",
    "Onkyo": "https://www.ecoustics.com/search/Onkyo/feed/rss2/",
    "Pioneer": "https://www.ecoustics.com/search/Pioneer/feed/rss2/",
    "Klipsch": "https://www.ecoustics.com/search/Klipsch/feed/rss2/",
    "KEF": "https://www.ecoustics.com/search/KEF/feed/rss2/",
    "Bowers & Wilkins": "https://www.ecoustics.com/search/Bowers+%26+Wilkins/feed/rss2/",
    "SVS": "https://www.ecoustics.com/search/SVS/feed/rss2/",
    "Bose": "https://www.ecoustics.com/search/Bose/feed/rss2/"
}

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
        print(f"✅ Posted to Radar: {title}")
    except Exception as e:
        print(f"❌ Error: {e}")

for brand, rss_url in FEEDS.items():
    print(f"📡 Connecting to broker channel for: {brand}...")
    try:
        # Added a timestamp token to completely eliminate broker cache reuse
        broker_url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.parse.quote_plus(rss_url)}&_cb={int(time.time())}"
        
        req = urllib.request.Request(broker_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'ok':
                items = data.get('items', [])
                print(f"   Success! Received {len(items)} items for {brand}.")
                
                for item in items[:3]:
                    title = item.get('title')
                    link = item.get('link')
                    if title and link:
                        create_github_issue(title, link, brand)
            else:
                print(f"   ⚠️ Broker feed translation skipped for {brand}")
                    
    except Exception as e:
        print(f"❌ Connection error for {brand}: {e}")
    time.sleep(1)
    
