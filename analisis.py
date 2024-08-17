import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_dataset(file_path):
    # Cargar el dataset
    df = pd.read_csv(file_path)
    
    # Información básica
    print(f"Dimensiones del dataset: {df.shape}")
    print("\nColumnas presentes:")
    print(df.columns.tolist())
    
    # Información general sobre los datos
    print("\nInformación de tipos de datos y valores no nulos:")
    print(df.info())
    
    # Estadísticas descriptivas
    print("\nEstadísticas descriptivas para columnas numéricas:")
    print(df.describe())
    
    # Análisis de valores únicos y nulos
    print("\nAnálisis de valores únicos y nulos:")
    for col in df.columns:
        unique_count = df[col].nunique()
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / len(df)) * 100
        print(f"{col}: {unique_count} valores únicos, {null_percentage:.2f}% nulos")
    
    # Análisis de la distribución de géneros
    genre_columns = [col for col in df.columns if 'genre' in col.lower()]
    for genre_col in genre_columns:
        print(f"\nDistribución de {genre_col}:")
        genre_distribution = df[genre_col].value_counts(normalize=True) * 100
        print(genre_distribution)
    
    # Análisis temporal
    track_date_columns = [col for col in df.columns if 'track_date' in col.lower()]
    for track_date_col in track_date_columns:
        df[track_date_col] = pd.to_datetime(df[track_date_col], errors='coerce')
        print("\nRango de fechas:")
        print(f"Desde: {df[track_date_col].min()}")
        print(f"Hasta: {df[track_date_col].max()}")
        
    #if 'track_date' in df.columns:
    #    df['track_date'] = pd.to_datetime(df['track_date'], errors='coerce')
    #    print("\nRango de fechas:")
    #    print(f"Desde: {df['track_date'].min()}")
    #    print(f"Hasta: {df['track_date'].max()}")
    
    # Correlaciones entre características numéricas
    #numeric_features = ["genre_id", "artist_bio","artist_location", "artist_latitude", "artist_longitude"]
    #available_features = [col for col in numeric_features if col in df.columns]
    available_features=[]
    if available_features:
        corr_matrix = df[available_features].corr()
        
        # Visualización de la matriz de correlación
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title("Matriz de correlación de características")
        plt.tight_layout()
        plt.savefig('correlation_matrix.png')
        plt.close()
    for track_date_col in track_date_columns:
        plt.figure(figsize=(12, 6))
        df[track_date_col].dt.year.value_counts().sort_index().plot(kind='line')
        plt.title("Distribución de canciones por año")
        plt.tight_layout()
        plt.savefig('songs_per_year.png')
        plt.close()
        
    for genre_col in genre_columns:
        plt.figure(figsize=(12, 6))
        df[genre_col].value_counts().plot(kind='bar')
        plt.title(f"Distribución de {genre_col}")
        plt.tight_layout()
        plt.savefig(f'{genre_col}_distribution.png')
        plt.close()
    
    
    
    
    print("\nSe han guardado visualizaciones en archivos PNG.")
    
    # Verificación de adecuación para modelos específicos
    print("\nVerificación de adecuación para modelos:")
    
    # Para clasificación de género
    if any('genre' in col.lower() for col in df.columns) and df[genre_columns[0]].nunique() > 1:
        print("- Clasificación de género: Adecuado")
    else:
        print("- Clasificación de género: No adecuado (falta columna de género o solo hay un género)")
    
    # Para análisis de estilo del artista
    if 'artist_name' in df.columns and len(available_features) > 0:
        print("- Análisis de estilo del artista: Adecuado")
    else:
        print("- Análisis de estilo del artista: No adecuado (faltan características del artista)")
    
    # Para predicción de trayectoria de carrera
    if 'artist_name' in df.columns and any('track_date' in col for col in df.columns) and 'career_length' in df.columns:
        print("- Predicción de trayectoria de carrera: Adecuado")
    else:
        print("- Predicción de trayectoria de carrera: No adecuado (falta información temporal o de artista)")
    
    # Análisis adicional si hay género predicho
    if 'predicted_genre' in df.columns and 'genre_top' in df.columns:
        accuracy = (df['predicted_genre'] == df['genre_top']).mean()
        print(f"\nPrecisión del género predicho vs género real: {accuracy:.2%}")
        
        print("\nMatriz de confusión de géneros predichos vs reales:")
        confusion_matrix = pd.crosstab(df['genre_top'], df['predicted_genre'], normalize='index')
        print(confusion_matrix)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(confusion_matrix, annot=True, cmap='YlGnBu')
        plt.title('Matriz de confusión de géneros predichos vs reales')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        plt.close()

# Uso de la función
analyze_dataset('combined_music_dataset.csv')
