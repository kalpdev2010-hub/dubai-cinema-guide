import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

# Strictly synchronized with the 21 brand buttons on your website frontend
FEEDS = {
    "Bose": "https://www.ecoustics.com/search/Bose/feed/rss2/",
    "Denon": "https://www.ecoustics.com/search/Denon+Receiver/feed/rss2/",
    "Elac": "https://www.ecoustics.com/search/Elac/feed/rss2/",
    "Hisense": "https://www.ecoustics.com/search/Hisense/feed/rss2/",
    "JBL": "https://www.ecoustics.com/search/JBL/feed/rss2/",
    "KEF": "https://www.ecoustics.com/search/KEF/feed/rss2/",
    "Klipsch": "https://www.ecoustics.com/search/Klipsch/feed/rss2/",
    "LG": "https://www.ecoustics.com/search/LG/feed/rss2/",
    "Marantz": "https://www.ecoustics.com/search/Marantz/feed/rss2/",
    "Nakamichi": "https://www.ecoustics.com/search/Nakamichi/feed/rss2/",
    "Onkyo": "https://www.ecoustics.com/search/Onkyo/feed/rss2/",
    "Pioneer": "https://www.ecoustics.com/search/Pioneer+AVR/feed/rss2/",
    "Polk Audio": "https://www.ecoustics.com/search/Polk+Audio/feed/rss2/",
    "Samsung": "https://www.ecoustics.com/search/Samsung/feed/rss2/",
    "Sennheiser": "https://www.ecoustics.com/search/Sennheiser/feed/rss2/",
    "Sonos": "https://www.ecoustics.com/search/Sonos/feed/rss2/",
    "Sony": "https://www.ecoustics.com/search/Sony+TV/feed/rss2/",
    "SVS": "https://www.ecoustics.com/search/SVS/feed/rss2/",
    "TCL": "https://www.ecoustics.com/search/TCL/feed/rss2/",
    "Ultimea": "https://www.ecoustics.com/search/Ultimea/feed/rss2/",
    "Yamaha": "https://www.ecoustics.com/search/Yamaha+Receiver/feed/rss2/"
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

# Processes feeds using an unthrottled open-source network proxy to bypass 429 blocks
for brand, rss_url in FEEDS.items():
    print(f"📡 Fetching unthrottled data tunnel for: {brand}...")
    try:
        # Routes requests via AllOrigins raw proxy tunnel
        proxy_url = f"https://api.allorigins.win/raw?url={urllib.parse.quote_plus(rss_url)}"
        req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_data)
            
            items = root.findall('.//item')
            print(f"   Success! Located {len(items)} matching radar stories.")
            
            for item in items[:3]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and link_elem is not None:
                    create_github_issue(title_elem.text, link_elem.text, brand)
                    
    except Exception as e:
        print(f"⚠️ Skipped processing cycle for {brand}. Reason: {e}")
        
    time.sleep(2)
    
    
