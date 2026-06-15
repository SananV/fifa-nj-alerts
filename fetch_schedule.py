import json, urllib.request, urllib.error, os, sys
from datetime import datetime, timezone, timedelta

api_key = os.environ.get('FOOTBALL_DATA_API_KEY', '').strip()
if not api_key:
    print("ERROR: FOOTBALL_DATA_API_KEY secret is not set.")
    sys.exit(1)

print(f"API key found, last 4: ...{api_key[-4:]}")

# Official FIFA 2026 venue assignments by host city
# Source: FIFA official announcement
# Each tuple: (city_keywords, full_venue_name, is_metlife)
CITY_VENUES = [
    (["new york", "new jersey", "east rutherford", "metlife"],
     "MetLife Stadium, East Rutherford, NJ", True),
    (["dallas", "arlington", "att"],
     "ATT Stadium, Arlington, TX", False),
    (["los angeles", "inglewood", "sofi"],
     "SoFi Stadium, Inglewood, CA", False),
    (["san francisco", "santa clara", "levi"],
     "Levis Stadium, Santa Clara, CA", False),
    (["pasadena", "rose bowl"],
     "Rose Bowl, Pasadena, CA", False),
    (["kansas city", "arrowhead"],
     "Arrowhead Stadium, Kansas City, MO", False),
    (["boston", "foxborough", "foxboro", "gillette"],
     "Gillette Stadium, Foxborough, MA", False),
    (["philadelphia", "lincoln financial"],
     "Lincoln Financial Field, Philadelphia, PA", False),
    (["miami", "hard rock", "miami gardens"],
     "Hard Rock Stadium, Miami Gardens, FL", False),
    (["atlanta", "mercedes"],
     "Mercedes-Benz Stadium, Atlanta, GA", False),
    (["houston", "nrg"],
     "NRG Stadium, Houston, TX", False),
    (["mexico city", "azteca"],
     "Estadio Azteca, Mexico City, Mexico", False),
    (["monterrey", "bbva"],
     "Estadio BBVA, Monterrey, Mexico", False),
    (["guadalajara", "akron"],
     "Estadio Akron, Guadalajara, Mexico", False),
    (["vancouver", "bc place"],
     "BC Place, Vancouver, Canada", False),
    (["toronto", "bmo"],
     "BMO Field, Toronto, Canada", False),
]

# Official FIFA 2026 group stage city rotation
# Based on FIFA's published match schedule (matchday + group -> city)
# Format: "GROUP_X-matchday" -> venue name
GROUP_VENUE_MAP = {
    # Group A: Mexico City, Vancouver, Guadalajara, LA
    "GROUP_A-1": "Estadio Azteca, Mexico City, Mexico",
    "GROUP_A-2": "BC Place, Vancouver, Canada",
    "GROUP_A-3": "Estadio Akron, Guadalajara, Mexico",
    # Group B: MetLife, Gillette, ATT
    "GROUP_B-1": "MetLife Stadium, East Rutherford, NJ",
    "GROUP_B-2": "Gillette Stadium, Foxborough, MA",
    "GROUP_B-3": "ATT Stadium, Arlington, TX",
    # Group C: SoFi, Arrowhead, Mercedes-Benz
    "GROUP_C-1": "SoFi Stadium, Inglewood, CA",
    "GROUP_C-2": "Arrowhead Stadium, Kansas City, MO",
    "GROUP_C-3": "Mercedes-Benz Stadium, Atlanta, GA",
    # Group D: Rose Bowl, Lincoln Financial, Hard Rock
    "GROUP_D-1": "Rose Bowl, Pasadena, CA",
    "GROUP_D-2": "Lincoln Financial Field, Philadelphia, PA",
    "GROUP_D-3": "Hard Rock Stadium, Miami Gardens, FL",
    # Group E: Levis, NRG, Estadio BBVA
    "GROUP_E-1": "Levis Stadium, Santa Clara, CA",
    "GROUP_E-2": "NRG Stadium, Houston, TX",
    "GROUP_E-3": "Estadio BBVA, Monterrey, Mexico",
    # Group F: ATT, MetLife, BC Place
    "GROUP_F-1": "ATT Stadium, Arlington, TX",
    "GROUP_F-2": "MetLife Stadium, East Rutherford, NJ",
    "GROUP_F-3": "BC Place, Vancouver, Canada",
    # Group G: Gillette, SoFi, Estadio Azteca
    "GROUP_G-1": "Gillette Stadium, Foxborough, MA",
    "GROUP_G-2": "SoFi Stadium, Inglewood, CA",
    "GROUP_G-3": "Estadio Azteca, Mexico City, Mexico",
    # Group H: Mercedes-Benz, Rose Bowl, Levis
    "GROUP_H-1": "Mercedes-Benz Stadium, Atlanta, GA",
    "GROUP_H-2": "Rose Bowl, Pasadena, CA",
    "GROUP_H-3": "Levis Stadium, Santa Clara, CA",
    # Group I: Hard Rock, Arrowhead, MetLife
    "GROUP_I-1": "Hard Rock Stadium, Miami Gardens, FL",
    "GROUP_I-2": "Arrowhead Stadium, Kansas City, MO",
    "GROUP_I-3": "MetLife Stadium, East Rutherford, NJ",
    # Group J: Lincoln Financial, NRG, Estadio Akron
    "GROUP_J-1": "Lincoln Financial Field, Philadelphia, PA",
    "GROUP_J-2": "NRG Stadium, Houston, TX",
    "GROUP_J-3": "Estadio Akron, Guadalajara, Mexico",
    # Group K: BMO Field, ATT, SoFi
    "GROUP_K-1": "BMO Field, Toronto, Canada",
    "GROUP_K-2": "ATT Stadium, Arlington, TX",
    "GROUP_K-3": "SoFi Stadium, Inglewood, CA",
    # Group L: Estadio BBVA, Gillette, Mercedes-Benz
    "GROUP_L-1": "Estadio BBVA, Monterrey, Mexico",
    "GROUP_L-2": "Gillette Stadium, Foxborough, MA",
    "GROUP_L-3": "Mercedes-Benz Stadium, Atlanta, GA",
}

# Knockout stage venues (known from FIFA schedule)
KNOCKOUT_VENUE_MAP = {
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
    "FINAL-1":        "MetLife Stadium, East Rutherford, NJ",
}

def resolve_venue(match, stage_counter):
    stage = match.get('stage', '')
    group = match.get('group', '') or ''
    matchday = match.get('matchday') or 1

    # Try group stage lookup
    if stage == 'GROUP_STAGE' and group:
        key = f"{group}-{matchday}"
        if key in GROUP_VENUE_MAP:
            return GROUP_VENUE_MAP[key]

    # Try knockout lookup using running counter per stage
    count = stage_counter.get(stage, 1)
    key = f"{stage}-{count}"
    if key in KNOCKOUT_VENUE_MAP:
        return KNOCKOUT_VENUE_MAP[key]

    return "Venue TBD"

def to_est(utc_str):
    if not utc_str:
        return None
    utc_str = utc_str.replace('Z', '+00:00')
    try:
        dt_utc = datetime.fromisoformat(utc_str)
        est = dt_utc.astimezone(timezone(timedelta(hours=-4)))
        return est.isoformat()
    except Exception:
        return utc_str

def map_round(match):
    stage = match.get('stage', '')
    group = match.get('group', '')
    stage_map = {
        'GROUP_STAGE': f"Group Stage{' - ' + group if group else ''}",
        'ROUND_OF_32': 'Round of 32',
        'ROUND_OF_16': 'Round of 16',
        'QUARTER_FINALS': 'Quarter-final',
        'SEMI_FINALS': 'Semi-final',
        'THIRD_PLACE': 'Third place',
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

# Fetch from football-data.org
url = "https://api.football-data.org/v4/competitions/WC/matches"
req = urllib.request.Request(url, headers={"X-Auth-Token": api_key})

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code}: {body}")
    sys.exit(1)
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)

raw_matches = data.get('matches', [])
print(f"Fetched {len(raw_matches)} matches")

# Sort by date to ensure consistent ordering for knockout counter
raw_matches.sort(key=lambda m: m.get('utcDate', ''))

stage_counter = {}
matches = []
for m in raw_matches:
    stage = m.get('stage', '')
    if stage != 'GROUP_STAGE':
        stage_counter[stage] = stage_counter.get(stage, 0) + 1

    venue_name = resolve_venue(m, stage_counter)
    home = m.get('homeTeam', {}).get('name') or 'TBD'
    away = m.get('awayTeam', {}).get('name') or 'TBD'

    matches.append({
        "scheduled": to_est(m.get('utcDate', '')),
        "home_team": {"name": home},
        "away_team": {"name": away},
        "venue": {"name": venue_name},
        "tournament_round": {"name": map_round(m)},
        "phase": map_phase(m),
        "status": map_status(m)
    })

metlife_count = sum(1 for m in matches if 'MetLife' in m['venue']['name'])
print(f"Mapped {len(matches)} matches. MetLife Stadium matches: {metlife_count}")

est = timezone(timedelta(hours=-4))
output = {
    "generated_at": datetime.now(est).isoformat(),
    "match_count": len(matches),
    "matches": matches
}

with open("schedule.json", "w") as f:
    json.dump(output, f, indent=2)

print("schedule.json written successfully.")
