from flask import Flask, render_template, request, jsonify
import os
import pickle
import requests

app = Flask(__name__)

# Cargar el modelo
def load_model():
    model_path = os.path.join('models', 'model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

# Función para obtener datos de la API de MusicBrainz
def fetch_data(entity_type, params=None):
    base_url = f"https://musicbrainz.org/ws/2/{entity_type}"
    headers = {'Accept': 'application/json'}
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching data from MusicBrainz: {response.status_code} - {response.text}")
        return None
    return response.json()

# Función para buscar artistas
def search_artists(query):
    params = {'query': query, 'limit': 5, 'fmt': 'json'}
    return fetch_data('artist', params=params)

# Función para obtener lanzamientos de un artista
def collect_releases(artist_id):
    params = {'fmt': 'json', 'artist': artist_id, 'limit': 5}
    return fetch_data('release', params=params)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_page')
def search_page():
    return render_template('search.html')

# Ruta para manejar las búsquedas
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    artists_data = search_artists(query)
    results = []

    if artists_data and artists_data.get('artists'):
        for artist in artists_data['artists']:
            artist_id = artist['id']
            releases = collect_releases(artist_id)
            results.append({
                'artist': artist['name'],
                'releases': releases.get('releases', []) if releases else []
            })
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
