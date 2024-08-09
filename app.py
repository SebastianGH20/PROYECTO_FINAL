from flask import Flask, render_template, request, jsonify
import os
import pickle
import requests
from functools import lru_cache
import logging
import traceback
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Cargar el modelo
def load_model():
    model_path = os.path.join('models', 'model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def params_to_tuple(params):
    if params is None:
        return None
    return tuple(sorted(params.items()))

@lru_cache(maxsize=100)
def fetch_data_cached(entity_type, params_tuple):
    base_url = f"https://musicbrainz.org/ws/2/{entity_type}"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'YourAppName/1.0 ( your@email.com )'
    }
    params = dict(params_tuple) if params_tuple else None
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        return json.dumps(response.json())  # Convertimos a string para que sea hashable
    except requests.RequestException as e:
        app.logger.error(f"Error fetching data from MusicBrainz: {str(e)}")
        return None

def fetch_data(entity_type, params=None):
    params_tuple = params_to_tuple(params)
    result = fetch_data_cached(entity_type, params_tuple)
    return json.loads(result) if result else None  # Convertimos de vuelta a diccionario

def search_artists(query):
    params = {'query': query, 'fmt': 'json'}
    data = fetch_data('artist', params=params)
    if data and data.get('artists'):
        return data['artists'][0]  # Devolver solo el primer artista
    return None

def get_artist_details(artist_id):
    params = {'fmt': 'json', 'inc': 'releases+recordings+url-rels+artist-rels'}
    return fetch_data(f'artist/{artist_id}', params=params)

def get_release_details(release_id):
    params = {'fmt': 'json', 'inc': 'recordings'}
    return fetch_data(f'release/{release_id}', params=params)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_page')
def search_page():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    app.logger.info(f"Searching for: {query}")
    
    try:
        artist = search_artists(query)
        
        if not artist:
            app.logger.info(f"No results found for: {query}")
            return jsonify({"error": "No se encontraron resultados."}), 404
        
        app.logger.info(f"Artist found: {artist['name']}")
        artist_details = get_artist_details(artist['id'])
        
        releases = artist_details.get('releases', [])
        detailed_releases = []
        for release in releases[:10]:
            release_details = get_release_details(release['id'])
            detailed_releases.append({
                'id': release['id'],
                'title': release['title'],
                'date': release.get('date', 'Unknown'),
                'type': release.get('release-group', {}).get('primary-type', 'Unknown'),
                'track_count': len(release_details.get('media', [{}])[0].get('tracks', []))
            })
        
        related_artists = [
            {'id': rel['artist']['id'], 'name': rel['artist']['name']}
            for rel in artist_details.get('relations', [])
            if rel['type'] in ['collaboration', 'member of band']
        ]
        
        result = {
            'name': artist['name'],
            'type': artist.get('type', 'Unknown'),
            'country': artist.get('country', 'Unknown'),
            'life-span': artist.get('life-span', {}),
            'genres': [genre['name'] for genre in artist.get('genres', [])],
            'releases': detailed_releases,
            'urls': [url['url']['resource'] for url in artist_details.get('relations', []) if url['type'] == 'official homepage'],
            'related_artists': related_artists[:5]
        }
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error processing search request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Error al procesar la búsqueda: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)