import re

TARGET_PER_ELO_RANGE = 20_000 # number of games to extract per ELO range; 5 ranges * 20K = 100K total
MAX_GAMES_PER_PLAYER = 5 # per-player cap to keep the sample diverse
TIME_CONTROL_FILTER = {'blitz', 'rapid', 'classical'} # filter out bullet and unknown time controls (noisy)

ELO_RANGES = [
    ('<1400', 0, 1400),
    ('1400_1700', 1400, 1700),
    ('1700_2000', 1700, 2000),
    ('2000_2300', 2000, 2300),
    ('2300<', 2300, 10_000),
]

EVAL_RE = re.compile(r'\[%eval (#?-?[\d.]+)\]') # captures either a centipawn eval ('0.34', -1.2') or a mate score ('#3', '#-5')
CLK_RE  = re.compile(r'\[%clk (\d+):(\d+):(\d+)\]') # captures hours, minutes, seconds as integers

CSV_COLUMNS = [
    'game_id', 'event', 'white', 'black', 'white_elo', 'black_elo',
    'white_rating_diff', 'black_rating_diff', 'white_title', 'black_title',
    'result', 'eco', 'opening', 'time_control', 'termination', 'utc_date', 
    'utc_time', 'ply_count', 'moves', 'evals', 'clocks',
]
