import os
import json
import urllib.request
import urllib.parse
import datetime

# 1. Grab the secret key from the GitHub Vault
API_KEY = os.environ.get("TMDB_API_KEY")

if not API_KEY:
    print("Error: TMDB_API_KEY secret is missing!")
    exit(1)

print("Bot is waking up and connecting to TMDB...")

# 2. Setup the "New Release" window
# Looking back 90 days ensures we don't miss anything that hit Dubai slightly later
today = datetime.date.today()
last_quarter = today - datetime.timedelta(days=90)

# 3. Ask TMDB for movies
# CRITICAL FIX: We use pipes (|) so the bot looks for Action OR Sci-Fi OR Thriller.
# Using commas (,) was forcing the bot to find movies that were ALL genres at once.
GENRES = "28|878|53|80|27|9648"

# SORT FIX: We use 'primary_release_date.desc' to prioritize the newest releases
url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={GENRES}&sort_by=primary_release_date.desc&primary_release_date.gte={last_quarter}&primary_release_date.lte={today}"

# Safety check for spaces
url = url.replace(" ", "").strip()

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    tmdb_data = json.loads(response.read().decode())
except Exception as e:
    print(f"Error connecting to TMDB: {e}")
    exit(1)

# 4. Open your website's data vault
try:
    with open('movies.json', 'r') as file:
        movies = json.load(file)
except FileNotFoundError:
    print("Error: movies.json not found.")
    exit(1)

# Make a list of movies we already have so we don't duplicate
existing_titles = [movie['title'].split(" (")[0].lower() for movie in movies]
movies_added = 0

# 5. Scan the top 20 newest results
# Increased to 20 to ensure we find new entries even if the very top ones are already listed
for result in tmdb_data.get('results', [])[:20]:
    title = result['title']
    
    # Handle potentially missing release dates safely
    raw_date = result.get('release_date')
    year = raw_date[:4] if raw_date else "2026"
    full_title = f"{title} ({year})"

    # 6. If we don't have it, add it!
    if title.lower() not in existing_titles:
        print(f"New release found: {full_title}!")
        
        # Automatically build the Amazon.ae Affiliate Link
        search_query = urllib.parse.quote(f"{full_title} 4K Blu-ray")
        amazon_link = f"https://www.amazon.ae/s?k={search_query}&tag=dubaicinema-21"

        new_movie = {
            "genre": "New Release", 
            "badge": "NEW | 4K ATMOS / DTS:X",
            "title": full_title,
            "amazon_link": amazon_link
        }
        
        # Insert at the very top (index 0)
        movies.insert(0, new_movie) 
        existing_titles.append(title.lower())
        movies_added += 1

# 7. Save the vault only if new movies were found
if movies_added > 0:
    with open('movies.json', 'w') as file:
        json.dump(movies, file, indent=2)
    print(f"Success: {movies_added} new movies injected into the vault!")
else:
    print("Vault is already up to date with the latest releases. Going back to sleep.")
