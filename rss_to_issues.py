import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

FEEDS = {
    "Hisense": "https://www.google.com/alerts/feeds/17291303775024850829/5960888969352555332",
    "Sony": "https://www.google.com/alerts/feeds/17291303775024850829/10303995424947548603",
    "TCL": "https://www.google.com/alerts/feeds/17291303775024850829/3220531133169958105",
    "Bose": "https://www.google.com/alerts/feeds/17291303775024850829/8335236053045408598",
    "Denon": "https://www.google.com/alerts/feeds/17291303775024850829/10983863551238171227",
    "Elac": "https://www.google.com/alerts/feeds/17291303775024850829/954187907946175596",
    "JBL": "https://www.google.com/alerts/feeds/17291303775024850829/8770291637029842920",
    "KEF": "https://www.google.com/alerts/feeds/17291303775024850829/16568459237653120296",
    "Klipsch": "https://www.google.com/alerts/feeds/17291303775024850829/4876680161368429316",
    "Marantz": "https://www.google.com/alerts/feeds/17291303775024850829/9277765981800493523",
    "Nakamichi": "https://www.google.com/alerts/feeds/17291303775024850829/8770291637029839827",
    "Onkyo": "https://www.google.com/alerts/feeds/17291303775024850829/3779327338424839596",
    "Pioneer": "https://www.google.com/alerts/feeds/17291303775024850829/3779327338424837370",
    "Polk Audio": "https://www.google.com/alerts/feeds/17291303775024850829/954187907946176341",
    "LG": "https://www.google.com/alerts/feeds/17291303775024850829/5960888969352555350",
    "Sennheiser": "https://www.google.com/alerts/feeds/17291303775024850829/4876680161368428601",
    "Sonos": "https://www.google.com/alerts/feeds/17291303775024850829/8335236053045409735",
    "SVS": "https://www.google.com/alerts/feeds/17291303775024850829/954187907946176256",
    "Ultimea": "https://www.google.com/alerts/feeds/17291303775024850829/2380353577314263395",
    "Yamaha": "https://www.google.com/alerts/feeds/17291303775024850829/13713156402188461531"
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
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                raw_link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                clean_link = raw_link.split('url=')[1].split('&ct=ga')[0] if 'url=' in raw_link else raw_link
                
                create_github_issue(title, clean_link, brand)
    except Exception as e:
        print(f"Error checking {brand}: {e}")
