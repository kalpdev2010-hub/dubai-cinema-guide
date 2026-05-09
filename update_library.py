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

# Calculate today's date and the date 30 days ago to create a "New Release" window
today = datetime.date.today()
last_month = today - datetime.timedelta(days=30)

# Search for the most popular movies released in the last 30 days within your specific genres
url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres=28,878,53,28,80,27,9648 &sort_by=popularity.desc&primary_release_date.gte={last_month}&primary_release_date.lte={today}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
tmdb_data = json.loads(response.read().decode())

# 3. Open your website's data vault
with open('movies.json', 'r') as file:
    movies = json.load(file)

# Make a list of movies we already have so we don't duplicate
existing_titles = [movie['title'].split(" (")[0].lower() for movie in movies]
movies_added = 0

# 4. Look at the top 3 trending movies right now
for result in tmdb_data.get('results', [])[:3]:
    title = result['title']
    year = result['release_date'][:4] if result.get('release_date') else "2026"
    full_title = f"{title} ({year})"

    # 5. If we don't have it, add it!
    if title.lower() not in existing_titles:
        print(f"New release found: {full_title}!")
        
        # Automatically build the Amazon.ae Affiliate Link
        search_query = urllib.parse.quote(f"{full_title} 4K Blu-ray")
        amazon_link = f"https://www.amazon.ae/s?k={search_query}&tag=dubaicinema-21"

        new_movie = {
            "genre": "Action", 
            "badge": "NEW | 4K ATMOS / DTS:X",
            "title": full_title,
            "amazon_link": amazon_link
        }
        
        movies.insert(0, new_movie) # Add to the very top
        existing_titles.append(title.lower())
        movies_added += 1

# 6. Save the vault if we found new movies
if movies_added > 0:
    with open('movies.json', 'w') as file:
        json.dump(movies, file, indent=2)
    print(f"Success: {movies_added} new movies injected into the vault!")
else:
    print("Vault is already up to date. Going back to sleep.")
