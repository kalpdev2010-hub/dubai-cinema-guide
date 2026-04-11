import json
import urllib.request
import urllib.parse

# THE REGISTRY
TARGET_UPGRADES = [
    {"old": "LG C4 OLED", "new": "LG C6 OLED", "slug": "lg-c6-oled"},
    {"old": "Samsung HW-Q990D", "new": "Samsung HW-Q990H", "slug": "samsung-hw-q990h"},
    {"old": "Sony Bravia 8", "new": "Sony Bravia 8 II", "slug": "sony-bravia-8-ii"}
]

def verify_global_existence(slug):
    """Gate 1: RTINGS Technical Footprint"""
    try:
        url = f"https://www.rtings.com/tv/reviews/lg/{slug}" 
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.getcode() == 200
    except:
        return False

def check_local_stock(model_name):
    """Gate 2: STRICT Check - Does the model exist as a BUYABLE product?"""
    try:
        query = urllib.parse.quote(model_name)
        url = f"https://www.amazon.ae/s?k={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8').lower()
            
            # The search query text is always on the page. 
            # We look for the "Results" count or specific price tags to ensure it's a real listing.
            if "did not match any" in content or "no results" in content:
                return False
            
            # Stricter: Is the specific model (e.g. 'c6') mentioned at least 3 times? 
            # (Once in header, once in title, once in description)
            if content.count(model_name.lower()) > 2:
                return True
            return False
    except:
        return False

print("Running Repair & Sync...")

with open('hardware.json', 'r') as file:
    data = json.load(file)

changes = 0

for target in TARGET_UPGRADES:
    global_ok = verify_global_existence(target['slug'])
    local_ok = check_local_stock(target['new'])

    for category in data:
        for item in category['items']:
            # We check if the item is EITHER the old one OR the already-upgraded one
            if item['model'] == target['old'] or item['model'] == target['new']:
                
                if global_ok and local_ok:
                    print(f"✅ {target['new']} is Verified & In-Stock.")
                    item['model'] = target['new']
                    item['badge'] = "2026 CHOICE | VERIFIED"
                    item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['new'])}&tag=dubaicinema-21"
                
                elif global_ok and not local_ok:
                    print(f"⚠️ {target['new']} is Coming Soon (Not on Amazon.ae yet).")
                    item['model'] = target['new'] # We show the new name
                    item['badge'] = "COMING SOON | 2026 MODEL"
                    # We link back to the OLD model search so they can still buy the current gear
                    item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['old'])}&tag=dubaicinema-21"
                
                changes += 1

if changes > 0:
    with open('hardware.json', 'w') as file:
        json.dump(data, file, indent=2)
    print(f"Sync complete. {changes} items updated.")
