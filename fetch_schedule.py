import json, urllib.request, urllib.error, os, sys
from datetime import datetime, timezone, timedelta

# Free API from football-data.org — sign up at https://www.football-data.org/client/register
# Store your free API key as GitHub Secret: FOOTBALL_DATA_API_KEY
api_key = os.environ.get('FOOTBALL_DATA_API_KEY', '').strip()
if not api_key:
    print("ERROR: FOOTBALL_DATA_API_KEY secret is not set.")
    print("Sign up free at https://www.football-data.org/client/register")
    print("Then add the key as a GitHub Secret named FOOTBALL_DATA_API_KEY")
    sys.exit(1)

print(f"API key found, last 4: ...{api_key[-4:]}")

# FIFA World Cup 2026 competition ID on football-data.org is WC (or 2000 for World Cup)
# Fetch all matches for the tournament
url = "https://api.football-data.org/v4/competitions/WC/matches"

req = urllib.request.Request(
    url,
    headers={"X-Auth-Token": api_key}
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code} from football-data.org: {body}")
    sys.exit(1)
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)

raw_matches = data.get('matches', [])
print(f"Fetched {len(raw_matches)} matches from football-data.org")

# Venue mapping — football-data.org doesn't always include venue details
# so we map by city/stadium from known FIFA 2026 host city assignments
VENUE_MAP = {
    "New York": "MetLife Stadium, East Rutherford, NJ",
    "New Jersey": "MetLife Stadium, East Rutherford, NJ",
    "East Rutherford": "MetLife Stadium, East Rutherford, NJ",
    "Dallas": "ATT Stadium, Arlington, TX",
    "Arlington": "ATT Stadium, Arlington, TX",
    "Los Angeles": "SoFi Stadium, Inglewood, CA",
    "Inglewood": "SoFi Stadium, Inglewood, CA",
    "San Francisco": "Levis Stadium, Santa Clara, CA",
    "Santa Clara": "Levis Stadium, Santa Clara, CA",
    "Pasadena": "Rose Bowl, Pasadena, CA",
    "Kansas City": "Arrowhead Stadium, Kansas City, MO",
    "Boston": "Gillette Stadium, Foxborough, MA",
    "Foxborough": "Gillette Stadium, Foxborough, MA",
    "Philadelphia": "Lincoln Financial Field, Philadelphia, PA",
    "Miami": "Hard Rock Stadium, Miami Gardens, FL",
    "Atlanta": "Mercedes-Benz Stadium, Atlanta, GA",
    "Houston": "NRG Stadium, Houston, TX",
    "Mexico City": "Estadio Azteca, Mexico City",
    "Monterrey": "Estadio BBVA, Monterrey",
    "Guadalajara": "Estadio Akron, Guadalajara",
    "Vancouver": "BC Place, Vancouver",
    "Toronto": "BMO Field, Toronto",
}

def resolve_venue(match):
    # Try venue name from API first
    venue = match.get('venue', '') or ''
    if venue:
        for key, full in VENUE_MAP.items():
            if key.lower() in venue.lower():
                return full
        return venue
    # Fall back to home team city if available
    area = match.get('homeTeam', {}).get('area', {}).get('name', '')
    for key, full in VENUE_MAP.items():
        if key.lower() in area.lower():
            return full
    return "Venue TBD"

def to_est(utc_str):
    if not utc_str:
        return None
    # Parse UTC datetime string like "2026-06-11T19:00:00Z"
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
    stage = match.get('stage', '')
    return 'group' if stage == 'GROUP_STAGE' else 'knockout'

def map_status(match):
    s = match.get('status', '').upper()
    if s in ('FINISHED', 'AWARDED'): return 'closed'
    if s in ('IN_PLAY', 'PAUSED', 'LIVE'): return 'live'
    return 'scheduled'

matches = []
for m in raw_matches:
    home = m.get('homeTeam', {}).get('name') or 'TBD'
    away = m.get('awayTeam', {}).get('name') or 'TBD'
    utc_dt = m.get('utcDate', '')
    matches.append({
        "scheduled": to_est(utc_dt),
        "home_team": {"name": home},
        "away_team": {"name": away},
        "venue": {"name": resolve_venue(m)},
        "tournament_round": {"name": map_round(m)},
        "phase": map_phase(m),
        "status": map_status(m)
    })

print(f"Mapped {len(matches)} matches.")

est = timezone(timedelta(hours=-4))
output = {
    "generated_at": datetime.now(est).isoformat(),
    "match_count": len(matches),
    "matches": matches
}

with open("schedule.json", "w") as f:
    json.dump(output, f, indent=2)

print("schedule.json written successfully.")
