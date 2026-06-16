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

def elo_probs(home, away):
    h = ELO.get(home, 1700)
    a = ELO.get(away, 1700)
    # Standard Elo win probability formula
    exp_h = 1 / (1 + 10 ** ((a - h) / 400))
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
def resolve_venue(match, stage_counter):
    stage = match.get('stage', '')
    group = match.get('group', '') or ''
    matchday = match.get('matchday') or 1
    home_name = (match.get('homeTeam', {}).get('name') or '').lower().strip()

    if home_name in MATCH_VENUE_OVERRIDE and stage == 'GROUP_STAGE':
        return MATCH_VENUE_OVERRIDE[home_name]

    if stage == 'GROUP_STAGE' and group:
        key = f"{group}-{matchday}"
        if key in GROUP_VENUE_MAP:
            return GROUP_VENUE_MAP[key]

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

stage_counter = {}
matches = []
for m in raw_matches:
    stage = m.get('stage', '')
    if stage != 'GROUP_STAGE':
        stage_counter[stage] = stage_counter.get(stage, 0) + 1

    home = m.get('homeTeam', {}).get('name') or 'TBD'
    away = m.get('awayTeam', {}).get('name') or 'TBD'
    probs = elo_probs(home, away) if home != 'TBD' and away != 'TBD' else None

    score = m.get('score', {})
    full = score.get('fullTime', {})

    matches.append({
        "scheduled": to_est(m.get('utcDate', '')),
        "home_team": {"name": home},
        "away_team": {"name": away},
        "venue": {"name": resolve_venue(m, stage_counter)},
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
}

with open("schedule.json", "w") as f:
    json.dump(output, f, indent=2)

print("schedule.json written successfully.")
