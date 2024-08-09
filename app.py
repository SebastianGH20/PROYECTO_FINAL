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
    params = {'query': query, 'fmt': 'json'}
    data = fetch_data('artist', params=params)
    if data and data.get('artists'):
        return data['artists'][0]  # Devolver solo el primer artista
    return None

# Función para obtener detalles de un artista
def get_artist_details(artist_id):
    params = {'fmt': 'json', 'inc': 'releases+recordings+url-rels'}
    return fetch_data(f'artist/{artist_id}', params=params)

# Función para obtener lanzamientos de un artista
def collect_releases(artist_id):
    params = {'fmt': 'json', 'artist': artist_id, 'limit': 5}
    return fetch_data('release', params=params)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la página de búsqueda
@app.route('/search_page')
def search_page():
    return render_template('search.html')

# Ruta para manejar las búsquedas
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    artist = search_artists(query)
    
    if artist:
        artist_details = get_artist_details(artist['id'])
        releases = collect_releases(artist['id'])
        
        result = {
            'name': artist['name'],
            'type': artist.get('type', 'Unknown'),
            'country': artist.get('country', 'Unknown'),
            'life-span': artist.get('life-span', {}),
            'genres': [genre['name'] for genre in artist.get('genres', [])],
            'releases': releases.get('releases', []) if releases else [],
            'urls': [url['url']['resource'] for url in artist_details.get('relations', []) if url['type'] == 'official homepage']
        }
        
        return jsonify(result)
    
    return jsonify({"error": "No se encontraron resultados."})

if __name__ == "__main__":
    app.run(debug=True)
