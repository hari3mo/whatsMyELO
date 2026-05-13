from src import extract_games
from src import create_features
import time

if __name__ == "__main__":
    start_time = time.time()
    # Step 1: Process games and save to CSV)
    print('Extracting games...')
    extract_start = time.time()
    extract_games.main()
    extract_end = time.time()
    print(f'Game extraction completed in {extract_end - extract_start} seconds.')
    # Step 2: Feature engineering
    print('Creating features...')
    features_start = time.time()
    create_features.main()
    features_end = time.time()
    print(f'Feature creation completed in {features_end - features_start} seconds.')
    # Step 3: Model training
    ...
    # Step 4: Model evaluation
    ...
    end_time = time.time()
    print(f'Pipeline completed in {end_time - start_time} seconds.')