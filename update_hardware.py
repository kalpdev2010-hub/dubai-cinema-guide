import json
import urllib.parse

# 1. THE BRAIN: The Successor Map (2026 Flagship Edition)
# This is where the bot learns which new gear replaces the old ones.
UPGRADE_MAP = {
    "Samsung HW-Q990D": {
        "new_model": "Samsung HW-Q990H",
        "new_badge": "2026 FLAGSHIP | 11.1.4 CH",
        "new_desc": "The 2026 evolution of the world's #1 soundbar. Adds 'Sound Elevation' AI to place dialogue perfectly at screen level."
    },
    "LG C4 OLED": {
        "new_model": "LG C6 OLED",
        "new_badge": "2026 CHOICE | 165Hz OLED",
        "new_desc": "The 2026 standard. Featuring the new 2nd Gen Tandem WOLED panel and a blistering 165Hz refresh rate for gaming."
    },
    "Samsung HW-Q800D": {
        "new_model": "Samsung HW-Q800H",
        "new_badge": "2026 PREMIUM | 5.1.2 CH",
        "new_desc": "The 2026 sweet spot. Massive Atmos performance with updated Auto Volume tech to keep commercials quiet."
    }
}

def generate_amazon_link(model_name):
    query = urllib.parse.quote(f"{model_name} UAE version")
    return f"https://www.amazon.ae/s?k={query}&tag=dubaicinema-21"

print("Hardware Bot is scanning the vault for outdated gear...")

# 2. Open the Vault
with open('hardware.json', 'r') as file:
    categories = json.load(file)

upgrades_performed = 0

# 3. Scan each category and each item
for category in categories:
    for item in category['items']:
        current_model = item['model']
        
        # 4. If the bot finds an old model in the upgrade map, it performs the surgery
        if current_model in UPGRADE_MAP:
            upgrade = UPGRADE_MAP[current_model]
            print(f"!!! Upgrade Found: Replacing {current_model} with {upgrade['new_model']}")
            
            item['model'] = upgrade['new_model']
            item['badge'] = upgrade['new_badge']
            item['description'] = upgrade['new_desc']
            item['amazon_link'] = generate_amazon_link(upgrade['new_model'])
            
            upgrades_performed += 1

# 5. Save the updated Vault
if upgrades_performed > 0:
    with open('hardware.json', 'w') as file:
        json.dump(categories, file, indent=2)
    print(f"Success: {upgrades_performed} items auto-upgraded to 2026 specs!")
else:
    print("All hardware is currently up to date. No upgrades needed.")
