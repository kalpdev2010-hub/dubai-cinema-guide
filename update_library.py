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

# GENRE MAPPER: This tells the bot how to translate TMDB numbers into your website's filter names
GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    878: "Sci-Fi",
    53: "Thriller",
    80: "Crime",
    27: "Horror",
    9648: "Mystery",
    18: "Drama",
    35: "Comedy",
    16: "Animation"
}

print("Bot is waking up and connecting to TMDB...")

# 2. Setup the "New Release" window (Last 90 days)
today = datetime.date.today()
last_quarter = today - datetime.timedelta(days=90)

# 3. Ask TMDB for the POPULAR new releases
# We include all your preferred genres
GENRES = "28|878|53|80|27|9648|18|12"

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

# 5. Scan the results
for result in tmdb_data.get('results', [])[:20]:
    title = result['title']
    
    # --- DYNAMIC GENRE PICKER ---
    # Get the list of genre IDs for this movie (e.g., [28, 878])
    genre_ids = result.get('genre_ids', [])
    
    # Find the first ID that matches our map, default to "Action" if no match
    assigned_genre = "Action" 
    for gid in genre_ids:
        if gid in GENRE_MAP:
            assigned_genre = GENRE_MAP[gid]
            break # Stop once we find the primary matching genre
    
    raw_date = result.get('release_date')
    year = raw_date[:4] if raw_date else "2026"
    full_title = f"{title} ({year})"

    if title.lower() not in existing_titles:
        print(f"Adding {full_title} as genre: {assigned_genre}")
        
        search_query = urllib.parse.quote(f"{full_title} 4K Blu-ray")
        amazon_link = f"https://www.amazon.ae/s?k={search_query}&tag=dubaicinema-21"

        new_movie = {
            "genre": assigned_genre, # <--- THIS FIXES THE FILTER
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
    print(f"✅ Success: {movies_added} movies added with correct filter tags!")
else:
    print("Vault is already up to date.")
