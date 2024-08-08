import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier

# Función para entrenar y guardar el modelo
def train_and_save_model():
    # Simulación de datos para el entrenamiento
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [5, 4, 3, 2, 1],
        'target': [0, 1, 0, 1, 0]  # Ejemplo de columna objetivo
    }
    
    df = pd.DataFrame(data)
    X = df[['feature1', 'feature2']]
    y = df['target']
    
    model = RandomForestClassifier()
    model.fit(X, y)

    # Crear la carpeta 'models' si no existe
    os.makedirs('models', exist_ok=True)

    # Guardar el modelo entrenado en la carpeta 'models'
    model_path = os.path.join('models', 'model.pkl')
    with open(model_path, 'wb') as f:  # Asegúrate de abrirlo en modo 'wb' (write binary)
        pickle.dump(model, f)
    print(f"Modelo guardado correctamente en {model_path}.")

if __name__ == "__main__":
    train_and_save_model()
