import os
import json
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# =========================================================
# CONFIG
# =========================================================

JSON_DIR = "../ipl_json"
OUTPUT_CSV = "output/ipl_ball_by_ball_dataset.csv"

TEAM_MAPPING_PATH = "csvs/canonical_team_mapping.csv"
VENUE_MAPPING_PATH = "csvs/canonical_venue_mapping.csv"
STAGE_MAPPING_PATH = "csvs/canonical_stage_mapping.csv"

# =========================================================
# LOAD MAPPINGS
# =========================================================

def build_alias_lookup(csv_path, id_col, alias_col):

    df = pd.read_csv(csv_path)
    lookup = {}

    for _, row in df.iterrows():

        aliases = str(row[alias_col]).split("|")

        for alias in aliases:
            lookup[alias.strip()] = row[id_col]

    return lookup


TEAM_LOOKUP = build_alias_lookup(
    TEAM_MAPPING_PATH,
    "team_id",
    "aliases"
)

VENUE_LOOKUP = build_alias_lookup(
    VENUE_MAPPING_PATH,
    "venue_id",
    "aliases"
)

STAGE_LOOKUP = build_alias_lookup(
    STAGE_MAPPING_PATH,
    "stage_id",
    "aliases"
)

# =========================================================
# CITY MAPPING
# =========================================================

CITY_ID_MAP = {
    "Abu Dhabi": 1,
    "Ahmedabad": 2,
    "Bangalore": 3,
    "Bengaluru": 4,
    "Bloemfontein": 5,
    "Cape Town": 6,
    "Centurion": 7,
    "Chandigarh": 8,
    "Chennai": 9,
    "Cuttack": 10,
    "Delhi": 11,
    "Dharamsala": 12,
    "Dubai": 13,
    "Durban": 14,
    "East London": 15,
    "Guwahati": 16,
    "Hyderabad": 17,
    "Indore": 18,
    "Jaipur": 19,
    "Johannesburg": 20,
    "Kanpur": 21,
    "Kimberley": 22,
    "Kochi": 23,
    "Kolkata": 24,
    "Lucknow": 25,
    "Mohali": 26,
    "Mumbai": 27,
    "Nagpur": 28,
    "Navi Mumbai": 29,
    "New Chandigarh": 30,
    "Port Elizabeth": 31,
    "Pune": 32,
    "Raipur": 33,
    "Rajkot": 34,
    "Ranchi": 35,
    "Sharjah": 36,
    "Visakhapatnam": 37,
}

# =========================================================
# HELPERS
# =========================================================

def safe_divide(a, b):
    return a / b if b != 0 else 0


def get_phase(ball_number):

    if ball_number <= 36:
        return 1
    elif ball_number <= 90:
        return 2

    return 3


def get_stage_id(info):

    event = info.get("event", {})

    if "match_number" in event:
        return STAGE_LOOKUP.get("League", 1)

    stage = event.get("stage")

    return STAGE_LOOKUP.get(stage, -1)

# =========================================================
# MAIN
# =========================================================

rows = []

json_files = [
    f for f in os.listdir(JSON_DIR)
    if f.endswith(".json")
]

for filename in tqdm(json_files):

    filepath = os.path.join(JSON_DIR, filename)

    try:

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        info = data.get("info", {})

        # -------------------------------
        # Match Level
        # -------------------------------

        venue = info.get("venue")
        city = info.get("city")

        venue_id = VENUE_LOOKUP.get(venue, -1)
        city_id = CITY_ID_MAP.get(city, -1)

        stage_id = get_stage_id(info)

        toss_winner = info.get("toss", {}).get("winner")

        event = info.get("event", {})
        league_match_number = event.get("match_number")

        innings_list = data.get("innings", [])

        # -------------------------------
        # Process Each Innings
        # -------------------------------

        for innings_index, innings_data in enumerate(innings_list):

            innings_num = innings_index + 1

            batting_team = innings_data.get("team")

            batting_team_won_toss = 1 if batting_team == toss_winner else 0

            # -------------------------------
            # Final innings score
            # -------------------------------

            final_score = 0

            for over in innings_data.get("overs", []):
                for delivery in over.get("deliveries", []):
                    final_score += delivery.get("runs", {}).get("total", 0)

            # -------------------------------
            # Running State
            # -------------------------------

            total_runs = 0
            wickets_lost = 0
            legal_balls = 0

            extras_total = 0
            wides_total = 0
            noballs_total = 0

            batter_runs = defaultdict(int)
            batter_balls = defaultdict(int)

            bowler_runs = defaultdict(int)
            bowler_balls = defaultdict(int)
            bowler_wickets = defaultdict(int)

            batting_order = {}
            batting_position_counter = 1

            for over in innings_data.get("overs", []):

                deliveries = over.get("deliveries", [])

                for delivery in deliveries:

                    batter = delivery.get("batter")
                    non_striker = delivery.get("non_striker")
                    bowler = delivery.get("bowler")

                    # -------------------------------
                    # Batting position tracking
                    # -------------------------------

                    for player in [batter, non_striker]:

                        if player not in batting_order:
                            batting_order[player] = batting_position_counter
                            batting_position_counter += 1

                    # -------------------------------
                    # Delivery Runs
                    # -------------------------------

                    runs_data = delivery.get("runs", {})

                    delivery_total = runs_data.get("total", 0)
                    batter_runs_scored = runs_data.get("batter", 0)

                    extras = delivery.get("extras", {})

                    # -------------------------------
                    # Extras Tracking
                    # -------------------------------

                    ball_extras = sum(extras.values()) if extras else 0
                    extras_total += ball_extras

                    if "wides" in extras:
                        wides_total += extras["wides"]

                    if "noballs" in extras:
                        noballs_total += extras["noballs"]

                    total_runs += delivery_total

                    # -------------------------------
                    # Legal Ball
                    # -------------------------------

                    is_legal = True

                    if "wides" in extras or "noballs" in extras:
                        is_legal = False

                    if is_legal:
                        legal_balls += 1
                        batter_balls[batter] += 1
                        bowler_balls[bowler] += 1

                    # -------------------------------
                    # Batter Stats
                    # -------------------------------

                    batter_runs[batter] += batter_runs_scored

                    # -------------------------------
                    # Bowler Runs
                    # -------------------------------

                    bowler_conceded = delivery_total

                    if "byes" in extras:
                        bowler_conceded -= extras["byes"]

                    if "legbyes" in extras:
                        bowler_conceded -= extras["legbyes"]

                    bowler_runs[bowler] += bowler_conceded

                    # -------------------------------
                    # Wickets
                    # -------------------------------

                    wickets = delivery.get("wickets", [])

                    if len(wickets) > 0:
                        wickets_lost += 1
                        bowler_wickets[bowler] += 1

                    # -------------------------------
                    # Derived Features
                    # -------------------------------

                    balls_remaining = 120 - legal_balls

                    striker_runs = batter_runs[batter]
                    striker_balls = batter_balls[batter]
                    striker_sr = safe_divide(striker_runs * 100, striker_balls)

                    non_striker_runs = batter_runs[non_striker]
                    non_striker_balls = batter_balls[non_striker]

                    wickets_remaining = 10 - wickets_lost

                    current_run_rate = safe_divide(total_runs * 6, legal_balls)

                    bowler_runs_conceded = bowler_runs[bowler]
                    bowler_balls_bowled = bowler_balls[bowler]
                    bowler_wickets_taken = bowler_wickets[bowler]

                    bowler_economy = safe_divide(
                        bowler_runs_conceded * 6,
                        bowler_balls_bowled
                    )

                    innings_phase = get_phase(legal_balls)

                    # -------------------------------
                    # Row
                    # -------------------------------

                    row = {
                        "innings": innings_num,
                        "batting_team_won_toss": batting_team_won_toss,
                        "venue_id": venue_id,
                        "city_id": city_id,
                        "stage_id": stage_id,
                        "league_match_number": league_match_number,
                        "balls_bowled": legal_balls,
                        "balls_remaining": balls_remaining,
                        "runs_scored": total_runs,
                        "wickets_lost": wickets_lost,
                        "wickets_remaining": wickets_remaining,
                        "current_run_rate": current_run_rate,
                        "extras_total": extras_total,
                        "wides_total": wides_total,
                        "noballs_total": noballs_total,
                        "striker_runs": striker_runs,
                        "striker_balls_faced": striker_balls,
                        "striker_strike_rate": striker_sr,
                        "non_striker_runs": non_striker_runs,
                        "non_striker_balls_faced": non_striker_balls,
                        "striker_batting_position": batting_order[batter],
                        "non_striker_batting_position": batting_order[non_striker],
                        "bowler_runs_conceded": bowler_runs_conceded,
                        "bowler_balls_bowled": bowler_balls_bowled,
                        "bowler_wickets_taken": bowler_wickets_taken,
                        "bowler_economy": bowler_economy,
                        "innings_phase": innings_phase,
                        "target_final_score": final_score,
                    }

                    rows.append(row)

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# =========================================================
# SAVE
# =========================================================

df = pd.DataFrame(rows)

os.makedirs("output", exist_ok=True)

df = df[df["balls_bowled"] > 0]

df.to_csv(OUTPUT_CSV, index=False)

print("\nDataset created successfully")
print(f"Rows: {len(df)}")
print(f"Saved to: {OUTPUT_CSV}")
