import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
import time # NEW: Imports the time module to slow the bot down

# Contains only the 20 links routed to the Cinema Guide
FEEDS = {
    "Sony": "https://www.google.com/alerts/feeds/17291303775024850829/4282056408381308358",
    "LG": "https://www.google.com/alerts/feeds/17291303775024850829/3966050588725823454",
    "Samsung": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469530916",
    "TCL": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169958105",
    "Hisense": "https://www.google.com/alerts/feeds/17291303775024850829/8594716954966055531",
    "Epson": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169957755",
    "JVC": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169958971",
    "BenQ": "https://www.google.com/alerts/feeds/17291303775024850829/10430992398900947754",
    "AWOL Vision": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469531862",
    "Formovie": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469531273",
    "Denon": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469532524",
    "Marantz": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469532135",
    "Yamaha": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469531498",
    "Onkyo": "https://www.google.com/alerts/feeds/17291303775024850829/8594716954966056501",
    "Pioneer": "https://www.google.com/alerts/feeds/17291303775024850829/8594716954966056346",
    "Klipsch": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169959681",
    "KEF": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169957388",
    "Bowers & Wilkins": "https://www.google.com/alerts/feeds/17291303775024850829/10430992398900948574",
    "SVS": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169958742",
    "Bose": "https://www.google.com/alerts/feeds/17291303775024850829/4282056408381307615"
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

# NEW: A robust browser disguise to prevent Google from blocking the connection
req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

for brand, rss_url in FEEDS.items():
    try:
        req = urllib.request.Request(rss_url, headers=req_headers)
        with urllib.request.urlopen(req) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:5]:
                raw_title = entry.find('{http://www.w3.org/2005/Atom}title').text
                clean_title = html.unescape(re.sub(r'<[^>]+>', '', raw_title))
                
                raw_link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                clean_link = raw_link.split('url=')[1].split('&ct=ga')[0] if 'url=' in raw_link else raw_link
                
                create_github_issue(clean_title, clean_link, brand)
    except Exception as e:
        print(f"Error checking {brand}: {e}")
    
    # NEW: Forces the script to pause for 2 seconds before moving to the next brand
    time.sleep(2)
