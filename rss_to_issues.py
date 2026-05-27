import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

FEEDS = {
    "Bose": "https://www.ecoustics.com/search/Bose/feed/rss2/",
    "Denon": "https://www.ecoustics.com/search/Denon/feed/rss2/",
    "Elac": "https://www.ecoustics.com/search/Elac/feed/rss2/",
    "Hisense": "https://www.ecoustics.com/search/Hisense/feed/rss2/",
    "JBL": "https://www.ecoustics.com/search/JBL/feed/rss2/",
    "KEF": "https://www.ecoustics.com/search/KEF/feed/rss2/",
    "Klipsch": "https://www.ecoustics.com/search/Klipsch/feed/rss2/",
    "LG": "https://www.ecoustics.com/search/LG/feed/rss2/",
    "Marantz": "https://www.ecoustics.com/search/Marantz/feed/rss2/",
    "Nakamichi": "https://www.ecoustics.com/search/Nakamichi/feed/rss2/",
    "Onkyo": "https://www.ecoustics.com/search/Onkyo/feed/rss2/",
    "Pioneer": "https://www.ecoustics.com/search/Pioneer/feed/rss2/",
    "Polk Audio": "https://www.ecoustics.com/search/Polk/feed/rss2/",
    "Samsung": "https://www.ecoustics.com/search/Samsung/feed/rss2/",
    "Sennheiser": "https://www.ecoustics.com/search/Sennheiser/feed/rss2/",
    "Sonos": "https://www.ecoustics.com/search/Sonos/feed/rss2/",
    "Sony": "https://www.ecoustics.com/search/Sony/feed/rss2/",
    "SVS": "https://www.ecoustics.com/search/SVS/feed/rss2/",
    "TCL": "https://www.ecoustics.com/search/TCL/feed/rss2/",
    "Ultimea": "https://www.ecoustics.com/search/Ultimea/feed/rss2/",
    "Yamaha": "https://www.ecoustics.com/search/Yamaha/feed/rss2/"
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
    print(f"📡 Requesting high-speed tunnel stream for: {brand}...")
    try:
        # Routing via the fast, unthrottled corsproxy network engine
        proxy_url = f"https://corsproxy.io/?{urllib.parse.quote(rss_url)}"
        req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=20) as response:
            xml_data = response.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            
            valid_count = 0
            for item in items:
                if valid_count >= 3: 
                    break
                    
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and link_elem is not None:
                    title_text = title_elem.text
                    link_text = link_elem.text
                    
                    search_keyword = "polk" if brand.lower() == "polk audio" else brand.lower()
                    if search_keyword not in title_text.lower():
                        continue
                        
                    create_github_issue(title_text, link_text, brand)
                    valid_count += 1
            
            print(f"   Done. Synced {valid_count} verified updates for {brand}.")
                    
    except Exception as e:
        print(f"⚠️ Skipped {brand}: {e}")
        
    time.sleep(1)
    
