import os
import json
import urllib.request
import urllib.parse
import datetime

# 1. Grab the secret key
API_KEY = os.environ.get("TMDB_API_KEY")

if not API_KEY:
    print("Error: TMDB_API_KEY secret is missing!")
    exit(1)

print("Bot is waking up and connecting to TMDB...")

# 2. Setup the "New Release" window (Last 90 days)
today = datetime.date.today()
last_quarter = today - datetime.timedelta(days=90)

# 3. Ask TMDB for the POPULAR new releases
# Added 18 (Drama) and 12 (Adventure) to catch movies like Mother Mary & Project Hail Mary
GENRES = "28|878|53|80|27|9648|18|12"

# SWEET SPOT: Sort by Popularity + Filter by Date + English Language
url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={GENRES}&sort_by=popularity.desc&primary_release_date.gte={last_quarter}&primary_release_date.lte={today}&with_original_language=en"

url = url.replace(" ", "").strip()

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    tmdb_data = json.loads(response.read().decode())
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# 4. Open movies.json
try:
    with open('movies.json', 'r') as file:
        movies = json.load(file)
except FileNotFoundError:
    print("Error: movies.json not found.")
    exit(1)

existing_titles = [movie['title'].split(" (")[0].lower() for movie in movies]
movies_added = 0

# 5. Scan the top 20 popular results
for result in tmdb_data.get('results', [])[:20]:
    title = result['title']
    raw_date = result.get('release_date')
    year = raw_date[:4] if raw_date else "2026"
    full_title = f"{title} ({year})"

    if title.lower() not in existing_titles:
        print(f"New release found: {full_title}!")
        
        search_query = urllib.parse.quote(f"{full_title} 4K Blu-ray")
        amazon_link = f"https://www.amazon.ae/s?k={search_query}&tag=dubaicinema-21"

        new_movie = {
            "genre": "New Release", 
            "badge": "NEW | 4K ATMOS / DTS:X",
            "title": full_title,
            "amazon_link": amazon_link
        }
        
        movies.insert(0, new_movie) 
        existing_titles.append(title.lower())
        movies_added += 1

# 6. Save if new movies found
if movies_added > 0:
    with open('movies.json', 'w') as file:
        json.dump(movies, file, indent=2)
    print(f"✅ Success: {movies_added} high-quality movies added!")
else:
    print("Vault is already up to date.")
