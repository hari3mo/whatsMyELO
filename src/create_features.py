import pandas as pd
import numpy as np

GAMES_CSV_PATH = 'data/lichess_games.csv' # output from extract_games.py

def create_player_features(game):
    evals = [float(x) if x else 0 for x in game['evals'].split(';')]
    clocks = [float(x) if x else 0 for x in game['clocks'].split(';')]

    start_time = float(game['time_control'].split('+')[0])
    increment = float(game['time_control'].split('+')[1])
    clocks = np.array(2 * [start_time] + clocks) # add initial clock times for both players
    time_spent = (clocks[:-2] - clocks[2:]) + increment # turn time = clock time before move - clock time after move (+increment)

    centipawns = [1000 if eval * 100 > 1000 else -1000 if eval * 100 < -1000 \
        else eval * 100 for eval in evals] # unit measuring how strong a position/move is; more positive = better for white/more negative = better for black
    centipawns = [20.0] + centipawns # add 20.0 centipawns to account for the implicit advantage of white moving first
    diffs = np.diff(centipawns) # calculate change in centipawns after each turn (quantifies how good/bad a move was)

    white_cpl = np.maximum(0, -diffs[0::2]) # centipawn loss (positive values represent more loss)
    black_cpl = np.maximum(0, diffs[1::2])  

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
        'w_shift_move_time': np.mean(white_shift_time) if len(white_shift_time) > 0 else 0, # average time spent on moves with significant change in centipawns
        'b_shift_move_time': np.mean(black_shift_time) if len(black_shift_time) > 0 else 0
    })

def format_df(games):
    df = pd.read_csv(games)
    features_df = df.apply(create_player_features, axis=1)
    df = pd.concat([df, features_df], axis=1)
    df = df.dropna(subset=['w_acpl', 'b_acpl'])
    df[['w_shift_move_time', 'b_shift_move_time']] = \
        df[['w_shift_move_time', 'b_shift_move_time']].fillna(0)
    
    shared_cols = ['eco', 'ply_count', 'eval_volatility', 'category']

    white_cols = [
        'white_elo', 'w_acpl', 'w_blunders', 'w_mistakes', 'w_inaccuracies', 
        'w_avg_move_time', 'w_time_trouble_moves', 'w_opening_speed', 'w_shift_move_time'
    ]
    white_df = df[shared_cols + white_cols].copy()
    white_df['is_white'] = 1 
    white_df.columns = white_df.columns.str.replace('w_', '').str.replace('white_', '')

    black_cols = [
        'black_elo', 'b_acpl', 'b_blunders', 'b_mistakes', 'b_inaccuracies', 
        'b_avg_move_time', 'b_time_trouble_moves', 'b_opening_speed', 'b_shift_move_time'
    ]
    black_df = df[shared_cols + black_cols].copy()
    black_df['is_white'] = 0 
    black_df.columns = black_df.columns.str.replace('b_', '').str.replace('black_', '')

    features_df = pd.concat([white_df, black_df], ignore_index=True)
    features_df = features_df.sample(frac=1, random_state=42).reset_index(drop=True) # sample rows to shuffle dataset
    features_df.to_csv('data/lichess_features.csv', index=False)

    return features_df

def main():
    features = format_df(GAMES_CSV_PATH)
    features.to_csv('data/lichess_features.csv', index=False)
    return

if __name__ == "__main__":
    main()

    