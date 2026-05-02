# How batting has changed over time in IPL

## Overview

This dataset was created using the IPL match archive from the Cricsheet dataset, covering IPL matches available up to **28-04-2026**.

The dataset is designed for:

- Cricket analytics
- Machine learning
- Score prediction
- Ball-by-ball modeling
- Sports data science

Each row in the dataset represents the **state of an innings after a delivery**.

The target variable is the final innings score.

---

# Dataset Source

Primary data source:

- Cricsheet IPL JSON archive

Data was processed using a custom Python pipeline that converts raw JSON match files into a structured ball-by-ball machine learning dataset.

---

# Dataset Description

Each row represents the state of a match at a specific legal delivery.

Example:

| balls_bowled | runs_scored | wickets_lost | target_final_score |
|--------------|-------------|---------------|---------------------|
| 48 | 67 | 2 | 182 |

Meaning:

> At ball 48, the batting side was 67/2 and eventually finished with 182 runs.

---

# Dataset Features

## Match Context

| Column | Description |
|--------|-------------|
| innings | Innings number (1 or 2) |
| batting_team_won_toss | Whether batting team won toss (1/0) |
| venue_id | Encoded venue ID |
| city_id | Encoded city ID |
| stage_id | Encoded match stage |
| league_match_number | Match number in league stage (nullable for knockout matches) |

---

## Match State

| Column | Description |
|--------|-------------|
| balls_bowled | Legal balls bowled so far |
| balls_remaining | Balls remaining in innings |
| runs_scored | Runs scored so far |
| wickets_lost | Wickets lost so far |
| wickets_remaining | Remaining wickets |
| current_run_rate | Current run rate |

---

## Extras Features

| Column | Description |
|--------|-------------|
| extras_total | Total extras conceded so far |
| wides_total | Total wides bowled so far |
| noballs_total | Total no-balls bowled so far |

---

## Batter Features

| Column | Description |
|--------|-------------|
| striker_runs | Runs scored by striker |
| striker_balls_faced | Balls faced by striker |
| striker_strike_rate | Strike rate of striker |
| non_striker_runs | Runs scored by non-striker |
| non_striker_balls_faced | Balls faced by non-striker |
| striker_batting_position | Batting order position of striker |
| non_striker_batting_position | Batting order position of non-striker |

---

## Bowler Features

| Column | Description |
|--------|-------------|
| bowler_runs_conceded | Runs conceded by current bowler |
| bowler_balls_bowled | Balls bowled by current bowler |
| bowler_wickets_taken | Wickets taken by current bowler |
| bowler_economy | Economy rate of current bowler |

---

## Derived Features

| Column | Description |
|--------|-------------|
| innings_phase | Phase of innings |

Phase Mapping:

| innings_phase | Ball Range |
|---------------|-----------|
| 1 | 1–36 |
| 2 | 37–90 |
| 3 | 91–120 |

---

## Target Variable

| Column | Description |
|--------|-------------|
| target_final_score | Final innings total |

---

# Mapping CSV Files

The dataset uses encoded categorical values.

Included mapping files:

- canonical_team_mapping.csv
- canonical_stage_mapping.csv
- canonical_venue_mapping.csv
- city_mapping.csv

---

## Team Mapping

Teams were normalized to account for franchise renaming.

Examples:

| Alias | Canonical Team |
|-------|-----------------|
| Delhi Daredevils | Delhi Capitals |
| Kings XI Punjab | Punjab Kings |
| Royal Challengers Bangalore | Royal Challengers Bengaluru |
| Rising Pune Supergiants | Rising Pune Supergiant |

---

## Venue Mapping

Venue aliases were normalized.

Examples:

| Alias | Canonical Venue |
|-------|------------------|
| Feroz Shah Kotla | Arun Jaitley Stadium |
| M.Chinnaswamy Stadium | M Chinnaswamy Stadium |
| Wankhede Stadium, Mumbai | Wankhede Stadium |

---

## Stage Mapping

Match stages include:

- League
- Qualifier 1
- Qualifier 2
- Eliminator
- Semi Final
- Final
- 3rd Place Play-Off

"Elimination Final" is mapped to "Eliminator".

---

# Dataset Generation Logic

The dataset was generated using a custom `build_dataset.py` pipeline.

The pipeline performs the following:

1. Reads all IPL JSON files from folder
2. Loads canonical mapping CSVs
3. Processes innings → overs → deliveries
4. Tracks score progression
5. Tracks batter statistics
6. Tracks bowler statistics
7. Tracks extras
8. Creates one row per legal delivery
9. Computes final innings target
10. Writes consolidated CSV

---

# Important Assumptions

- Dataset uses only legal deliveries for ball progression
- Wide/no-ball deliveries do not increment legal ball count
- Bowler economy excludes byes and leg-byes
- One row = state after one delivery
- Match stages inferred from Cricsheet event schema

---

# Suggested Use Cases

- First innings score prediction
- Match simulation
- Win probability modeling
- Batter momentum modeling
- Bowler impact analysis
- Sports ML experimentation

---

# Kaggle Dataset Contents

```text
ipl-ball-by-ball-dataset/
│
├── ipl_ball_by_ball_dataset.csv
├── city_mapping.csv
├── canonical_team_mapping.csv
├── canonical_stage_mapping.csv
├── canonical_venue_mapping.csv
├── README.md
└── build_dataset.py
```

---

# Attribution

Raw cricket data sourced from Cricsheet.

Dataset engineering, normalization, and feature creation performed for machine learning applications.
