import pandas as pd
import os
import ast

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

#Convierte los minutos en formato mm:ss a minutos
def convert_duration_to_minutes(duration_str):
    try:
        minutes, seconds = map(int, duration_str.split(':'))
        return minutes + seconds / 60
    except:
        return None
    
# Directorio que contiene los archivos CSV
directory = r"E:\fma_metadata\raw_data"

# Diccionario para almacenar los dataframes
dataframes = {}

# Leer todos los archivos CSV en el directorio y los almacena en el diccionario de dataframes
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        name = filename.split('.')[0]
        file_path = os.path.join(directory, filename)
        dataframes[name] = pd.read_csv(file_path)
        print(f"Loaded {filename}")

#Genera una columna genre_id desde el valor de otra columna.
def extract_genre_id(genre_str):
    try:
        # Convertir la cadena a un diccionario
        genre_dict = ast.literal_eval(genre_str)
        # Retornar el 'genre_id' del primer diccionario en la lista
        return genre_dict[0]['genre_id'] if genre_dict else None
    except (ValueError, IndexError, KeyError):
        return None

# Aplicar la función a la columna relevante en raw_tracks
dataframes['raw_tracks']['genre_id'] = dataframes['raw_tracks']['track_genres'].apply(extract_genre_id)


# Realizar los merges específicos
# Merge tracks con albums
merged_df = pd.merge(dataframes['raw_tracks'], dataframes['raw_albums'], on='album_id', how='left', suffixes=('_track', '_album'))
print("Merged tracks with albums")


# Merge con artists
if 'raw_artists' in dataframes:
    merged_df = pd.merge(merged_df, dataframes['raw_artists'], on='artist_id', how='left', suffixes=('', '_artist'))
    print("Merged with artists")

# Merge con genres si existe
if 'raw_genres' in dataframes:
    merged_df['genre_id']=merged_df['genre_id'].astype(str)
    dataframes['raw_genres']['genre_id']=dataframes['raw_genres']['genre_id'].astype(str)
    merged_df = pd.merge(merged_df, dataframes['raw_genres'], on='genre_id', how='left', suffixes=('', '_genre'))
    print("Merged with genres")

# Limpieza y preparación de datos
# Supongamos que queremos mantener estas columnas (ajusta según tus necesidades)
#columns_to_keep = ['track_id', 'album_id', 'artist_id', 'genre_id', 'track_title', 'album_title', 
#                   'artist_name', 'genre_title', 'track_date_created', 'track_date_recorded',
#                   'album_date_created', 'album_date_released', 'track_duration']

#merged_df = merged_df[columns_to_keep]

# Preparación de datos para clasificación de género
if 'genre_title' in merged_df.columns:
    genre_encoder = LabelEncoder()
    merged_df['genre_encoded'] = genre_encoder.fit_transform(merged_df['genre_title'])

# Preparación de datos para análisis de estilo del artista
# Convertir track_duration de mm:ss a minutos
merged_df['track_duration_minutes'] = merged_df['track_duration'].apply(convert_duration_to_minutes)

# Preparación de datos para predicción de trayectoria de carrera
merged_df['release_year'] = pd.to_datetime(merged_df['album_date_released']).dt.year
current_year = pd.Timestamp.now().year
merged_df['career_length'] = current_year - merged_df['release_year']

# Dividir los datos en conjuntos de entrenamiento y prueba
X = merged_df[['track_duration_minutes', 'release_year']]
y_genre = merged_df['genre_encoded'] if 'genre_encoded' in merged_df.columns else None
y_career = merged_df['career_length']

if y_genre is not None:
    X_train, X_test, y_genre_train, y_genre_test, y_career_train, y_career_test = train_test_split(
        X, y_genre, y_career, test_size=0.2, random_state=42
    )
else:
    X_train, X_test, y_career_train, y_career_test = train_test_split(
        X, y_career, test_size=0.2, random_state=42
    )

# Guardar el dataset combinado y preparado
merged_df.to_csv('combined_music_dataset.csv', index=False)

print("Dataset combinado y preparado guardado como 'combined_music_dataset.csv'")
print("Formas de los conjuntos de entrenamiento y prueba:")
print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")