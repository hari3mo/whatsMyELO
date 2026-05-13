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

    white_shift_time = white_time_spent[np.abs(diffs[0::2]) > 100] # time spent on moves with significant change in centipawns 
    black_shift_time = black_time_spent[np.abs(diffs[1::2]) > 100]

    return pd.Series({
        # Centipawn features
        'w_acpl': np.mean(white_cpl), # average centipawn loss
        'b_acpl': np.mean(black_cpl),
        'eval_volatility': np.std(centipawns), # standard deviation of centipawns (quantifies how much the position fluctuated during the game)
        
        # Error features
        'w_blunders': np.sum(white_cpl > 300), # inacuraccies <= 100 cpl < mistakes <= 300 cpl < blunders 
        'b_blunders': np.sum(black_cpl > 300),
        'w_mistakes': np.sum((white_cpl > 100) & (white_cpl <= 300)),
        'b_mistakes': np.sum((black_cpl > 100) & (black_cpl <= 300)),
        'w_inaccuracies': np.sum((white_cpl > 50) & (white_cpl <= 100)),
        'b_inaccuracies': np.sum((black_cpl > 50) & (black_cpl <= 100)),

        # Temporal features
        'w_avg_move_time': np.mean(white_time_spent),
        'b_avg_move_time': np.mean(black_time_spent),
        'w_time_trouble_moves': np.sum(clocks[0::2] < start_time * 0.1), # number of moves where player had less than 10% time left
        'b_time_trouble_moves': np.sum(clocks[1::2] < start_time * 0.1),
        'w_opening_speed': np.mean(white_time_spent[:5]), # average time spent on first 5 moves (opening phase of the game)
        'b_opening_speed': np.mean(black_time_spent[:5]),
        'w_shift_move_time': np.mean(white_shift_time), # average time spent on moves with significant change in centipawns
        'b_shift_move_time': np.mean(black_shift_time)
    })

def format_df():
    return

def main():
    games = pd.read_csv(GAMES_CSV_PATH)
    features = games.apply(create_player_features, axis=1)
    features.columns = ['evals', 'clocks']
    return features

if __name__ == "__main__":
    features = main()
    