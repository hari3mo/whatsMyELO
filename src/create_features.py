import pandas as pd
import numpy as np

GAMES_CSV_PATH = 'data/lichess_games.csv' # output from extract_games.py

def create_player_features(row):
    evals = np.array([float(x) for x in row['evals'].split(';') if x])
    clocks = np.array([float(x) for x in row['clocks'].split(';') if x])
    
    return pd.Series([evals, clocks])

def format_df():
    return

def main():
    games = pd.read_csv(GAMES_CSV_PATH)
    features = games.apply(create_player_features, axis=1)
    features.columns = ['evals', 'clocks']
    return features

if __name__ == "__main__":
    features = main()
    