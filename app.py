from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Initialize Spotipy client with additional scopes for user authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='e6849b973ecc4aa5a562b46479aae1c0',
                                               client_secret='22b9ad37ccd04125925749ab1161c286',
                                               redirect_uri='http://localhost:3000',
                                               scope='user-top-read'))

# Function to get music recommendations based on mood and genres
def get_recommendations(seed_genres, seed_tracks=None, limit=12):
    try:
        recommendations = sp.recommendations(seed_genres=seed_genres, seed_tracks=seed_tracks, limit=limit)
        return recommendations['tracks']
    except spotipy.SpotifyException as e:
        print("Error fetching recommendations:", e)
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None

# Function to map mood keywords to Spotify genre seeds
def map_mood_to_genres(mood):
    mood_mappings = {
        'happy': ['pop', 'dance', 'party', 'k-pop', 'upbeat'],
        'sad': ['ambient', 'chill', 'blues', 'melancholic'],
        'relaxed': ['ambient', 'chill', 'acoustic', 'indie', 'calm'],
        'angry': ['punk', 'metal', 'rock', 'aggressive'],
        'excited': ['pop', 'dance', 'party', 'k-pop', 'upbeat']
        # Add more mappings as needed
    }
    mood = mood.strip().lower()
    if mood.lower() in mood_mappings:
        return mood_mappings[mood.lower()]
    else:
        return []



# Function to fetch user's top tracks
def get_user_top_tracks(user_id, limit=30):
    try:
        top_tracks = sp.current_user_top_tracks(limit=limit)
        return top_tracks['items']
    except spotipy.SpotifyException as e:
        print("Error fetching user's top tracks:", e)
        return None

def get_user_top_artists(user_id, limit=20):
    try:
        top_artists = sp.current_user_top_artists(limit=limit)
        return top_artists['items']
    except spotipy.SpotifyException as e:
        print("Error fetching user's top artists:", e)
        return None



def get_top_artist_genres(artists):
    print("Artists:", artists) # Debugging line
    if not artists:
        print("No artists provided.")
        return set()
    genres = set()
    for artist in artists:
        print("Artist:", artist) # Debugging line
        for genre in artist['genres']:
            print("Genre:", genre) # Debugging line
            genres.add(genre)
    return genres


# Flask route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form['mood']
    # Fetch user's top artists
    top_artists = get_user_top_artists(user_id=None) # Assuming user_id is not needed for this approach
    if not top_artists:
        return "Error fetching user's top artists.", 400

    # Map mood to genres
    mood_genres = map_mood_to_genres(mood)
    print(mood)
    print(mood_genres)
    if not mood_genres:
        return "Sorry, I couldn't understand that mood. Please try again."
    # Fetch recommendations based on mood genres
    recommendations = get_recommendations(seed_genres=mood_genres)
    if recommendations:
        return render_template('recommendations.html', tracks=recommendations)
    else:
        return "Sorry, I couldn't find any recommendations for that mood."



# # Flask route for music recommendations
# @app.route('/recommend', methods=['POST'])
# def recommend():
#     try:
#         mood_input = request.form['mood']
#         mood_genres = map_mood_to_genres(mood_input)
#         if not mood_genres:
#             return "Sorry, I couldn't understand that mood. Please try again."
#         recommendations = get_recommendations(seed_genres=mood_genres)
#         if recommendations:
#             return render_template('recommendations.html', tracks=recommendations)
#         else:
#             return "Sorry, I couldn't find any recommendations for that mood."
#     except Exception as e:
#         print("Error processing recommendation request:", e)
#         return "An error occurred while processing your request. Please try again later."

# Flask route for user authentication
@app.route('/login')
def login():
    auth_url = sp.auth_manager.get_authorize_url()
    return redirect(auth_url)

# Flask route for handling the callback from Spotify
@app.route('/callback')
def callback():
    sp.auth_manager.get_access_token(request.args.get('code'))
    return redirect(url_for('index'))

@app.route('/recommend/top-tracks')
def top_tracks():
    # Fetch the user's top tracks
    top_tracks = get_user_top_tracks(user_id=None, limit=10) # Assuming user_id is not needed for this approach
    if not top_tracks:
        return "Error fetching user's top tracks.", 400
    # Render the tracks on a template
    return render_template('top_tracks.html', tracks=top_tracks)


if __name__ == '__main__':
    app.run(debug=True)
