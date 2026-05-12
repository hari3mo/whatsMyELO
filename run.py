from src import extract_games
import time

if __name__ == "__main__":
    time_start = time.time()
    # Step 1: Process games and save to CSV)
    print('Extracting games...')
    extract_games.main()
    # Step 2: Feature engineering
    ...
    # Step 3: Model training
    ...
    # Step 4: Model evaluation
    ...
    time_end = time.time()
    print(f'Total execution time: {time_end - time_start} seconds')