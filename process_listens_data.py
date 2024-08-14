import json
import csv
import os
from datetime import datetime

def process_json_files(input_directory, output_file):
    processed_files = 0
    processed_lines = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'user_name', 'timestamp', 'track_name', 'artist_name', 'release_name', 'recording_msid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for root, dirs, files in os.walk(input_directory):
            for filename in files:
                if filename.endswith('.listens'):
                    file_path = os.path.join(root, filename)
                    print(f"Processing file: {file_path}")
                    processed_files += 1
                    with open(file_path, 'r', encoding='utf-8') as jsonfile:
                        for line in jsonfile:
                            try:
                                data = json.loads(line)
                                writer.writerow({
                                    'user_id': data['user_id'],
                                    'user_name': data['user_name'],
                                    'timestamp': datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                                    'track_name': data['track_metadata']['track_name'],
                                    'artist_name': data['track_metadata']['artist_name'],
                                    'release_name': data['track_metadata'].get('release_name', ''),
                                    'recording_msid': data.get('recording_msid', '')
                                })
                                processed_lines += 1
                            except json.JSONDecodeError:
                                print(f"Error decoding JSON in file {filename}")
                            except KeyError as e:
                                print(f"Missing key in JSON data: {e} in file {filename}")
    
    print(f"Processed {processed_files} files and {processed_lines} lines.")
    print(f"Dataset created: {output_file}")

if __name__ == "__main__":
    input_directory = r'E:\listenbrainz-listens-dump-1806-20240801-040003-full.tar\listenbrainz-listens-dump-1806-20240801-040003-full\listens'  # Ajusta esta ruta
    output_file = 'listens_dataset.csv'
    process_json_files(input_directory, output_file)