import json
import urllib.request
import urllib.parse
import re

# CONFIRMED 2026 SUCCESSOR MAP
# We use the technical model strings found in expert reviews
TARGET_UPGRADES = [
    {"old": "LG C4 OLED", "new": "LG C6 OLED", "slug": "lg-c6-oled"},
    {"old": "Samsung HW-Q990D", "new": "Samsung HW-Q990H", "slug": "samsung-hw-q990h"},
    {"old": "Sony Bravia 8", "new": "Sony Bravia 8 II", "slug": "sony-bravia-8-ii"}
]

def verify_global_existence(slug):
    """Gate 1: Check RTINGS or AVForums for a technical footprint"""
    try:
        # We check the RTINGS review URL structure
        url = f"https://www.rtings.com/tv/reviews/lg/{slug}" # Simplified for example
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.getcode() == 200
    except:
        return False

def check_local_stock(model):
    """Gate 2: Check Amazon.ae for actual UAE availability"""
    try:
        query = urllib.parse.quote(model)
        url = f"https://www.amazon.ae/s?k={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return "results for" in content.lower() and "did not match any" not in content.lower()
    except:
        return False

print("Starting Double-Gate Verification...")

with open('hardware.json', 'r') as file:
    data = json.load(file)

upgrades = 0

for target in TARGET_UPGRADES:
    global_ok = verify_global_existence(target['slug'])
    local_ok = check_local_stock(target['new'])

    if global_ok:
        for category in data:
            for item in category['items']:
                if item['model'] == target['old']:
                    if local_ok:
                        print(f"✅ FULL UPGRADE: {target['new']} is live in UAE.")
                        item['model'] = target['new']
                        item['badge'] = "2026 CHOICE | VERIFIED"
                        item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['new'])}&tag=dubaicinema-21"
                    else:
                        print(f"⚠️ COMING SOON: {target['new']} exists globally, but not in UAE yet.")
                        item['badge'] = "COMING SOON | 2026 MODEL"
                    upgrades += 1

if upgrades > 0:
    with open('hardware.json', 'w') as file:
        json.dump(data, file, indent=2)
    print(f"Process complete. {upgrades} status updates pushed.")
