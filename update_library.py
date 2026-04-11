import json

print("Bot is waking up...")

# 1. Open the vault
with open('movies.json', 'r') as file:
    movies = json.load(file)

# 2. Create a test movie to prove the bot works
test_movie = {
    "genre": "Sci-Fi",
    "badge": "#0 | BOT TEST MOVIE",
    "title": "The Automation Protocol (2026)",
    "amazon_link": "#"
}

# 3. Check if the test movie is already there so we don't create duplicates!
already_exists = any(movie['title'] == test_movie['title'] for movie in movies)

if not already_exists:
    # Add the new movie to the very top of the list (Index 0)
    movies.insert(0, test_movie)
    
    # 4. Save and lock the vault
    with open('movies.json', 'w') as file:
        json.dump(movies, file, indent=2)
    print("Success: Test movie injected into the vault!")
else:
    print("Movie already exists. Going back to sleep.")
