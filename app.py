from flask import Flask, render_template, request, jsonify
import os
import pickle
import requests
from functools import lru_cache
import logging
import traceback
import json
from datetime import datetime

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
    try:
        result = fetch_data_cached(entity_type, params_tuple)
        return json.loads(result) if result else None
    except json.JSONDecodeError:
        app.logger.error(f"Error decoding JSON for {entity_type} with params {params}")
        return None

def search_artists(query):
    params = {'query': query, 'fmt': 'json'}
    data = fetch_data('artist', params=params)
    if data and data.get('artists'):
        return data['artists'][0]  # Devolver solo el primer artista
    return None

def get_artist_details(artist_id):
    params = {'fmt': 'json', 'inc': 'releases+recordings+url-rels+artist-rels+genres'}
    return fetch_data(f'artist/{artist_id}', params=params) or {}

def get_release_details(release_id):
    params = {'fmt': 'json', 'inc': 'recordings+artist-credits'}
    return fetch_data(f'release/{release_id}', params=params) or {}

def get_all_releases(artist_id):
    offset = 0
    limit = 100
    all_releases = []
    while True:
        params = {'artist': artist_id, 'fmt': 'json', 'inc': 'genres', 'limit': limit, 'offset': offset}
        data = fetch_data('release', params=params)
        if not data or not data.get('releases'):
            break
        all_releases.extend(data['releases'])
        if len(data['releases']) < limit:
            break
        offset += limit
    return all_releases

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
        app.logger.info(f"Artist search result: {artist}")
        
        if not artist:
            app.logger.info(f"No results found for: {query}")
            return jsonify({"error": "No se encontraron resultados."}), 404
        
        app.logger.info(f"Artist found: {artist['name']}")
        artist_details = get_artist_details(artist['id'])
        app.logger.info(f"Artist details: {artist_details}")
        
        if not artist_details:
            app.logger.error(f"Failed to get artist details for {artist['name']}")
            return jsonify({"error": "No se pudieron obtener los detalles del artista."}), 500
        
        all_releases = get_all_releases(artist['id'])
        app.logger.info(f"Number of releases found: {len(all_releases)}")
        
        timeline_events = []
        collaborations = set()
        genres_evolution = {}
        event_id = 1  # Inicializamos un contador para los IDs de eventos

        for release in all_releases:
            release_date = release.get('date')
            if release_date:
                try:
                    release_date = datetime.strptime(release_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        release_date = datetime.strptime(release_date, "%Y-%m").strftime("%Y-%m")
                    except ValueError:
                        release_date = datetime.strptime(release_date, "%Y").strftime("%Y")

                timeline_events.append({
                    'id': f'event_{event_id}',  # Asignamos un ID único
                    'date': release_date,
                    'type': 'release',
                    'title': release['title'],
                    'release_id': release['id']
                })
                event_id += 1  # Incrementamos el contador

                # Géneros del lanzamiento
                release_genres = [genre['name'] for genre in release.get('genres', [])]
                for genre in release_genres:
                    if genre not in genres_evolution:
                        genres_evolution[genre] = []
                    genres_evolution[genre].append(release_date)

                # Colaboraciones
                release_details = get_release_details(release['id'])
                if release_details:
                    for artist_credit in release_details.get('artist-credit', []):
                        if 'artist' in artist_credit and artist_credit['artist']['id'] != artist['id']:
                            collaborations.add((artist_credit['artist']['id'], artist_credit['artist']['name']))
                            timeline_events.append({
                                'id': f'event_{event_id}',  # Asignamos un ID único
                                'date': release_date,
                                'type': 'collaboration',
                                'title': f"Colaboración con {artist_credit['artist']['name']}",
                                'artist_id': artist_credit['artist']['id']
                            })
                            event_id += 1  # Incrementamos el contador

        # Ordenar eventos cronológicamente
        timeline_events.sort(key=lambda x: x['date'])

        result = {
            'name': artist['name'],
            'type': artist.get('type', 'Unknown'),
            'country': artist.get('country', 'Unknown'),
            'life-span': artist.get('life-span', {}),
            'genres': [genre['name'] for genre in artist_details.get('genres', [])],
            'timeline_events': timeline_events,
            'collaborations': list(collaborations),
            'genres_evolution': genres_evolution,
            'urls': [url['url']['resource'] for url in artist_details.get('relations', []) if url['type'] == 'official homepage'],
        }
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error processing search request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Error al procesar la búsqueda: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)