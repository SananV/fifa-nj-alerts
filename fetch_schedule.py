import json, urllib.request, urllib.error, os, sys
from datetime import datetime, timezone, timedelta

api_key = os.environ.get('FOOTBALL_DATA_API_KEY', '').strip()
if not api_key:
    print("ERROR: FOOTBALL_DATA_API_KEY secret is not set.")
    sys.exit(1)

print(f"API key found, last 4: ...{api_key[-4:]}")

# ---------------------------------------------------------------------------
# VENUE MAPS
# ---------------------------------------------------------------------------
CITY_VENUES = [
    (["new york", "new jersey", "east rutherford", "metlife", "nynj", "new york new jersey"],
     "MetLife Stadium, East Rutherford, NJ", True),
    (["dallas", "arlington", "att"], "ATT Stadium, Arlington, TX", False),
    (["los angeles", "inglewood", "sofi"], "SoFi Stadium, Inglewood, CA", False),
    (["san francisco", "santa clara", "levi"], "Levis Stadium, Santa Clara, CA", False),
    (["pasadena", "rose bowl"], "Rose Bowl, Pasadena, CA", False),
    (["kansas city", "arrowhead"], "Arrowhead Stadium, Kansas City, MO", False),
    (["boston", "foxborough", "foxboro", "gillette"], "Gillette Stadium, Foxborough, MA", False),
    (["philadelphia", "lincoln financial"], "Lincoln Financial Field, Philadelphia, PA", False),
    (["miami", "hard rock", "miami gardens"], "Hard Rock Stadium, Miami Gardens, FL", False),
    (["atlanta", "mercedes"], "Mercedes-Benz Stadium, Atlanta, GA", False),
    (["houston", "nrg"], "NRG Stadium, Houston, TX", False),
    (["mexico city", "azteca"], "Estadio Azteca, Mexico City, Mexico", False),
    (["monterrey", "bbva"], "Estadio BBVA, Monterrey, Mexico", False),
    (["guadalajara", "akron"], "Estadio Akron, Guadalajara, Mexico", False),
    (["vancouver", "bc place"], "BC Place, Vancouver, Canada", False),
    (["toronto", "bmo"], "BMO Field, Toronto, Canada", False),
]

GROUP_VENUE_MAP = {
    "GROUP_A-1": "Estadio Azteca, Mexico City, Mexico",
    "GROUP_A-2": "BC Place, Vancouver, Canada",
    "GROUP_A-3": "Estadio Akron, Guadalajara, Mexico",
    "GROUP_B-1": "MetLife Stadium, East Rutherford, NJ",
    "GROUP_B-2": "Gillette Stadium, Foxborough, MA",
    "GROUP_B-3": "ATT Stadium, Arlington, TX",
    "GROUP_C-1": "SoFi Stadium, Inglewood, CA",
    "GROUP_C-2": "Arrowhead Stadium, Kansas City, MO",
    "GROUP_C-3": "Mercedes-Benz Stadium, Atlanta, GA",
    "GROUP_D-1": "Rose Bowl, Pasadena, CA",
    "GROUP_D-2": "Lincoln Financial Field, Philadelphia, PA",
    "GROUP_D-3": "Hard Rock Stadium, Miami Gardens, FL",
    "GROUP_E-1": "Levis Stadium, Santa Clara, CA",
    "GROUP_E-2": "NRG Stadium, Houston, TX",
    "GROUP_E-3": "Estadio BBVA, Monterrey, Mexico",
    "GROUP_F-1": "ATT Stadium, Arlington, TX",
    "GROUP_F-2": "MetLife Stadium, East Rutherford, NJ",
    "GROUP_F-3": "BC Place, Vancouver, Canada",
    "GROUP_G-1": "Gillette Stadium, Foxborough, MA",
    "GROUP_G-2": "SoFi Stadium, Inglewood, CA",
    "GROUP_G-3": "Estadio Azteca, Mexico City, Mexico",
    "GROUP_H-1": "Mercedes-Benz Stadium, Atlanta, GA",
    "GROUP_H-2": "Rose Bowl, Pasadena, CA",
    "GROUP_H-3": "Levis Stadium, Santa Clara, CA",
    "GROUP_I-1": "MetLife Stadium, East Rutherford, NJ",
    "GROUP_I-2": "Gillette Stadium, Foxborough, MA",
    "GROUP_I-3": "Arrowhead Stadium, Kansas City, MO",
    "GROUP_J-1": "Lincoln Financial Field, Philadelphia, PA",
    "GROUP_J-2": "NRG Stadium, Houston, TX",
    "GROUP_J-3": "Estadio Akron, Guadalajara, Mexico",
    "GROUP_K-1": "BMO Field, Toronto, Canada",
    "GROUP_K-2": "ATT Stadium, Arlington, TX",
    "GROUP_K-3": "SoFi Stadium, Inglewood, CA",
    "GROUP_L-1": "Estadio BBVA, Monterrey, Mexico",
    "GROUP_L-2": "Gillette Stadium, Foxborough, MA",
    "GROUP_L-3": "Mercedes-Benz Stadium, Atlanta, GA",
}

KNOCKOUT_VENUE_MAP = {
    "LAST_32-1":  "MetLife Stadium, East Rutherford, NJ",
    "LAST_32-2":  "ATT Stadium, Arlington, TX",
    "LAST_32-3":  "SoFi Stadium, Inglewood, CA",
    "LAST_32-4":  "Hard Rock Stadium, Miami Gardens, FL",
    "LAST_32-5":  "Levis Stadium, Santa Clara, CA",
    "LAST_32-6":  "Arrowhead Stadium, Kansas City, MO",
    "LAST_32-7":  "Lincoln Financial Field, Philadelphia, PA",
    "LAST_32-8":  "Mercedes-Benz Stadium, Atlanta, GA",
    "LAST_32-9":  "Rose Bowl, Pasadena, CA",
    "LAST_32-10": "NRG Stadium, Houston, TX",
    "LAST_32-11": "Gillette Stadium, Foxborough, MA",
    "LAST_32-12": "BC Place, Vancouver, Canada",
    "LAST_32-13": "BMO Field, Toronto, Canada",
    "LAST_32-14": "Estadio Azteca, Mexico City, Mexico",
    "LAST_32-15": "Estadio BBVA, Monterrey, Mexico",
    "LAST_32-16": "Estadio Akron, Guadalajara, Mexico",
    "ROUND_OF_32-1":  "MetLife Stadium, East Rutherford, NJ",
    "ROUND_OF_32-2":  "ATT Stadium, Arlington, TX",
    "ROUND_OF_32-3":  "SoFi Stadium, Inglewood, CA",
    "ROUND_OF_32-4":  "Hard Rock Stadium, Miami Gardens, FL",
    "ROUND_OF_32-5":  "Levis Stadium, Santa Clara, CA",
    "ROUND_OF_32-6":  "Arrowhead Stadium, Kansas City, MO",
    "ROUND_OF_32-7":  "Lincoln Financial Field, Philadelphia, PA",
    "ROUND_OF_32-8":  "Mercedes-Benz Stadium, Atlanta, GA",
    "ROUND_OF_32-9":  "Rose Bowl, Pasadena, CA",
    "ROUND_OF_32-10": "NRG Stadium, Houston, TX",
    "ROUND_OF_32-11": "Gillette Stadium, Foxborough, MA",
    "ROUND_OF_32-12": "BC Place, Vancouver, Canada",
    "ROUND_OF_32-13": "BMO Field, Toronto, Canada",
    "ROUND_OF_32-14": "Estadio Azteca, Mexico City, Mexico",
    "ROUND_OF_32-15": "Estadio BBVA, Monterrey, Mexico",
    "ROUND_OF_32-16": "Estadio Akron, Guadalajara, Mexico",
    "LAST_16-1":  "MetLife Stadium, East Rutherford, NJ",
    "LAST_16-2":  "SoFi Stadium, Inglewood, CA",
    "LAST_16-3":  "ATT Stadium, Arlington, TX",
    "LAST_16-4":  "Hard Rock Stadium, Miami Gardens, FL",
    "LAST_16-5":  "Levis Stadium, Santa Clara, CA",
    "LAST_16-6":  "Mercedes-Benz Stadium, Atlanta, GA",
    "LAST_16-7":  "Rose Bowl, Pasadena, CA",
    "LAST_16-8":  "Arrowhead Stadium, Kansas City, MO",
    "ROUND_OF_16-1":  "MetLife Stadium, East Rutherford, NJ",
    "ROUND_OF_16-2":  "SoFi Stadium, Inglewood, CA",
    "ROUND_OF_16-3":  "ATT Stadium, Arlington, TX",
    "ROUND_OF_16-4":  "Hard Rock Stadium, Miami Gardens, FL",
    "ROUND_OF_16-5":  "Levis Stadium, Santa Clara, CA",
    "ROUND_OF_16-6":  "Mercedes-Benz Stadium, Atlanta, GA",
    "ROUND_OF_16-7":  "Rose Bowl, Pasadena, CA",
    "ROUND_OF_16-8":  "Arrowhead Stadium, Kansas City, MO",
    "QUARTER_FINALS-1": "MetLife Stadium, East Rutherford, NJ",
    "QUARTER_FINALS-2": "SoFi Stadium, Inglewood, CA",
    "QUARTER_FINALS-3": "ATT Stadium, Arlington, TX",
    "QUARTER_FINALS-4": "Hard Rock Stadium, Miami Gardens, FL",
    "SEMI_FINALS-1":  "ATT Stadium, Arlington, TX",
    "SEMI_FINALS-2":  "MetLife Stadium, East Rutherford, NJ",
    "THIRD_PLACE-1":  "Hard Rock Stadium, Miami Gardens, FL",
    "PLAY_OFF_FOR_THIRD_PLACE-1": "Hard Rock Stadium, Miami Gardens, FL",
    "FINAL-1":        "MetLife Stadium, East Rutherford, NJ",
}


# ---------------------------------------------------------------------------
# OFFICIAL FIFA MATCH-BASED VENUE OVERRIDE (Round of 32 onward)
# Source: FIFA official schedule, confirmed matchups as of Round of 32 draw.
# Keyed by sorted tuple of (home_team, away_team) lowercase, OR by stage+matchday
# fallback when teams are still TBD/Winner placeholders.
# ---------------------------------------------------------------------------
KNOCKOUT_MATCH_VENUES = {
    # Round of 32 (Match 73-88) - confirmed teams once group stage completed
    frozenset(["south africa", "canada"]): "SoFi Stadium, Inglewood, CA",
    frozenset(["germany", "paraguay"]): "Gillette Stadium, Foxborough, MA",
    frozenset(["netherlands", "morocco"]): "Estadio BBVA, Monterrey, Mexico",
    frozenset(["brazil", "japan"]): "NRG Stadium, Houston, TX",
    frozenset(["france", "sweden"]): "MetLife Stadium, East Rutherford, NJ",
    frozenset(["ivory coast", "norway"]): "ATT Stadium, Arlington, TX",
    frozenset(["côte d'ivoire", "norway"]): "ATT Stadium, Arlington, TX",
    frozenset(["mexico", "ecuador"]): "Estadio Azteca, Mexico City, Mexico",
    frozenset(["england", "congo dr"]): "Mercedes-Benz Stadium, Atlanta, GA",
    frozenset(["england", "dr congo"]): "Mercedes-Benz Stadium, Atlanta, GA",
    frozenset(["usa", "bosnia and herzegovina"]): "Levis Stadium, Santa Clara, CA",
    frozenset(["usa", "bosnia-herzegovina"]): "Levis Stadium, Santa Clara, CA",
    frozenset(["belgium", "senegal"]): "Lumen Field, Seattle, WA",
    frozenset(["portugal", "croatia"]): "BMO Field, Toronto, Canada",
    frozenset(["spain", "austria"]): "SoFi Stadium, Inglewood, CA",
    frozenset(["switzerland", "algeria"]): "BC Place, Vancouver, Canada",
    frozenset(["argentina", "cabo verde"]): "Hard Rock Stadium, Miami Gardens, FL",
    frozenset(["argentina", "cape verde"]): "Hard Rock Stadium, Miami Gardens, FL",
    frozenset(["colombia", "ghana"]): "Arrowhead Stadium, Kansas City, MO",
    frozenset(["australia", "egypt"]): "ATT Stadium, Arlington, TX",
}

# Round of 16 onward: keyed by match number since teams are still "Winner X"
# placeholders until Round of 32 completes. Match number = order in tournament.
MATCH_NUMBER_VENUES = {
    89: "Lincoln Financial Field, Philadelphia, PA",
    90: "NRG Stadium, Houston, TX",
    91: "MetLife Stadium, East Rutherford, NJ",
    92: "Estadio Azteca, Mexico City, Mexico",
    93: "ATT Stadium, Arlington, TX",
    94: "Lumen Field, Seattle, WA",
    95: "Mercedes-Benz Stadium, Atlanta, GA",
    96: "BC Place, Vancouver, Canada",
    97: "Gillette Stadium, Foxborough, MA",
    98: "SoFi Stadium, Inglewood, CA",
    99: "Hard Rock Stadium, Miami Gardens, FL",
    100: "Arrowhead Stadium, Kansas City, MO",
    101: "ATT Stadium, Arlington, TX",
    102: "Mercedes-Benz Stadium, Atlanta, GA",
    103: "Hard Rock Stadium, Miami Gardens, FL",
    104: "MetLife Stadium, East Rutherford, NJ",
}

MATCH_VENUE_OVERRIDE = {
    "france":   "MetLife Stadium, East Rutherford, NJ",
    "iraq":     "Gillette Stadium, Foxborough, MA",
    "norway":   "MetLife Stadium, East Rutherford, NJ",
    "senegal":  "BMO Field, Toronto, Canada",
}

# ---------------------------------------------------------------------------
# ELO RATINGS (as of June 2026, approximate)
# ---------------------------------------------------------------------------
ELO = {
    "France": 2003, "Brazil": 1982, "England": 1968, "Spain": 1966,
    "Argentina": 1960, "Portugal": 1944, "Netherlands": 1938,
    "Germany": 1925, "Belgium": 1912, "Italy": 1905,
    "Uruguay": 1890, "Colombia": 1878, "Mexico": 1872,
    "Croatia": 1865, "Denmark": 1858, "Switzerland": 1850,
    "USA": 1848, "Morocco": 1845, "Japan": 1838, "Senegal": 1830,
    "South Korea": 1822, "Australia": 1815, "Ecuador": 1808,
    "Poland": 1800, "Sweden": 1798, "Norway": 1792,
    "Canada": 1788, "Peru": 1782, "Chile": 1778, "Turkey": 1775,
    "Qatar": 1740, "Iran": 1738, "Saudi Arabia": 1735,
    "Nigeria": 1732, "Ivory Coast": 1728, "Egypt": 1725,
    "Ghana": 1720, "Cameroon": 1715, "Algeria": 1710,
    "Tunisia": 1705, "South Africa": 1700, "Iraq": 1695,
    "Paraguay": 1692, "Bolivia": 1688, "Venezuela": 1685,
    "Panama": 1680, "Costa Rica": 1678, "Honduras": 1670,
    "El Salvador": 1660, "Jamaica": 1655,
    "Haiti": 1640, "New Zealand": 1638, "Slovenia": 1650,
    "Slovakia": 1645, "Czech Republic": 1648, "Austria": 1655,
    "Scotland": 1648, "Czechia": 1648, "Bosnia-Herzegovina": 1635,
    "Curacao": 1580, "Thailand": 1560,
}

def expected_score(rating_a, rating_b):
    """Standard Elo expected-score formula for team A vs team B."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(live_ratings, home, away, home_goals, away_goals, stage):
    """
    Apply one completed match result to the live ratings table in place.
    Uses the classic Elo update with a goal-difference multiplier (common
    in football Elo systems, e.g. the World Football Elo Ratings model)
    and a higher K-factor for knockout matches since they carry more
    tournament significance than group games.
    """
    r_h = live_ratings.get(home, 1700)
    r_a = live_ratings.get(away, 1700)

    if home_goals > away_goals:
        actual_h, actual_a = 1.0, 0.0
    elif home_goals < away_goals:
        actual_h, actual_a = 0.0, 1.0
    else:
        actual_h, actual_a = 0.5, 0.5

    exp_h = expected_score(r_h, r_a)
    exp_a = 1 - exp_h

    # Base K-factor: higher stakes = bigger rating swings
    K = 20 if stage == 'GROUP_STAGE' else 35

    # Goal-difference multiplier (soft cap so blowouts don't dominate)
    gd = abs(home_goals - away_goals)
    gd_multiplier = 1 + min(gd, 4) * 0.18

    delta_h = K * gd_multiplier * (actual_h - exp_h)
    delta_a = K * gd_multiplier * (actual_a - exp_a)

    live_ratings[home] = r_h + delta_h
    live_ratings[away] = r_a + delta_a

def build_live_ratings(all_raw_matches):
    """
    Walk every COMPLETED match in chronological order, starting from the
    static pre-tournament Elo table, applying Elo updates as we go.
    Returns a fresh ratings dict reflecting current tournament form —
    this is what powers win probabilities for all upcoming matches.

    Knockout matches decided on penalties show as a 90-minute draw in the
    fullTime score, but football-data.org's score.winner field correctly
    identifies who actually advanced. We use winner when present so a
    penalty-shootout win still counts as a win for Elo purposes, not a draw.
    """
    live = dict(ELO)  # start from pre-tournament baseline
    completed = [m for m in all_raw_matches if (m.get('status', '').upper() in ('FINISHED', 'AWARDED'))]
    completed.sort(key=lambda m: m.get('utcDate', ''))

    updates_applied = 0
    for m in completed:
        home = m.get('homeTeam', {}).get('name')
        away = m.get('awayTeam', {}).get('name')
        if not home or not away:
            continue
        score = m.get('score', {})
        full = score.get('fullTime', {})
        hg, ag = full.get('home'), full.get('away')
        if hg is None or ag is None:
            continue

        winner = score.get('winner')  # 'HOME_TEAM' / 'AWAY_TEAM' / 'DRAW' / None
        if winner == 'HOME_TEAM' and hg == ag:
            # Penalty-shootout win for home side — nudge goal differential
            # to 1 for Elo purposes so it registers as a win, not a draw.
            hg_for_elo, ag_for_elo = hg + 1, ag
        elif winner == 'AWAY_TEAM' and hg == ag:
            hg_for_elo, ag_for_elo = hg, ag + 1
        else:
            hg_for_elo, ag_for_elo = hg, ag

        update_elo(live, home, away, hg_for_elo, ag_for_elo, m.get('stage', ''))
        updates_applied += 1

    print(f"Live Elo: applied {updates_applied} completed-match updates on top of baseline ratings.")
    return live

def elo_probs(home, away, ratings_table):
    h = ratings_table.get(home, 1700)
    a = ratings_table.get(away, 1700)
    # Standard Elo win probability formula
    exp_h = expected_score(h, a)
    exp_a = 1 - exp_h
    # Allocate draw probability from middle ground
    draw = 0.28 - abs(exp_h - 0.5) * 0.20
    draw = max(0.12, min(0.30, draw))
    win_h = exp_h * (1 - draw / 2)
    win_a = exp_a * (1 - draw / 2)
    total = win_h + draw + win_a
    return {
        "home_win": round(win_h / total * 100),
        "draw": round(draw / total * 100),
        "away_win": round(win_a / total * 100),
    }

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def resolve_venue(match, stage_counter, match_number=None):
    stage = match.get('stage', '')
    group = match.get('group', '') or ''
    matchday = match.get('matchday') or 1
    home_name = (match.get('homeTeam', {}).get('name') or '').lower().strip()
    away_name = (match.get('awayTeam', {}).get('name') or '').lower().strip()

    # GROUP STAGE: team-name override first, then group/matchday map
    if stage == 'GROUP_STAGE':
        if home_name in MATCH_VENUE_OVERRIDE:
            return MATCH_VENUE_OVERRIDE[home_name]
        if group:
            key = f"{group}-{matchday}"
            if key in GROUP_VENUE_MAP:
                return GROUP_VENUE_MAP[key]
        return "Venue TBD"

    # KNOCKOUT: try exact confirmed matchup first (most reliable)
    if home_name and away_name and home_name != 'tbd' and away_name != 'tbd':
        matchup = frozenset([home_name, away_name])
        if matchup in KNOCKOUT_MATCH_VENUES:
            return KNOCKOUT_MATCH_VENUES[matchup]

    # KNOCKOUT: fall back to official match number (for "Winner X" placeholder games)
    if match_number and match_number in MATCH_NUMBER_VENUES:
        return MATCH_NUMBER_VENUES[match_number]

    # Last resort: old slot-counter system (least reliable, used only if above fail)
    count = stage_counter.get(stage, 1)
    key = f"{stage}-{count}"
    if key in KNOCKOUT_VENUE_MAP:
        return KNOCKOUT_VENUE_MAP[key]

    return "Venue TBD"

def to_est(utc_str):
    if not utc_str:
        return None
    try:
        dt_utc = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
        return dt_utc.astimezone(timezone(timedelta(hours=-4))).isoformat()
    except Exception:
        return utc_str

def map_round(match):
    stage = match.get('stage', '')
    group = match.get('group', '')
    stage_map = {
        'GROUP_STAGE': f"Group Stage{' - ' + group if group else ''}",
        'LAST_32': 'Round of 32', 'ROUND_OF_32': 'Round of 32',
        'LAST_16': 'Round of 16', 'ROUND_OF_16': 'Round of 16',
        'QUARTER_FINALS': 'Quarter-final',
        'SEMI_FINALS': 'Semi-final',
        'THIRD_PLACE': 'Third place',
        'PLAY_OFF_FOR_THIRD_PLACE': 'Third place',
        'FINAL': 'Final',
    }
    return stage_map.get(stage, stage or 'Match')

def map_phase(match):
    return 'group' if match.get('stage') == 'GROUP_STAGE' else 'knockout'

def map_status(match):
    s = match.get('status', '').upper()
    if s in ('FINISHED', 'AWARDED'): return 'closed'
    if s in ('IN_PLAY', 'PAUSED', 'LIVE'): return 'live'
    return 'scheduled'

def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Auth-Token": api_key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# ---------------------------------------------------------------------------
# FETCH MATCHES
# ---------------------------------------------------------------------------
try:
    data = fetch_json("https://api.football-data.org/v4/competitions/WC/matches")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")
    sys.exit(1)

raw_matches = sorted(data.get('matches', []), key=lambda m: m.get('utcDate', ''))
print(f"Fetched {len(raw_matches)} matches")

# Build dynamic Elo ratings from completed results before computing any
# win probabilities, so future-match predictions reflect actual tournament
# form rather than frozen pre-tournament reputation.
live_ratings = build_live_ratings(raw_matches)

stage_counter = {}
matches = []
knockout_match_num = 72  # Match 73 is the first knockout game
for m in raw_matches:
    stage = m.get('stage', '')
    if stage != 'GROUP_STAGE':
        stage_counter[stage] = stage_counter.get(stage, 0) + 1
        knockout_match_num += 1

    home = m.get('homeTeam', {}).get('name') or 'TBD'
    away = m.get('awayTeam', {}).get('name') or 'TBD'
    probs = elo_probs(home, away, live_ratings) if home != 'TBD' and away != 'TBD' else None

    score = m.get('score', {})
    full = score.get('fullTime', {})

    venue_name = resolve_venue(m, stage_counter, knockout_match_num if stage != 'GROUP_STAGE' else None)

    matches.append({
        "scheduled": to_est(m.get('utcDate', '')),
        "home_team": {"name": home},
        "away_team": {"name": away},
        "venue": {"name": venue_name},
        "tournament_round": {"name": map_round(m)},
        "phase": map_phase(m),
        "status": map_status(m),
        "score": {
            "home": full.get('home'),
            "away": full.get('away'),
        },
        "win_probability": probs,
    })

metlife = sum(1 for m in matches if 'MetLife' in m['venue']['name'])
print(f"Mapped {len(matches)} matches. MetLife: {metlife}")

# ---------------------------------------------------------------------------
# FETCH STANDINGS
# ---------------------------------------------------------------------------
standings_data = []
try:
    sdata = fetch_json("https://api.football-data.org/v4/competitions/WC/standings")
    for group in sdata.get('standings', []):
        group_name = group.get('group', '')
        table = []
        for row in group.get('table', []):
            table.append({
                "position": row.get('position'),
                "team": row.get('team', {}).get('name', 'TBD'),
                "played": row.get('playedGames', 0),
                "won": row.get('won', 0),
                "drawn": row.get('draw', 0),
                "lost": row.get('lost', 0),
                "gf": row.get('goalsFor', 0),
                "ga": row.get('goalsAgainst', 0),
                "gd": row.get('goalDifference', 0),
                "points": row.get('points', 0),
            })
        standings_data.append({"group": group_name, "table": table})
    print(f"Fetched standings for {len(standings_data)} groups")
except Exception as e:
    print(f"Standings fetch failed (non-fatal): {e}")

# ---------------------------------------------------------------------------
# WRITE OUTPUT
# ---------------------------------------------------------------------------
est = timezone(timedelta(hours=-4))
output = {
    "generated_at": datetime.now(est).isoformat(),
    "match_count": len(matches),
    "matches": matches,
    "standings": standings_data,
    "live_elo_ratings": {k: round(v) for k, v in sorted(live_ratings.items(), key=lambda x: -x[1])},
}

with open("schedule.json", "w") as f:
    json.dump(output, f, indent=2)

print("schedule.json written successfully.")
