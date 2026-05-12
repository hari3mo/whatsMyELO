import zstandard as zstd
import chess
import re
import io

RAW_PGN_PATH = 'data/lichess_db_standard_rated_2023-12.pgn.zst' # path to raw PGN file downloaded from https://database.lichess.org/ (January 2026)
RAW_CSV_OUTPUT_PATH = 'data/lichess_games.csv'
FINAL_CSV_OUTPUT_PATH = 'data/games.csv'

TARGET_PER_ELO_RANGE = 20_000 # number of games to extract per ELO range; 5 ranges * 20K = 100K total
MAX_GAMES_PER_PLAYER = 5 # per-player cap to keep the sample diverse
TIME_CONTROL_FILTER = {'blitz', 'rapid', 'classical'} # filter out bullet and unknown time controls (noisy)

ELO_RANGES = [
    ('<1400', 0, 1400),
    ('1400_1700', 1400, 1700),
    ('1700_2000', 1700, 2000),
    ('2000_2300', 2000, 2300),
    ('2300<', 2300, 10_000)
]

EVAL_REGEX = re.compile(r'\[%eval (#?-?[\d.]+)\]') # captures either a centipawn eval ('0.34', -1.2') or a mate score ('#3', '#-5')
CLOCK_REGEX  = re.compile(r'\[%clk (\d+):(\d+):(\d+)\]') # captures hours, minutes, seconds as integers

CSV_COLUMNS = [
    'game_id', 'event', 'white', 'black', 'white_elo', 'black_elo',
    'white_rating_diff', 'black_rating_diff', 'white_title', 'black_title',
    'result', 'eco', 'opening', 'time_control', 'termination', 'utc_date', 
    'utc_time', 'ply_count', 'moves', 'evals', 'clocks'
]

# Extracts ELO range
def get_elo_range(elo):
    for label, low, high in ELO_RANGES:
        if low <= elo < high:
            return label
    return None

# Extracts time control category
def get_time_control_category(time_control_str):
    base, increment = time_control_str.split("+")
    total = int(base) + 40 * int(increment)
    if total < 180:   
        return 'bullet'
    if total < 480:   
        return 'blitz'
    if total < 1500:  
        return 'rapid'
    return 'classical'

# Extracts evaluation score
def get_evaluation_score(comment):
    match = EVAL_REGEX.search(comment)
    if not match:
        return None
    evaluation = match.group(1)
    if evaluation.startswith('#'):
        return 100.0 if int(evaluation[1:]) > 0 else -100.0
    return float(evaluation)

# Extracts clock time in seconds
def get_clock_time(comment):
    match = CLOCK_REGEX.search(comment)
    if not match:
        return None
    hours, minutes, seconds = [int(x) for x in match.groups()]
    return hours * 3600 + minutes * 60 + seconds

# Extracts game ID from lichess url
def get_game_id(url):
    return url.split('/')[-1]

# Extract game/PGN as a CSV row
def extract_row(game):
    headers = game.headers
    moves, evals, clocks = [], [], []
    node = game
    while node.variations:
        node = node.variation(0)
        moves.append(node.san())
        evaluation = get_evaluation_score(node.comment)
        evals.append('' if evaluation is None else f'{evaluation:g}')
        clock = get_clock_time(node.comment)
        clocks.append('' if clock is None else str(clock))

    return {
        'game_id': get_game_id(headers.get('Site', '')),
        'event': headers.get('Event', ''),
        'white': headers.get('White', ''),
        'black': headers.get('Black', ''),
        'white_elo': headers.get('WhiteElo', ''),
        'black_elo': headers.get('BlackElo', ''),
        'white_rating_diff': headers.get('WhiteRatingDiff', ''),
        'black_rating_diff': headers.get('BlackRatingDiff', ''),
        'white_title': headers.get('WhiteTitle', ''),
        'black_title': headers.get('BlackTitle', ''),
        'result': headers.get('Result', ''),
        'eco': headers.get('ECO', ''),
        'opening': headers.get('Opening', ''),
        'time_control': headers.get('TimeControl', ''),
        'termination': headers.get('Termination', ''),
        'utc_date': headers.get('UTCDate', ''),
        'utc_time': headers.get('UTCTime', ''),
        'ply_count': len(moves),
        'moves': ' '.join(moves),
        'evals': ';'.join(evals),
        'clocks': ';'.join(clocks)
    }

# Sequentially read games from pgn.zst file; file is too large to fit in memory (~30 gb)
# **Code from Gemini**
def stream_games():
    dctx = zstd.ZstdDecompressor(max_window_size=2**31)
    with open(RAW_PGN_PATH, "rb") as fh, dctx.stream_reader(fh) as reader:
        text = io.TextIOWrapper(reader, encoding="utf-8", errors="replace")
        while (g := chess.pgn.read_game(text)) is not None:
            yield g

def main():
    ...

if __name__ == "__main__":
    main()
