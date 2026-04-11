import json
import urllib.request
import urllib.parse
import re

# 1. THE REGISTRY: Confirmed 2026 Successors
# We use technical slugs for RTINGS and the full name for Amazon
TARGET_UPGRADES = [
    {"old": "LG C4 OLED", "new": "LG C6 OLED", "slug": "lg-c6-oled"},
    {"old": "Samsung HW-Q990D", "new": "Samsung HW-Q990H", "slug": "samsung-hw-q990h"},
    {"old": "Sony Bravia 8", "new": "Sony Bravia 8 II", "slug": "sony-bravia-8-ii"}
]

def verify_global_existence(slug):
    """Gate 1: Check RTINGS for a technical review footprint"""
    try:
        # We check the professional review path
        url = f"https://www.rtings.com/tv/reviews/lg/{slug}" 
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.getcode() == 200
    except:
        return False

def check_local_stock(model):
    """Gate 2: STRICT Check for actual UAE availability on Amazon.ae"""
    try:
        query = urllib.parse.quote(model)
        url = f"https://www.amazon.ae/s?k={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8').lower()
            
            # THE FIX: We only return True if the specific model string 
            # (e.g. 'c6') actually appears in the search results text,
            # and Amazon hasn't displayed the "did not match any" message.
            if model.lower() in content and "did not match any" not in content:
                return True
            return False
    except:
        return False

print("Double-Gate Verification is starting...")

with open('hardware.json', 'r') as file:
    data = json.load(file)

upgrades = 0

for target in TARGET_UPGRADES:
    print(f"Checking {target['new']}...")
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
                        # Create the specific link for the new model
                        item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['new'])}&tag=dubaicinema-21"
                    else:
                        # This is the "Safety State" - doesn't change your buy link!
                        print(f"⚠️ COMING SOON: {target['new']} found globally, but not in UAE yet.")
                        item['badge'] = "COMING SOON | 2026 MODEL"
                    upgrades += 1

if upgrades > 0:
    with open('hardware.json', 'w') as file:
        json.dump(data, file, indent=2)
    print(f"Success. {upgrades} hardware statuses updated.")
else:
    print("All models are current. No upgrades available at this moment.")
