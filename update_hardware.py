import json
import urllib.request
import urllib.parse

# 1. THE REGISTRY (Global Verification - Gate 1)
# You only put models here that you know are real for 2026.
TARGET_UPGRADES = [
    {"old": "LG C4 OLED", "new": "LG C6 OLED"},
    {"old": "Samsung HW-Q990D", "new": "Samsung HW-Q990H"},
    {"old": "Sony Bravia 8", "new": "Sony Bravia 8 II"}
]

def check_local_stock(model_name):
    """Gate 2: STRICT Check - Does the model exist on Amazon.ae?"""
    try:
        query = urllib.parse.quote(model_name)
        url = f"https://www.amazon.ae/s?k={query}"
        # We use a real browser user-agent so Amazon doesn't block the check
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8').lower()
            
            # If Amazon flat out says it's not there, fail the check
            if "did not match any" in content or "no results" in content:
                return False
                
            # STRICT REQUIREMENT: The exact model string must appear 
            # multiple times on the page to prove it's a real product listing
            if content.count(model_name.lower()) > 2:
                return True
            return False
    except Exception as e:
        print(f"Error checking Amazon: {e}")
        return False

print("Running Local UAE Verification & Sync...")

with open('hardware.json', 'r') as file:
    data = json.load(file)

actual_changes = 0

for target in TARGET_UPGRADES:
    print(f"Checking {target['new']} on Amazon.ae...")
    local_ok = check_local_stock(target['new'])

    for category in data:
        for item in category['items']:
            # Find the item whether it has the old name OR the new name
            if item['model'] == target['old'] or item['model'] == target['new']:
                
                if local_ok:
                    print(f"✅ {target['new']} is In-Stock in UAE.")
                    item['model'] = target['new']
                    item['badge'] = "2026 CHOICE | VERIFIED"
                    item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['new'])}&tag=dubaicinema-21"
                    actual_changes += 1
                
                else:
                    print(f"⚠️ {target['new']} is Coming Soon (Not on Amazon.ae yet).")
                    item['model'] = target['new'] 
                    item['badge'] = "COMING SOON | 2026 MODEL"
                    # Safe fallback: Keep the buy link pointing to the older model
                    item['amazon_link'] = f"https://www.amazon.ae/s?k={urllib.parse.quote(target['old'])}&tag=dubaicinema-21"
                    actual_changes += 1

# Only write to the file if we ACTUALLY changed something
if actual_changes > 0:
    with open('hardware.json', 'w') as file:
        json.dump(data, file, indent=2)
    print(f"Sync complete. {actual_changes} items were written to the vault.")
else:
    print("No updates required.")
