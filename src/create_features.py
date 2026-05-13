import pandas as pd
import numpy as np

GAMES_CSV_PATH = 'data/lichess_games.csv' # output from extract_games.py

def create_player_features(game):
    evals = [float(x) for x in game['evals'].split(';') if x]
    clocks = [float(x) for x in game['clocks'].split(';') if x]

    start_time = float(game['time_control'].split('+')[0])
    increment = float(game['time_control'].split('+')[1])
    clocks = 2 * [start_time] + clocks # add initial clock times for both players
    time_spent = np.array(clocks[:-2]) - np.array(clocks[2:]) + increment # turn time = clock time before move - clock time after move (+increment)

    centipawns = [1000 if eval * 100 > 1000 else -1000 if eval * 100 < -1000 \
        else eval * 100 for eval in evals] # unit measuring how strong a position/move is; more positive = better for white/more negative = better for black
    centipawns = [20.0] + centipawns # add 20.0 centipawns to account for the implicit advantage of white moving first
    diffs = np.diff(centipawns) # calculate change in centipawns after each turn (quantifies how good/bad a move was)

    white_cpl = [-diff if -diff > 0 else 0 for diff in diffs[0::2]] # centipawn loss (positive values represent more loss)
    black_cpl = [diff if diff > 0 else 0 for diff in diffs[1::2]]

    white_time_spent = time_spent[0::2]
    black_time_spent = time_spent[1::2]
    
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
    